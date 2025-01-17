from gensim import corpora, models
from backend.app.models.embedder import SentenceEmbedder
from typing import List, Dict, Optional
from backend.app.models.text_processor import TextProcessor
import stanza
from bertopic import BERTopic
import asyncio
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from bertopic.representation import MaximalMarginalRelevance
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import logging
import jieba
from sentence_transformers import SentenceTransformer
import umap


class TopicModeler:
    def __init__(self, num_topics=20, embed_model=None, language=None, bertopic_config: Optional[dict] = None):
        self.num_topics = num_topics
        self.embedder = embed_model if embed_model else SentenceEmbedder()
        self.text_processor = TextProcessor(language=language)
        self.nlp = stanza.Pipeline(language if language else 'en', processors="tokenize,pos", verbose=False)
        self.lemmatizer = WordNetLemmatizer()
        self.language = language if language else 'en'
        self.jieba_cut = lambda x: " ".join(jieba.cut(x))
        self.bertopic_config = bertopic_config if bertopic_config else {}
        self.logger = logging.getLogger(__name__)
        self.sentence_model_zh = None

        self.umap_model = umap.UMAP(n_neighbors=15,
                                    n_components=5,
                                    metric='cosine',
                                    random_state=42,
                                    min_dist=0.0)

        self.ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
        self.representation_model = KeyBERTInspired()
        self.representation_model_mmr = MaximalMarginalRelevance(diversity=0.2)
        self.vectorizer_model = None

    def _get_bertopic_model(self):
        """初始化BERTopic模型"""
        if self.language == "zh":
            if not self.sentence_model_zh:
                self.sentence_model_zh = SentenceTransformer('moka-ai/m3e-base',
                                                             device=self.embedder.device)
            self.vectorizer_model = CountVectorizer(ngram_range=(1, 2),
                                                    stop_words=None,
                                                    preprocessor=self.jieba_cut)
            sentence_model = self.sentence_model_zh
        else:

            sentence_model = self.embedder._model
            self.logger.info(f"Using language {self.language}.")
            self.logger.info("Language not yet supported for customized vectorizer. Use default.")

        model = BERTopic(verbose=True,
                         umap_model=self.umap_model,
                         ctfidf_model=self.ctfidf_model,
                         vectorizer_model=self.vectorizer_model,
                         embedding_model=sentence_model,
                         representation_model=self.representation_model_mmr,
                         nr_topics=None,
                         low_memory=True,
                         calculate_probabilities=False,
                         **self.bertopic_config)
        return model

    async def train_lda(self, sentences: List[str]) -> models.LdaModel:
        processed_sentences = []
        for sent in sentences:
            processed_sentences.append(await self.text_processor.preprocess_text(sent))
        tokens = []
        for item in processed_sentences:
            tokens.extend([token for tokens_list in item[1] for token in tokens_list])
        dictionary = corpora.Dictionary(tokens)
        corpus = [dictionary.doc2bow(text) for text in tokens]
        lda_model = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=self.num_topics, random_state=42)
        return lda_model

    def singularize_concept(self, concept):
        words = concept.split()  # 将概念拆分为单词
        singular_words = [self.lemmatizer.lemmatize(word, wordnet.NOUN) for word in words]  # 进行词形还原
        return ' '.join(singular_words)  # 返回还原后的单词组成的概念

    async def _get_concepts_from_str(self, text: str) -> List[str]:
        """从单个字符串中提取概念"""
        sentences_list, _ = await self.text_processor.preprocess_text(text)
        if not sentences_list:
            return []
        elif len(sentences_list) == 1:
            lda_model = await self.train_lda(sentences_list)
            concepts = []
            for topic in lda_model.show_topics(formatted=False):
                for word, _ in topic[1]:
                    try:
                        doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                        for sent in doc.sentences:
                            for token in sent.tokens:
                                if token.xpos.startswith("NN"):
                                    concepts.append(token.text)
                    except Exception as e:
                        self.logger.error(f"Error during stanza processing: {e}")
                        continue
            return list(set(concepts))
        else:
            topic_model = self._get_bertopic_model()
            try:
                topics, _ = topic_model.fit_transform(sentences_list)
                self.logger.info(f"BERTopic topics: {topics}")
                self.logger.info(f"BERTopic topic_info: {topic_model.get_topic_info()}")
                concepts = []
                for topic in topic_model.get_topics():
                    topic_words = topic_model.get_topic(topic)
                    for word, _ in topic_words:
                        try:
                            doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                            for sent in doc.sentences:
                                for token in sent.tokens:
                                    if token.xpos.startswith("NN"):
                                        concepts.append(token.text)
                        except Exception as e:
                            self.logger.error(f"Error during stanza processing: {e}")
                            continue
                return list(set(concepts))
            except Exception as e:
                self.logger.error(f"Error during BERTopic processing: {e}")
                return []

    async def _get_concepts_from_list(self, sentences: List[str]) -> List[str]:
        try:
            topic_model = self._get_bertopic_model()
            topics, _ = topic_model.fit_transform(sentences)
            self.logger.info(f"BERTopic topics: {topics}")
            self.logger.info(f"BERTopic topic_info: {topic_model.get_topic_info()}")
            concepts = []
            for topic in topic_model.get_topics():
                topic_words = topic_model.get_topic(topic)
                for word, _ in topic_words:
                    try:
                        doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                        for sent in doc.sentences:
                            for token in sent.tokens:
                                if token.xpos.startswith("NN"):
                                    concepts.append(token.text)
                    except Exception as e:
                        self.logger.error(f"Error during stanza processing: {e}")
                        continue
            return list(set(concepts))
        except Exception as e:
            self.logger.error(f"Error during BERTopic processing: {e}")
            return []

    async def _get_concepts_from_dict(self, sentences: List[dict]) -> List[str]:
        try:
            texts = [item["text"] for item in sentences]
            topic_model = self._get_bertopic_model()
            topics, _ = topic_model.fit_transform(texts)
            self.logger.info(f"BERTopic topics: {topics}")
            self.logger.info(f"BERTopic topic_info: {topic_model.get_topic_info()}")
            concepts = []
            for topic in topic_model.get_topics():
                topic_words = topic_model.get_topic(topic)
                for word, _ in topic_words:
                    try:
                        doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                        for sent in doc.sentences:
                            for token in sent.tokens:
                                if token.xpos.startswith("NN"):
                                    concepts.append(token.text)
                    except Exception as e:
                        self.logger.error(f"Error during stanza processing: {e}")
                        continue
            return list(set(concepts))
        except Exception as e:
            self.logger.error(f"Error during BERTopic processing: {e}")
            return []

    async def _get_concepts_from_nested_list(self, sentences: List[List[str]]) -> List[str]:
        try:
            flat_sentences = [sent for sublist in sentences for sent in sublist]
            topic_model = self._get_bertopic_model()
            topics, _ = topic_model.fit_transform(flat_sentences)
            self.logger.info(f"BERTopic topics: {topics}")
            self.logger.info(f"BERTopic topic_info: {topic_model.get_topic_info()}")
            concepts = []
            for topic in topic_model.get_topics():
                topic_words = topic_model.get_topic(topic)
                for word, _ in topic_words:
                    try:
                        doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                        for sent in doc.sentences:
                            for token in sent.tokens:
                                if token.xpos.startswith("NN"):
                                    concepts.append(token.text)
                    except Exception as e:
                        self.logger.error(f"Error during stanza processing: {e}")
                        continue
            return list(set(concepts))
        except Exception as e:
            self.logger.error(f"Error during BERTopic processing: {e}")
            return []

    async def get_concepts(self, sentences: List) -> List[str]:
        try:
            if not sentences:
                return []

            if isinstance(sentences[0], str):
                return await self._get_concepts_from_str(sentences[0] if len(sentences) == 1 else sentences)
            elif isinstance(sentences[0], dict):
                return await self._get_concepts_from_dict(sentences)
            elif isinstance(sentences[0], list):
                return await self._get_concepts_from_nested_list(sentences)
            else:
                self.logger.error("sentences parameter does not match the requirement")
                return []
        except Exception as e:
            self.logger.error(f"Error during BERTopic/LDA processing: {e}")
            raise