/**
 * Favorites List Component
 * Display user's saved/favorite properties
 */

'use client';

import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import type { FavoriteWithProperty } from '@/types';
import { Heart, Trash2, Edit3, MapPin, Home, AlertCircle } from 'lucide-react';

export default function FavoritesList() {
  const [favorites, setFavorites] = useState<FavoriteWithProperty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingNotes, setEditingNotes] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.favorites.getAll({ page_size: 100 });
      setFavorites(response.items);
    } catch (err: any) {
      setError(err.detail || 'Không thể tải danh sách yêu thích');
      console.error('Favorites error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (propertyId: string) => {
    if (!confirm('Bạn có chắc muốn xóa bất động sản này khỏi danh sách yêu thích?')) {
      return;
    }

    try {
      await api.favorites.remove(propertyId);
      setFavorites((prev) => prev.filter((fav) => fav.property_id !== propertyId));
    } catch (err: any) {
      alert(err.detail || 'Không thể xóa khỏi yêu thích');
    }
  };

  const handleUpdateNotes = async (propertyId: string, notes: string) => {
    try {
      await api.favorites.updateNotes(propertyId, { notes });
      setFavorites((prev) =>
        prev.map((fav) => (fav.property_id === propertyId ? { ...fav, notes } : fav))
      );
      setEditingNotes((prev) => {
        const newState = { ...prev };
        delete newState[propertyId];
        return newState;
      });
    } catch (err: any) {
      alert(err.detail || 'Không thể cập nhật ghi chú');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải danh sách yêu thích...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-3 text-red-800">
            <AlertCircle className="w-6 h-6" />
            <div>
              <h3 className="font-semibold">Lỗi tải dữ liệu</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={loadFavorites}
            className="mt-4 w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Danh sách yêu thích</h1>
          <p className="mt-2 text-gray-600">{favorites.length} bất động sản đã lưu</p>
        </div>

        {favorites.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {favorites.map((favorite) => (
              <div key={favorite.property_id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="p-6">
                  {/* Property Info */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{favorite.property.title}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                        <MapPin className="w-4 h-4" />
                        <span>
                          {favorite.property.district}, {favorite.property.city}
                        </span>
                      </div>
                      <p className="text-2xl font-bold text-blue-600">
                        {favorite.property.price_display || `${favorite.property.price.toLocaleString()} VND`}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span>{favorite.property.area}m²</span>
                        <span>{favorite.property.bedrooms} PN</span>
                        <span>{favorite.property.bathrooms} PT</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemove(favorite.property_id)}
                      className="ml-4 text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors"
                      title="Xóa khỏi yêu thích"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Notes */}
                  <div className="border-t pt-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Edit3 className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">Ghi chú:</span>
                    </div>

                    {editingNotes[favorite.property_id] !== undefined ? (
                      <div>
                        <textarea
                          value={editingNotes[favorite.property_id]}
                          onChange={(e) =>
                            setEditingNotes((prev) => ({
                              ...prev,
                              [favorite.property_id]: e.target.value,
                            }))
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                          rows={2}
                          placeholder="Thêm ghi chú về bất động sản này..."
                        />
                        <div className="flex gap-2 mt-2">
                          <button
                            onClick={() => handleUpdateNotes(favorite.property_id, editingNotes[favorite.property_id])}
                            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                          >
                            Lưu
                          </button>
                          <button
                            onClick={() =>
                              setEditingNotes((prev) => {
                                const newState = { ...prev };
                                delete newState[favorite.property_id];
                                return newState;
                              })
                            }
                            className="px-3 py-1 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition-colors"
                          >
                            Hủy
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div
                        onClick={() =>
                          setEditingNotes((prev) => ({
                            ...prev,
                            [favorite.property_id]: favorite.notes || '',
                          }))
                        }
                        className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors min-h-[60px]"
                      >
                        {favorite.notes || 'Nhấn để thêm ghi chú...'}
                      </div>
                    )}
                  </div>

                  <div className="mt-4">
                    <a
                      href={`/properties/${favorite.property_id}`}
                      className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Xem chi tiết
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Heart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Chưa có bất động sản yêu thích</h3>
            <p className="text-gray-600 mb-6">Lưu các bất động sản bạn quan tâm để dễ dàng theo dõi sau này</p>
            <a
              href="/search"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tìm kiếm bất động sản
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
