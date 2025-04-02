# backend/app/models/graph_fusioner.py
import networkx as nx
import re
from typing import List, Tuple, Dict, Optional
from backend.app.models.llm_chain import LLMChain
from backend.app.utils.exceptions import LLMException
from llama_index.core import Settings
import logging
from backend.app.utils.database import neo4j_client
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict

logger = logging.getLogger(__name__)


class GraphFusioner:
    TRIPLE_REGEX = re.compile(r'(\w+)\s*\((\w+)\)\s*,\s*(\w+)\s*\((\w+)\)\s*,\s*(\w+)')
    
    def __init__(self, relation_defs: dict, templates: dict):
        self.relation_defs = relation_defs
        self.templates = templates
        self.llm_chain = LLMChain()
        
        # 初始化语义相似度模型
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 图融合的置信度阈值
        self.confidence_threshold = 0.7
        
        # 多粒度图的权重
        self.granularity_weights = {
            'fine': 1.0,
            'medium': 0.8,
            'coarse': 0.6,
            'cross_granularity': 0.9
        }

    async def fuse_graph(self, triples, annotated_triples=None):
        """图融合 - 支持单一粒度和多粒度三元组
        
        参数:
            triples: 可以是单一级别的三元组列表 List[Tuple[str, str, str]] 
                    或多粒度三元组字典 Dict[str, List[Tuple[str, str, str]]]
            annotated_triples: 可选，标注的三元组，格式同triples
            
        返回:
            单一粒度模式: List[Tuple[str, str, str]]
            多粒度模式: Dict[str, List[Tuple[str, str, str]]]
        """
        try:
            neo4j_client.connect()
            
            # 判断是否为多粒度模式
            is_multi_granularity = isinstance(triples, dict)
            
            if not is_multi_granularity:
                # 单一粒度模式
                return await self._fuse_graph_single_granularity(triples, annotated_triples or triples)
            
            # 多粒度模式
            # 构建多粒度知识图
            graphs = self._build_multi_granularity_graphs(annotated_triples or triples)
            
            # 融合后的多粒度图
            fused_graphs = {
                'fine': [],
                'medium': [],
                'coarse': [],
                'cross_granularity': []
            }
            
            # 对每个粒度级别进行图融合
            for level, level_triples in triples.items():
                if level == 'cross_granularity':
                    continue
                    
                graph = graphs[level]
                fused_level_triples = await self._fuse_graph_single_granularity(level_triples, level_triples, graph, level)
                fused_graphs[level].extend(fused_level_triples)
            
            # 处理跨粒度关系
            cross_granularity_triples = self._process_cross_granularity_relations(triples, graphs)
            fused_graphs['cross_granularity'].extend(cross_granularity_triples)
            
            # 将融合后的图写入数据库
            self._write_to_database(fused_graphs)
            
            neo4j_client.close()
            return fused_graphs
            
        except Exception as e:
            logger.error(f"An unexpected error occurred in graph fusioner: {e}")
            if is_multi_granularity:
                return {level: [] for level in ['fine', 'medium', 'coarse', 'cross_granularity']}
            else:
                return []
                
    async def _fuse_graph_single_granularity(self, triples, annotated_triples, graph=None, level=None):
        """融合单一粒度级别的图"""
        if graph is None:
            # 构建图
            graph = nx.DiGraph()
            for s, r, o in annotated_triples:
                graph.add_edge(s, o, label=r, level=level or 'default')
                
        fused_triples = []
        for concept, concept_triples in self._group_triples(triples).items():
            try:
                prompt = self._format_prompt(concept, concept_triples, graph, level or 'default')
                result = await self.llm_chain.query_llm(prompt)
                parsed_triples = self._parse_result(result)
                
                # 验证和过滤融合后的三元组
                for triple in parsed_triples:
                    confidence = self._calculate_triple_confidence(triple, graph, level or 'default')
                    if confidence >= self.confidence_threshold:
                        fused_triples.append(triple)
                        
            except LLMException as e:
                logger.error(f"LLM fusion failed for concept {concept}: {e}")
                continue
            except Exception as e:
                logger.error(f"An unexpected error occurred when fusion graph for concept {concept}: {e}")
                continue
                
        return fused_triples

    def _build_multi_granularity_graphs(self, annotated_triples: Dict[str, List[Tuple[str, str, str]]]) -> Dict[str, nx.DiGraph]:
        """构建多粒度知识图"""
        graphs = {}
        for level, triples in annotated_triples.items():
            graph = nx.DiGraph()
            for s, r, o in triples:
                graph.add_edge(s, o, label=r, level=level)
            graphs[level] = graph
        return graphs

    def _group_triples(self, triples: List[Tuple[str, str, str]]) -> Dict[str, List[Tuple[str, str, str]]]:
        """按概念分组三元组"""
        grouped_triples = defaultdict(list)
        for s, r, o in triples:
            grouped_triples[s].append((s, r, o))
            grouped_triples[o].append((s, r, o))
        return dict(grouped_triples)

    def _format_prompt(self, concept: str, concept_triples: List[Tuple[str, str, str]], 
                      graph: nx.DiGraph, level: str) -> str:
        """格式化提示词"""
        prompt = f"Concept: {concept}\nGranularity Level: {level}\n\n"
        prompt += "Candidate Triples:\n"
        for s, r, o in concept_triples:
            prompt += f"{s} ({r}) {o}\n"
        prompt += "\nPrior Knowledge Graph:\n"
        for n1, n2, data in graph.edges(data=True):
            prompt += f"{n1} ({data['label']}) {n2}\n"
        for relation, definition in self.relation_defs.items():
            prompt += f"{relation}: {definition}\n"
        prompt += self.templates["graph_fusion"]
        return prompt

    def _parse_result(self, result: str) -> List[Tuple[str, str, str]]:
        """解析LLM返回的结果"""
        triples = []
        for line in result.split("\n"):
            match = GraphFusioner.TRIPLE_REGEX.match(line)
            if match:
                subject, subject_type, relation, object_type, object_ = match.groups()
                triples.append((subject, relation, object_))
        return triples

    def _calculate_triple_confidence(self, triple: Tuple[str, str, str], 
                                   graph: nx.DiGraph, level: str) -> float:
        """计算三元组的置信度"""
        subject, relation, object_ = triple
        
        # 计算关系类型与图中已有关系的语义相似度
        relation_embedding = self.sentence_model.encode(relation)
        graph_relations = [data['label'] for _, _, data in graph.edges(data=True)]
        
        if not graph_relations:
            return 1.0
            
        graph_embeddings = self.sentence_model.encode(graph_relations)
        similarities = np.dot(relation_embedding, graph_embeddings.T) / (
            np.linalg.norm(relation_embedding) * np.linalg.norm(graph_embeddings, axis=1)
        )
        
        # 考虑粒度级别的权重
        granularity_weight = self.granularity_weights[level]
        
        # 计算路径相似度
        path_similarity = self._calculate_path_similarity(subject, object_, graph)
        
        return (np.max(similarities) * 0.6 + path_similarity * 0.4) * granularity_weight

    def _calculate_path_similarity(self, subject: str, object_: str, graph: nx.DiGraph) -> float:
        """计算两个节点之间的路径相似度"""
        try:
            # 计算最短路径
            path = nx.shortest_path(graph, subject, object_)
            if len(path) <= 2:
                return 1.0
                
            # 路径越长，相似度越低
            return 1.0 / (len(path) - 1)
        except nx.NetworkXNoPath:
            return 0.0

    def _process_cross_granularity_relations(self, triples: Dict[str, List[Tuple[str, str, str]]], 
                                           graphs: Dict[str, nx.DiGraph]) -> List[Tuple[str, str, str]]:
        """处理跨粒度关系"""
        cross_relations = []
        
        # 获取不同粒度级别的概念
        fine_concepts = set(s for s, _, _ in triples['fine'])
        medium_concepts = set(s for s, _, _ in triples['medium'])
        coarse_concepts = set(s for s, _, _ in triples['coarse'])
        
        # 计算概念之间的语义相似度
        concept_embeddings = {}
        for level, level_triples in triples.items():
            for s, _, o in level_triples:
                for concept in [s, o]:
                    if concept not in concept_embeddings:
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

    def _are_concepts_related(self, concept1: str, concept2: str, 
                            embeddings: Dict[str, np.ndarray]) -> bool:
        """判断两个概念是否相关"""
        if concept1 not in embeddings or concept2 not in embeddings:
            return False
            
        similarity = np.dot(embeddings[concept1], embeddings[concept2]) / (
            np.linalg.norm(embeddings[concept1]) * np.linalg.norm(embeddings[concept2])
        )
        
        return similarity > 0.7  # 相似度阈值

    def _write_to_database(self, fused_graphs: Dict[str, List[Tuple[str, str, str]]]):
        """将融合后的图写入数据库"""
        try:
            for level, triples in fused_graphs.items():
                for s, r, o in triples:
                    try:
                        source_id = neo4j_client.create_node(s, f'entity_{level}')
                        target_id = neo4j_client.create_node(o, f'entity_{level}')
                        if source_id and target_id:
                            neo4j_client.create_relationship(source_id, target_id, r)
                    except Exception as e:
                        logger.error(f"Error writing triple ({s}, {r}, {o}) to database: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error writing to database: {e}")