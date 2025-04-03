# Graphuison: 基于多粒度知识融合的智能知识图谱平台

## 关键技术

- **多粒度知识表示**
  - 细粒度(fine)、中粒度(medium)和粗粒度(coarse)概念提取
  - 跨粒度关系建模与推理

- **零样本知识图谱构建**
  - 无需预定义实体列表，自动从自由文本中提取关键实体和关系
  - 基于主题建模的种子实体生成

- **全局知识融合**
  - 融合局部知识图谱，解决信息孤岛问题
  - 基于大模型的关系提取和知识融合

- **智能问答系统**
  - 基于知识图谱的智能问答
  - 多轮对话支持

## 系统架构

Graphuison平台采用前后端分离的架构设计，包含以下主要组件：

1. **前端**
   - 基于React框架开发的用户界面
   - 直观的图谱可视化和交互体验

2. **后端API**
   - 使用FastAPI构建的RESTful API服务
   - 处理文档上传、知识抽取和图谱查询等请求

3. **知识图谱引擎**
   - 文本处理器：负责文本预处理、分词和特殊术语处理
   - 主题建模器：使用BERTopic进行主题建模，发现文本中的主题和概念
   - 关系提取器：使用大型语言模型提取实体间的关系
   - 图谱融合器：融合局部图谱，处理关系冲突并推断新的关系

4. **存储层**
   - Neo4j图数据库：存储和查询知识图谱数据
   - 文件存储：管理用户上传的文档
   - 用户数据：存储用户信息和权限数据

## 快速开始

### 环境要求

- Docker 与 Docker Compose
- 至少8GB内存（推荐16GB以上）
- 支持CUDA的GPU（可选，用于加速处理）

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/Graphuison.git
cd Graphuison
```

2. 配置环境变量：
```bash
cd backend
cp .env.example .env
```
编辑`.env`文件，配置必要的参数，主要包括：

- **基础配置**
  - `API_PORT`: API服务端口（默认8000）
  - `SECRET_KEY`: JWT密钥（生产环境请修改）
  - `LOG_FILE`: 日志文件路径

- **OpenAI配置**
  - `OPENAI_API_KEY`: OpenAI API密钥
  - `OPENAI_BASE_URL`: OpenAI API基础URL
  - `LLM_MODEL`: 使用的语言模型
  - `EMBED_MODEL_NAME`: 使用的嵌入模型

- **数据库配置**
  - `NEO4J_URI`: Neo4j数据库连接地址
  - `NEO4J_USERNAME`: 数据库用户名
  - `NEO4J_PASSWORD`: 数据库密码

- **模型配置**
  - `DEVICE`: 运行设备（cpu/cuda）
  - `LANGUAGE`: 默认语言（zh/en）
  - `TRANSFORMATIONS_CHUNK_SIZE`: 文本分块大小
  - `CONTEXT_WINDOW`: 上下文窗口大小

- **知识图谱配置**
  - `RELATION_DEFINITIONS`: 关系类型定义
  - `RELATION_EXTRACTION_TEMPLATE`: 关系抽取提示模板
  - `GRAPH_FUSION_TEMPLATE`: 图谱融合提示模板

- **存储配置**
  - `DOCUMENT_STORAGE_PATH`: 文档存储路径
  - `GRAPH_STORAGE_PATH`: 图谱存储路径
  - `USER_STORAGE_PATH`: 用户数据存储路径

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问平台：
   - 前端界面：http://localhost:3000
   - API文档：http://localhost:8000/docs
   - Neo4j浏览器：http://localhost:7474 (默认用户名/密码: neo4j/password)

### 使用指南

1. **用户注册与登录**
   - 通过`/auth/register`接口注册新用户
   - 通过`/auth/token`接口获取访问令牌

2. **文档上传与图谱生成**
   - 登录后，通过`/kg/upload`接口上传文档并指定图谱名称
   - 使用`/kg/status/{task_id}`查看处理进度
   - 处理完成后，可以通过`/kg/graphs`查看所有生成的图谱

3. **知识图谱查询**
   - 使用`/kg/search`搜索图谱中的实体
   - 通过`/kg/entity/{entity_name}`查询实体关系
   - 使用`/kg/granularity/{level}`查询特定粒度级别的图谱

4. **智能问答**
   - 通过`/chat/`接口提交问题，获取基于知识图谱的回答

5. **数据导出**
   - 使用`/kg/graphs/{graph_id}/export`导出图谱数据

## 技术栈

- **后端**：Python, FastAPI, asyncio, Neo4j
- **大模型集成**：OpenAI API, LlamaIndex, SentenceTransformers
- **自然语言处理**：BERTopic, Stanza, jieba (中文分词)
- **前端**：React, TypeScript, D3.js (可视化)
- **部署**：Docker, Docker Compose

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 引用

如果您在研究中使用了本项目或论文，请引用以下论文：
[Graphuison](https://arxiv.org/abs/2407.10794)

## 联系方式

如有任何问题，请通过以下方式联系我们：
[448486810@qq.com]

---

# Graphuison: Intelligent Knowledge Graph Platform Based on Multi-granularity Knowledge Fusion

## Key Technologies

- **Multi-granularity Knowledge Representation**
  - Fine-grained, medium-grained, and coarse-grained concept extraction
  - Cross-granularity relation modeling and reasoning

- **Zero-shot Knowledge Graph Construction**
  - Automatic extraction of key entities and relations from free text without predefined entity lists
  - Seed entity generation based on topic modeling

- **Global Knowledge Fusion**
  - Fusion of local knowledge graphs to solve information silos
  - Relation extraction and knowledge fusion based on large language models

- **Intelligent Q&A System**
  - Knowledge graph-based intelligent Q&A
  - Multi-turn conversation support

## System Architecture

Graphuison platform adopts a front-end and back-end separated architecture, including the following main components:

1. **Frontend**
   - User interface developed based on React framework
   - Intuitive graph visualization and interaction experience

2. **Backend API**
   - RESTful API service built with FastAPI
   - Handle document upload, knowledge extraction, and graph query requests

3. **Knowledge Graph Engine**
   - Text processor: responsible for text preprocessing, word segmentation, and special term processing
   - Topic modeler: uses BERTopic for topic modeling to discover topics and concepts in text
   - Relation extractor: uses large language models to extract relations between entities
   - Graph fusioner: fuses local graphs, handles relation conflicts and infers new relations

4. **Storage Layer**
   - Neo4j graph database: stores and queries knowledge graph data
   - File storage: manages user-uploaded documents
   - User data: stores user information and permission data

## Quick Start

### Requirements

- Docker and Docker Compose
- At least 8GB RAM (16GB+ recommended)
- CUDA-enabled GPU (optional, for acceleration)

### Installation Steps

1. Clone repository:
```bash
git clone https://github.com/yourusername/Graphuison.git
cd Graphuison
```

2. Configure environment variables:
```bash
cd backend
cp .env.example .env
```
Edit `.env` file to configure necessary parameters, including OpenAI API key

3. Start services:
```bash
docker-compose up -d
```

4. Access platform:
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - Neo4j browser: http://localhost:7474 (Default username/password: neo4j/password)

### User Guide

1. **User Registration and Login**
   - Register new user via `/auth/register`
   - Get access token via `/auth/token`

2. **Document Upload and Graph Generation**
   - After login, upload documents and specify graph name via `/kg/upload`
   - Check processing progress via `/kg/status/{task_id}`
   - After processing, view all generated graphs via `/kg/graphs`

3. **Knowledge Graph Query**
   - Search entities in graph via `/kg/search`
   - Query entity relations via `/kg/entity/{entity_name}`
   - Query graphs at specific granularity levels via `/kg/granularity/{level}`

4. **Intelligent Q&A**
   - Submit questions via `/chat/` to get knowledge graph-based answers

5. **Data Export**
   - Export graph data via `/kg/graphs/{graph_id}/export`

## Tech Stack

- **Backend**: Python, FastAPI, asyncio, Neo4j
- **LLM Integration**: OpenAI API, LlamaIndex, SentenceTransformers
- **NLP**: BERTopic, Stanza, jieba (Chinese word segmentation)
- **Frontend**: React, TypeScript, D3.js (visualization)
- **Deployment**: Docker, Docker Compose

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Citation

If you use this project or paper in your research, please cite:
[Graphuison](https://arxiv.org/abs/2407.10794)

## Contact

For any questions, please contact us at:
[448486810@qq.com]

## 功能特点

- 多粒度概念抽取：支持细粒度、中粒度和粗粒度概念识别
- 多粒度关系抽取：支持同粒度及跨粒度关系抽取
- 智能问答：基于知识图谱的智能问答系统
- 用户认证：完整的用户注册和认证系统
- 数据持久化：支持文档和知识图谱的存储与管理

## 系统要求

- Python 3.8+
- Neo4j 5.0+
- OpenAI API密钥（用于LLM功能）

## 安装说明

1. 克隆项目并进入项目目录：
```bash
git clone https://github.com/yourusername/Graphuison.git
cd Graphuison
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装后端依赖：
```bash
cd backend
pip install -r requirements.txt
```

