/**
 * Inquiry Form Component
 * Form for buyers to send inquiries to sellers
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '@/services/api';
import type { InquiryCreate } from '@/types';
import { Send, CheckCircle, AlertCircle, MessageSquare } from 'lucide-react';

interface InquiryFormProps {
  propertyId: string;
  propertyTitle: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function InquiryForm({ propertyId, propertyTitle, onSuccess, onCancel }: InquiryFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<InquiryCreate>({
    defaultValues: {
      property_id: propertyId,
    },
  });

  const onSubmit = async (data: InquiryCreate) => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      await api.inquiries.send(data);

      setSuccess(true);
      reset();

      // Call success callback after 2 seconds
      setTimeout(() => {
        onSuccess?.();
      }, 2000);
    } catch (err: any) {
      setError(err.detail || 'Không thể gửi câu hỏi');
      console.error('Inquiry error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-blue-100 rounded-full p-2">
          <MessageSquare className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Liên hệ chủ nhà</h2>
          <p className="text-sm text-gray-600">{propertyTitle}</p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-red-800">
            <p className="font-semibold">Lỗi</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-green-800">
            <p className="font-semibold">Gửi thành công!</p>
            <p className="text-sm">Chủ nhà sẽ liên hệ với bạn sớm nhất</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Message */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nội dung tin nhắn <span className="text-red-500">*</span>
          </label>
          <textarea
            {...register('message', {
              required: 'Vui lòng nhập nội dung tin nhắn',
              minLength: { value: 10, message: 'Tin nhắn phải có ít nhất 10 ký tự' },
            })}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Tôi quan tâm đến bất động sản này. Vui lòng liên hệ với tôi để biết thêm chi tiết..."
          />
          {errors.message && <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>}
        </div>

        {/* Contact Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email liên hệ</label>
          <input
            type="email"
            {...register('contact_email', {
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Email không hợp lệ',
              },
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="email@example.com"
          />
          {errors.contact_email && <p className="mt-1 text-sm text-red-600">{errors.contact_email.message}</p>}
        </div>

        {/* Contact Phone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại liên hệ</label>
          <input
            type="tel"
            {...register('contact_phone', {
              pattern: {
                value: /^[0-9]{10,11}$/,
                message: 'Số điện thoại không hợp lệ (10-11 số)',
              },
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0901234567"
          />
          {errors.contact_phone && <p className="mt-1 text-sm text-red-600">{errors.contact_phone.message}</p>}
        </div>

        {/* Preferred Contact Time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Thời gian liên hệ thuận tiện</label>
          <select
            {...register('preferred_contact_time')}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">-- Chọn thời gian --</option>
            <option value="morning">Buổi sáng (8h - 12h)</option>
            <option value="afternoon">Buổi chiều (13h - 17h)</option>
            <option value="evening">Buổi tối (18h - 21h)</option>
            <option value="anytime">Bất kỳ lúc nào</option>
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
          )}

          <button
            type="submit"
            disabled={loading || success}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Gửi câu hỏi
              </>
            )}
          </button>
        </div>
      </form>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-800">
          <strong>Lưu ý:</strong> Thông tin liên hệ của bạn sẽ được gửi cho chủ nhà. Vui lòng cung cấp email hoặc số điện thoại để nhận phản hồi.
        </p>
      </div>
    </div>
  );
}
