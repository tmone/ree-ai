/**
 * REE AI RAG Service API Client
 * Handles retrieval-augmented generation for property queries
 */

import { WEBUI_BASE_URL } from '$lib/constants';

export interface RAGRequest {
	query: string;
	user_id?: string;
	filters?: Record<string, any>;
	top_k?: number;
}

export interface RAGResponse {
	answer: string;
	sources: Array<{
		property_id: string;
		title: string;
		snippet: string;
		score: number;
	}>;
	context_used: string[];
	metadata?: Record<string, any>;
}

/**
 * Send a query to RAG service for context-aware responses
 */
export const queryRAG = async (token: string, request: RAGRequest): Promise<RAGResponse> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/rag/query`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'RAG query failed');
	}

	return await res.json();
};

/**
 * Index a new property document for RAG
 */
export const indexProperty = async (
	token: string,
	propertyData: Record<string, any>
): Promise<{ success: boolean; property_id: string }> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/rag/index`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(propertyData)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Property indexing failed');
	}

	return await res.json();
};
