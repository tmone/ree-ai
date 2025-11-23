/**
 * CompactPropertyCard.test.ts
 *
 * Test suite for CompactPropertyCard component
 * Ensures OpenAI Apps SDK compliance and accessibility
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import CompactPropertyCard from './CompactPropertyCard.svelte';

describe('CompactPropertyCard', () => {
	const mockProperty = {
		id: '123',
		title: 'Căn hộ cao cấp Vinhomes',
		address: 'Quận 1, TP.HCM',
		location: 'Quận 1, TP.HCM',
		price: '5.2 tỷ',
		priceUnit: 'VNĐ',
		bedrooms: 2,
		area: 75,
		areaDisplay: '75',
		imageUrl: 'https://example.com/image.jpg'
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('Rendering', () => {
		it('should render property card with all data points', () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			// Check all 4 data points (OpenAI "Simple" principle)
			expect(screen.getByText(mockProperty.title)).toBeInTheDocument();
			expect(screen.getByText(/Quận 1, TP.HCM/)).toBeInTheDocument();
			expect(screen.getByText(/5.2 tỷ/)).toBeInTheDocument();
			expect(screen.getByText('Xem chi tiết →')).toBeInTheDocument();
		});

		it('should render with image when imageUrl is provided', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			const img = screen.getByAltText(mockProperty.title);
			expect(img).toBeInTheDocument();
			expect(img).toHaveAttribute('src', mockProperty.imageUrl);
			expect(img).toHaveAttribute('loading', 'lazy');
		});

		it('should render placeholder when imageUrl is missing', () => {
			const propertyWithoutImage = { ...mockProperty, imageUrl: undefined };
			render(CompactPropertyCard, { props: { property: propertyWithoutImage } });

			const placeholder = screen.getByRole('img', { name: 'No image available' });
			expect(placeholder).toBeInTheDocument();
			expect(placeholder).toHaveClass('placeholder');
		});

		it('should display key feature with bedrooms (2PN 75m²)', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			expect(screen.getByText(/2PN 75m²/)).toBeInTheDocument();
		});

		it('should display key feature without bedrooms when bedrooms = 0', () => {
			const landProperty = { ...mockProperty, bedrooms: 0, area: 200 };
			render(CompactPropertyCard, { props: { property: landProperty } });

			expect(screen.getByText(/200m²/)).toBeInTheDocument();
			expect(screen.queryByText(/PN/)).not.toBeInTheDocument();
		});
	});

	describe('Interactions', () => {
		it('should call onClick when card is clicked', async () => {
			const onClick = vi.fn();
			render(CompactPropertyCard, { props: { property: mockProperty, onClick } });

			const card = screen.getByRole('button', { name: `Property: ${mockProperty.title}` });
			await fireEvent.click(card);

			expect(onClick).toHaveBeenCalledWith(mockProperty);
		});

		it('should call onClick when CTA button is clicked', async () => {
			const onClick = vi.fn();
			render(CompactPropertyCard, { props: { property: mockProperty, onClick } });

			const ctaButton = screen.getByText('Xem chi tiết →');
			await fireEvent.click(ctaButton);

			expect(onClick).toHaveBeenCalledWith(mockProperty);
		});

		it('should support keyboard navigation (Enter key)', async () => {
			const onClick = vi.fn();
			render(CompactPropertyCard, { props: { property: mockProperty, onClick } });

			const card = screen.getByRole('button', { name: `Property: ${mockProperty.title}` });
			await fireEvent.keyPress(card, { key: 'Enter', code: 'Enter' });

			expect(onClick).toHaveBeenCalledWith(mockProperty);
		});

		it('should not call onClick when onClick is not provided', async () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			const card = screen.getByRole('button');
			await fireEvent.click(card);

			// Should not throw error when onClick is undefined
			expect(container).toBeInTheDocument();
		});
	});

	describe('Accessibility (WCAG AA)', () => {
		it('should have proper ARIA attributes', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			const card = screen.getByRole('button', { name: `Property: ${mockProperty.title}` });
			expect(card).toHaveAttribute('tabindex', '0');
			expect(card).toHaveAttribute('aria-label', `Property: ${mockProperty.title}`);
		});

		it('should have screen reader only labels for metadata', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			expect(screen.getByText('Location:')).toHaveClass('sr-only');
			expect(screen.getByText('Price:')).toHaveClass('sr-only');
		});

		it('should have accessible CTA button', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			const ctaButton = screen.getByLabelText('View property details');
			expect(ctaButton).toBeInTheDocument();
		});

		it('should have visible focus indicator', () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			// Check focus-visible styles exist in CSS
			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('focus-visible');
		});
	});

	describe('OpenAI Design System Compliance', () => {
		it('should use system colors (not brand colors for background)', () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			const card = container.querySelector('.compact-property-card');
			const computedStyle = window.getComputedStyle(card!);

			// Background should be white (#ffffff) in light mode
			expect(computedStyle.backgroundColor).toBe('rgb(255, 255, 255)');
		});

		it('should use brand color ONLY on CTA button', () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			const ctaButton = screen.getByText('Xem chi tiết →');
			const computedStyle = window.getComputedStyle(ctaButton);

			// CTA button should have brand blue color
			expect(computedStyle.backgroundColor).toBe('rgb(59, 130, 246)');
		});

		it('should have max-width of 400px per Figma specs', () => {
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			const card = container.querySelector('.compact-property-card');
			const computedStyle = window.getComputedStyle(card!);

			expect(computedStyle.maxWidth).toBe('400px');
		});

		it('should have 60px thumbnail per Figma specs', () => {
			render(CompactPropertyCard, { props: { property: mockProperty } });

			const img = screen.getByAltText(mockProperty.title);
			const computedStyle = window.getComputedStyle(img);

			expect(computedStyle.width).toBe('60px');
			expect(computedStyle.height).toBe('60px');
		});
	});

	describe('Mobile Responsive', () => {
		it('should render mobile layout for screens < 480px', () => {
			// Note: This test requires manual verification or using a viewport library
			const { container } = render(CompactPropertyCard, { props: { property: mockProperty } });

			// Check that mobile-specific media query exists
			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('@media (max-width: 480px)');
			expect(styles).toContain('flex-direction: column');
		});
	});

	describe('Edge Cases', () => {
		it('should handle missing optional fields gracefully', () => {
			const minimalProperty = {
				id: '456',
				title: 'Test Property',
				price: '1 tỷ'
			};

			const { container } = render(CompactPropertyCard, { props: { property: minimalProperty } });

			expect(screen.getByText('Test Property')).toBeInTheDocument();
			expect(screen.getByText(/1 tỷ/)).toBeInTheDocument();
		});

		it('should truncate long titles with ellipsis', () => {
			const longTitle = 'Căn hộ cao cấp với đầy đủ tiện nghi hiện đại tại khu vực trung tâm thành phố';
			const propertyWithLongTitle = { ...mockProperty, title: longTitle };

			const { container } = render(CompactPropertyCard, { props: { property: propertyWithLongTitle } });

			const titleElement = screen.getByText(longTitle);
			const computedStyle = window.getComputedStyle(titleElement);

			expect(computedStyle.whiteSpace).toBe('nowrap');
			expect(computedStyle.overflow).toBe('hidden');
			expect(computedStyle.textOverflow).toBe('ellipsis');
		});

		it('should handle missing priceUnit with default', () => {
			const propertyWithoutUnit = { ...mockProperty, priceUnit: undefined };
			render(CompactPropertyCard, { props: { property: propertyWithoutUnit } });

			expect(screen.getByText(/VNĐ/)).toBeInTheDocument();
		});
	});
});
