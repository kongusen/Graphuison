# text_processor.py
import stanza
from stanza.pipeline.core import Pipeline
from typing import List, Tuple
from app.config import settings
import os
import asyncio

class TextProcessor:
    def __init__(self, language=None, processors="tokenize,lemma,pos,ner,depparse"):
        self.language = language if language else settings.DEFAULT_LANGUAGE
        self.nlp = Pipeline(self.language, processors=processors, use_gpu=False, verbose=False)

    async def preprocess_text(self, text: str) -> Tuple[List[str], List[List[str]]]:
        sentences = []
        tokens_list = []

        # 使用 Stanza 进行句子分割和分词
        doc = await asyncio.get_running_loop().run_in_executor(None, self.nlp, text)
        for sent in doc.sentences:
            sent_tokens_list = [token.text if self.language == 'zh' else token.lemma for token in sent.tokens]
            tokens_list.append(sent_tokens_list)
            sentences.append(sent.text)

        return sentences, tokens_list

    def extract_information(self, text: str) -> dict:
        """
        使用 Stanza 提取文本中的命名实体和依存关系
        """
        doc = asyncio.get_running_loop().run_in_executor(None,self.nlp,text)
        entities = []
        relations = []
        for sent in doc.sentences:
            for ent in sent.ents:
                entities.append((ent.text, ent.type))
            for word in sent.words:
                if word.head > 0:
                    head_word = sent.words[word.head - 1]
                    relations.append((word.text, word.deprel, head_word.text))
        return {
            "entities": entities,
            "relations": relations
        }

    async def process_files(self, file_paths: List[str]) -> List[str]:
        results = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                sentences, _ = await self.preprocess_text(text)
                results.extend(sentences)
            except FileNotFoundError:
                pass
        return results