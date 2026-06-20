import type { Friend, POI, Promotion } from '../components/finderz/types';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

type RequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  getFriends: () => request<Friend[]>('/friends'),
  createFriend: (friend: Friend) => request<Friend>('/friends', { method: 'POST', body: friend }),
  toggleFaro: (friendId: string) => request<Friend>(`/friends/${friendId}/faro`, { method: 'PATCH' }),

  getPois: () => request<POI[]>('/pois'),

  getPromotions: () => request<Promotion[]>('/promotions'),
  createPromotion: (promotion: Promotion) => request<Promotion>('/promotions', { method: 'POST', body: promotion }),
  usePromotion: (promotionId: string) => request<Promotion>(`/promotions/${promotionId}/use`, { method: 'PATCH' }),
  clearNewPromotion: (promotionId: string) => request<Promotion>(`/promotions/${promotionId}/clear-new`, { method: 'PATCH' }),
};
