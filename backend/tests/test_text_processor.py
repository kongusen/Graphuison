import unittest
import asyncio
from backend.app.models.text_processor import TextProcessor

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = TextProcessor(language="en")  # 或者指定你需要的语言

    def test_preprocess_text(self):
       async def run_test():
            text = "This is a test sentence. Here is another one."
            sentences, tokens = await self.processor.preprocess_text(text)
            self.assertEqual(len(sentences), 2)
            self.assertEqual(len(tokens), 2)
            self.assertIsInstance(sentences,list)
            self.assertIsInstance(tokens,list)
            self.assertTrue(all(isinstance(item,list) for item in tokens))
            self.assertTrue(all(isinstance(item,str) for item in sentences))
            self.assertTrue(all(isinstance(item,str) for sublist in tokens for item in sublist))


       asyncio.run(run_test())
    def test_extract_information(self):
        text = "Apple is a company and it is located in USA."
        info = self.processor.extract_information(text)
        self.assertIn('entities', info)
        self.assertIn('relations',info)
        self.assertIsInstance(info['entities'],list)
        self.assertIsInstance(info['relations'],list)
        self.assertTrue(all(isinstance(item,tuple) for item in info['entities']))
        self.assertTrue(all(isinstance(item,tuple) for item in info['relations']))
    def test_process_files(self):
        async def run_test():
           with open("test.txt",'w') as f:
             f.write("This is a test file")
           files = ["test.txt"]
           sentences = await self.processor.process_files(files)
           self.assertEqual(len(sentences),1)
           self.assertIsInstance(sentences, list)
           self.assertTrue(all(isinstance(item,str) for item in sentences))
           import os
           os.remove("test.txt")

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()