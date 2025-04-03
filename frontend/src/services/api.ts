import axios, { AxiosError } from 'axios';
import { APIError, APIResponse } from '@/types/api';
import { getToken } from '@/utils/auth';
import {
  User,
  AuthResponse,
  UpdateProfileRequest,
  ChangePasswordRequest,
} from '@/types/user';
import type { LoginForm, RegisterForm, Document, KnowledgeGraph, SearchResult, ChatMessage, ExportOptions } from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<APIError>) => {
    const apiError: APIError = {
      detail: error.response?.data?.detail || '请求失败，请重试',
      code: error.response?.data?.code,
      status: error.response?.status,
    };
    return Promise.reject(apiError);
  }
);

export const APIService = {
  // 认证相关
  login: async (data: { username: string; password: string }) => {
    return api.post<APIResponse<AuthResponse>>('/auth/login', data);
  },

  register: async (data: { username: string; email: string; password: string }) => {
    return api.post<APIResponse<AuthResponse>>('/auth/register', data);
  },

  getCurrentUser: async () => {
    return api.get<APIResponse<User>>('/auth/me');
  },

  updateProfile: async (data: UpdateProfileRequest) => {
    return api.put<APIResponse<User>>('/auth/me', data);
  },

  changePassword: async (data: ChangePasswordRequest) => {
    return api.put<APIResponse<void>>('/auth/me/password', data);
  },

  // 文档相关
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<APIResponse<Document>>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getDocuments: async () => {
    return api.get<APIResponse<Document[]>>('/documents');
  },

  deleteDocument: async (id: string) => {
    return api.delete<APIResponse<void>>(`/documents/${id}`);
  },

  // 知识图谱相关
  getGraphs: async () => {
    return api.get<APIResponse<KnowledgeGraph[]>>('/kg');
  },

  searchGraph: async (query: string) => {
    return api.get<APIResponse<SearchResult[]>>('/kg/search', { params: { query } });
  },

  exportGraph: async (id: string, options: { format: string; granularity: string; includeMetadata: boolean }) => {
    return api.get<Blob>(`/kg/${id}/export`, {
      params: options,
      responseType: 'blob',
    });
  },

  // 聊天相关
  sendMessage: async (message: string) => {
    return api.post<APIResponse<ChatMessage>>('/chat/message', { message });
  },
}; 