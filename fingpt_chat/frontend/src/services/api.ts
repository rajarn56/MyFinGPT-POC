/** API client for REST endpoints */
import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { API_BASE_URL } from '../config/api';
import type {
  ChatRequest,
  ChatResponse,
  ChatHistoryResponse,
  SessionResponse
} from '../types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/chat', {
      session_id: sessionId,
      message,
    } as ChatRequest);
    return response.data;
  }

  async getHistory(
    sessionId: string,
    limit = 100,
    offset = 0
  ): Promise<ChatMessage[]> {
    const response = await this.client.get<ChatHistoryResponse>(
      `/api/chat/history/${sessionId}`,
      {
        params: { limit, offset },
      }
    );
    return response.data.messages;
  }

  async createSession(): Promise<SessionResponse> {
    const response = await this.client.post<SessionResponse>('/api/chat/session');
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/chat/session/${sessionId}`);
  }

  async healthCheck(): Promise<any> {
    const response = await this.client.get('/api/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Re-export types for convenience
import type { ChatMessage } from '../types/chat';
export type { ChatMessage };

