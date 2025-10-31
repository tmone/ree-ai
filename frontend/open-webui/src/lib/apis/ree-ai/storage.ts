/**
 * REE AI Storage API Client
 * Handles property search and retrieval from OpenSearch
 */

import { WEBUI_BASE_URL } from '$lib/constants';

export interface PropertySearchRequest {
	query: string;
	filters?: {
		property_type?: string[];
		location?: string[];
		min_price?: number;
		max_price?: number;
		min_area?: number;
		max_area?: number;
	};
	limit?: number;
	offset?: number;
}

export interface Property {
	id: string;
	title: string;
	description: string;
	property_type: string;
	location: string;
	price: number;
	area: number;
	bedrooms?: number;
	bathrooms?: number;
	images?: string[];
	source_url?: string;
	created_at: string;
	score?: number;
}

export interface PropertySearchResponse {
	results: Property[];
	total: number;
	took: number;
}

/**
 * Search properties using semantic search and filters
 */
export const searchProperties = async (
	token: string,
	request: PropertySearchRequest
): Promise<PropertySearchResponse> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/storage/search`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Property search failed');
	}

	return await res.json();
};

/**
 * Get property by ID
 */
export const getPropertyById = async (token: string, propertyId: string): Promise<Property> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/storage/properties/${propertyId}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get property');
	}

	return await res.json();
};

/**
 * Get property suggestions based on user preferences
 */
export const getPropertySuggestions = async (
	token: string,
	userId: string,
	limit: number = 5
): Promise<Property[]> => {
	const res = await fetch(
		`${WEBUI_BASE_URL}/api/storage/suggestions?user_id=${userId}&limit=${limit}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				...(token && { authorization: `Bearer ${token}` })
			}
		}
	);

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Failed to get suggestions');
	}

	return await res.json();
};
