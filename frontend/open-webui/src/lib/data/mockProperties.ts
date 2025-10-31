/**
 * Mock Property Data
 * For development and testing without backend
 */

import type { Property } from '$lib/apis/ree-ai/storage';

export const mockProperties: Property[] = [
	{
		id: 'prop-001',
		title: 'Căn hộ cao cấp 2 phòng ngủ view sông Saigon',
		description:
			'Căn hộ đẹp, nội thất cao cấp, view sông thoáng mát. Đầy đủ tiện nghi: máy lạnh, tủ lạnh, máy giặt, bếp từ. Khu vực an ninh 24/7, hồ bơi, gym, sân chơi trẻ em.',
		property_type: 'apartment',
		location: 'Quận 1, TP.HCM',
		price: 3500000000,
		area: 75,
		bedrooms: 2,
		bathrooms: 2,
		images: [
			'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
			'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800',
			'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'
		],
		source_url: 'https://example.com/property-001',
		created_at: '2025-10-25T10:00:00Z',
		score: 0.95
	},
	{
		id: 'prop-002',
		title: 'Nhà phố 3 tầng mặt tiền đường lớn',
		description:
			'Nhà mới xây, thiết kế hiện đại, mặt tiền rộng 5m. Vị trí kinh doanh đắc địa, gần trường học, bệnh viện, siêu thị. Phù hợp ở hoặc kinh doanh.',
		property_type: 'townhouse',
		location: 'Quận 3, TP.HCM',
		price: 8500000000,
		area: 120,
		bedrooms: 4,
		bathrooms: 3,
		images: [
			'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800',
			'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'
		],
		source_url: 'https://example.com/property-002',
		created_at: '2025-10-28T14:30:00Z',
		score: 0.88
	},
	{
		id: 'prop-003',
		title: 'Biệt thự đơn lập có hồ bơi riêng',
		description:
			'Biệt thự sang trọng trong khu compound cao cấp. Sân vườn rộng rãi, hồ bơi riêng, garage 2 xe. An ninh 24/7, cảnh quan đẹp. Nội thất nhập khẩu.',
		property_type: 'villa',
		location: 'Quận 7, TP.HCM',
		price: 25000000000,
		area: 350,
		bedrooms: 5,
		bathrooms: 4,
		images: [
			'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
			'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800',
			'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800'
		],
		source_url: 'https://example.com/property-003',
		created_at: '2025-10-20T09:00:00Z',
		score: 0.92
	},
	{
		id: 'prop-004',
		title: 'Căn hộ studio hiện đại gần trung tâm',
		description:
			'Studio 1PN thiết kế thông minh, tối ưu không gian. Đầy đủ nội thất, máy lạnh, bếp. Gần công viên, quán café, nhà hàng. Phù hợp cho người độc thân hoặc cặp đôi trẻ.',
		property_type: 'studio',
		location: 'Quận 2, TP.HCM',
		price: 1800000000,
		area: 35,
		bedrooms: 1,
		bathrooms: 1,
		images: [
			'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800',
			'https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800'
		],
		source_url: 'https://example.com/property-004',
		created_at: '2025-10-30T16:00:00Z',
		score: 0.85
	},
	{
		id: 'prop-005',
		title: 'Đất nền khu đô thị mới quy hoạch đẹp',
		description:
			'Lô đất đẹp trong khu đô thị hiện đại. Đầy đủ hạ tầng: điện, nước, đường nhựa. Gần trường học, bệnh viện, chợ. Sổ hồng riêng, pháp lý rõ ràng.',
		property_type: 'land',
		location: 'Bình Dương',
		price: 2500000000,
		area: 100,
		images: ['https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800'],
		source_url: 'https://example.com/property-005',
		created_at: '2025-10-22T11:00:00Z',
		score: 0.78
	},
	{
		id: 'prop-006',
		title: 'Penthouse duplex view toàn cảnh thành phố',
		description:
			'Penthouse 2 tầng siêu đẹp, view 360 độ. Sân thượng riêng, bể bơi infinity. Nội thất sang trọng, thiết bị điện tử thông minh. Dành cho khách hàng VIP.',
		property_type: 'penthouse',
		location: 'Quận 1, TP.HCM',
		price: 45000000000,
		area: 250,
		bedrooms: 4,
		bathrooms: 5,
		images: [
			'https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=800',
			'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800',
			'https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4?w=800'
		],
		source_url: 'https://example.com/property-006',
		created_at: '2025-10-15T10:00:00Z',
		score: 0.98
	},
	{
		id: 'prop-007',
		title: 'Nhà riêng hẻm xe hơi yên tĩnh',
		description:
			'Nhà 2 tầng trong hẻm yên tĩnh, xe hơi ra vào thoải mái. Gần chợ, trường học. Phù hợp cho gia đình nhỏ. Giá tốt.',
		property_type: 'house',
		location: 'Bình Thạnh, TP.HCM',
		price: 4200000000,
		area: 60,
		bedrooms: 3,
		bathrooms: 2,
		images: [
			'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800',
			'https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=800'
		],
		source_url: 'https://example.com/property-007',
		created_at: '2025-10-27T13:00:00Z',
		score: 0.82
	},
	{
		id: 'prop-008',
		title: 'Văn phòng hạng A view đẹp',
		description:
			'Văn phòng tại tòa nhà hạng A, tầng cao view sông. Đầy đủ hệ thống điều hòa trung tâm, thang máy hiện đại. Bãi đỗ xe rộng rãi.',
		property_type: 'office',
		location: 'Quận 1, TP.HCM',
		price: 120000000,
		area: 150,
		images: [
			'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
			'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800'
		],
		source_url: 'https://example.com/property-008',
		created_at: '2025-10-29T09:00:00Z',
		score: 0.90
	},
	{
		id: 'prop-009',
		title: 'Căn hộ 3PN view công viên xanh mát',
		description:
			'Căn góc 3 phòng ngủ, view công viên Gia Định. Ban công rộng, thoáng mát. Gần trường quốc tế, siêu thị, bệnh viện. An ninh tốt.',
		property_type: 'apartment',
		location: 'Phú Nhuận, TP.HCM',
		price: 5800000000,
		area: 110,
		bedrooms: 3,
		bathrooms: 2,
		images: [
			'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800',
			'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'
		],
		source_url: 'https://example.com/property-009',
		created_at: '2025-10-26T15:00:00Z',
		score: 0.87
	},
	{
		id: 'prop-010',
		title: 'Shophouse mặt tiền kinh doanh sầm uất',
		description:
			'Nhà mặt tiền đường lớn, vị trí đắc địa cho kinh doanh. Khu vực đông dân cư, gần chợ, trường học. Giá đầu tư hợp lý.',
		property_type: 'shophouse',
		location: 'Gò Vấp, TP.HCM',
		price: 12000000000,
		area: 80,
		bedrooms: 3,
		bathrooms: 3,
		images: [
			'https://images.unsplash.com/photo-1555636222-cae831e670b3?w=800',
			'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800'
		],
		source_url: 'https://example.com/property-010',
		created_at: '2025-10-24T12:00:00Z',
		score: 0.84
	}
];

