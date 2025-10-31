/**
 * REE AI Utility Functions
 * Helper functions for REE AI frontend
 */

/**
 * Format Vietnamese currency
 */
export function formatPrice(price: number): string {
	if (price >= 1000000000) {
		return `${(price / 1000000000).toFixed(2)} tỷ`;
	}
	if (price >= 1000000) {
		return `${(price / 1000000).toFixed(0)} triệu`;
	}
	return `${price.toLocaleString('vi-VN')} VNĐ`;
}

/**
 * Format area with unit
 */
export function formatArea(area: number, unit: string = 'm²'): string {
	return `${area.toFixed(0)} ${unit}`;
}

/**
 * Calculate price per square meter
 */
export function calculatePricePerSqm(price: number, area: number): number {
	if (!area || area === 0) return 0;
	return price / area;
}

/**
 * Format price per square meter
 */
export function formatPricePerSqm(price: number, area: number): string {
	const pricePerSqm = calculatePricePerSqm(price, area);
	return `${pricePerSqm.toLocaleString('vi-VN', { maximumFractionDigits: 0 })} VNĐ/m²`;
}

/**
 * Get property type label in Vietnamese
 */
export function getPropertyTypeLabel(type: string): string {
	const labels: Record<string, string> = {
		apartment: 'Căn hộ',
		house: 'Nhà riêng',
		villa: 'Biệt thự',
		land: 'Đất nền',
		townhouse: 'Nhà phố',
		office: 'Văn phòng',
		shophouse: 'Nhà mặt tiền',
		warehouse: 'Kho xưởng',
		penthouse: 'Penthouse',
		duplex: 'Duplex',
		studio: 'Studio'
	};
	return labels[type] || type;
}

/**
 * Format Vietnamese date
 */
export function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return date.toLocaleDateString('vi-VN', {
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	});
}

/**
 * Format relative time (e.g., "2 ngày trước")
 */
export function formatRelativeTime(dateString: string): string {
	const date = new Date(dateString);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffSecs = Math.floor(diffMs / 1000);
	const diffMins = Math.floor(diffSecs / 60);
	const diffHours = Math.floor(diffMins / 60);
	const diffDays = Math.floor(diffHours / 24);
	const diffMonths = Math.floor(diffDays / 30);
	const diffYears = Math.floor(diffDays / 365);

	if (diffSecs < 60) return 'Vừa xong';
	if (diffMins < 60) return `${diffMins} phút trước`;
	if (diffHours < 24) return `${diffHours} giờ trước`;
	if (diffDays < 30) return `${diffDays} ngày trước`;
	if (diffMonths < 12) return `${diffMonths} tháng trước`;
	return `${diffYears} năm trước`;
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
	if (!text) return '';
	if (text.length <= maxLength) return text;
	return text.substring(0, maxLength) + '...';
}

/**
 * Parse price string to number (e.g., "3.5 tỷ" -> 3500000000)
 */
export function parsePriceString(priceStr: string): number | null {
	const cleaned = priceStr.toLowerCase().trim();

	// Handle billion (tỷ)
	const billionMatch = cleaned.match(/(\d+\.?\d*)\s*(tỷ|ty|billion)/);
	if (billionMatch) {
		return parseFloat(billionMatch[1]) * 1000000000;
	}

	// Handle million (triệu)
	const millionMatch = cleaned.match(/(\d+\.?\d*)\s*(triệu|tr|million)/);
	if (millionMatch) {
		return parseFloat(millionMatch[1]) * 1000000;
	}

	// Handle plain number
	const numberMatch = cleaned.match(/(\d+\.?\d*)/);
	if (numberMatch) {
		return parseFloat(numberMatch[1]);
	}

	return null;
}

/**
 * Validate Vietnamese phone number
 */
export function isValidPhoneNumber(phone: string): boolean {
	const phoneRegex = /^(0|\+84)(3|5|7|8|9)\d{8}$/;
	return phoneRegex.test(phone.replace(/\s/g, ''));
}

/**
 * Format phone number
 */
export function formatPhoneNumber(phone: string): string {
	const cleaned = phone.replace(/\s/g, '');
	if (cleaned.length === 10) {
		return `${cleaned.substring(0, 4)} ${cleaned.substring(4, 7)} ${cleaned.substring(7)}`;
	}
	return phone;
}

/**
 * Get property status label
 */
export function getPropertyStatusLabel(status: string): string {
	const labels: Record<string, string> = {
		available: 'Còn trống',
		sold: 'Đã bán',
		rented: 'Đã cho thuê',
		pending: 'Đang giao dịch',
		reserved: 'Đã đặt cọc'
	};
	return labels[status] || status;
}

/**
 * Get property status color
 */
