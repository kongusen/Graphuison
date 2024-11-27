from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired

def create_topic_model(language="chinese", stop_words=None):
    """
    根据语言配置并创建BERTopic模型。
    """
    if language == "chinese":
        vectorizer_model = CountVectorizer(ngram_range=(2, 4),
                                           stop_words=stop_words)
        sentence_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    else:
        raise NotImplementedError("Currently, only Chinese is supported.")

    umap_model = UMAP(n_neighbors=20, n_components=50, metric="cosine", min_dist=0.0, random_state=37)
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
    representation_model = KeyBERTInspired()

    return BERTopic(verbose=True,
                    umap_model=umap_model,
                    ctfidf_model=ctfidf_model,
                    vectorizer_model=vectorizer_model,
                    embedding_model=sentence_model,
                    representation_model=representation_model,
                    nr_topics=50,
                    low_memory=True,
                    calculate_probabilities=False)