4. 安装spaCy中文语言模型：
```bash
python -m spacy download zh_core_web_sm
```

5. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

## 配置说明

在`.env`文件中配置以下必要参数：

```env
# 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI配置
OPENAI_API_KEY=your_api_key

# JWT配置
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 存储路径配置
DOCUMENT_STORAGE_PATH=./data/documents
GRAPH_STORAGE_PATH=./data/graphs
```

## 启动服务

1. 启动后端服务：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端服务：
```bash
cd frontend
npm install
npm run dev
```

## API文档

启动服务后访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

### 1. 用户认证
- 用户注册：`POST /auth/register`
- 用户登录：`POST /auth/token`
- 获取用户信息：`GET /auth/me`

### 2. 知识图谱管理
- 文档上传：`POST /kg/upload`
- 知识抽取：`POST /kg/extract`
- 图谱生成：`POST /kg/generate`
- 图谱查询：`GET /kg/granularity/{level}`
- 图谱导出：`GET /kg/graphs/{graph_id}/export`

### 3. 智能问答
- 问答接口：`POST /chat/`

## 开发说明

### 项目结构
```
Graphuison/
├── backend/
│   ├── app/
│   │   ├── models/      # 模型定义
│   │   ├── routers/     # API路由
│   │   ├── schemas/     # 数据模式
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试文件
│   ├── requirements.txt # 依赖配置
│   └── main.py         # 主程序
├── frontend/           # 前端代码
└── data/              # 数据存储
```

### 测试
```bash
cd backend
pytest
```

## 许可证

MIT License
