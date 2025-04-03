# text_processor.py
import spacy
from typing import List, Tuple
from app.config import settings
import asyncio

class TextProcessor:
    def __init__(self, language=None, processors=None):
        self.language = language if language else settings.DEFAULT_LANGUAGE
        if self.language == "zh":
            self.nlp = spacy.load("zh_core_web_sm")
        else:
            self.nlp = spacy.load("en_core_web_sm")


    async def preprocess_text(self, text: str) -> Tuple[List[str], List[List[str]]]:
        sentences = []
        tokens_list = []
        doc = asyncio.get_running_loop().run_in_executor(None,self.nlp,text)
        doc = await doc

        for sent in doc.sents:
           sent_tokens_list = [token.text if self.language == 'zh' else token.lemma_ for token in sent]
           tokens_list.append(sent_tokens_list)
           sentences.append(sent.text)


        return sentences, tokens_list

    def extract_information(self, text: str) -> dict:
        """
        使用 spaCy 提取文本中的命名实体和依存关系
        """
        doc = self.nlp(text)
        entities = []
        relations = []
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        for token in doc:
             if token.dep_ != "ROOT":
                relations.append((token.text, token.dep_, token.head.text))
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