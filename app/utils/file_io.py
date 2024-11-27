import json
import pandas as pd

def write_concepts_to_file(concepts, file_path):
    with open(file_path, "w") as f:
        for concept in concepts:
            f.write(f"{concept}\n")

def write_abstracts_to_file(concept_abstracts, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(concept_abstracts, f, ensure_ascii=False, indent=4)