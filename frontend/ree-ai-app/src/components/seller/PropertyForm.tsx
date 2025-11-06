/**
 * Property Form Component
 * Form for creating and editing property listings
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '@/services/api';
import type { PropertyCreate, PropertyUpdate, Property } from '@/types';
import { Save, Send, AlertCircle, CheckCircle } from 'lucide-react';

interface PropertyFormProps {
  property?: Property; // If editing existing property
  onSuccess?: (property: Property) => void;
  onCancel?: () => void;
}

export default function PropertyForm({ property, onSuccess, onCancel }: PropertyFormProps) {
  const isEditing = !!property;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<PropertyCreate>({
    defaultValues: property
      ? {
          title: property.title,
          description: property.description,
          property_type: property.property_type,
          listing_type: property.listing_type,
          address: property.address,
          district: property.district,
          city: property.city,
          price: property.price,
          area: property.area,
          bedrooms: property.bedrooms,
          bathrooms: property.bathrooms,
          floors: property.floors,
        }
      : {
          listing_type: 'sale',
          bedrooms: 1,
          bathrooms: 1,
        },
  });

  const onSubmit = async (data: PropertyCreate, publishImmediately: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      let result: Property;

      if (isEditing && property) {
        // Update existing property
        const updateData: PropertyUpdate = { ...data };
        result = await api.property.update(property.property_id, updateData);
      } else {
        // Create new property
        data.publish_immediately = publishImmediately;
        result = await api.property.create(data);
      }

      setSuccess(true);

      // Call success callback after 1 second
      setTimeout(() => {
        onSuccess?.(result);
      }, 1000);
    } catch (err: any) {
      setError(err.detail || 'Không thể lưu bất động sản');
      console.error('Form error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDraft = handleSubmit((data) => onSubmit(data, false));
  const handlePublish = handleSubmit((data) => onSubmit(data, true));

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {isEditing ? 'Chỉnh sửa bất động sản' : 'Đăng tin bất động sản mới'}
      </h2>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-red-800">
            <p className="font-semibold">Lỗi</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-green-800">
            <p className="font-semibold">Thành công!</p>
            <p className="text-sm">Bất động sản đã được lưu</p>
          </div>
        </div>
      )}

      <form onSubmit={handlePublish} className="space-y-6">
        {/* Basic Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Thông tin cơ bản</h3>

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tiêu đề <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                {...register('title', { required: 'Vui lòng nhập tiêu đề' })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="VD: Căn hộ 2 phòng ngủ tại Quận 7"
              />
              {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mô tả <span className="text-red-500">*</span>
              </label>
              <textarea
                {...register('description', { required: 'Vui lòng nhập mô tả' })}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Mô tả chi tiết về bất động sản..."
              />
              {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>}
            </div>

            {/* Property Type & Listing Type */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Loại bất động sản <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('property_type', { required: 'Vui lòng chọn loại' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">-- Chọn loại --</option>
                  <option value="apartment">Căn hộ</option>
                  <option value="house">Nhà phố</option>
                  <option value="villa">Biệt thự</option>
                  <option value="land">Đất nền</option>
                  <option value="commercial">Thương mại</option>
                </select>
                {errors.property_type && <p className="mt-1 text-sm text-red-600">{errors.property_type.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hình thức <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('listing_type', { required: 'Vui lòng chọn hình thức' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="sale">Bán</option>
                  <option value="rent">Cho thuê</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Location */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Vị trí</h3>

          <div className="space-y-4">
            {/* City & District */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Thành phố <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('city', { required: 'Vui lòng chọn thành phố' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">-- Chọn thành phố --</option>
                  <option value="Hồ Chí Minh">Hồ Chí Minh</option>
                  <option value="Hà Nội">Hà Nội</option>
                  <option value="Đà Nẵng">Đà Nẵng</option>
                  <option value="Cần Thơ">Cần Thơ</option>
                  <option value="Bình Dương">Bình Dương</option>
                </select>
                {errors.city && <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quận/Huyện <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  {...register('district', { required: 'Vui lòng nhập quận/huyện' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="VD: Quận 7"
                />
                {errors.district && <p className="mt-1 text-sm text-red-600">{errors.district.message}</p>}
              </div>
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Địa chỉ chi tiết</label>
              <input
                type="text"
                {...register('address')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="VD: 123 Đường Nguyễn Văn Linh"
              />
            </div>
          </div>
        </div>

        {/* Pricing & Specifications */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Giá & Thông số</h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giá (VND) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                {...register('price', {
                  required: 'Vui lòng nhập giá',
                  min: { value: 0, message: 'Giá phải lớn hơn 0' },
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="5000000000"
              />
              {errors.price && <p className="mt-1 text-sm text-red-600">{errors.price.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Diện tích (m²) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.1"
                {...register('area', {
                  required: 'Vui lòng nhập diện tích',
                  min: { value: 0, message: 'Diện tích phải lớn hơn 0' },
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="80"
              />
              {errors.area && <p className="mt-1 text-sm text-red-600">{errors.area.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Số phòng ngủ <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                {...register('bedrooms', {
                  required: 'Vui lòng nhập số phòng ngủ',
                  min: { value: 0, message: 'Phải từ 0 trở lên' },
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="2"
              />
              {errors.bedrooms && <p className="mt-1 text-sm text-red-600">{errors.bedrooms.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Số phòng tắm <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                {...register('bathrooms', {
                  required: 'Vui lòng nhập số phòng tắm',
                  min: { value: 0, message: 'Phải từ 0 trở lên' },
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="2"
              />
              {errors.bathrooms && <p className="mt-1 text-sm text-red-600">{errors.bathrooms.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Số tầng</label>
              <input
                type="number"
                {...register('floors')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="1"
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 pt-6 border-t">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
          )}

          {!isEditing && (
            <button
              type="button"
              onClick={handleSaveDraft}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              Lưu nháp
            </button>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 ml-auto"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            ) : (
              <>
                <Send className="w-4 h-4" />
                {isEditing ? 'Cập nhật' : 'Đăng tin'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
