<script lang="ts">
	import type { Property } from '$lib/apis/ree-ai';

	export let property: Property;
	export let onClick: ((property: Property) => void) | undefined = undefined;

	const formatPrice = (price: number): string => {
		if (price >= 1000000000) {
			return `${(price / 1000000000).toFixed(1)} tỷ`;
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
</script>

<button
	class="property-card"
	on:click={() => onClick && onClick(property)}
	type="button"
>
	<div class="property-image">
		{#if property.images && property.images.length > 0}
			<img src={property.images[0]} alt={property.title} />
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
		<div class="property-type-badge">
			{getPropertyTypeLabel(property.property_type)}
		</div>
	</div>

	<div class="property-content">
		<h3 class="property-title">{property.title}</h3>

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

		<div class="property-stats">
			<div class="stat">
				<span class="stat-label">Diện tích</span>
				<span class="stat-value">{formatArea(property.area)}</span>
			</div>
			{#if property.bedrooms}
				<div class="stat">
					<span class="stat-label">Phòng ngủ</span>
					<span class="stat-value">{property.bedrooms}</span>
				</div>
			{/if}
			{#if property.bathrooms}
				<div class="stat">
					<span class="stat-label">Phòng tắm</span>
					<span class="stat-value">{property.bathrooms}</span>
				</div>
			{/if}
		</div>

		<div class="property-price">
			{formatPrice(property.price)} VNĐ
		</div>

		{#if property.score}
			<div class="property-score">
				Độ phù hợp: {(property.score * 100).toFixed(0)}%
			</div>
		{/if}
	</div>
</button>

<style>
	.property-card {
		display: flex;
		flex-direction: column;
		background: white;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition: all 0.3s ease;
		cursor: pointer;
		width: 100%;
		text-align: left;
		border: 1px solid #e5e7eb;
	}

	.property-card:hover {
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
		transform: translateY(-2px);
	}

	.property-image {
		position: relative;
		width: 100%;
		height: 200px;
		background: #f3f4f6;
		overflow: hidden;
	}

	.property-image img {
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
		width: 64px;
		height: 64px;
	}

	.property-type-badge {
		position: absolute;
		top: 12px;
		right: 12px;
		background: rgba(59, 130, 246, 0.9);
		color: white;
		padding: 4px 12px;
		border-radius: 16px;
		font-size: 12px;
		font-weight: 600;
	}

	.property-content {
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.property-title {
		font-size: 16px;
		font-weight: 600;
		color: #111827;
		margin: 0;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.property-location {
		display: flex;
		align-items: center;
		gap: 6px;
		color: #6b7280;
		font-size: 14px;
	}

	.property-location svg {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
	}

	.property-stats {
		display: flex;
		gap: 16px;
		padding: 12px 0;
		border-top: 1px solid #e5e7eb;
		border-bottom: 1px solid #e5e7eb;
	}

	.stat {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.stat-label {
		font-size: 12px;
		color: #6b7280;
	}

	.stat-value {
		font-size: 14px;
		font-weight: 600;
		color: #111827;
	}

	.property-price {
		font-size: 20px;
		font-weight: 700;
		color: #dc2626;
	}

	.property-score {
		font-size: 12px;
		color: #059669;
		background: #d1fae5;
		padding: 4px 8px;
		border-radius: 4px;
		width: fit-content;
	}
</style>
