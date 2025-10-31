<script lang="ts">
	import type { Property } from '$lib/apis/ree-ai';

	export let property: Property;
	export let onClose: (() => void) | undefined = undefined;

	const formatPrice = (price: number): string => {
		if (price >= 1000000000) {
			return `${(price / 1000000000).toFixed(2)} tỷ`;
		}
		return `${(price / 1000000).toFixed(0)} triệu`;
	};

	const formatArea = (area: number): string => {
		return `${area.toFixed(0)} m²`;
	};

	const getPropertyTypeLabel = (type: string): string => {
		const labels: Record<string, string> = {
			apartment: 'Căn hộ',
			house: 'Nhà riêng',
			villa: 'Biệt thự',
			land: 'Đất nền',
			townhouse: 'Nhà phố',
			office: 'Văn phòng'
		};
		return labels[type] || type;
	};

	const formatDate = (dateString: string): string => {
		const date = new Date(dateString);
		return date.toLocaleDateString('vi-VN');
	};

	let currentImageIndex = 0;

	const nextImage = () => {
		if (property.images && property.images.length > 0) {
			currentImageIndex = (currentImageIndex + 1) % property.images.length;
		}
	};

	const prevImage = () => {
		if (property.images && property.images.length > 0) {
			currentImageIndex =
				(currentImageIndex - 1 + property.images.length) % property.images.length;
		}
	};
</script>

