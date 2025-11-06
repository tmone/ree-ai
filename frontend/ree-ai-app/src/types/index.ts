/**
 * REE AI Frontend Types
 * Based on backend shared models
 */

// ============================================================================
// User Types
// ============================================================================

export type UserType = 'seller' | 'buyer' | 'both';
export type UserRole = 'pending' | 'user' | 'admin';

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  user_type: UserType;
  role: UserRole;
  phone_number?: string;
  company_name?: string;
  license_number?: string;
  verified: boolean;
  created_at: string;
}

export interface UserRegistration {
  email: string;
  password: string;
  full_name: string;
  user_type: UserType;
  phone_number?: string;
  company_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user: User;
}

// ============================================================================
// Property Types
// ============================================================================

export type PropertyStatus = 'draft' | 'pending' | 'active' | 'sold' | 'rented' | 'paused';
export type VerificationStatus = 'unverified' | 'pending' | 'verified' | 'rejected';
export type ListingType = 'sale' | 'rent';

export interface Property {
  property_id: string;
  owner_id: string;
  title: string;
  description: string;
  property_type: string;
  listing_type: ListingType;

  // Location
  address?: string;
  district: string;
  city: string;
  location?: string;

  // Pricing
  price: number;
  price_display?: string;
  price_per_sqm?: number;

  // Specifications
  area: number;
  area_display?: string;
  bedrooms: number;
  bathrooms: number;
  floors?: number;

  // Status
  status: PropertyStatus;
  verification_status: VerificationStatus;

  // Images
  images?: string[];
  thumbnail?: string;

  // Engagement metrics
  views_count: number;
  favorites_count: number;
  inquiries_count: number;

  // Timestamps
  created_at: string;
  updated_at: string;
  published_at?: string;

  // Flexible attributes (OpenSearch allows unlimited fields)
  [key: string]: any;
}

export interface PropertyCreate {
  title: string;
  description: string;
  property_type: string;
  listing_type: ListingType;

  // Location
  address?: string;
  district: string;
  city: string;

  // Pricing
  price: number;

  // Specifications
  area: number;
  bedrooms: number;
  bathrooms: number;
  floors?: number;

  // Options
  publish_immediately?: boolean;

  // Additional attributes
  [key: string]: any;
}

export interface PropertyUpdate {
  title?: string;
  description?: string;
  property_type?: string;
  listing_type?: ListingType;
  address?: string;
  district?: string;
  city?: string;
  price?: number;
  area?: number;
  bedrooms?: number;
  bathrooms?: number;
  floors?: number;
  [key: string]: any;
}

export interface PropertyStatusUpdate {
  status: PropertyStatus;
  reason?: string;
}

// ============================================================================
// Favorites Types
// ============================================================================

export interface Favorite {
  id: number;
  user_id: string;
  property_id: string;
  notes?: string;
  created_at: string;
}

export interface FavoriteWithProperty extends Favorite {
  property: Property;
}

export interface FavoriteCreate {
  property_id: string;
  notes?: string;
}

export interface FavoriteUpdate {
  notes: string;
}

// ============================================================================
// Saved Search Types
// ============================================================================

export interface SavedSearch {
  id: number;
  user_id: string;
  name: string;
  query: string;
  filters: SearchFilters;
  notify_email: boolean;
  notify_frequency: 'instant' | 'daily' | 'weekly';
  active: boolean;
  created_at: string;
  last_notified_at?: string;
}

export interface SearchFilters {
  property_type?: string;
  listing_type?: ListingType;
  city?: string;
  district?: string;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  min_bathrooms?: number;
  max_bathrooms?: number;
  [key: string]: any;
}

export interface SavedSearchCreate {
  name: string;
  query: string;
  filters?: SearchFilters;
  notify_email?: boolean;
  notify_frequency?: 'instant' | 'daily' | 'weekly';
}

export interface SavedSearchUpdate {
  name?: string;
  query?: string;
  filters?: SearchFilters;
  notify_email?: boolean;
  notify_frequency?: 'instant' | 'daily' | 'weekly';
  active?: boolean;
}

// ============================================================================
// Inquiry Types
// ============================================================================

export type InquiryStatus = 'pending' | 'responded' | 'closed';

export interface Inquiry {
  inquiry_id: string;
  property_id: string;
  sender_id: string;
  receiver_id: string;
  message: string;
  contact_email?: string;
  contact_phone?: string;
  preferred_contact_time?: string;
  status: InquiryStatus;
  response_message?: string;
  responded_at?: string;
  created_at: string;
}

export interface InquiryWithDetails extends Inquiry {
  property: Property;
  sender: User;
  receiver: User;
}

export interface InquiryCreate {
  property_id: string;
  message: string;
  contact_email?: string;
  contact_phone?: string;
  preferred_contact_time?: string;
}

export interface InquiryResponse {
  response_message: string;
}

export interface InquiryStatusUpdate {
  status: InquiryStatus;
}

export interface InquiryStats {
  total_inquiries: number;
  pending_count: number;
  responded_count: number;
  closed_count: number;
  response_rate: number;
  avg_response_time_hours?: number;
}

// ============================================================================
// Search & API Response Types
// ============================================================================

export interface SearchRequest {
  query: string;
  filters?: SearchFilters;
  limit?: number;
}

export interface SearchResponse {
  results: Property[];
  total: number;
  execution_time_ms: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
