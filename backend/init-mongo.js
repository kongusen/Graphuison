// 创建数据库
db = db.getSiblingDB('graphuison');

// 创建用户集合
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });

// 创建文档集合
db.createCollection('documents');
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "created_at": -1 });

// 创建向量集合
db.createCollection('vectors');
db.vectors.createIndex({ "document_id": 1 });
db.vectors.createIndex({ "user_id": 1 });
db.vectors.createIndex({ "created_at": -1 });

// 创建主题集合
db.createCollection('topics');
db.topics.createIndex({ "document_id": 1 });
db.topics.createIndex({ "user_id": 1 });
db.topics.createIndex({ "created_at": -1 });

// 创建关系集合
db.createCollection('relations');
db.relations.createIndex({ "document_id": 1 });
db.relations.createIndex({ "user_id": 1 });
db.relations.createIndex({ "created_at": -1 });

// 创建知识图谱集合
db.createCollection('knowledge_graphs');
db.knowledge_graphs.createIndex({ "user_id": 1 });
db.knowledge_graphs.createIndex({ "created_at": -1 });

// 创建聊天历史集合
db.createCollection('chat_history');
db.chat_history.createIndex({ "user_id": 1 });
db.chat_history.createIndex({ "created_at": -1 });

// 创建系统设置集合
db.createCollection('settings');
db.settings.createIndex({ "user_id": 1 }, { unique: true }); 