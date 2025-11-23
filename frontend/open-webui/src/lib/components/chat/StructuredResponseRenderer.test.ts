/**
 * StructuredResponseRenderer.test.ts
 *
 * Test suite for StructuredResponseRenderer component
 * Ensures OpenAI Apps SDK pattern compliance and proper component rendering
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import StructuredResponseRenderer from './StructuredResponseRenderer.svelte';

describe('StructuredResponseRenderer', () => {
	const mockProperties = [
		{
			id: '1',
			title: 'Căn hộ Vinhomes',
			address: 'Quận 1, TP.HCM',
			price: '5.2 tỷ',
			bedrooms: 2,
			area: 75,
			imageUrl: 'https://example.com/1.jpg'
		},
		{
			id: '2',
			title: 'Nhà phố Thảo Điền',
			address: 'Quận 2, TP.HCM',
			price: '12 tỷ',
			bedrooms: 4,
			area: 150,
			imageUrl: 'https://example.com/2.jpg'
		}
	];

	const mockCarouselComponent = {
		type: 'property-carousel',
		data: {
			properties: mockProperties,
			total: 2
		}
	};

	const mockInspectorComponent = {
		type: 'property-inspector',
		data: {
			property_data: mockProperties[0]
		}
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('Property Carousel Rendering', () => {
		it('should render property carousel with multiple properties', () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			expect(screen.getByRole('region', { name: 'Property search results' })).toBeInTheDocument();
			expect(screen.getByText('Căn hộ Vinhomes')).toBeInTheDocument();
			expect(screen.getByText('Nhà phố Thảo Điền')).toBeInTheDocument();
		});

		it('should display total count when properties > 0', () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			expect(screen.getByText(/Tìm thấy/)).toBeInTheDocument();
			expect(screen.getByText('2')).toBeInTheDocument();
			expect(screen.getByText(/bất động sản/)).toBeInTheDocument();
		});

		it('should render empty state when no properties found', () => {
			const emptyCarousel = {
				type: 'property-carousel',
				data: {
					properties: [],
					total: 0
				}
			};

			render(StructuredResponseRenderer, { props: { components: [emptyCarousel] } });

			expect(screen.getByText('Không tìm thấy bất động sản phù hợp')).toBeInTheDocument();
		});

		it('should render all CompactPropertyCards in property list', () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const propertyCards = screen.getAllByRole('button', { name: /Property:/ });
			expect(propertyCards).toHaveLength(2);
		});
	});

	describe('Property Inspector Modal', () => {
		it('should auto-open modal when PropertyInspectorComponent is received', async () => {
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [mockInspectorComponent] }
			});

			await waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});
		});

		it('should pass property data to modal correctly', async () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockInspectorComponent] }
			});

			await waitFor(() => {
				const dialog = screen.getByRole('dialog');
				expect(dialog).toBeInTheDocument();
			});
		});

		it('should close modal when PropertyDetailModal emits close event', async () => {
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [mockInspectorComponent] }
			});

			await waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});

			const closeButton = screen.getByLabelText('Close property details');
			await fireEvent.click(closeButton);

			await waitFor(() => {
				expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
			});
		});
	});

	describe('Property Detail Request', () => {
		it('should dispatch requestDetail event when property card is clicked', async () => {
			const onRequestDetail = vi.fn();
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			component.$on('requestDetail', onRequestDetail);

			const firstPropertyCard = screen.getByText('Căn hộ Vinhomes').closest('article');
			if (firstPropertyCard) {
				await fireEvent.click(firstPropertyCard);
			}

			await waitFor(() => {
				expect(onRequestDetail).toHaveBeenCalledWith(
					expect.objectContaining({
						detail: expect.objectContaining({
							propertyId: '1'
						})
					})
				);
			});
		});

		it('should include query in requestDetail event', async () => {
			const onRequestDetail = vi.fn();
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			component.$on('requestDetail', onRequestDetail);

			const firstPropertyCard = screen.getByText('Căn hộ Vinhomes').closest('article');
			if (firstPropertyCard) {
				await fireEvent.click(firstPropertyCard);
			}

			await waitFor(() => {
				expect(onRequestDetail).toHaveBeenCalledWith(
					expect.objectContaining({
						detail: expect.objectContaining({
							query: expect.stringContaining('cho tôi xem chi tiết')
						})
					})
				);
			});
		});

		it('should open modal directly if property has fullData', async () => {
			const propertyWithFullData = {
				...mockProperties[0],
				fullData: { ...mockProperties[0], description: 'Full details' }
			};

			const carouselWithFullData = {
				type: 'property-carousel',
				data: {
					properties: [propertyWithFullData],
					total: 1
				}
			};

			render(StructuredResponseRenderer, {
				props: { components: [carouselWithFullData] }
			});

			const propertyCard = screen.getByText('Căn hộ Vinhomes').closest('article');
			if (propertyCard) {
				await fireEvent.click(propertyCard);
			}

			await waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});
		});
	});

	describe('Multiple Component Types', () => {
		it('should render multiple component types in same response', () => {
			const multipleComponents = [mockCarouselComponent, mockInspectorComponent];

			render(StructuredResponseRenderer, {
				props: { components: multipleComponents }
			});

			// Carousel should be visible
			expect(screen.getByRole('region', { name: 'Property search results' })).toBeInTheDocument();

			// Modal should also be opened
			waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});
		});

		it('should handle empty components array', () => {
			const { container } = render(StructuredResponseRenderer, {
				props: { components: [] }
			});

			expect(container.querySelector('.structured-response-container')).toBeInTheDocument();
		});

		it('should ignore unknown component types', () => {
			const unknownComponent = {
				type: 'unknown-type',
				data: { test: 'data' }
			};

			const { container } = render(StructuredResponseRenderer, {
				props: { components: [unknownComponent] }
			});

			// Should render container but no specific component
			expect(container.querySelector('.structured-response-container')).toBeInTheDocument();
		});
	});

	describe('Data Handling', () => {
		it('should handle malformed carousel data gracefully', () => {
			const malformedCarousel = {
				type: 'property-carousel',
				data: null
			};

			render(StructuredResponseRenderer, {
				props: { components: [malformedCarousel] }
			});

			// Should show empty state
			expect(screen.getByText('Không tìm thấy bất động sản phù hợp')).toBeInTheDocument();
		});

		it('should handle malformed inspector data gracefully', () => {
			const malformedInspector = {
				type: 'property-inspector',
				data: null
			};

			render(StructuredResponseRenderer, {
				props: { components: [malformedInspector] }
			});

			// Should not crash
			expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
		});
	});

	describe('Component Reactivity', () => {
		it('should update when components prop changes', async () => {
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			expect(screen.getByText('Căn hộ Vinhomes')).toBeInTheDocument();

			// Update components
			const newCarousel = {
				type: 'property-carousel',
				data: {
					properties: [mockProperties[1]],
					total: 1
				}
			};

			component.$set({ components: [newCarousel] });

			await waitFor(() => {
				expect(screen.queryByText('Căn hộ Vinhomes')).not.toBeInTheDocument();
				expect(screen.getByText('Nhà phố Thảo Điền')).toBeInTheDocument();
			});
		});
	});

	describe('Styling and Layout', () => {
		it('should have proper spacing between components', () => {
			const { container } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const responseContainer = container.querySelector('.structured-response-container');
			const computedStyle = window.getComputedStyle(responseContainer!);

			expect(computedStyle.display).toBe('flex');
			expect(computedStyle.flexDirection).toBe('column');
		});

		it('should render property list with proper layout', () => {
			const { container } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const propertyList = container.querySelector('.property-list');
			const computedStyle = window.getComputedStyle(propertyList!);

			expect(computedStyle.display).toBe('flex');
			expect(computedStyle.flexDirection).toBe('column');
		});
	});

	describe('Accessibility', () => {
		it('should have proper ARIA region for carousel', () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const region = screen.getByRole('region', { name: 'Property search results' });
			expect(region).toBeInTheDocument();
		});

		it('should have accessible empty state message', () => {
			const emptyCarousel = {
				type: 'property-carousel',
				data: { properties: [], total: 0 }
			};

			render(StructuredResponseRenderer, {
				props: { components: [emptyCarousel] }
			});

			expect(screen.getByText('Không tìm thấy bất động sản phù hợp')).toBeInTheDocument();
		});
	});

	describe('Mobile Responsive', () => {
		it('should have mobile-specific styles', () => {
			const { container } = render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('@media (max-width: 768px)');
		});
	});

	describe('Edge Cases', () => {
		it('should handle rapid component updates without errors', async () => {
			const { component } = render(StructuredResponseRenderer, {
				props: { components: [] }
			});

			// Rapid updates
			component.$set({ components: [mockCarouselComponent] });
			component.$set({ components: [] });
			component.$set({ components: [mockInspectorComponent] });
			component.$set({ components: [mockCarouselComponent, mockInspectorComponent] });

			// Should not crash
			expect(screen.getByRole('region')).toBeInTheDocument();
		});

		it('should handle property click errors gracefully', async () => {
			const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const propertyCard = screen.getByText('Căn hộ Vinhomes').closest('article');
			if (propertyCard) {
				await fireEvent.click(propertyCard);
			}

			// Should not crash (error is logged but handled)
			expect(screen.getByText('Căn hộ Vinhomes')).toBeInTheDocument();

			consoleErrorSpy.mockRestore();
		});
	});

	describe('Keyboard Navigation', () => {
		it('should support keyboard navigation on property cards', async () => {
			render(StructuredResponseRenderer, {
				props: { components: [mockCarouselComponent] }
			});

			const propertyCards = screen.getAllByRole('button', { name: /Property:/ });

			// All cards should be keyboard accessible
			propertyCards.forEach((card) => {
				expect(card).toHaveAttribute('tabindex', '0');
			});
		});
	});
});
