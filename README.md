# Graphusion: A RAG-based Framework for Scientific Knowledge Graph Construction

## Introduction

Graphusion is a framework based on Retrieval Augmented Generation (RAG) for constructing scientific knowledge graphs from free text. Unlike traditional methods for knowledge graph construction, Graphusion adopts a global perspective by fusing local knowledge to generate a more comprehensive and accurate knowledge graph. While primarily designed for the Natural Language Processing (NLP) domain, this framework also demonstrates potential in educational settings.

## Core Features

*   **Zero-Shot Knowledge Graph Construction**: Automatically extracts key entities and relationships from free text without requiring predefined entity lists.
*   **Global Knowledge Fusion**: Fuses local knowledge graphs to resolve information silos and achieve a more comprehensive knowledge representation.
*   **Flexible Relationship Types**: Supports various relationship types (e.g., `Prerequisite_of`, `Used_for`, `Compare`) and can handle relationship conflicts.
*   **Applicability in Educational Settings**: Validated with the `TutorQA` benchmark dataset, showcasing its potential in educational question-answering scenarios.
*   **Utilizes LLM for Knowledge Fusion**: Leverages LLMs not only for relation extraction but also during knowledge fusion, which is rare in previous methods.
*   **Entity Seed Guidance**: Employs topic modeling to generate seed entity lists, improving the accuracy of entity extraction.
*   **Rule-based Post-processing**: Applies rule-based post-processing to the tokenization results, further optimizing the results.

## Project Structure

*   `graph_fusioner.py`: Responsible for fusing local knowledge graphs, resolving relationship conflicts, and discovering new relationships.
*   `relation_extractor.py`: Uses LLMs to extract entities and relationships from text.
*   `text_processor.py`: Text preprocessor responsible for tokenization, lemmatization, and handling special terms.
*   `llm_chain.py`: Manages LLM calls and result retrieval.
*   `topic_modeler.py`: Employs LDA topic modeling to discover themes and concepts in the text.
*   `embedder.py`: Utilizes sentence transformers to generate sentence embeddings.

## Paper Contributions

*   Introduced the Graphusion framework for constructing scientific knowledge graphs from a global perspective.
*   Designed a three-stage knowledge graph construction pipeline: seed entity generation, candidate triple extraction, and knowledge graph fusion.
*   Introduced the `TutorQA` benchmark dataset to validate the application of knowledge graphs in educational question-answering scenarios.
*   Experimental results show that Graphusion achieves good performance in both entity extraction and relation identification.

## Main Steps

1.  **Seed Entity Generation**: Uses topic modeling (BERTopic) to extract representative entities from the text.
2.  **Candidate Triple Extraction**: Utilizes LLMs and Chain-of-Thought (CoT) prompting to extract triples containing seed entities.
3.  **Knowledge Graph Fusion**: Fuses local knowledge graphs to resolve relationship conflicts and infer new triples.
    *   **Entity Merging**: Merges semantically similar entities.
    *   **Conflict Resolution**: Selects the most accurate relationship.
    *   **Novel Triple Inference**: Infers new relationships from the background text.

## How to Use

1.  **Environment Setup**: Ensure you have Python 3.8 or higher installed, and install all project dependencies using the `requirements.txt` file to ensure compatibility.
2.  **Parameter Adjustment**: Configure the `config.yaml` file based on your project needs, including `relation_defs` (relationship definitions), `templates` (LLM prompt templates), and other required parameters.
3.  **Execution**: Refer to the examples in the `examples/` directory for complete knowledge graph generation and question-answering processing tests.

## TutorQA Benchmark Dataset

*   Includes 1200 QA pairs covering 6 different difficulty levels:
    *   Relation Judgment
    *   Prerequisite Prediction
    *   Path Searching
    *   Subgraph Completion
    *   Clustering
    *   Idea Hamster
*   Highlights the application of knowledge graphs in educational settings.
*   Provides expert-validated question-answer pairs to ensure data quality.

## Experimental Results

*   Graphusion achieved high expert scores in both entity extraction and relation identification tasks (2.92 and 2.37 respectively, out of a maximum score of 3).
*   In the `TutorQA` benchmark, using knowledge graphs constructed by Graphusion for question-answering resulted in significant performance improvements compared to the pure LLM baseline in multiple tasks.

## Ethical Statement

*   Encourages manual verification of the accuracy of automatgit remote -ved knowledge extraction.
*   Uses reliable data sources but still requires attention to potential biases in LLMs and knowledge graphs.
*   All experiments adhere to AI ethical standards and do not use any personal or sensitive data.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Citation

If you use this project or paper in your research, please cite the following paper:
[Graphusion](https://arxiv.org/abs/2407.10794)

## Contact Information

For any questions, please contact us through:

[448486810@qq.com]
