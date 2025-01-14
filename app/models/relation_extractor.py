import re
import stanza
from typing import List, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.models.llm_chain import LLMChain
from app.utils.exceptions import LLMException
from llama_index.core import Settings


class RelationExtractor:
    def __init__(self, model_name: str, relation_defs: dict, templates: dict):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.relation_defs = relation_defs
        self.templates = templates
        self.nlp = stanza.Pipeline('en',processors="tokenize,lemma,depparse",verbose=False)
    async def extract_relations(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        triples = []
        llm_chain=LLMChain()
        for concept in concepts:
            try:
                prompt = self.format_prompt(text, concept)
                result = await llm_chain.query_llm(prompt)
                triples.extend(self.parse_result(result))
            except LLMException as e:
                 # 这里记录详细的异常信息
                print(f"LLM 提取失败，跳过 concept {concept}：{e}")
                continue
        return triples

    def format_prompt(self, text: str, concept: str) -> str:
        prompt = f"Text: {text}\n\nConcept: {concept}\n\n"
        for relation, definition in self.relation_defs.items():
            prompt += f"{relation}: {definition}\n\n"
        prompt += self.templates["relation_extraction"]
        return prompt

    def parse_result(self, result: str) -> List[Tuple[str, str, str]]:
        triples = []
        for line in result.split("\n"):
            match = re.match(r'(\w+)\s*\((\w+)\)\s*,\s*(\w+)\s*\((\w+)\)\s*,\s*(\w+)', line)
            if match:
                subject, subject_type, relation, object_type, object_ = match.groups()
                if self.validate_triple((subject, relation, object_)):
                    triples.append((subject, relation, object_))
        return triples

    def validate_triple(self, triple: Tuple[str, str, str]) -> bool:
        subject, relation, object_ = triple
        doc = self.nlp(f"{subject} {relation} {object_}")
        for sent in doc.sentences:
            if sent.dependencies:
                return True
        return False