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
import os


logger = logging.getLogger(__name__)


class TopicModeler:
    def __init__(self, num_topics=20, embed_model=None, language=None, bertopic_config: Optional[dict] = None):
        self.num_topics = num_topics
        self.embedder = embed_model if embed_model else SentenceEmbedder()
        self.text_processor = TextProcessor(language=language)
        self.language = language if language else settings.DEFAULT_LANGUAGE
        
        # 多粒度主题模型配置
        self.topic_levels = {
            'fine': {'num_topics': num_topics * 2, 'min_topic_size': 10},
            'medium': {'num_topics': num_topics, 'min_topic_size': 20},
            'coarse': {'num_topics': num_topics // 2, 'min_topic_size': 30}
        }
        
        if self.language == "zh":
            self.nlp = spacy.load("zh_core_web_sm")
            self.stopwords = self._load_stopwords()
            # 加载领域特定词典
            self._load_domain_dictionaries()
        else:
            self.nlp = spacy.load("en_core_web_sm")
            self.stopwords = None
            
        self.lemmatizer = WordNetLemmatizer()
        self.jieba_cut = lambda x: " ".join(jieba.cut(x))
        self.bertopic_config = bertopic_config if bertopic_config else {}
        self.sentence_model_zh = None
        
        # 多粒度UMAP配置
        self.umap_models = {
            'fine': umap.UMAP(n_neighbors=10, n_components=5, metric='cosine', random_state=42),
            'medium': umap.UMAP(n_neighbors=15, n_components=5, metric='cosine', random_state=42),
            'coarse': umap.UMAP(n_neighbors=20, n_components=5, metric='cosine', random_state=42)
        }
        
        self.ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
        self.representation_model = KeyBERTInspired()
        self.representation_model_mmr = MaximalMarginalRelevance(diversity=0.3)
        self.vectorizer_model = None
        
        # 初始化多粒度主题模型
        self.topic_models = self._initialize_topic_models()
        
    def _load_stopwords(self):
        """加载中文停用词列表"""
        # 常见中文停用词
        common_stopwords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', 
                          '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这个', 
                          '那个', '啊', '吧', '呢', '啥', '呀', '哦', '嗯', '哈', '嘛', '吗', '诶', '喂', '哎', '哟', 
                          '哇', '唉', '哼', '哩', '咦', '呵', '哒']
        
        # 这里可以从文件加载更多停用词
        # 如果有停用词文件，可以从文件加载
        # if os.path.exists('path/to/stopwords.txt'):
        #    with open('path/to/stopwords.txt', 'r', encoding='utf-8') as f:
        #        file_stopwords = [line.strip() for line in f.readlines()]
        #    common_stopwords.extend(file_stopwords)
        
        return common_stopwords

    def _load_domain_dictionaries(self):
        """加载领域特定词典"""
        domain_dict_path = os.path.join(settings.BASE_DIR, 'data', 'domain_dictionaries')
        if os.path.exists(domain_dict_path):
            for dict_file in os.listdir(domain_dict_path):
                if dict_file.endswith('.txt'):
                    dict_path = os.path.join(domain_dict_path, dict_file)
                    jieba.load_userdict(dict_path)
                    
    def _initialize_topic_models(self):
        """初始化多粒度主题模型"""
        models = {}
        for level, config in self.topic_levels.items():
            if self.language == "zh":
                if not self.sentence_model_zh:
                    self.sentence_model_zh = SentenceTransformer('moka-ai/m3e-base',
                                                               device=self.embedder.device)
                self.vectorizer_model = CountVectorizer(
                    ngram_range=(1, 3),
                    stop_words=self.stopwords,
                    preprocessor=self.jieba_cut,
                    min_df=2,
                    max_df=0.85
                )
                sentence_model = self.sentence_model_zh
            else:
                sentence_model = self.embedder._model
                
            models[level] = BERTopic(
                verbose=True,
                umap_model=self.umap_models[level],
                ctfidf_model=self.ctfidf_model,
                vectorizer_model=self.vectorizer_model,
                embedding_model=sentence_model,
                representation_model=self.representation_model_mmr,
                nr_topics=config['num_topics'],
                min_topic_size=config['min_topic_size'],
                low_memory=True,
                calculate_probabilities=True,
                **self.bertopic_config
            )
        return models
        
    async def _extract_concepts(self, sentences: List[str]) -> Dict[str, List[str]]:
        """多粒度概念提取"""
        concepts = {
            'fine': [],
            'medium': [],
            'coarse': []
        }
        
        try:
            # 对每个粒度级别进行主题建模
            for level, model in self.topic_models.items():
                topics, probs = model.fit_transform(sentences)
                topic_info = model.get_topic_info()
                
                # 提取该粒度级别的概念
                level_concepts = []
                for topic in model.get_topics():
                    if topic == -1:
                        continue
                        
                    topic_words = model.get_topic(topic)
                    topic_importance = topic_info[topic_info['Topic'] == topic]['Count'].values[0] if topic in topic_info['Topic'].values else 0
                    
                    # 动态阈值调整
                    base_threshold = 0.01
                    if level == 'fine':
                        base_threshold = 0.008
                    elif level == 'coarse':
                        base_threshold = 0.015
                        
                    topic_weight_threshold = base_threshold
                    if topic_importance > 0:
                        topic_weight_threshold = max(base_threshold * 0.5, base_threshold - 0.001 * topic_importance)
                    
                    for word, weight in topic_words:
                        if weight < topic_weight_threshold:
                            continue
                            
                        if len(word) < 2 and self.language == "zh":
                            continue
                            
                        try:
                            doc = asyncio.get_running_loop().run_in_executor(None, self.nlp, word)
                            doc = await doc
                            
                            should_add = False
                            for token in doc:
                                if self.language == "zh":
                                    if token.pos_ in ["NOUN", "PROPN"]:
                                        should_add = True
                                else:
                                    if token.pos_ == "PROPN" or (token.pos_ == "NOUN" and token.text[0].isupper()):
                                        should_add = True
                                    elif token.pos_ == "NOUN":
                                        should_add = True
                                        
                            if should_add:
                                level_concepts.append(word)
                        except Exception as e:
                            logger.error(f"Error during NLP processing: {e}")
                            if len(word) >= 2:
                                level_concepts.append(word)
                
                # 使用MMR进行概念选择
                if level_concepts:
                    embeddings = self.sentence_model_zh.encode(level_concepts) if self.language == "zh" else self.embedder._model.encode(level_concepts)
                    mmr_indices = self._mmr_selection(embeddings, diversity=0.3, top_n=min(30, len(level_concepts)))
                    concepts[level] = [level_concepts[idx] for idx in mmr_indices]
                    
            return concepts
            
        except Exception as e:
            logger.error(f"Error during multi-granularity topic modeling: {e}")
            return concepts
            
    async def get_concepts(self, sentences: List) -> Dict[str, List[str]]:
        """获取多粒度概念"""
        try:
            if not sentences:
                return {'fine': [], 'medium': [], 'coarse': []}
                
            if isinstance(sentences[0], str):
                if len(sentences) == 1:
                    sentences_list, _ = await self.text_processor.preprocess_text(sentences[0])
                    if not sentences_list:
                        return {'fine': [], 'medium': [], 'coarse': []}
                    return await self._extract_concepts(sentences_list)
                return await self._extract_concepts(sentences)
            elif isinstance(sentences[0], dict):
                texts = [item["text"] for item in sentences]
                return await self._extract_concepts(texts)
            elif isinstance(sentences[0], list):
                flat_sentences = [sent for sublist in sentences for sent in sublist]
                return await self._extract_concepts(flat_sentences)
            else:
                logger.error("sentences parameter does not match the requirement")
                return {'fine': [], 'medium': [], 'coarse': []}
        except Exception as e:
            logger.error(f"Error during concept extraction: {e}")
            return {'fine': [], 'medium': [], 'coarse': []}

    def singularize_concept(self, concept):
        words = concept.split()
        singular_words = [self.lemmatizer.lemmatize(word, wordnet.NOUN) for word in words]
        return ' '.join(singular_words)

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

    def _mmr_selection(self, embeddings, diversity=0.3, top_n=30):
        """使用最大边际相关性算法选择多样化的词汇"""
        # 初始化
        S = []
        R = list(range(len(embeddings)))
        
        # 选择第一个
        if not R:
            return S
        S.append(R.pop(0))
        
        # 贪婪选择
        while R and len(S) < top_n:
            best_score = -np.inf
            best_idx = -1
            
            # 计算候选向量和已选向量的相似度
            for i in R:
                # 最大相似度
                sim_S = max([np.dot(embeddings[i], embeddings[j]) / 
                            (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])) 
                            for j in S]) if S else 0
                
                # MMR得分
                mmr_score = (1 - diversity) * np.linalg.norm(embeddings[i]) - diversity * sim_S
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            if best_idx != -1:
                S.append(best_idx)
                R.remove(best_idx)
            else:
                break
                
        return S