export function getPropertyStatusColor(status: string): string {
	const colors: Record<string, string> = {
		available: 'green',
		sold: 'red',
		rented: 'blue',
		pending: 'yellow',
		reserved: 'orange'
	};
	return colors[status] || 'gray';
}

/**
 * Extract location parts (district, city)
 */
export function parseLocation(location: string): { district?: string; city?: string } {
	const parts = location.split(',').map((p) => p.trim());

	if (parts.length >= 2) {
		return {
			district: parts[0],
			city: parts[parts.length - 1]
		};
	}

	return { city: location };
}

/**
 * Generate property share URL
 */
export function getPropertyShareUrl(propertyId: string): string {
	if (typeof window !== 'undefined') {
		return `${window.location.origin}/properties/${propertyId}`;
	}
	return `/properties/${propertyId}`;
}

/**
 * Copy to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
	try {
		if (navigator.clipboard) {
			await navigator.clipboard.writeText(text);
			return true;
		}
		// Fallback for older browsers
		const textarea = document.createElement('textarea');
		textarea.value = text;
		textarea.style.position = 'fixed';
		textarea.style.opacity = '0';
		document.body.appendChild(textarea);
		textarea.select();
		document.execCommand('copy');
		document.body.removeChild(textarea);
		return true;
	} catch (error) {
		console.error('Copy to clipboard failed:', error);
		return false;
	}
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
	func: T,
	wait: number
): (...args: Parameters<T>) => void {
	let timeout: ReturnType<typeof setTimeout> | null = null;

	return function executedFunction(...args: Parameters<T>) {
		const later = () => {
			timeout = null;
			func(...args);
		};

		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(later, wait);
	};
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
	func: T,
	limit: number
): (...args: Parameters<T>) => void {
	let inThrottle: boolean;

	return function executedFunction(...args: Parameters<T>) {
		if (!inThrottle) {
			func(...args);
			inThrottle = true;
			setTimeout(() => (inThrottle = false), limit);
		}
	};
}

/**
 * Check if property is new (posted within 7 days)
 */
export function isNewProperty(createdAt: string): boolean {
	const date = new Date(createdAt);
	const now = new Date();
	const diffDays = (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);
	return diffDays <= 7;
}

/**
 * Calculate property score based on various factors
 */
export function calculatePropertyScore(property: {
	price: number;
	area: number;
	location: string;
	bedrooms?: number;
	bathrooms?: number;
}): number {
	let score = 0;

	// Price per sqm (lower is better)
	const pricePerSqm = property.price / property.area;
	if (pricePerSqm < 50000000) score += 30;
	else if (pricePerSqm < 70000000) score += 20;
	else if (pricePerSqm < 100000000) score += 10;

	// Location (premium districts)
	const premiumDistricts = ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 7', 'Bình Thạnh'];
	if (premiumDistricts.some((d) => property.location.includes(d))) {
		score += 20;
	}

	// Size
	if (property.area >= 50 && property.area <= 100) score += 15;
	else if (property.area > 100 && property.area <= 200) score += 10;

	// Bedrooms
	if (property.bedrooms && property.bedrooms >= 2 && property.bedrooms <= 3) {
		score += 15;
	}

	// Bathrooms
	if (property.bathrooms && property.bathrooms >= 2) {
		score += 10;
	}

	return Math.min(score, 100);
}

/**
 * Get property image URL or placeholder
 */
export function getPropertyImageUrl(images?: string[]): string {
	if (images && images.length > 0) {
		return images[0];
	}
	return '/static/placeholder-property.png';
}

/**
 * Format number with thousands separator
 */
export function formatNumber(num: number): string {
	return num.toLocaleString('vi-VN');
}

/**
 * Sanitize search query
 */
export function sanitizeSearchQuery(query: string): string {
	return query.trim().replace(/[<>]/g, '');
}

/**
 * Check if user is on mobile
 */
export function isMobile(): boolean {
	if (typeof window === 'undefined') return false;
	return window.innerWidth < 768;
}

/**
 * Storage helpers
 */
export const storage = {
	get: (key: string): any => {
		if (typeof window === 'undefined') return null;
		try {
			const item = localStorage.getItem(key);
			return item ? JSON.parse(item) : null;
		} catch {
			return null;
		}
	},

	set: (key: string, value: any): void => {
		if (typeof window === 'undefined') return;
		try {
			localStorage.setItem(key, JSON.stringify(value));
		} catch (error) {
			console.error('Storage set error:', error);
		}
	},

	remove: (key: string): void => {
		if (typeof window === 'undefined') return;
		localStorage.removeItem(key);
	},

	clear: (): void => {
		if (typeof window === 'undefined') return;
		localStorage.clear();
	}
};
