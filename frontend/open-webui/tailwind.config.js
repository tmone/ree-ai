import typography from '@tailwindcss/typography';
import containerQueries from '@tailwindcss/container-queries';

/** @type {import('tailwindcss').Config} */
export default {
	darkMode: 'class',
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				// Gray scale from Figma design system
				gray: {
					50: 'var(--color-gray-50, #f9f9f9)',
					100: 'var(--color-gray-100, #ececec)',
					200: 'var(--color-gray-200, #e3e3e3)',
					300: 'var(--color-gray-300, #cdcdcd)',
					400: 'var(--color-gray-400, #b4b4b4)',
					500: 'var(--color-gray-500, #9b9b9b)',
					600: 'var(--color-gray-600, #676767)',
					700: 'var(--color-gray-700, #4e4e4e)',
					800: 'var(--color-gray-800, #333333)',
					850: 'var(--color-gray-850, #262626)',
					900: 'var(--color-gray-900, #171717)',
					950: 'var(--color-gray-950, #0d0d0d)'
				},
				// Semantic colors from OpenAI design system
				bg: {
					primary: 'var(--bg-primary)',
					secondary: 'var(--bg-secondary)',
					tertiary: 'var(--bg-tertiary)'
				},
				text: {
					primary: 'var(--text-primary)',
					secondary: 'var(--text-secondary)',
					tertiary: 'var(--text-tertiary)',
					inverse: 'var(--text-inverse)'
				},
				icon: {
					primary: 'var(--icon-primary)',
					secondary: 'var(--icon-secondary)',
					tertiary: 'var(--icon-tertiary)',
					inverse: 'var(--icon-inverse)'
				},
				accent: {
					blue: 'var(--accent-blue)',
					red: 'var(--accent-red)',
					orange: 'var(--accent-orange)',
					green: 'var(--accent-green)'
				},
				brand: {
					primary: 'var(--brand-primary)',
					'primary-hover': 'var(--brand-primary-hover)',
					'primary-active': 'var(--brand-primary-active)',
					'primary-disabled': 'var(--brand-primary-disabled)',
					secondary: 'var(--brand-secondary)',
					'secondary-hover': 'var(--brand-secondary-hover)'
				},
				status: {
					success: 'var(--color-success)',
					'success-bg': 'var(--color-success-bg)',
					warning: 'var(--color-warning)',
					'warning-bg': 'var(--color-warning-bg)',
					error: 'var(--color-error)',
					'error-bg': 'var(--color-error-bg)',
					info: 'var(--color-info)',
					'info-bg': 'var(--color-info-bg)'
				}
			},
			fontFamily: {
				sans: ['var(--font-sans)'],
				mono: ['var(--font-mono)']
			},
			fontSize: {
				// Typography scale from Figma
				'heading-1': ['var(--text-heading1-size)', {
					lineHeight: 'var(--text-heading1-line-height)',
					letterSpacing: 'var(--text-heading1-letter-spacing)',
					fontWeight: 'var(--text-heading1-weight)'
				}],
				'heading-2': ['var(--text-heading2-size)', {
					lineHeight: 'var(--text-heading2-line-height)',
					letterSpacing: 'var(--text-heading2-letter-spacing)',
					fontWeight: 'var(--text-heading2-weight)'
				}],
				'heading-3': ['var(--text-heading3-size)', {
					lineHeight: 'var(--text-heading3-line-height)',
					letterSpacing: 'var(--text-heading3-letter-spacing)',
					fontWeight: 'var(--text-heading3-weight)'
				}],
				'body': ['var(--text-body-size)', {
					lineHeight: 'var(--text-body-line-height)',
					letterSpacing: 'var(--text-body-letter-spacing)',
					fontWeight: 'var(--text-body-weight)'
				}],
				'body-small': ['var(--text-body-small-size)', {
					lineHeight: 'var(--text-body-small-line-height)',
					letterSpacing: 'var(--text-body-small-letter-spacing)',
					fontWeight: 'var(--text-body-small-weight)'
				}],
				'caption': ['var(--text-caption-size)', {
					lineHeight: 'var(--text-caption-line-height)',
					letterSpacing: 'var(--text-caption-letter-spacing)',
					fontWeight: 'var(--text-caption-weight)'
				}]
			},
			spacing: {
				// Spacing scale from Figma
				'space-0': 'var(--space-0)',
				'space-1': 'var(--space-1)',
				'space-2': 'var(--space-2)',
				'space-3': 'var(--space-3)',
				'space-4': 'var(--space-4)',
				'space-5': 'var(--space-5)',
				'space-6': 'var(--space-6)',
				'space-7': 'var(--space-7)',
				'space-8': 'var(--space-8)',
				'space-9': 'var(--space-9)',
				'space-10': 'var(--space-10)',
				'space-11': 'var(--space-11)'
			},
			borderRadius: {
				// Border radius from Figma
				'radius-sm': 'var(--radius-sm)',
				'radius-base': 'var(--radius-base)',
				'radius-md': 'var(--radius-md)',
				'radius-lg': 'var(--radius-lg)',
				'radius-xl': 'var(--radius-xl)',
				'radius-full': 'var(--radius-full)'
			},
			boxShadow: {
				// Shadows from Figma
				'shadow-sm': 'var(--shadow-sm)',
				'shadow-base': 'var(--shadow-base)',
				'shadow-md': 'var(--shadow-md)',
				'shadow-lg': 'var(--shadow-lg)',
				'shadow-xl': 'var(--shadow-xl)'
			},
			transitionDuration: {
				'fast': '150ms',
				'base': '200ms',
				'slow': '300ms'
			},
			typography: {
				DEFAULT: {
					css: {
						pre: false,
						code: false,
						'pre code': false,
						'code::before': false,
						'code::after': false
					}
				}
			},
			padding: {
				'safe-bottom': 'env(safe-area-inset-bottom)'
			},
			transitionProperty: {
				width: 'width'
			}
		}
	},
	plugins: [typography, containerQueries]
};
