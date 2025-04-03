import { create } from 'zustand';
import type { Document, KnowledgeGraph, ChatMessage } from '@/types';

interface AppState {
  // 用户状态
  user: {
    id: string | null;
    username: string | null;
    email: string | null;
  } | null;
  setUser: (user: AppState['user']) => void;
  clearUser: () => void;

  // 文档状态
  documents: Document[];
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  updateDocument: (id: string, document: Partial<Document>) => void;
  deleteDocument: (id: string) => void;

  // 图谱状态
  graphs: KnowledgeGraph[];
  currentGraph: KnowledgeGraph | null;
  setGraphs: (graphs: KnowledgeGraph[]) => void;
  setCurrentGraph: (graph: KnowledgeGraph | null) => void;
  addGraph: (graph: KnowledgeGraph) => void;
  updateGraph: (id: string, graph: Partial<KnowledgeGraph>) => void;
  deleteGraph: (id: string) => void;

  // 聊天状态
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
}

export const useStore = create<AppState>((set) => ({
  // 用户状态
  user: null,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),

  // 文档状态
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),
  updateDocument: (id, document) =>
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === id ? { ...doc, ...document } : doc
      ),
    })),
  deleteDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
    })),

  // 图谱状态
  graphs: [],
  currentGraph: null,
  setGraphs: (graphs) => set({ graphs }),
  setCurrentGraph: (graph) => set({ currentGraph: graph }),
  addGraph: (graph) =>
    set((state) => ({ graphs: [...state.graphs, graph] })),
  updateGraph: (id, graph) =>
    set((state) => ({
      graphs: state.graphs.map((g) =>
        g.id === id ? { ...g, ...graph } : g
      ),
    })),
  deleteGraph: (id) =>
    set((state) => ({
      graphs: state.graphs.filter((g) => g.id !== id),
      currentGraph: state.currentGraph?.id === id ? null : state.currentGraph,
    })),

  // 聊天状态
  messages: [],
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  clearMessages: () => set({ messages: [] }),
})); 