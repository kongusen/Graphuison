import unittest
import asyncio
from backend.app.models.topic_modeler import TopicModeler
from backend.app.models.embedder import SentenceEmbedder


class TestTopicModeler(unittest.TestCase):
    def setUp(self):
       self.model = TopicModeler(embed_model=SentenceEmbedder(),language="en")

    def test_train_lda(self):
       async def run_test():
          sentences = ["This is a test sentence.", "Another test sentence here."]
          lda_model = await self.model.train_lda(sentences)
          self.assertIsNotNone(lda_model)
          self.assertIsInstance(lda_model, models.LdaModel)
       asyncio.run(run_test())

    def test_get_concepts(self):
        async def run_test():
          sentences = ["This is a test sentence about machine learning.", "Another sentence about data science."]
          concepts = await self.model.get_concepts(sentences)
          self.assertIsInstance(concepts, list)
          self.assertTrue(all(isinstance(item,str) for item in concepts))
        asyncio.run(run_test())
if __name__ == '__main__':
    unittest.main()