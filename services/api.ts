// API Client for SocialAgent Pro Backend

export const BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('auth_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options?.headers as Record<string, string> || {})
  };

  const doFetch = async (): Promise<T> => {
    const response = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });

    if (!response.ok) {
      let detail = `${response.statusText}`;
      try {
        const body = await response.json();
        detail = body.detail || body.message || detail;
      } catch {}
      throw new ApiError(response.status, detail);
    }

    return await response.json();
  };

  try {
    return await doFetch();
  } catch (error) {
    // Retry once on network failure (TypeError means fetch itself failed)
    if (error instanceof TypeError) {
      return await doFetch();
    }
    throw error;
  }
}

// --- Dashboard ---

export const DashboardAPI = {
  getOverview: (timeframe: '24h' | '7d' | '30d') =>
    apiFetch<any>(`/dashboard/overview?timeframe=${timeframe}`),

  getPlatformStats: (platform: string) =>
    apiFetch<any>(`/dashboard/${platform}`),
};

// --- Review Queue ---

export const ReviewAPI = {
  getQueue: (filters?: { platform?: string; risk?: string }) => {
    const params = new URLSearchParams();
    if (filters?.platform) params.set('platform', filters.platform);
    if (filters?.risk) params.set('risk', filters.risk);
    const qs = params.toString();
    return apiFetch<any[]>(`/review/queue${qs ? `?${qs}` : ''}`);
  },

  decide: (id: string, decision: 'approve' | 'reject' | 'edit', finalComment?: string) =>
    apiFetch<{ success: boolean }>(`/review/${id}/decide`, {
      method: 'POST',
      body: JSON.stringify({ decision, final_comment: finalComment }),
    }),

  getHistory: (date?: string) => {
    const qs = date ? `?date=${date}` : '';
    return apiFetch<any[]>(`/review/history${qs}`);
  },
};

// --- Personas ---

export const PersonaAPI = {
  getPersonas: () =>
    apiFetch<any[]>('/personas'),

  createPersona: (data: any) =>
    apiFetch<any>('/personas', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updatePersona: (id: string, data: any) =>
    apiFetch<any>(`/personas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  generatePersona: (documentContext: string) =>
    apiFetch<{ coreIdentity: string; toneModifiers: string }>('/personas/generate', {
      method: 'POST',
      body: JSON.stringify({ document_context: documentContext }),
    }),
};

// --- Platform Hubs ---

export const HubAPI = {
  getStats: (platform: string) =>
    apiFetch<any>(`/hubs/${platform}/stats`),

  smartDiscovery: (query: string, maxResults = 10) =>
    apiFetch<any>(`/hubs/x/smart-discovery`, {
      method: 'POST',
      body: JSON.stringify({ query, max_results: maxResults }),
    }),
};

// --- Jen (Review Posts) ---

export const JenAPI = {
  getResponseQueue: (limit = 10) =>
    apiFetch<{ posts: any[] }>(`/jen/response-queue?limit=${limit}`),

  getReviewPosts: (status: string = 'pending') =>
    apiFetch<{ posts: any[] }>(`/jen/review-posts?status=${status}`),

  addReviewPost: (post: any) =>
    apiFetch<any>('/jen/review-posts', {
      method: 'POST',
      body: JSON.stringify(post),
    }),

  saveDraft: (postId: string, comment: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}/draft`, {
      method: 'PUT',
      body: JSON.stringify({ comment }),
    }),

  approvePost: (postId: string, comment: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comment }),
    }),

  deletePost: (postId: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}`, {
      method: 'DELETE',
    }),
};

// --- Agent ---

export const AgentAPI = {
  autoRefresh: () =>
    apiFetch<any>('/agent/auto-refresh', { method: 'POST' }),
};

// --- Comments / Library ---

export const CommentsAPI = {
  getComments: (filters?: { category?: string; search?: string; platform?: string; page?: number }) => {
    const params = new URLSearchParams();
    if (filters?.category && filters.category !== 'All') params.set('category', filters.category);
    if (filters?.search) params.set('search', filters.search);
    if (filters?.platform) params.set('platform', filters.platform);
    if (filters?.page) params.set('page', String(filters.page));
    const qs = params.toString();
    return apiFetch<any[]>(`/comments${qs ? `?${qs}` : ''}`);
  },

  saveComment: (id: number, tags: string[], notes: string) =>
    apiFetch<any>(`/comments/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ tags, notes }),
    }),

  exportCsv: (filters?: { category?: string }) => {
    const params = new URLSearchParams();
    if (filters?.category) params.set('category', filters.category);
    const qs = params.toString();
    return apiFetch<Blob>(`/comments/export${qs ? `?${qs}` : ''}`);
  },
};