/**
 * Mock API responses
 */
export const mockSearchResponse = {
	results: mockProperties,
	total: mockProperties.length,
	took: 0.123
};

/**
 * Get random properties
 */
export function getRandomProperties(count: number = 5): Property[] {
	const shuffled = [...mockProperties].sort(() => Math.random() - 0.5);
	return shuffled.slice(0, count);
}

/**
 * Filter properties by criteria
 */
export function filterProperties(criteria: {
	query?: string;
	property_type?: string[];
	min_price?: number;
	max_price?: number;
	min_area?: number;
	max_area?: number;
	location?: string[];
}): Property[] {
	let filtered = [...mockProperties];

	// Filter by query (search in title and description)
	if (criteria.query) {
		const query = criteria.query.toLowerCase();
		filtered = filtered.filter(
			(p) =>
				p.title.toLowerCase().includes(query) || p.description.toLowerCase().includes(query)
		);
	}

	// Filter by property type
	if (criteria.property_type && criteria.property_type.length > 0) {
		filtered = filtered.filter((p) => criteria.property_type!.includes(p.property_type));
	}

	// Filter by price range
	if (criteria.min_price !== undefined) {
		filtered = filtered.filter((p) => p.price >= criteria.min_price!);
	}
	if (criteria.max_price !== undefined) {
		filtered = filtered.filter((p) => p.price <= criteria.max_price!);
	}

	// Filter by area range
	if (criteria.min_area !== undefined) {
		filtered = filtered.filter((p) => p.area >= criteria.min_area!);
	}
	if (criteria.max_area !== undefined) {
		filtered = filtered.filter((p) => p.area <= criteria.max_area!);
	}

	// Filter by location
	if (criteria.location && criteria.location.length > 0) {
		filtered = filtered.filter((p) =>
			criteria.location!.some((loc) => p.location.includes(loc))
		);
	}

	return filtered;
}

/**
 * Get property by ID
 */
export function getPropertyById(id: string): Property | undefined {
	return mockProperties.find((p) => p.id === id);
}

/**
 * Get property suggestions
 */
export function getPropertySuggestions(count: number = 5): Property[] {
	return getRandomProperties(count);
}
