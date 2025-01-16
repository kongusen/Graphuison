import traceback

from gensim import corpora, models
from backend.app.models.embedder import SentenceEmbedder
from typing import List, Dict
from backend.app.models.text_processor import TextProcessor
import stanza
from bertopic import BERTopic
import asyncio
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import logging
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopicModeler:
    def __init__(self, num_topics=20, embed_model=None, language=None):
        self.num_topics = num_topics
        self.embedder = embed_model if embed_model else SentenceEmbedder()
        self.language = language
        self.text_processor = TextProcessor(language=language)
        self.nlp = stanza.Pipeline(language if language else 'en', processors="tokenize,pos", verbose=False)
        self.lemmatizer = WordNetLemmatizer()

    async def train_lda(self, sentences: List[str]) -> models.LdaModel:
        processed_sentences = []
        for sent in sentences:
            processed_sentences.append(await self.text_processor.preprocess_text(sent))
        tokens = [item[1][0] for item in processed_sentences]
        dictionary = corpora.Dictionary(tokens)
        corpus = [dictionary.doc2bow(text) for text in tokens]
        lda_model = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=self.num_topics, random_state=42)
        return lda_model

    def singularize_concept(self, concept):
        words = concept.split()  # 将概念拆分为单词
        singular_words = [self.lemmatizer.lemmatize(word, wordnet.NOUN) for word in words]  # 进行词形还原
        return ' '.join(singular_words)  # 返回还原后的单词组成的概念

    async def get_concepts(self, sentences: List) -> List[str]:
        try:
            if not sentences:
                return []

            if isinstance(sentences[0], str):
                if len(sentences) == 1:
                    # 单句情况，使用分句后的句子列表进行处理
                    text = sentences[0]
                    sentences_list, _ = await self.text_processor.preprocess_text(text)
                    if not sentences_list or len(sentences_list) == 0:
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
                                            if token.upos == "NOUN":
                                                concepts.append(token.text)
                                except Exception as e:
                                    # 打印堆栈信息
                                    error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
                                    logger.error(error_message)
                                    print(f"Error during stanza processing: {e}")
                                    continue
                        return list(set(concepts))
                    else:
                        # 多句情况，用 BERTopic 处理
                        if self.language == "zh":
                            vectorizer_model = CountVectorizer(ngram_range=(2, 4), stop_words=None)
                            sentence_model = self.embedder._model
                        else:
                            vectorizer_model = None
                            sentence_model = self.embedder._model
                            logging.info(f"Using language {self.language}.")
                            logging.info("Language not yet supported for customized vectorizer. Use default.")
                        ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
                        representation_model = KeyBERTInspired()
                        topic_model = BERTopic(verbose=True,
                                               umap_model=None,
                                               ctfidf_model=ctfidf_model,
                                               vectorizer_model=vectorizer_model,
                                               embedding_model=sentence_model,
                                               representation_model=representation_model,
                                               nr_topics=None,
                                               low_memory=True,
                                               calculate_probabilities=False,
                                               min_topic_size=5)
                        topics, _ = topic_model.fit_transform(sentences_list)
                        print(f"BERTopic topics: {topics}")
                        print(f"BERTopic topic_info: {topic_model.get_topic_info()}")
                        concepts = []
                        for topic in topic_model.get_topics():
                            topic_words = topic_model.get_topic(topic)
                            for word, _ in topic_words:
                                try:
                                    doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                                    for sent in doc.sentences:
                                        for token in sent.tokens:
                                            for word in token.words:
                                                if word.pos == "NOUN":
                                                    concepts.append(word.text)
                                except Exception as e:
                                    # 打印堆栈信息
                                    error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
                                    logger.error(error_message)
                                    print(f"Error during stanza processing: {e}")
                                    continue
                        return list(set(concepts))
                else:
                    # 多句情况，用 BERTopic 处理
                    if self.language == "zh":
                        vectorizer_model = CountVectorizer(ngram_range=(2, 4), stop_words=None)
                        sentence_model = self.embedder._model
                    else:
                        vectorizer_model = None
                        sentence_model = self.embedder._model
                        logging.info(f"Using language {self.language}.")
                        logging.info("Language not yet supported for customized vectorizer. Use default.")
                    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
                    representation_model = KeyBERTInspired()
                    topic_model = BERTopic(verbose=True,
                                           umap_model=None,
                                           ctfidf_model=ctfidf_model,
                                           vectorizer_model=vectorizer_model,
                                           embedding_model=sentence_model,
                                           representation_model=representation_model,
                                           nr_topics=None,
                                           low_memory=True,
                                           calculate_probabilities=False)
                    topics, _ = topic_model.fit_transform(sentences)
                    print(f"BERTopic topics: {topics}")
                    print(f"BERTopic topic_info: {topic_model.get_topic_info()}")
                    concepts = []
                    for topic in topic_model.get_topics():
                        topic_words = topic_model.get_topic(topic)
                        for word, _ in topic_words:
                            try:
                                doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                                for sent in doc.sentences:
                                    for token in sent.tokens:
                                        if token.upos == "NOUN":
                                            concepts.append(token.text)
                            except Exception as e:
                                # 打印堆栈信息
                                error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
                                logger.error(error_message)
                                print(f"Error during stanza processing: {e}")
                                continue
                    return list(set(concepts))
            elif isinstance(sentences[0], dict):
                # 处理包含元数据的字典列表
                texts = [item["text"] for item in sentences]
                if self.language == "zh":
                    vectorizer_model = CountVectorizer(ngram_range=(2, 4), stop_words=None)
                    sentence_model = self.embedder._model
                else:
                    vectorizer_model = None
                    sentence_model = self.embedder._model
                    logging.info(f"Using language {self.language}.")
                    logging.info("Language not yet supported for customized vectorizer. Use default.")
                ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
                representation_model = KeyBERTInspired()
                topic_model = BERTopic(verbose=True,
                                       umap_model=None,
                                       ctfidf_model=ctfidf_model,
                                       vectorizer_model=vectorizer_model,
                                       embedding_model=sentence_model,
                                       representation_model=representation_model,
                                       nr_topics=None,
                                       low_memory=True,
                                       calculate_probabilities=False)
                topics, _ = topic_model.fit_transform(texts)
                print(f"BERTopic topics: {topics}")
                print(f"BERTopic topic_info: {topic_model.get_topic_info()}")
                concepts = []
                for topic in topic_model.get_topics():
                    topic_words = topic_model.get_topic(topic)
                    for word, _ in topic_words:
                        try:
                            doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                            for sent in doc.sentences:
                                for token in sent.tokens:
                                    if token.upos == "NOUN":
                                        concepts.append(token.text)
                        except Exception as e:
                            # 打印堆栈信息
                            error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
                            logger.error(error_message)
                            print(f"Error during stanza processing: {e}")
                            continue
                return list(set(concepts))
            elif isinstance(sentences[0], list):
                # 处理句子列表的列表
                flat_sentences = [sent for sublist in sentences for sent in sublist]
                if self.language == "zh":
                    vectorizer_model = CountVectorizer(ngram_range=(2, 4), stop_words=None)
                    sentence_model = self.embedder._model
                else:
                    vectorizer_model = None
                    sentence_model = self.embedder._model
                    logging.info(f"Using language {self.language}.")
                    logging.info("Language not yet supported for customized vectorizer. Use default.")
                ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=False)
                representation_model = KeyBERTInspired()
                topic_model = BERTopic(verbose=True,
                                       umap_model=None,
                                       ctfidf_model=ctfidf_model,
                                       vectorizer_model=vectorizer_model,
                                       embedding_model=sentence_model,
                                       representation_model=representation_model,
                                       nr_topics=None,
                                       low_memory=True,
                                       calculate_probabilities=False)
                topics, _ = topic_model.fit_transform(flat_sentences)
                print(f"BERTopic topics: {topics}")
                print(f"BERTopic topic_info: {topic_model.get_topic_info()}")
                concepts = []
                for topic in topic_model.get_topics():
                    topic_words = topic_model.get_topic(topic)
                    for word, _ in topic_words:
                        try:
                            doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                            for sent in doc.sentences:
                                for token in sent.tokens:
                                    if token.upos == "NOUN":
                                        concepts.append(token.text)
                        except Exception as e:
                            # 打印堆栈信息
                            error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
                            logger.error(error_message)
                            print(f"Error during stanza processing: {e}")
                            continue
                return list(set(concepts))
            else:
                print("sentences parameter does not match the requirement")
                return []
        except Exception as e:
            print(f"Error during BERTopic/LDA processing: {e}")
            raise
