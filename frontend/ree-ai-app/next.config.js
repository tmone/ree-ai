/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_DB_GATEWAY_URL: process.env.NEXT_PUBLIC_DB_GATEWAY_URL,
    NEXT_PUBLIC_USER_MANAGEMENT_URL: process.env.NEXT_PUBLIC_USER_MANAGEMENT_URL,
  },

  // Image optimization
  images: {
    domains: ['localhost', 'via.placeholder.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Output configuration
  output: 'standalone',
};

module.exports = nextConfig;
