from gensim import corpora, models
from app.models.embedder import SentenceEmbedder
from typing import List, Dict
from app.models.text_processor import TextProcessor


class TopicModeler:
    def __init__(self, num_topics=20, embed_model=None,language=None):
        self.num_topics = num_topics
        self.embedder = embed_model if embed_model else SentenceEmbedder()
        self.text_processor = TextProcessor(language=language)
        
    def train_lda(self, sentences: List[str]) -> models.LdaModel:
        processed_sentences = [self.text_processor.preprocess_text(sent) for sent in sentences]
        tokens = [item[1][0] for item in processed_sentences]
        dictionary = corpora.Dictionary(tokens)
        corpus = [dictionary.doc2bow(text) for text in tokens]
        
        lda_model = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=self.num_topics,random_state=42)
        return lda_model
    
    def get_concepts(self, lda_model: models.LdaModel) -> List[str]:
        concepts = []
        for topic in lda_model.show_topics(formatted=False):
            concepts.extend([word for word, _ in topic[1]])
        return list(set(concepts))