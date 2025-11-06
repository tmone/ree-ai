/**
 * Property Card Component
 * Reusable card component for displaying property information
 */

'use client';

import type { Property } from '@/types';
import { MapPin, Bed, Bath, Maximize, Heart, Eye } from 'lucide-react';

interface PropertyCardProps {
  property: Property;
  onFavoriteToggle?: (propertyId: string) => void;
  isFavorited?: boolean;
  showEngagementMetrics?: boolean;
  onClick?: (propertyId: string) => void;
}

export default function PropertyCard({
  property,
  onFavoriteToggle,
  isFavorited = false,
  showEngagementMetrics = false,
  onClick,
}: PropertyCardProps) {
  const handleClick = () => {
    if (onClick) {
      onClick(property.property_id);
    } else {
      window.location.href = `/properties/${property.property_id}`;
    }
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFavoriteToggle?.(property.property_id);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-lg shadow hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden group"
    >
      {/* Image */}
      <div className="relative h-48 bg-gray-200 overflow-hidden">
        {property.thumbnail || property.images?.[0] ? (
          <img
            src={property.thumbnail || property.images?.[0]}
            alt={property.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-blue-50">
            <MapPin className="w-16 h-16 text-blue-300" />
          </div>
        )}

        {/* Favorite Button */}
        {onFavoriteToggle && (
          <button
            onClick={handleFavoriteClick}
            className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-sm transition-all ${
              isFavorited
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-white/80 text-gray-600 hover:bg-white hover:text-red-500'
            }`}
            title={isFavorited ? 'Bỏ yêu thích' : 'Yêu thích'}
          >
            <Heart className={`w-5 h-5 ${isFavorited ? 'fill-current' : ''}`} />
          </button>
        )}

        {/* Listing Type Badge */}
        <div className="absolute top-3 left-3">
          <span
            className={`px-3 py-1 text-xs font-semibold rounded-full backdrop-blur-sm ${
              property.listing_type === 'sale'
                ? 'bg-blue-500/90 text-white'
                : 'bg-green-500/90 text-white'
            }`}
          >
            {property.listing_type === 'sale' ? 'Bán' : 'Cho thuê'}
          </span>
        </div>

        {/* Status Badge */}
        {property.status !== 'active' && (
          <div className="absolute bottom-3 left-3">
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full backdrop-blur-sm ${
                property.status === 'sold' || property.status === 'rented'
                  ? 'bg-gray-500/90 text-white'
                  : property.status === 'pending'
                  ? 'bg-yellow-500/90 text-white'
                  : 'bg-gray-400/90 text-white'
              }`}
            >
              {property.status === 'sold'
                ? 'Đã bán'
                : property.status === 'rented'
                ? 'Đã cho thuê'
                : property.status === 'pending'
                ? 'Đang xử lý'
                : property.status}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-lg text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
          {property.title}
        </h3>

        {/* Location */}
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
          <MapPin className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">
            {property.district}, {property.city}
          </span>
        </div>

        {/* Price */}
        <div className="mb-3">
          <p className="text-2xl font-bold text-blue-600">
            {property.price_display || `${property.price.toLocaleString()} VND`}
          </p>
          {property.price_per_sqm && (
            <p className="text-xs text-gray-500 mt-1">
              {property.price_per_sqm.toLocaleString()} VND/m²
            </p>
          )}
        </div>

        {/* Specifications */}
        <div className="flex items-center gap-4 text-sm text-gray-600 pb-3 border-b border-gray-100">
          <div className="flex items-center gap-1">
            <Maximize className="w-4 h-4" />
            <span>{property.area}m²</span>
          </div>
          <div className="flex items-center gap-1">
            <Bed className="w-4 h-4" />
            <span>{property.bedrooms} PN</span>
          </div>
          <div className="flex items-center gap-1">
            <Bath className="w-4 h-4" />
            <span>{property.bathrooms} PT</span>
          </div>
        </div>

        {/* Engagement Metrics */}
        {showEngagementMetrics && (
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              <span>{property.views_count}</span>
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-4 h-4" />
              <span>{property.favorites_count}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