<div class="property-details-modal" on:click={onClose} role="presentation">
	<div class="modal-content" on:click|stopPropagation role="presentation">
		<button class="close-button" on:click={onClose} type="button">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>

		<div class="image-gallery">
			{#if property.images && property.images.length > 0}
				<img src={property.images[currentImageIndex]} alt={property.title} />
				{#if property.images.length > 1}
					<button class="nav-button prev" on:click={prevImage} type="button">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 19l-7-7 7-7"
							/>
						</svg>
					</button>
					<button class="nav-button next" on:click={nextImage} type="button">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5l7 7-7 7"
							/>
						</svg>
					</button>
					<div class="image-indicator">
						{currentImageIndex + 1} / {property.images.length}
					</div>
				{/if}
			{:else}
				<div class="placeholder-image">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
						/>
					</svg>
				</div>
			{/if}
		</div>

		<div class="property-info">
			<div class="property-header">
				<div class="property-type-badge">
					{getPropertyTypeLabel(property.property_type)}
				</div>
				<h2>{property.title}</h2>
				<div class="property-location">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
						/>
					</svg>
					<span>{property.location}</span>
				</div>
			</div>

			<div class="price-section">
				<div class="price-label">Giá</div>
				<div class="price-value">{formatPrice(property.price)} VNĐ</div>
			</div>

			<div class="property-stats">
				<div class="stat">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
						/>
					</svg>
					<div>
						<div class="stat-label">Diện tích</div>
						<div class="stat-value">{formatArea(property.area)}</div>
					</div>
				</div>

				{#if property.bedrooms}
					<div class="stat">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
							/>
						</svg>
						<div>
							<div class="stat-label">Phòng ngủ</div>
							<div class="stat-value">{property.bedrooms}</div>
						</div>
					</div>
				{/if}

				{#if property.bathrooms}
					<div class="stat">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
							/>
						</svg>
						<div>
							<div class="stat-label">Phòng tắm</div>
							<div class="stat-value">{property.bathrooms}</div>
						</div>
					</div>
				{/if}
			</div>

			<div class="description-section">
				<h3>Mô tả</h3>
				<p>{property.description}</p>
			</div>

			<div class="meta-section">
				<div class="meta-item">
					<span class="meta-label">Mã tin:</span>
					<span class="meta-value">{property.id}</span>
				</div>
				<div class="meta-item">
					<span class="meta-label">Ngày đăng:</span>
					<span class="meta-value">{formatDate(property.created_at)}</span>
				</div>
				{#if property.source_url}
					<div class="meta-item">
						<span class="meta-label">Nguồn:</span>
						<a href={property.source_url} target="_blank" rel="noopener noreferrer">
							Xem chi tiết
						</a>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.property-details-modal {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.75);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 24px;
		overflow-y: auto;
	}

	.modal-content {
		background: white;
		border-radius: 16px;
		max-width: 900px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		position: relative;
	}

	.close-button {
		position: absolute;
		top: 16px;
		right: 16px;
		width: 40px;
		height: 40px;
		background: rgba(0, 0, 0, 0.5);
		color: white;
		border: none;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 10;
		transition: background 0.2s;
	}

	.close-button:hover {
		background: rgba(0, 0, 0, 0.7);
	}

	.close-button svg {
		width: 24px;
		height: 24px;
	}

	.image-gallery {
		position: relative;
		width: 100%;
		height: 400px;
		background: #f3f4f6;
		border-radius: 16px 16px 0 0;
		overflow: hidden;
	}

	.image-gallery img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.placeholder-image {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #9ca3af;
	}

	.placeholder-image svg {
		width: 80px;
		height: 80px;
	}

	.nav-button {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		width: 48px;
		height: 48px;
		background: rgba(0, 0, 0, 0.5);
		color: white;
		border: none;
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background 0.2s;
	}

	.nav-button:hover {
		background: rgba(0, 0, 0, 0.7);
	}

	.nav-button svg {
		width: 24px;
		height: 24px;
	}

	.nav-button.prev {
		left: 16px;
	}

	.nav-button.next {
		right: 16px;
	}

	.image-indicator {
		position: absolute;
		bottom: 16px;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.7);
		color: white;
		padding: 6px 12px;
		border-radius: 16px;
		font-size: 14px;
	}

	.property-info {
		padding: 32px;
	}

	.property-header {
		margin-bottom: 24px;
	}

	.property-type-badge {
		display: inline-block;
		background: #dbeafe;
		color: #1e40af;
		padding: 6px 12px;
		border-radius: 16px;
		font-size: 14px;
		font-weight: 600;
		margin-bottom: 12px;
	}

	.property-header h2 {
		font-size: 28px;
		font-weight: 700;
		color: #111827;
		margin: 0 0 12px 0;
		line-height: 1.3;
	}

	.property-location {
		display: flex;
		align-items: center;
		gap: 8px;
		color: #6b7280;
		font-size: 16px;
	}

	.property-location svg {
		width: 20px;
		height: 20px;
	}

	.price-section {
		background: #fef2f2;
		padding: 20px;
		border-radius: 12px;
		margin-bottom: 24px;
	}

	.price-label {
		font-size: 14px;
		color: #991b1b;
		margin-bottom: 4px;
	}

	.price-value {
		font-size: 32px;
		font-weight: 700;
		color: #dc2626;
	}

	.property-stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 20px;
		padding: 24px 0;
		border-top: 2px solid #e5e7eb;
		border-bottom: 2px solid #e5e7eb;
		margin-bottom: 24px;
	}

	.stat {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.stat svg {
		width: 32px;
		height: 32px;
		color: #3b82f6;
		flex-shrink: 0;
	}

	.stat-label {
		font-size: 14px;
		color: #6b7280;
		margin-bottom: 4px;
	}

	.stat-value {
		font-size: 18px;
		font-weight: 700;
		color: #111827;
	}

	.description-section {
		margin-bottom: 24px;
	}

	.description-section h3 {
		font-size: 20px;
		font-weight: 700;
		color: #111827;
		margin: 0 0 12px 0;
	}

	.description-section p {
		font-size: 16px;
		line-height: 1.6;
		color: #374151;
		margin: 0;
		white-space: pre-wrap;
	}

	.meta-section {
		background: #f9fafb;
		padding: 20px;
		border-radius: 12px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.meta-item {
		display: flex;
		gap: 8px;
		font-size: 14px;
	}

	.meta-label {
		font-weight: 600;
		color: #6b7280;
	}

	.meta-value {
		color: #111827;
	}

	.meta-item a {
		color: #3b82f6;
		text-decoration: none;
	}

	.meta-item a:hover {
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		.modal-content {
			max-height: 100vh;
			border-radius: 0;
		}

		.image-gallery {
			height: 300px;
			border-radius: 0;
		}

		.property-info {
			padding: 24px 16px;
		}

		.property-header h2 {
			font-size: 24px;
		}

		.price-value {
			font-size: 28px;
		}

		.property-stats {
			grid-template-columns: 1fr;
		}
	}
</style>
