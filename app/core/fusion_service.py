from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Dict, List
import json
from tqdm import tqdm

def fuse_triples(input_data):
    candidate_triples = input_data.candidate_triples
    data = input_data.data
    relation_def = input_data.relation_def
    config = input_data.config

    prompt_template_txt = open(config.get('prompt_fusion', 'prompts/prompt_fusion.txt')).read()
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "您是一个知识图谱构建者。"),
        ("user", prompt_template_txt)
    ])
    model = None # Loading model logic goes here

    fused_triplets = []

    for candidate_triple in tqdm(candidate_triples, desc="Fusing triples"):
        # Assume your fusion logic here
        # This should analyze candidate_triple with existing knowledge graph
        response = model.invoke(prompt)
        if response != "None":
            fused_triplets.append(json.loads(response))

    if not fused_triplets:
        raise HTTPException(status_code=500, detail="No triples fused.")

    return {"fused_triples": fused_triplets}