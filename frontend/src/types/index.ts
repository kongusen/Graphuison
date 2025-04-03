// 用户认证相关类型
export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

// 文档相关类型
export interface Document {
  id: string;
  name: string;
  description: string;
  size: number;
  created_at: string;
  status: 'processing' | 'completed' | 'failed';
  graph_id?: string;
}

// 知识图谱相关类型
export interface KnowledgeGraph {
  id: string;
  name: string;
  description: string;
  created_at: string;
  document_id: string;
  stats: {
    nodes: number;
    relationships: number;
  };
}

export interface SearchResult {
  entity: string;
  type: string;
  relationships: Array<{
    target: string;
    type: string;
    confidence: number;
  }>;
}

export type Granularity = 'fine' | 'medium' | 'coarse';

// 聊天相关类型
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// 导出相关类型
export interface ExportOptions {
  format: 'json' | 'csv' | 'graphml';
  granularity: Granularity;
  includeMetadata: boolean;
} 