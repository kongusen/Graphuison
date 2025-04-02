# Graphuison API文档

## 目录
1. [认证接口](#1-认证接口)
2. [知识图谱管理](#2-知识图谱管理)
3. [文档管理](#3-文档管理)
4. [知识图谱查询](#4-知识图谱查询)
5. [智能问答](#5-智能问答)
6. [系统管理](#6-系统管理)

## 1. 认证接口

### 1.1 用户注册

**接口路径**: `/auth/register`  
**请求方式**: POST  
**接口描述**: 注册新用户

**请求参数**:
```json
{
  "username": "user123",  // 用户名（3-50个字符）
  "email": "user@example.com",  // 邮箱地址
  "password": "password123",  // 密码（至少6个字符）
  "display_name": "测试用户"  // 显示名称（可选）
}
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "user123",
  "email": "user@example.com",
  "display_name": "测试用户",
  "is_admin": false,
  "roles": ["user"],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00",
  "last_login": null
}
```

### 1.2 用户登录

**接口路径**: `/auth/token`  
**请求方式**: POST  
**接口描述**: 登录获取访问令牌

**请求参数**:
```
username=user123&password=password123
```
> 注意：此接口采用form表单提交方式

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 1.3 获取当前用户信息

**接口路径**: `/auth/me`  
**请求方式**: GET  
**接口描述**: 获取当前登录用户信息
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "user123",
  "email": "user@example.com",
  "display_name": "测试用户",
  "is_admin": false,
  "roles": ["user"],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00",
  "last_login": "2023-01-02T14:30:00"
}
```

### 1.4 更新用户信息

**接口路径**: `/auth/me`  
**请求方式**: PUT  
**接口描述**: 更新当前用户信息
**请求头**: Authorization: Bearer {token}

**请求参数**:
```json
{
  "display_name": "新用户名",  // 可选
  "email": "newemail@example.com",  // 可选
  "password": "newpassword123"  // 可选
}
```

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "user123",
  "email": "newemail@example.com",
  "display_name": "新用户名",
  "is_admin": false,
  "roles": ["user"],
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-03T09:15:00",
  "last_login": "2023-01-02T14:30:00"
}
```

## 2. 知识图谱管理

### 2.1 上传文档并生成知识图谱

**接口路径**: `/kg/upload`  
**请求方式**: POST  
**接口描述**: 上传文档并开始生成知识图谱
**请求头**: Authorization: Bearer {token}

**请求参数**:
- `file`: 文件（multipart/form-data）
- `name`: 图谱名称
- `description`: 图谱描述（可选）

**响应示例**:
```json
{
  "task_id": "task_20230105_123045",
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "doc_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "文档上传成功，开始处理"
}
```

### 2.2 获取任务处理状态

**接口路径**: `/kg/status/{task_id}`  
**请求方式**: GET  
**接口描述**: 获取知识图谱生成任务的处理状态
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "status": "processing",
  "progress": 0.4,
  "message": "多粒度概念提取完成",
  "timestamp": "2023-01-05T12:31:22",
  "result": null
}
```

### 2.3 获取处理结果

**接口路径**: `/kg/result/{task_id}`  
**请求方式**: GET  
**接口描述**: 获取知识图谱生成的详细结果
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "concepts": {
    "fine": ["概念1", "概念2", "概念3"],
    "medium": ["概念A", "概念B"],
    "coarse": ["主题1"]
  },
  "triples": {
    "fine": [["概念1", "isA", "概念2"], ["概念2", "partOf", "概念3"]],
    "medium": [["概念A", "uses", "概念B"]],
    "coarse": [["主题1", "contains", "概念A"]]
  },
  "fused_graphs": {
    "fine": [["概念1", "isA", "概念2"], ["概念2", "partOf", "概念3"]],
    "medium": [["概念A", "uses", "概念B"]],
    "coarse": [["主题1", "contains", "概念A"]],
    "cross_granularity": [["概念1", "belongsTo", "主题1"]]
  }
}
```

### 2.4 获取用户所有图谱

**接口路径**: `/kg/graphs`  
**请求方式**: GET  
**接口描述**: 获取当前用户的所有知识图谱
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "机器学习知识图谱",
    "description": "机器学习领域的概念图谱",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "created_at": "2023-01-05T12:30:45",
    "updated_at": "2023-01-05T12:45:22",
    "status": "completed",
    "document_id": "660e8400-e29b-41d4-a716-446655440000",
    "stats": {
      "entities_count": 45,
      "triples_count": 78,
      "relation_types_count": 6,
      "granularity_stats": {
        "fine": 45,
        "medium": 20,
        "coarse": 8,
        "cross_granularity": 5
      }
    }
  }
]
```

### 2.5 获取图谱详细信息

**接口路径**: `/kg/graphs/{graph_id}`  
**请求方式**: GET  
**接口描述**: 获取指定图谱的详细信息
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "机器学习知识图谱",
  "description": "机器学习领域的概念图谱",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-01-05T12:30:45",
  "updated_at": "2023-01-05T12:45:22",
  "status": "completed",
  "document_id": "660e8400-e29b-41d4-a716-446655440000",
  "stats": {
    "entities_count": 45,
    "triples_count": 78,
    "relation_types_count": 6,
    "granularity_stats": {
      "fine": 45,
      "medium": 20,
      "coarse": 8,
      "cross_granularity": 5
    }
  }
}
```

### 2.6 删除图谱

**接口路径**: `/kg/graphs/{graph_id}`  
**请求方式**: DELETE  
**接口描述**: 删除指定的知识图谱
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "message": "图谱已删除"
}
```

### 2.7 导出图谱数据

**接口路径**: `/kg/graphs/{graph_id}/export`  
**请求方式**: GET  
**接口描述**: 导出指定图谱的完整数据
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "metadata": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "机器学习知识图谱",
    "description": "机器学习领域的概念图谱",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "created_at": "2023-01-05T12:30:45",
    "updated_at": "2023-01-05T12:45:22",
    "status": "completed"
  },
  "triples": [
    {
      "source": "机器学习",
      "relation": "包含",
      "target": "深度学习",
      "source_type": "entity_coarse",
      "target_type": "entity_medium"
    },
    {
      "source": "深度学习",
      "relation": "使用",
      "target": "神经网络",
      "source_type": "entity_medium",
      "target_type": "entity_fine"
    }
  ]
}
```

## 3. 文档管理

### 3.1 获取用户所有文档

**接口路径**: `/kg/documents`  
**请求方式**: GET  
**接口描述**: 获取当前用户的所有文档
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "filename": "machine_learning.pdf",
    "original_name": "机器学习导论.pdf",
    "size": 1024567,
    "created_at": "2023-01-05T12:30:45",
    "updated_at": "2023-01-05T12:45:22",
    "status": "processed",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "graphs": ["550e8400-e29b-41d4-a716-446655440000"]
  }
]
```

### 3.2 获取文档详细信息

**接口路径**: `/kg/documents/{doc_id}`  
**请求方式**: GET  
**接口描述**: 获取指定文档的详细信息
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "filename": "machine_learning.pdf",
  "original_name": "机器学习导论.pdf",
  "size": 1024567,
  "created_at": "2023-01-05T12:30:45",
  "updated_at": "2023-01-05T12:45:22",
  "status": "processed",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "graphs": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

### 3.3 删除文档

**接口路径**: `/kg/documents/{doc_id}`  
**请求方式**: DELETE  
**接口描述**: 删除指定的文档
**请求头**: Authorization: Bearer {token}

**响应示例**:
```json
{
  "message": "文档已删除"
}
```

## 4. 知识图谱查询

### 4.1 搜索实体

**接口路径**: `/kg/search`  
**请求方式**: GET  
**接口描述**: 在知识图谱中搜索匹配的实体
**请求参数**:
- `query`: 搜索关键词
- `max_results`: 最大结果数（默认10，范围1-100）

**响应示例**:
```json
[
  {
    "name": "机器学习",
    "type": "entity_coarse"
  },
  {
    "name": "深度学习",
    "type": "entity_medium"
  },
  {
    "name": "机器学习算法",
    "type": "entity_medium"
  }
]
```

### 4.2 获取实体关系

**接口路径**: `/kg/entity/{entity_name}`  
**请求方式**: GET  
**接口描述**: 获取指定实体的关系信息
**请求参数**:
- `depth`: 关系深度（默认1，范围1-3）

**响应示例**:
```json
{
  "entity": "机器学习",
  "related_entities": [
    {
      "name": "深度学习",
      "type": "entity_medium"
    },
    {
      "name": "监督学习",
      "type": "entity_medium"
    },
    {
      "name": "无监督学习",
      "type": "entity_medium"
    }
  ],
  "relations": [
    {
      "source": "机器学习",
      "relation": "包含",
      "target": "深度学习",
      "source_type": "entity_coarse",
      "target_type": "entity_medium"
    },
    {
      "source": "机器学习",
      "relation": "包含",
      "target": "监督学习",
      "source_type": "entity_coarse",
      "target_type": "entity_medium"
    },
    {
      "source": "机器学习",
      "relation": "包含",
      "target": "无监督学习",
      "source_type": "entity_coarse",
      "target_type": "entity_medium"
    }
  ]
}
```

### 4.3 获取特定粒度的知识图谱

**接口路径**: `/kg/granularity/{level}`  
**请求方式**: GET  
**接口描述**: 获取特定粒度级别的知识图谱
**请求参数**:
- `level`: 粒度级别（fine, medium, coarse, cross_granularity, all）

**响应示例**:
```json
[
  {
    "source": "深度学习",
    "relation": "使用",
    "target": "神经网络",
    "source_type": "entity_medium",
    "target_type": "entity_fine"
  },
  {
    "source": "CNN",
    "relation": "是一种",
    "target": "神经网络",
    "source_type": "entity_fine",
    "target_type": "entity_fine"
  }
]
```

## 5. 智能问答

### 5.1 基于知识图谱的问答

**接口路径**: `/chat/`  
**请求方式**: POST  
**接口描述**: 基于多粒度知识图谱的智能问答

**请求参数**:
```json
{
  "query": "什么是机器学习？",
  "preferred_granularity": "medium"  // 可选，指定优先使用的粒度级别
}
```

**响应示例**:
```json
{
  "response": "机器学习是一种人工智能的分支，它主要研究如何使用计算机系统自动地从数据中学习规律和模式。它包含多个子领域，如深度学习、监督学习和无监督学习等。",
  "triples": [
    {
      "source": "机器学习",
      "relation": "是一种",
      "target": "人工智能技术",
      "source_type": "entity_coarse",
      "target_type": "entity_coarse"
    },
    {
      "source": "机器学习",
      "relation": "包含",
      "target": "深度学习",
      "source_type": "entity_coarse",
      "target_type": "entity_medium"
    }
  ],
  "relevant_entities": [
    {
      "name": "机器学习",
      "type": "entity_coarse"
    },
    {
      "name": "人工智能",
      "type": "entity_coarse"
    }
  ],
  "granularity_used": "medium"
}
```

### 5.2 获取聊天历史

**接口路径**: `/chat/history`  
**请求方式**: GET  
**接口描述**: 获取聊天历史记录
**请求参数**:
- `limit`: 记录数量上限（默认10，范围1-50）

**响应示例**:
```json
{
  "history": [
    {
      "id": "chat_20230105_123456",
      "query": "什么是机器学习？",
      "response": "机器学习是一种人工智能的分支，它主要研究如何使用计算机系统自动地从数据中学习规律和模式...",
      "timestamp": "2023-01-05T12:34:56"
    },
    {
      "id": "chat_20230105_123556",
      "query": "深度学习与机器学习有什么区别？",
      "response": "深度学习是机器学习的一个子领域，它特别关注基于人工神经网络的学习算法...",
      "timestamp": "2023-01-05T12:35:56"
    }
  ]
}
```

### 5.3 清空聊天历史

**接口路径**: `/chat/history`  
**请求方式**: DELETE  
**接口描述**: 清空聊天历史记录

**响应示例**:
```json
{
  "message": "聊天历史已清空"
}
```

## 6. 系统管理

### 6.1 获取系统基本信息

**接口路径**: `/`  
**请求方式**: GET  
**接口描述**: 获取系统基本信息

**响应示例**:
```json
{
  "name": "Graphuison 知识图谱平台",
  "version": "1.0.0",
  "description": "基于多粒度知识融合的智能知识图谱平台"
}
```

### 6.2 获取知识图谱统计信息

**接口路径**: `/stats`  
**请求方式**: GET  
**接口描述**: 获取知识图谱统计信息

**响应示例**:
```json
{
  "entities_count": 156,
  "triples_count": 243,
  "relation_types_count": 8,
  "granularity_stats": {
    "fine": 98,
    "medium": 45,
    "coarse": 36,
    "cross_granularity": 64
  }
}
```

### 6.3 清空知识图谱数据

**接口路径**: `/graph/clear`  
**请求方式**: DELETE  
**接口描述**: 清空知识图谱数据（管理员功能）

**响应示例**:
```json
{
  "message": "知识图谱数据已清空"
}
``` 