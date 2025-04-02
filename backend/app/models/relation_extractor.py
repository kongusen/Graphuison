import re
import stanza
from typing import List, Tuple, Dict, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.app.models.llm_chain import LLMChain
from backend.app.utils.exceptions import LLMException
from llama_index.core import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class RelationExtractor:
    def __init__(self, model_name: str, relation_defs: dict, templates: dict, llm_chain: LLMChain):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.relation_defs = relation_defs
        self.templates = templates
        self.nlp = stanza.Pipeline('en', processors="tokenize,lemma,depparse", verbose=False)
        self.llm_chain = llm_chain
        
        # 初始化语义相似度模型
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 关系类型层次结构
        self.relation_hierarchy = self._build_relation_hierarchy()
        
        # 关系提取的置信度阈值
        self.confidence_threshold = 0.6
        
    def _build_relation_hierarchy(self) -> Dict[str, List[str]]:
        """构建关系类型的层次结构"""
        hierarchy = {}
        for relation, definition in self.relation_defs.items():
            # 从定义中提取父关系
            parent_relations = self._extract_parent_relations(definition)
            hierarchy[relation] = parent_relations
        return hierarchy
        
    def _extract_parent_relations(self, definition: str) -> List[str]:
        """从关系定义中提取父关系"""
        parent_relations = []
        # 这里可以添加更复杂的逻辑来从定义中提取父关系
        # 例如通过关键词匹配或语义相似度
        return parent_relations
        
    async def extract_relations(self, text: str, concepts: List[str] | Dict[str, List[str]]) -> Dict[str, List[Tuple[str, str, str]]] | List[Tuple[str, str, str]]:
        """关系提取 - 支持单一粒度和多粒度概念"""
        # 返回结构初始化
        is_multi_granularity = isinstance(concepts, dict)
        if is_multi_granularity:
            relations = {
                'fine': [],
                'medium': [],
                'coarse': [],
                'cross_granularity': []
            }
        else:
            # 单一粒度模式
            return await self._extract_relations_single_granularity(text, concepts)
        
        try:
            # 多粒度模式
            # 对每个粒度级别提取关系
            for level, level_concepts in concepts.items():
                level_relations = await self._extract_relations_single_granularity(text, level_concepts)
                relations[level].extend(level_relations)
            
            # 提取跨粒度关系
            cross_granularity_relations = self._extract_cross_granularity_relations(concepts, text)
            relations['cross_granularity'].extend(cross_granularity_relations)
            
            return relations
            
        except Exception as e:
            logger.error(f"Error during relation extraction: {e}")
            if is_multi_granularity:
                return relations
            else:
                return []
    
    async def _extract_relations_single_granularity(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        """提取单一粒度级别的关系"""
        relations = []
        for concept in concepts:
            try:
                prompt = self.format_prompt(text, concept)
                result = await self.llm_chain.query_llm(prompt)
                extracted_relations = self.parse_result(result)
                
                # 验证和过滤关系
                for relation in extracted_relations:
                    if self.validate_triple(relation):
                        confidence = self._calculate_relation_confidence(relation, text)
                        if confidence >= self.confidence_threshold:
                            relations.append(relation)
                    
            except LLMException as e:
                logger.error(f"LLM extraction failed for concept {concept}: {e}")
                continue
        
        return relations
        
    def _calculate_relation_confidence(self, relation: Tuple[str, str, str], context: str) -> float:
        """计算关系的置信度"""
        subject, relation_type, object_ = relation
        
        # 计算关系类型与上下文的语义相似度
        relation_embedding = self.sentence_model.encode(relation_type)
        context_embedding = self.sentence_model.encode(context)
        similarity = np.dot(relation_embedding, context_embedding) / (
            np.linalg.norm(relation_embedding) * np.linalg.norm(context_embedding)
        )
        
        # 考虑关系类型的层次结构
        hierarchy_factor = self._get_hierarchy_factor(relation_type)
        
        return similarity * hierarchy_factor
        
    def _get_hierarchy_factor(self, relation_type: str) -> float:
        """基于关系层次结构计算因子"""
        if relation_type in self.relation_hierarchy:
            # 如果关系有父关系，降低其权重
            return 0.8 if self.relation_hierarchy[relation_type] else 1.0
        return 1.0
        
    def _extract_cross_granularity_relations(self, concepts: Dict[str, List[str]], text: str) -> List[Tuple[str, str, str]]:
        """提取跨粒度关系"""
        cross_relations = []
        
        # 获取不同粒度级别的概念
        fine_concepts = concepts['fine']
        medium_concepts = concepts['medium']
        coarse_concepts = concepts['coarse']
        
        # 计算概念之间的语义相似度
        concept_embeddings = {}
        for level, level_concepts in concepts.items():
            for concept in level_concepts:
                concept_embeddings[concept] = self.sentence_model.encode(concept)
        
        # 在不同粒度级别之间建立关系
        for fine_concept in fine_concepts:
            for medium_concept in medium_concepts:
                if self._are_concepts_related(fine_concept, medium_concept, concept_embeddings):
                    cross_relations.append((fine_concept, "BELONGS_TO", medium_concept))
                    
            for coarse_concept in coarse_concepts:
                if self._are_concepts_related(fine_concept, coarse_concept, concept_embeddings):
                    cross_relations.append((fine_concept, "BELONGS_TO", coarse_concept))
        
        return cross_relations
        
    def _are_concepts_related(self, concept1: str, concept2: str, embeddings: Dict[str, np.ndarray]) -> bool:
        """判断两个概念是否相关"""
        if concept1 not in embeddings or concept2 not in embeddings:
            return False
            
        similarity = np.dot(embeddings[concept1], embeddings[concept2]) / (
            np.linalg.norm(embeddings[concept1]) * np.linalg.norm(embeddings[concept2])
        )
        
        return similarity > 0.7  # 相似度阈值
        
    def format_prompt(self, text: str, concept: str) -> str:
        """格式化提示词"""
        prompt = f"Text: {text}\n\nConcept: {concept}\n\n"
        for relation, definition in self.relation_defs.items():
            prompt += f"{relation}: {definition}\n\n"
        prompt += self.templates["relation_extraction"]
        return prompt
        
    def parse_result(self, result: str) -> List[Tuple[str, str, str]]:
        """解析LLM返回的结果"""
        triples = []
        for line in result.split("\n"):
            match = re.match(r'(\w+)\s*\((\w+)\)\s*,\s*(\w+)\s*\((\w+)\)\s*,\s*(\w+)', line)
            if match:
                subject, subject_type, relation, object_type, object_ = match.groups()
                if self.validate_triple((subject, relation, object_)):
                    triples.append((subject, relation, object_))
        return triples
        
    def validate_triple(self, triple: Tuple[str, str, str]) -> bool:
        """验证三元组的有效性"""
        subject, relation, object_ = triple
        doc = self.nlp(f"{subject} {relation} {object_}")
        for sent in doc.sentences:
            if sent.dependencies:
                return True
        return False