// --- Connections ---

export const ConnectionsAPI = {
  getConnections: () =>
    apiFetch<any[]>('/connections'),

  connect: (platform: string) =>
    apiFetch<{ auth_url: string }>(`/connections/${platform}/connect`, { method: 'POST' }),

  disconnect: (platform: string) =>
    apiFetch<{ success: boolean }>(`/connections/${platform}/disconnect`, { method: 'POST' }),

  testConnection: (platform: string) =>
    apiFetch<{ healthy: boolean; message: string }>(`/connections/${platform}/test`, { method: 'POST' }),

  handleCallback: (platform: string, code: string, state: string) =>
    apiFetch<{ success: boolean }>(`/connections/${platform}/callback`, {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    }),
};

// --- Settings ---

export const SettingsAPI = {
  // Voice
  getVoiceConfig: () =>
    apiFetch<any>('/settings/voice'),

  updateVoiceConfig: (data: any) =>
    apiFetch<any>('/settings/voice', { method: 'PUT', body: JSON.stringify(data) }),

  testVoice: (context: string) =>
    apiFetch<{ results: any[] }>('/settings/voice/test', {
      method: 'POST',
      body: JSON.stringify({ post_context: context }),
    }),

  // Risk & Compliance
  getRiskConfig: () =>
    apiFetch<any>('/settings/risk'),

  updateRiskConfig: (data: any) =>
    apiFetch<any>('/settings/risk', { method: 'PUT', body: JSON.stringify(data) }),

  // Discovery
  getDiscoveryConfig: () =>
    apiFetch<any>('/settings/discovery'),

  updateDiscoveryConfig: (data: any) =>
    apiFetch<any>('/settings/discovery', { method: 'PUT', body: JSON.stringify(data) }),

  // Execution
  getExecutionConfig: () =>
    apiFetch<any>('/settings/execution'),

  updateExecutionConfig: (data: any) =>
    apiFetch<any>('/settings/execution', { method: 'PUT', body: JSON.stringify(data) }),

  // API Keys
  getApiKeys: () =>
    apiFetch<any[]>('/settings/api-keys'),

  updateApiKey: (provider: string, key: string) =>
    apiFetch<any>(`/settings/api-keys/${provider}`, {
      method: 'PUT',
      body: JSON.stringify({ key }),
    }),

  testApiKey: (provider: string) =>
    apiFetch<{ valid: boolean; message: string }>(`/settings/api-keys/${provider}/test`, { method: 'POST' }),

  // Notifications
  getNotificationConfig: () =>
    apiFetch<any>('/settings/notifications'),

  updateNotificationConfig: (data: any) =>
    apiFetch<any>('/settings/notifications', { method: 'PUT', body: JSON.stringify(data) }),

  // Knowledge Base files
  getFiles: (section: string) =>
    apiFetch<any[]>(`/settings/${section}/files`),

  uploadFile: (section: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('auth_token');
    return fetch(`${BASE_URL}/settings/${section}/files`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    }).then(async (res) => {
      if (!res.ok) throw new ApiError(res.status, 'Upload failed');
      return res.json();
    });
  },

  deleteFile: (section: string, fileId: string) =>
    apiFetch<{ success: boolean }>(`/settings/${section}/files/${fileId}`, { method: 'DELETE' }),

  syncKnowledgeBase: () =>
    apiFetch<{ success: boolean }>('/settings/knowledge-base/sync', { method: 'POST' }),
};

// --- Analytics ---

export const AnalyticsAPI = {
  getEngagementTimeline: (timeframe: '24h' | '7d' | '30d') =>
    apiFetch<any>(`/analytics/engagement-timeline?timeframe=${timeframe}`),

  getHashtagPerformance: () =>
    apiFetch<any[]>('/analytics/hashtag-performance'),
};

// --- Execution ---

export const ExecutionAPI = {
  getStatus: () =>
    apiFetch<any>('/execution/status'),

  setKillSwitch: (enabled: boolean) =>
    apiFetch<{ success: boolean }>('/execution/kill-switch', {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    }),

  getWorkers: () =>
    apiFetch<any[]>('/execution/workers'),
};

// --- Auth (legacy compat) ---

export const AuthAPI = {
  getAuthUrl: (platform: string) => `${BASE_URL}/auth/${platform}/authorize`,
  disconnect: (platform: string) => ConnectionsAPI.disconnect(platform),
};
