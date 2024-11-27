from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
import json
from fastapi import HTTPException

def extract_triples(input_data):
    relation_def = input_data.relation_def
    data = input_data.data
    config = input_data.config

    prompt_template_txt = open(config.get('prompt_tpextraction', 'prompts/prompt_tpextraction.txt')).read()
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "您是一个知识图谱构建者。"),
        ("user", prompt_template_txt)
    ])

    model = None  # Loading model logic goes here

    extracted_relations = []
    triples = [] 

    for concept_name, concept_data in data.items():
        abstracts = ' '.join(concept_data['abstracts'])
        prompt = prompt_template.invoke(
            {"abstracts": abstracts[:config.get('max_input_char', 10000)],
             "concepts": [concept_name],
             "relation_definitions": '\n'.join(
                 [f"{rel_type}: {rel_data['description']}" for rel_type, rel_data in
                  relation_def.items()])})
        response = model.invoke(prompt)
        if response != "None":
            response_json = json.loads(response)
            for triple in response_json:
                if triple['p'] not in list(relation_def.keys()):
                    continue
                triples.append(triple)

    if not triples:
        raise HTTPException(status_code=500, detail="No triples extracted.")

    return {"triples": triples}