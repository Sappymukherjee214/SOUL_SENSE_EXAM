'use client';

import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { profileApi, UserProfile, UpdateUserProfile } from '@/lib/api/profile';

export interface UseProfileReturn {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  updateProfile: (data: UpdateUserProfile) => Promise<void>;
  uploadAvatar: (file: File) => Promise<void>;
  deleteAvatar: () => Promise<void>;
  refetch: () => Promise<void>;
}

export function useProfile(): UseProfileReturn {
  const queryClient = useQueryClient();
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);

  const {
    data: profile,
    isLoading: fetchLoading,
    error: fetchError,
    refetch,
  } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.getUserProfile(),
  });

  const updateProfile = useCallback(
    async (data: UpdateUserProfile) => {
      setUpdateLoading(true);
      setUpdateError(null);

      try {
        await profileApi.updateUserProfile(data);
        // Invalidate and refetch the profile after successful update
        await queryClient.invalidateQueries({ queryKey: ['profile'] });
      } catch (error: any) {
        const errorMessage = error?.message || 'Failed to update profile';
        setUpdateError(errorMessage);
        throw error;
      } finally {
        setUpdateLoading(false);
      }
    },
    [queryClient]
  );

  const uploadAvatar = useCallback(
    async (file: File) => {
      setUpdateLoading(true);
      setUpdateError(null);

      try {
        await profileApi.uploadAvatar(file);
        // Refetch the profile after successful upload
        await refetch();
      } catch (error: any) {
        const errorMessage = error?.message || 'Failed to upload avatar';
        setUpdateError(errorMessage);
        throw error;
      } finally {
        setUpdateLoading(false);
      }
    },
    [refetch]
  );

  const deleteAvatar = useCallback(async () => {
    setUpdateLoading(true);
    setUpdateError(null);

    try {
      await profileApi.deleteAvatar();
      // Refetch the profile after successful deletion
      await refetch();
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to delete avatar';
      setUpdateError(errorMessage);
      throw error;
    } finally {
      setUpdateLoading(false);
    }
  }, [refetch]);

  return {
    profile,
    isLoading: fetchLoading || updateLoading,
    error: fetchError || updateError,
    updateProfile,
    uploadAvatar,
    deleteAvatar,
    refetch,
  };
}
