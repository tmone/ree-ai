/**
 * REE AI Orchestrator API Client
 * Handles AI-powered routing and intent detection
 */

import { WEBUI_BASE_URL } from '$lib/constants';

export interface OrchestratorRequest {
	query: string;
	user_id?: string;
	context?: Record<string, any>;
}

export interface OrchestratorResponse {
	intent: string;
	response: string;
	service_used: string;
	confidence: number;
	metadata?: Record<string, any>;
}

/**
 * Send a query to the Orchestrator for AI-powered routing
 */
export const sendOrchestratorQuery = async (
	token: string,
	request: OrchestratorRequest
): Promise<OrchestratorResponse> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/orchestrator/query`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(request)
	});

	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || 'Orchestrator request failed');
	}

	return await res.json();
};

/**
 * Get orchestrator health status
 */
export const getOrchestratorHealth = async (token: string): Promise<any> => {
	const res = await fetch(`${WEBUI_BASE_URL}/api/orchestrator/health`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	});

	if (!res.ok) {
		throw new Error('Failed to get orchestrator health');
	}

	return await res.json();
};
