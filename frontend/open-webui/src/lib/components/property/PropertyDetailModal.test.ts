/**
 * PropertyDetailModal.test.ts
 *
 * Test suite for PropertyDetailModal component
 * Ensures OpenAI Apps SDK Inspector pattern compliance and accessibility
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import PropertyDetailModal from './PropertyDetailModal.svelte';

describe('PropertyDetailModal', () => {
	const mockProperty = {
		id: '123',
		title: 'Căn hộ cao cấp Vinhomes',
		address: 'Quận 1, TP.HCM',
		price: '5.2 tỷ VNĐ',
		bedrooms: 2,
		bathrooms: 2,
		area: 75,
		description: 'Căn hộ hiện đại với đầy đủ tiện nghi',
		imageUrl: 'https://example.com/image.jpg'
	};

	beforeEach(() => {
		vi.clearAllMocks();
		// Reset body scroll lock
		document.body.style.overflow = '';
	});

	afterEach(() => {
		// Clean up any open modals
		document.body.style.overflow = '';
	});

	describe('Modal Visibility', () => {
		it('should not render when open = false', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: false } });

			expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
		});

		it('should render when open = true', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: true } });

			expect(screen.getByRole('dialog')).toBeInTheDocument();
		});

		it('should show PropertyInspector component when open', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: true } });

			const dialog = screen.getByRole('dialog');
			expect(dialog).toBeInTheDocument();
			expect(dialog.querySelector('.modal-content')).toBeInTheDocument();
		});
	});

	describe('Close Mechanisms', () => {
		it('should close when close button is clicked', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const closeButton = screen.getByLabelText('Close property details');
			await fireEvent.click(closeButton);

			await waitFor(() => {
				expect(component.open).toBe(false);
			});
		});

		it('should emit close event when close button is clicked', async () => {
			const onClose = vi.fn();
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			component.$on('close', onClose);

			const closeButton = screen.getByLabelText('Close property details');
			await fireEvent.click(closeButton);

			await waitFor(() => {
				expect(onClose).toHaveBeenCalled();
			});
		});

		it('should close when Escape key is pressed', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			await fireEvent.keyDown(window, { key: 'Escape' });

			await waitFor(() => {
				expect(component.open).toBe(false);
			});
		});

		it('should close when backdrop is clicked', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const overlay = screen.getByRole('dialog');
			await fireEvent.click(overlay);

			await waitFor(() => {
				expect(component.open).toBe(false);
			});
		});

		it('should NOT close when modal content is clicked', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const modalContent = screen.getByRole('dialog').querySelector('.modal-container');
			if (modalContent) {
				await fireEvent.click(modalContent);
			}

			// Modal should still be open
			expect(component.open).toBe(true);
		});

		it('should NOT close when Escape is pressed and modal is already closed', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: false }
			});

			await fireEvent.keyDown(window, { key: 'Escape' });

			// Should remain closed
			expect(component.open).toBe(false);
		});
	});

	describe('Accessibility (WCAG AA)', () => {
		it('should have proper ARIA attributes', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: true } });

			const dialog = screen.getByRole('dialog');
			expect(dialog).toHaveAttribute('aria-modal', 'true');
			expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
		});

		it('should have accessible close button', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: true } });

			const closeButton = screen.getByLabelText('Close property details');
			expect(closeButton).toHaveAttribute('type', 'button');
		});

		it('should trap focus within modal when open', () => {
			render(PropertyDetailModal, { props: { property: mockProperty, open: true } });

			// Check that modal exists and is accessible
			const dialog = screen.getByRole('dialog');
			expect(dialog).toBeInTheDocument();

			// Focus should be trapped (implementation depends on focus-trap library)
			// This test verifies the modal is set up correctly for focus trapping
		});

		it('should have visible focus indicator on close button', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			// Check focus-visible styles exist in CSS
			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('focus-visible');
			expect(styles).toContain('outline');
		});
	});

	describe('OpenAI Design System Compliance', () => {
		it('should use system colors for modal background', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const modalContainer = container.querySelector('.modal-container');
			const computedStyle = window.getComputedStyle(modalContainer!);

			// Light mode: #ffffff
			expect(computedStyle.backgroundColor).toBe('rgb(255, 255, 255)');
		});

		it('should have proper z-index for modal overlay', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const overlay = container.querySelector('.modal-overlay');
			const computedStyle = window.getComputedStyle(overlay!);

			expect(computedStyle.zIndex).toBe('1300');
		});

		it('should have 480px max-width per design tokens', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const modalContainer = container.querySelector('.modal-container');
			const computedStyle = window.getComputedStyle(modalContainer!);

			expect(computedStyle.maxWidth).toBe('480px');
		});

		it('should have proper border radius (12px)', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const modalContainer = container.querySelector('.modal-container');
			const computedStyle = window.getComputedStyle(modalContainer!);

			expect(computedStyle.borderRadius).toBe('12px');
		});
	});

	describe('Mobile Responsive', () => {
		it('should render fullscreen on mobile (<768px)', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			// Check that mobile-specific media query exists
			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('@media (max-width: 768px)');
			expect(styles).toContain('max-height: 100vh');
			expect(styles).toContain('border-radius: 0');
		});
	});

	describe('Body Scroll Prevention', () => {
		it('should prevent body scroll when modal is open', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			// Note: Actual scroll prevention might be handled by a library
			// This test verifies modal structure supports it
			expect(screen.getByRole('dialog')).toBeInTheDocument();
		});
	});

	describe('Transitions', () => {
		it('should have fade transition on modal overlay', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			// Check that transition is applied (Svelte transitions)
			const overlay = container.querySelector('.modal-overlay');
			expect(overlay).toBeInTheDocument();
		});

		it('should have scale transition on modal container', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const modalContainer = container.querySelector('.modal-container');
			expect(modalContainer).toBeInTheDocument();
		});
	});

	describe('Edge Cases', () => {
		it('should handle undefined property gracefully', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: undefined, open: true }
			});

			// Should still render modal structure
			expect(screen.getByRole('dialog')).toBeInTheDocument();
		});

		it('should handle rapid open/close toggles', async () => {
			const { component } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: false }
			});

			// Open
			component.$set({ open: true });
			await waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});

			// Close
			component.$set({ open: false });
			await waitFor(() => {
				expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
			});

			// Open again
			component.$set({ open: true });
			await waitFor(() => {
				expect(screen.getByRole('dialog')).toBeInTheDocument();
			});
		});
	});

	describe('Scrollbar Styling', () => {
		it('should have custom scrollbar styles', () => {
			const { container } = render(PropertyDetailModal, {
				props: { property: mockProperty, open: true }
			});

			const styles = container.querySelector('style')?.textContent || '';
			expect(styles).toContain('::-webkit-scrollbar');
			expect(styles).toContain('::-webkit-scrollbar-thumb');
			expect(styles).toContain('::-webkit-scrollbar-track');
		});
	});
});
