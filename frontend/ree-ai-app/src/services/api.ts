/**
 * REE AI API Service Layer
 * Centralized API client for all backend endpoints
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  User,
  UserRegistration,
  UserLogin,
  AuthTokens,
  Property,
  PropertyCreate,
  PropertyUpdate,
  PropertyStatusUpdate,
  FavoriteCreate,
  FavoriteUpdate,
  FavoriteWithProperty,
  SavedSearch,
  SavedSearchCreate,
  SavedSearchUpdate,
  InquiryCreate,
  InquiryResponse,
  InquiryStatusUpdate,
  InquiryWithDetails,
  InquiryStats,
  SearchRequest,
  SearchResponse,
  PaginatedResponse,
  ApiError,
} from '../types';

// API Base URLs
const DB_GATEWAY_URL = process.env.NEXT_PUBLIC_DB_GATEWAY_URL || 'http://localhost:8081';
const USER_MANAGEMENT_URL = process.env.NEXT_PUBLIC_USER_MANAGEMENT_URL || 'http://localhost:8085';

// Create axios instances
const dbGatewayClient: AxiosInstance = axios.create({
  baseURL: DB_GATEWAY_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const userManagementClient: AxiosInstance = axios.create({
  baseURL: USER_MANAGEMENT_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

dbGatewayClient.interceptors.request.use(addAuthToken);
userManagementClient.interceptors.request.use(addAuthToken);

// Response interceptor to handle errors
const handleError = (error: AxiosError<ApiError>) => {
  if (error.response?.status === 401) {
    // Unauthorized - clear token and redirect to login
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
  return Promise.reject(error.response?.data || { detail: 'An error occurred' });
};

dbGatewayClient.interceptors.response.use((response) => response, handleError);
userManagementClient.interceptors.response.use((response) => response, handleError);

// ============================================================================
// Authentication API
// ============================================================================

export const authApi = {
  /**
   * Register new user
   */
  register: async (data: UserRegistration): Promise<AuthTokens> => {
    const response = await userManagementClient.post<AuthTokens>('/register', data);

    // Save token and user to localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  },

  /**
   * Login existing user
   */
  login: async (credentials: UserLogin): Promise<AuthTokens> => {
    const response = await userManagementClient.post<AuthTokens>('/login', credentials);

    // Save token and user to localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  /**
   * Get current user from localStorage
   */
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },
};

// ============================================================================
// Property Management API (Seller)
// ============================================================================

export const propertyApi = {
  /**
   * Create new property listing
   */
  create: async (data: PropertyCreate): Promise<Property> => {
    const response = await dbGatewayClient.post<Property>('/properties', data);
    return response.data;
  },

  /**
   * Get seller's own properties
   */
  getMyListings: async (params?: {
    status_filter?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Property>> => {
    const response = await dbGatewayClient.get<PaginatedResponse<Property>>('/properties/my-listings', { params });
    return response.data;
  },

  /**
   * Get property by ID
   */
  getById: async (propertyId: string): Promise<Property> => {
    const response = await dbGatewayClient.get<Property>(`/properties/${propertyId}`);
    return response.data;
  },

  /**
   * Update property
   */
  update: async (propertyId: string, data: PropertyUpdate): Promise<Property> => {
    const response = await dbGatewayClient.put<Property>(`/properties/${propertyId}`, data);
    return response.data;
  },

  /**
   * Update property status
   */
  updateStatus: async (propertyId: string, data: PropertyStatusUpdate): Promise<Property> => {
    const response = await dbGatewayClient.put<Property>(`/properties/${propertyId}/status`, data);
    return response.data;
  },

  /**
   * Delete property
   */
  delete: async (propertyId: string): Promise<{ message: string }> => {
    const response = await dbGatewayClient.delete<{ message: string }>(`/properties/${propertyId}`);
    return response.data;
  },

  /**
   * Upload images
   */
  uploadImages: async (propertyId: string, images: string[]): Promise<Property> => {
    const response = await dbGatewayClient.post<Property>(`/properties/${propertyId}/images`, { images });
    return response.data;
  },
};

// ============================================================================
// Search API
// ============================================================================

export const searchApi = {
  /**
   * Search properties (BM25 full-text search)
   */
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await dbGatewayClient.post<SearchResponse>('/search', request);
    return response.data;
  },

  /**
   * Vector search properties (semantic search)
   */
  vectorSearch: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await dbGatewayClient.post<SearchResponse>('/vector-search', request);
    return response.data;
  },

  /**
   * Get database statistics
   */
  getStats: async (): Promise<{
    total_properties: number;
    by_type: Record<string, number>;
    by_district: Record<string, number>;
    by_city: Record<string, number>;
  }> => {
    const response = await dbGatewayClient.get('/stats');
    return response.data;
  },
};

