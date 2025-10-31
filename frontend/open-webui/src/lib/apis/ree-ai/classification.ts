/**
 * REE AI Classification API Client
 * Handles property classification and attribute extraction
 */

import { WEBUI_BASE_URL } from '$lib/constants';

export interface ClassificationRequest {
	text: string;
	options?: {
		extract_attributes?: boolean;
		confidence_threshold?: number;
	};
}

export interface ClassificationResponse {
	property_type: string;
	confidence: number;
	attributes?: {
		location?: string;
		price?: number;
		area?: number;
		bedrooms?: number;
		bathrooms?: number;
	};
	metadata?: Record<string, any>;
}

/**
 * Classify property text and extract attributes
 */
export const classifyProperty = async (
	token: string,
	request: ClassificationRequest
): Promise<ClassificationResponse> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/classification/classify`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Classification failed');
	}

	return await res.json();
};

/**
 * Extract attributes from property description
 */
export const extractAttributes = async (
	token: string,
	text: string
): Promise<Record<string, any>> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/classification/extract`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify({ text })
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Attribute extraction failed');
	}

	return await res.json();
};
