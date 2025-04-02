// frontend/utils/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
  });

export const preprocessText = async (text) => {
    try {
    const response = await api.post('/text/preprocess', { text });
    return response.data;
    } catch (error) {
    console.error('Error preprocessing text:', error);
    throw error;
    }
};

export const extractConcepts = async (sentences) => {
    try {
    const response = await api.post('/concepts/extract', { sentences });
    return response.data;
    } catch (error) {
    console.error('Error extracting concepts:', error);
    throw error;
    }
};

    export const extractRelations = async (concepts, file) => {
      try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/relations/extract', { concepts, file: formData }, {
          headers: {
              'Content-Type': 'multipart/form-data',
          }
        });
        return response.data;
      } catch (error) {
        console.error('Error extracting relations:', error);
        throw error;
      }
    };

export const fuseGraph = async (triples, annotated_triples, page = 1, page_size = 10) => {
    try {
    const response = await api.post('/graph/fuse', { triples, annotated_triples, page, page_size});
    return response.data;
    } catch (error) {
    console.error('Error fusing graph:', error);
    throw error;
    }
};

export const getAllGraphData = async() => {
    try {
      const response = await api.get('/graph/all');
      return response.data;
    } catch(error) {
       console.error("Error get all graph data:", error);
       throw error;
    }
};

export const getStats = async() => {
    try {
       const response = await api.get('/stats');
       return response.data;
    } catch(error) {
        console.error("Error get stats:", error);
        throw error;
    }
}
 export const sendMessage = async (query) => {
  try {
    const response = await api.post('/chat', { query });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getHistory = async() => {
    try{
      const response = await api.get('/chat/history');
      return response.data;
    } catch(error) {
       console.error('Error get chat history:', error);
        throw error;
    }
}
export default api;