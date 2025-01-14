import networkx as nx
from typing import List, Tuple, Dict
from app.models.llm_chain import LLMChain
from app.utils.exceptions import LLMException
from llama_index.core import Settings
class GraphFusioner:
    def __init__(self, relation_defs: dict, templates: dict):
        self.relation_defs = relation_defs
        self.templates = templates


    async def fuse_graph(self, triples: List[Tuple[str, str, str]], annotated_triples: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        graph = self.build_graph(annotated_triples)
        fused_triples = []
        llm_chain = LLMChain()
        for concept, concept_triples in self.group_triples(triples).items():
            try:
                prompt = self.format_prompt(concept, concept_triples, graph)
                result = await llm_chain.query_llm(prompt)
                fused_triples.extend(self.parse_result(result))
            except LLMException as e:
                print(f"LLM fusion failed for concept {concept}: {e}")
                continue
        return fused_triples

    def build_graph(self, triples: List[Tuple[str, str, str]]) -> nx.DiGraph:
        graph = nx.DiGraph()
        for s, r, o in triples:
            graph.add_edge(s, o, label=r)
        return graph

    def group_triples(self, triples: List[Tuple[str, str, str]]) -> Dict[str, List[Tuple[str, str, str]]]:
        grouped_triples = {}
        for s, r, o in triples:
            grouped_triples.setdefault(s, []).append((s, r, o))
            grouped_triples.setdefault(o, []).append((s, r, o))
        return grouped_triples

    def format_prompt(self, concept: str, concept_triples: List[Tuple[str, str, str]], graph: nx.DiGraph) -> str:
        prompt = f"Concept: {concept}\n\n"
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

    def parse_result(self, result: str) -> List[Tuple[str, str, str]]:
         triples = []
         for line in result.split("\n"):
            match = re.match(r'(\w+)\s*\((\w+)\)\s*,\s*(\w+)\s*\((\w+)\)\s*,\s*(\w+)', line)
            if match:
               subject, subject_type, relation, object_type, object_ = match.groups()
               triples.append((subject, relation, object_))
         return triples