// ============================================================================
// Favorites API (Buyer)
// ============================================================================

export const favoritesApi = {
  /**
   * Add property to favorites
   */
  add: async (data: FavoriteCreate): Promise<{ message: string; favorite_id: number }> => {
    const response = await dbGatewayClient.post('/favorites', data);
    return response.data;
  },

  /**
   * Get user's favorite properties
   */
  getAll: async (params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<FavoriteWithProperty>> => {
    const response = await dbGatewayClient.get<PaginatedResponse<FavoriteWithProperty>>('/favorites', { params });
    return response.data;
  },

  /**
   * Remove property from favorites
   */
  remove: async (propertyId: string): Promise<{ message: string }> => {
    const response = await dbGatewayClient.delete<{ message: string }>(`/favorites/${propertyId}`);
    return response.data;
  },

  /**
   * Update favorite notes
   */
  updateNotes: async (propertyId: string, data: FavoriteUpdate): Promise<{ message: string }> => {
    const response = await dbGatewayClient.put<{ message: string }>(`/favorites/${propertyId}`, data);
    return response.data;
  },
};

// ============================================================================
// Saved Searches API (Buyer)
// ============================================================================

export const savedSearchesApi = {
  /**
   * Create saved search
   */
  create: async (data: SavedSearchCreate): Promise<SavedSearch> => {
    const response = await dbGatewayClient.post<SavedSearch>('/saved-searches', data);
    return response.data;
  },

  /**
   * Get user's saved searches
   */
  getAll: async (params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<SavedSearch>> => {
    const response = await dbGatewayClient.get<PaginatedResponse<SavedSearch>>('/saved-searches', { params });
    return response.data;
  },

  /**
   * Find new matches for saved search
   */
  findNewMatches: async (searchId: string): Promise<{ new_matches: Property[]; count: number }> => {
    const response = await dbGatewayClient.get(`/saved-searches/${searchId}/new-matches`);
    return response.data;
  },

  /**
   * Update saved search
   */
  update: async (searchId: string, data: SavedSearchUpdate): Promise<SavedSearch> => {
    const response = await dbGatewayClient.put<SavedSearch>(`/saved-searches/${searchId}`, data);
    return response.data;
  },

  /**
   * Delete saved search
   */
  delete: async (searchId: string): Promise<{ message: string }> => {
    const response = await dbGatewayClient.delete<{ message: string }>(`/saved-searches/${searchId}`);
    return response.data;
  },
};

// ============================================================================
// Inquiries API (Buyer-Seller Communication)
// ============================================================================

export const inquiriesApi = {
  /**
   * Send inquiry to seller
   */
  send: async (data: InquiryCreate): Promise<{ message: string; inquiry_id: string }> => {
    const response = await dbGatewayClient.post('/inquiries', data);
    return response.data;
  },

  /**
   * Get sent inquiries (buyer)
   */
  getSent: async (params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<InquiryWithDetails>> => {
    const response = await dbGatewayClient.get<PaginatedResponse<InquiryWithDetails>>('/inquiries/sent', { params });
    return response.data;
  },

  /**
   * Get received inquiries (seller)
   */
  getReceived: async (params?: {
    status_filter?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<InquiryWithDetails>> => {
    const response = await dbGatewayClient.get<PaginatedResponse<InquiryWithDetails>>('/inquiries/received', { params });
    return response.data;
  },

  /**
   * Respond to inquiry (seller)
   */
  respond: async (inquiryId: string, data: InquiryResponse): Promise<{ message: string }> => {
    const response = await dbGatewayClient.put<{ message: string }>(`/inquiries/${inquiryId}/respond`, data);
    return response.data;
  },

  /**
   * Update inquiry status
   */
  updateStatus: async (inquiryId: string, data: InquiryStatusUpdate): Promise<{ message: string }> => {
    const response = await dbGatewayClient.put<{ message: string }>(`/inquiries/${inquiryId}/status`, data);
    return response.data;
  },

  /**
   * Get inquiry statistics (seller)
   */
  getStats: async (): Promise<InquiryStats> => {
    const response = await dbGatewayClient.get<InquiryStats>('/inquiries/stats');
    return response.data;
  },
};

// Export all APIs
export const api = {
  auth: authApi,
  property: propertyApi,
  search: searchApi,
  favorites: favoritesApi,
  savedSearches: savedSearchesApi,
  inquiries: inquiriesApi,
};

export default api;
