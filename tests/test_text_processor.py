import asyncio
import pytest
import sys
import os
from app.models.text_processor import TextProcessor


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
   

@pytest.mark.asyncio
async def test_preprocess_text_normal():
    processor = TextProcessor(language="zh")
    text = "This is a test sentence. This is another one."
    sentences, tokens = await processor.preprocess_text(text)
    assert len(sentences) == 2
    assert len(tokens) == 2
    assert all(isinstance(sent, str) for sent in sentences)
    assert all(isinstance(token, list) for token in tokens)
    assert ["test"] in tokens
    assert ["sentence"] in tokens


@pytest.mark.asyncio
async def test_preprocess_text_empty():
   processor = TextProcessor(language="zh")
   text = ""
   sentences, tokens = await processor.preprocess_text(text)
   assert len(sentences) == 0
   assert len(tokens) == 0

@pytest.mark.asyncio
async def test_process_file_normal():
    processor = TextProcessor(language="zh")
    file_paths = ["tests/test_data/test.txt"]
    sentences = await processor.process_files(file_paths)
    assert len(sentences) == 2
    assert all(isinstance(sent, str) for sent in sentences)

@pytest.mark.asyncio
async def test_process_file_notfound():
    processor = TextProcessor(language="zh")
    file_paths = ["tests/test_data/notfound.txt"]
    sentences = await processor.process_files(file_paths)
    assert len(sentences) == 0