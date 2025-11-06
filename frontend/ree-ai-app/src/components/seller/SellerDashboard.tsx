/**
 * Seller Dashboard Component
 * Main dashboard for property sellers showing stats, listings, and inquiries
 */

'use client';

import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import type { Property, InquiryStats } from '@/types';
import { Home, MessageSquare, Eye, Heart, TrendingUp, AlertCircle } from 'lucide-react';

interface DashboardStats {
  total_properties: number;
  active_properties: number;
  draft_properties: number;
  sold_properties: number;
  total_views: number;
  total_favorites: number;
  total_inquiries: number;
}

export default function SellerDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [inquiryStats, setInquiryStats] = useState<InquiryStats | null>(null);
  const [recentProperties, setRecentProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load properties
      const propertiesResponse = await api.property.getMyListings({ page: 1, page_size: 5 });
      setRecentProperties(propertiesResponse.items);

      // Calculate stats from properties
      const allPropertiesResponse = await api.property.getMyListings({ page_size: 1000 });
      const allProperties = allPropertiesResponse.items;

      const dashboardStats: DashboardStats = {
        total_properties: allProperties.length,
        active_properties: allProperties.filter((p) => p.status === 'active').length,
        draft_properties: allProperties.filter((p) => p.status === 'draft').length,
        sold_properties: allProperties.filter((p) => p.status === 'sold' || p.status === 'rented').length,
        total_views: allProperties.reduce((sum, p) => sum + p.views_count, 0),
        total_favorites: allProperties.reduce((sum, p) => sum + p.favorites_count, 0),
        total_inquiries: allProperties.reduce((sum, p) => sum + p.inquiries_count, 0),
      };

      setStats(dashboardStats);

      // Load inquiry stats
      const inquiryStatsData = await api.inquiries.getStats();
      setInquiryStats(inquiryStatsData);
    } catch (err: any) {
      setError(err.detail || 'Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải bảng điều khiển...</p>
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
            onClick={loadDashboardData}
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
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Bảng điều khiển</h1>
          <p className="mt-2 text-gray-600">Quản lý bất động sản của bạn</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Properties */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tổng bất động sản</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_properties || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats?.active_properties || 0} đang hoạt động, {stats?.draft_properties || 0} nháp
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Home className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Total Views */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Lượt xem</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_views.toLocaleString() || 0}</p>
                <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Tổng số lượt xem
                </p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <Eye className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Total Favorites */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Yêu thích</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_favorites || 0}</p>
                <p className="text-xs text-gray-500 mt-1">Số lần được lưu</p>
              </div>
              <div className="bg-pink-100 rounded-full p-3">
                <Heart className="w-6 h-6 text-pink-600" />
              </div>
            </div>
          </div>

          {/* Total Inquiries */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Câu hỏi</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_inquiries || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {inquiryStats?.pending_count || 0} chưa trả lời
                </p>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <MessageSquare className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Inquiry Performance */}
        {inquiryStats && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Hiệu suất trả lời</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600">Tỷ lệ trả lời</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {inquiryStats.response_rate.toFixed(1)}%
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${inquiryStats.response_rate}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">Thời gian trả lời trung bình</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {inquiryStats.avg_response_time_hours
                    ? `${inquiryStats.avg_response_time_hours.toFixed(1)}h`
                    : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Trạng thái</p>
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Chưa trả lời:</span>
                    <span className="font-semibold text-yellow-600">{inquiryStats.pending_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Đã trả lời:</span>
                    <span className="font-semibold text-green-600">{inquiryStats.responded_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Đã đóng:</span>
                    <span className="font-semibold text-gray-600">{inquiryStats.closed_count}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Properties */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Bất động sản gần đây</h2>
            <a href="/seller/properties" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              Xem tất cả →
            </a>
          </div>
          <div className="divide-y divide-gray-200">
            {recentProperties.length > 0 ? (
              recentProperties.map((property) => (
                <div key={property.property_id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{property.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {property.district}, {property.city}
                      </p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-lg font-semibold text-blue-600">
                          {property.price_display || `${property.price.toLocaleString()} VND`}
                        </span>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            property.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : property.status === 'draft'
                              ? 'bg-gray-100 text-gray-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {property.status === 'active'
                            ? 'Đang hoạt động'
                            : property.status === 'draft'
                            ? 'Nháp'
                            : property.status}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 flex gap-6 text-sm text-gray-600">
                      <div className="text-center">
                        <Eye className="w-4 h-4 mx-auto mb-1" />
                        <span>{property.views_count}</span>
                      </div>
                      <div className="text-center">
                        <Heart className="w-4 h-4 mx-auto mb-1" />
                        <span>{property.favorites_count}</span>
                      </div>
                      <div className="text-center">
                        <MessageSquare className="w-4 h-4 mx-auto mb-1" />
                        <span>{property.inquiries_count}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-12 text-center">
                <Home className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">Chưa có bất động sản nào</p>
                <a
                  href="/seller/properties/new"
                  className="mt-4 inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Đăng tin mới
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
