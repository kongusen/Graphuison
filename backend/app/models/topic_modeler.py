# backend/app/models/topic_modeler.py
from gensim import corpora, models
from backend.app.models.embedder import SentenceEmbedder
from typing import List, Dict, Optional
from backend.app.models.text_processor import TextProcessor
import spacy
from bertopic import BERTopic
import asyncio
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from bertopic.representation import MaximalMarginalRelevance
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import logging
import pandas as pd
import jieba
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
from backend.app.config import settings


logger = logging.getLogger(__name__)


class TopicModeler:
    def __init__(self, num_topics=20, embed_model=None, language=None, bertopic_config: Optional[dict] = None):
        self.num_topics = num_topics
        self.embedder = embed_model if embed_model else SentenceEmbedder()
        self.text_processor = TextProcessor(language=language)
        self.language = language if language else settings.DEFAULT_LANGUAGE
        if self.language == "zh":
            self.nlp = spacy.load("zh_core_web_sm")
        else:
            self.nlp = spacy.load("en_core_web_sm")
        self.lemmatizer = WordNetLemmatizer()
        self.jieba_cut = lambda x: " ".join(jieba.cut(x))
        self.bertopic_config = bertopic_config if bertopic_config else {}
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
        self.topic_model = self._get_bertopic_model()  # 初始化BERTopic模型

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
            logger.info(f"Using language {self.language}.")
            logger.info("Language not yet supported for customized vectorizer. Use default.")

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
        words = concept.split()
        singular_words = [self.lemmatizer.lemmatize(word, wordnet.NOUN) for word in words]
        return ' '.join(singular_words)

    async def _extract_concepts(self, sentences: List[str]) -> List[str]:
        """提取概念的通用方法"""
        concepts = []
        try:
            topics, _ = self.topic_model.fit_transform(sentences)
            logger.info(f"BERTopic topics: {topics}")
            logger.info(f"BERTopic topic_info: {self.topic_model.get_topic_info()}")
            for topic in self.topic_model.get_topics():
                topic_words = self.topic_model.get_topic(topic)
                for word, _ in topic_words:
                    try:
                        doc = asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                        doc = await doc
                        for token in doc:
                            if token.pos_ == "NOUN":
                                concepts.append(token.text)
                    except Exception as e:
                        logger.error(f"Error during stanza processing: {e}")
                        continue
        except Exception as e:
           logger.error(f"Error during BERTopic processing: {e}")
           return []
        return list(set(concepts))

    async def _get_concepts_from_str(self, text: str) -> List[str]:
        """从单个字符串中提取概念"""
        try:
            sentences_list, _ = await self.text_processor.preprocess_text(text)
            if not sentences_list:
                 return []
            elif len(sentences_list) == 1:
                 lda_model = await self.train_lda(sentences_list)
                 concepts = []
                 for topic in lda_model.show_topics(formatted=False):
                     for word, _ in topic[1]:
                        try:
                           doc = asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                           doc = await doc
                           for token in doc:
                              if token.pos_ == "NOUN":
                                 concepts.append(token.text)
                        except Exception as e:
                             logger.error(f"Error during stanza processing: {e}")
                             continue
                 return list(set(concepts))
            else:
                 return await self._extract_concepts(sentences_list)

        except Exception as e:
            logger.error(f"Error during topic model process:{e}")
            return []


    async def _get_concepts_from_list(self, sentences: List[str]) -> List[str]:
        try:
             return await self._extract_concepts(sentences)
        except Exception as e:
            logger.error(f"Error during topic model process:{e}")
            return []
    async def _get_concepts_from_dict(self, sentences: List[dict]) -> List[str]:
        try:
             texts = [item["text"] for item in sentences]
             return  await self._extract_concepts(texts)
        except Exception as e:
            logger.error(f"Error during topic model process:{e}")
            return []


    async def _get_concepts_from_nested_list(self, sentences: List[List[str]]) -> List[str]:
        try:
             flat_sentences = [sent for sublist in sentences for sent in sublist]
             return await self._extract_concepts(flat_sentences)
        except Exception as e:
            logger.error(f"Error during topic model process:{e}")
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
                logger.error("sentences parameter does not match the requirement")
                return []
        except Exception as e:
            logger.error(f"Error during BERTopic/LDA processing: {e}")
            raise