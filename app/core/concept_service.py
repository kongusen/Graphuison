from app.utils.nltk_utils import download_if_needed
from app.utils.bertopic_model import create_topic_model
from app.utils.text_processing import filter_abstracts_by_term

def extract_concepts(input_data):
    download_if_needed("wordnet")
    download_if_needed("omw-1.4")

    topic_model = create_topic_model(language=input_data.config.get('language', 'chinese'), stop_words=input_data.stop_words)
    
    topics, _ = topic_model.fit_transform(input_data.texts)
    all_topics = topic_model.get_topics()

    extracted_concepts = []
    for topic_num, keywords in all_topics.items():
        if topic_num != -1:
            extracted_concepts.extend([word for word, value in keywords])
    extracted_concepts = list(set(extracted_concepts))

    # 调用过滤
    concept_abstracts = {}
    for concept in extracted_concepts:
        filtered_abstracts = filter_abstracts_by_term(concept, input_data.texts)
        concept_abstracts[concept] = {"abstracts": filtered_abstracts, "label": 0}
    
    return {"concepts": extracted_concepts, "abstracts": concept_abstracts}