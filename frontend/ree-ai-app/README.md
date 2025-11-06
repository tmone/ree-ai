# REE AI Frontend Application

Modern, responsive frontend application for REE AI real estate platform built with Next.js 14, React, TypeScript, and TailwindCSS.

## Features

### For Sellers (Người bán/cho thuê)
- **Dashboard**: View property statistics, engagement metrics, and inquiry performance
- **Property Management**: Create, edit, publish/unpublish, and delete property listings
- **Property Form**: Rich form with validation for posting properties
- **Inquiry Management**: Receive and respond to buyer inquiries
- **Analytics**: Track views, favorites, and inquiries

### For Buyers (Người tìm nhà)
- **Property Search**: Full-text search with advanced filters
- **Favorites**: Save properties with personal notes
- **Saved Searches**: Save search criteria and get notifications for new matches
- **Inquiries**: Contact sellers directly through inquiry forms
- **Property Details**: View comprehensive property information

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand (planned)
- **Data Fetching**: SWR + Axios
- **Form Validation**: React Hook Form + Zod
- **Icons**: Lucide React

## Project Structure

```
frontend/ree-ai-app/
├── src/
│   ├── components/          # React components
│   │   ├── seller/         # Seller-specific components
│   │   │   ├── SellerDashboard.tsx
│   │   │   ├── PropertyForm.tsx
│   │   │   └── PropertyList.tsx
│   │   ├── buyer/          # Buyer-specific components
│   │   │   ├── FavoritesList.tsx
│   │   │   ├── SavedSearchesList.tsx
│   │   │   └── InquiryForm.tsx
│   │   └── shared/         # Shared components
│   │       ├── PropertyCard.tsx
│   │       └── SearchBar.tsx
│   ├── services/           # API service layer
│   │   └── api.ts         # Centralized API client
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   └── app/               # Next.js app directory (pages)
├── public/                # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm or yarn
- Backend services running (DB Gateway, User Management)

### Installation

1. **Clone the repository**:
```bash
cd /home/user/ree-ai/frontend/ree-ai-app
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment**:
```bash
cp .env.example .env.local
```

Edit `.env.local` and set your API URLs:
```env
NEXT_PUBLIC_DB_GATEWAY_URL=http://localhost:8081
NEXT_PUBLIC_USER_MANAGEMENT_URL=http://localhost:8085
```

4. **Run development server**:
```bash
npm run dev
```

5. **Open browser**:
Navigate to [http://localhost:3001](http://localhost:3001)

## Available Scripts

- `npm run dev` - Start development server on port 3001
- `npm run build` - Build production application
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## API Integration

The frontend communicates with backend services through a centralized API layer (`src/services/api.ts`):

### Authentication
```typescript
import { api } from '@/services/api';

// Register
const tokens = await api.auth.register({
  email: 'user@example.com',
  password: 'password123',
  full_name: 'John Doe',
  user_type: 'buyer'
});

// Login
const tokens = await api.auth.login({
  email: 'user@example.com',
  password: 'password123'
});

// Logout
api.auth.logout();
```

### Property Management
```typescript
// Create property
const property = await api.property.create({
  title: 'Căn hộ 2PN tại Q7',
  description: '...',
  property_type: 'apartment',
  listing_type: 'sale',
  city: 'Hồ Chí Minh',
  district: 'Quận 7',
  price: 5000000000,
  area: 80,
  bedrooms: 2,
  bathrooms: 2
});

// Get my listings
const listings = await api.property.getMyListings({ page: 1, page_size: 20 });

// Update property
const updated = await api.property.update(propertyId, { price: 5500000000 });

// Delete property
await api.property.delete(propertyId);
```

### Favorites
```typescript
// Add to favorites
await api.favorites.add({ property_id: '123', notes: 'Nice location' });

// Get favorites
const favorites = await api.favorites.getAll();

// Remove from favorites
await api.favorites.remove('123');
```

### Inquiries
```typescript
// Send inquiry
await api.inquiries.send({
  property_id: '123',
  message: 'I am interested in this property',
  contact_email: 'buyer@example.com',
  contact_phone: '0901234567'
});

// Get received inquiries (seller)
const inquiries = await api.inquiries.getReceived({ status_filter: 'pending' });

// Respond to inquiry
await api.inquiries.respond(inquiryId, {
  response_message: 'Thank you for your interest...'
});
```

## Component Usage

### SellerDashboard
```tsx
import SellerDashboard from '@/components/seller/SellerDashboard';

export default function DashboardPage() {
  return <SellerDashboard />;
}
```

### PropertyForm
```tsx
import PropertyForm from '@/components/seller/PropertyForm';

export default function NewPropertyPage() {
  return (
    <PropertyForm
      onSuccess={(property) => {
        console.log('Property created:', property);
        router.push('/seller/properties');
      }}
      onCancel={() => router.back()}
    />
  );
}
```

### FavoritesList
```tsx
import FavoritesList from '@/components/buyer/FavoritesList';

export default function FavoritesPage() {
  return <FavoritesList />;
}
```

### PropertyCard
```tsx
import PropertyCard from '@/components/shared/PropertyCard';

export default function SearchResults({ properties }) {
  return (
    <div className="grid grid-cols-3 gap-6">
      {properties.map(property => (
        <PropertyCard
          key={property.property_id}
          property={property}
          showEngagementMetrics
        />
      ))}
    </div>
  );
}
```

## Authentication Flow

1. User registers/logs in via `api.auth.register()` or `api.auth.login()`
2. JWT token is stored in `localStorage`
3. Axios interceptors automatically attach token to requests
4. On 401 error, user is redirected to login page
5. Protected routes check authentication status on mount

## Styling Guidelines

- Use TailwindCSS utility classes for styling
- Follow responsive design principles (mobile-first)
- Use consistent spacing (4px increments: p-2, p-4, p-6, p-8)
- Use color palette from `tailwind.config.js`
- Icons from Lucide React (consistent size: w-4 h-4, w-5 h-5, w-6 h-6)

## Future Enhancements

- [ ] Image upload with preview
- [ ] Advanced search filters
- [ ] Map integration for property locations
- [ ] Real-time notifications for inquiries
- [ ] Property comparison feature
- [ ] User profile management
- [ ] Payment integration
- [ ] Admin dashboard

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test thoroughly
3. Commit: `git commit -m "feat: add my feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## License

Proprietary - REE AI Platform
