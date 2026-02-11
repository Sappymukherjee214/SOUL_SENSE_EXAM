'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Loader2, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { Form, FormField } from '@/components/forms';
import { Button, Input } from '@/components/ui';
import { AuthLayout, SocialLogin, PasswordStrengthIndicator } from '@/components/auth';
import { registrationSchema } from '@/lib/validation';
import { z } from 'zod';
import { UseFormReturn } from 'react-hook-form';
import { useDebounce } from '@/hooks/useDebounce';
import { useEffect, useState, useMemo, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/errors';
import { useRateLimiter } from '@/hooks/useRateLimiter';
import { analyticsApi } from '@/lib/api/analytics';

type RegisterFormData = z.infer<typeof registrationSchema>;

interface RegisterFormContentProps {
  methods: UseFormReturn<RegisterFormData>;
  isLoading: boolean;
  setShowPassword: (show: boolean) => void;
  showPassword: boolean;
  lockoutTime?: number;
}

function RegisterFormContent({
  methods,
  isLoading,
  setShowPassword,
  showPassword,
  lockoutTime = 0,
}: RegisterFormContentProps) {
  const [availabilityStatus, setAvailabilityStatus] = useState<
    'idle' | 'loading' | 'available' | 'taken' | 'invalid'
  >('idle');

  // Analytics: Track field interactions
  const trackedFields = useRef<Set<string>>(new Set());
  const handleFocus = useCallback((fieldName: string) => {
    if (!trackedFields.current.has(fieldName)) {
      trackedFields.current.add(fieldName);
      analyticsApi.trackEvent({
        event_type: 'signup_workflow',
        event_name: 'field_focus',
        event_data: { field: fieldName },
      });
    }
  }, []);

  // Local cache to prevent redundant API calls
  const availabilityCache = useMemo(
    () => new Map<string, { available: boolean; message: string }>(),
    []
  );

  const usernameValue = methods.watch('username');
  const debouncedUsername = useDebounce(usernameValue, 500);

  useEffect(() => {
    if (!debouncedUsername || debouncedUsername.length < 3) {
      setAvailabilityStatus('idle');
      return;
    }

    // Client-side reserved words check
    const reserved = ['admin', 'root', 'support', 'soulsense', 'system', 'official'];
    if (reserved.includes(debouncedUsername.toLowerCase())) {
      setAvailabilityStatus('taken');
      return;
    }

    if (availabilityCache.has(debouncedUsername)) {
      setAvailabilityStatus(
        availabilityCache.get(debouncedUsername)!.available ? 'available' : 'taken'
      );
      return;
    }

    const checkAvailability = async () => {
      setAvailabilityStatus('loading');
      try {
        const data = await authApi.checkUsernameAvailability(debouncedUsername);
        availabilityCache.set(debouncedUsername, data);
        setAvailabilityStatus(data.available ? 'available' : 'taken');
      } catch (error) {
        console.error('Error checking username availability:', error);
        setAvailabilityStatus('idle');
      }
    };

    checkAvailability();
  }, [debouncedUsername, availabilityCache]);

  return (
    <>
      {methods.formState.errors.root && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive text-xs p-3 rounded-md flex items-center mb-4">
          <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
          {methods.formState.errors.root.message}
        </div>
      )}
      <div className="grid grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <FormField
            control={methods.control}
            name="firstName"
            label="First name"
            placeholder="John"
            required
            disabled={isLoading}
            onFocus={() => handleFocus('firstName')}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
        >
          <FormField
            control={methods.control}
            name="lastName"
            label="Last name"
            placeholder="Doe"
            disabled={isLoading}
            onFocus={() => handleFocus('lastName')}
          />
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        <FormField
          control={methods.control}
          name="username"
          label="Username"
          placeholder="johndoe"
          required
          disabled={isLoading}
          onFocus={() => handleFocus('username')}
        >
          {(fieldProps) => (
            <div className="relative">
              <Input
                {...fieldProps}
                className={cn(
                  fieldProps.className,
                  availabilityStatus === 'available' &&
                    'border-green-500 focus-visible:ring-green-500',
                  availabilityStatus === 'taken' && 'border-red-500 focus-visible:ring-red-500'
                )}
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center">
                {availabilityStatus === 'loading' && (
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                )}
                {availabilityStatus === 'available' && (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                )}
                {availabilityStatus === 'taken' && <XCircle className="h-4 w-4 text-red-500" />}
              </div>
              {availabilityStatus === 'taken' && (
                <p className="text-[10px] text-red-500 mt-1 absolute -bottom-4 left-0">
                  Username taken
                </p>
              )}
              {availabilityStatus === 'available' && (
                <p className="text-[10px] text-green-500 mt-1 absolute -bottom-4 left-0">
                  Available
                </p>
              )}
            </div>
          )}
        </FormField>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.25 }}
      >
        <FormField
          control={methods.control}
          name="email"
          label="Email"
          placeholder="you@example.com"
          type="email"
          required
          disabled={isLoading}
          onFocus={() => handleFocus('email')}
        />
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <FormField
            control={methods.control}
            name="age"
            label="Age"
            placeholder="25"
            type="number"
            required
            disabled={isLoading}
            onFocus={() => handleFocus('age')}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.35 }}
        >
          <FormField
            control={methods.control}
            name="gender"
            label="Gender"
            required
            onFocus={() => handleFocus('gender')}
          >
            {(fieldProps) => (
              <select
                {...fieldProps}
                disabled={isLoading}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            )}
          </FormField>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4 }}
      >
        <FormField
          control={methods.control}
          name="password"
          label="Password"
          required
          onFocus={() => handleFocus('password')}
        >
          {(fieldProps) => (
            <div className="relative space-y-2">
              <Input
                {...fieldProps}
                type={showPassword ? 'text' : 'password'}
                disabled={isLoading}
                autoComplete="new-password"
              />
              <PasswordStrengthIndicator password={fieldProps.value || ''} />
            </div>
          )}
        </FormField>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.45 }}
      >
        <FormField
          control={methods.control}
          name="confirmPassword"
          label="Confirm Password"
          required
          onFocus={() => handleFocus('confirmPassword')}
        >
          {(fieldProps) => (
            <div className="relative">
              <Input
                {...fieldProps}
                type={showPassword ? 'text' : 'password'}
                disabled={isLoading}
                autoComplete="new-password"
              />
            </div>
          )}
        </FormField>
      </motion.div>

      <div className="flex items-center space-x-2 mb-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setShowPassword(!showPassword)}
          disabled={isLoading}
          className="text-xs h-8"
        >
          {showPassword ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
          {showPassword ? 'Hide' : 'Show'} password
        </Button>
      </div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
      >
        <FormField
          control={methods.control}
          name="acceptTerms"
          onFocus={() => handleFocus('acceptTerms')}
        >
          {(fieldProps) => (
            <div className="flex items-start space-x-3 mb-4">
              <input
                type="checkbox"
                id="acceptTerms"
                checked={fieldProps.value || false}
                onChange={(e) => fieldProps.onChange(e.target.checked)}
                disabled={isLoading}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer disabled:cursor-not-allowed"
              />
              <label
                htmlFor="acceptTerms"
                className="text-xs text-muted-foreground cursor-pointer leading-tight"
              >
                I agree to the{' '}
                <Link
                  href="/terms"
                  className="text-primary hover:text-primary/80 underline"
                  target="_blank"
                >
                  Terms & Conditions
                </Link>
              </label>
            </div>
          )}
        </FormField>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.55 }}
      >
        <Button
          type="submit"
          className="w-full"
          disabled={isLoading || availabilityStatus === 'loading' || availabilityStatus === 'taken'}
        >
          {isLoading ? (
            lockoutTime > 0 ? (
              `Retry in ${lockoutTime}s`
            ) : (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Registering...
              </>
            )
          ) : (
            'Register'
          )}
        </Button>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
        <SocialLogin isLoading={isLoading} />
      </motion.div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.65 }}
        className="text-center text-sm text-muted-foreground mt-4"
      >
        Already have an account?{' '}
        <Link
          href="/login"
          className="text-primary hover:text-primary/80 font-medium transition-colors"
        >
          Sign in
        </Link>
      </motion.p>
    </>
  );
}

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const router = useRouter();

  const { lockoutTime, isLocked, handleRateLimitError } = useRateLimiter();

  // Analytics: Track page view
  useEffect(() => {
    analyticsApi.trackEvent({
      event_type: 'signup_workflow',
      event_name: 'signup_view',
    });
  }, []);

  const handleSubmit = async (data: RegisterFormData, methods: UseFormReturn<RegisterFormData>) => {
    if (isLocked) return;

    // Analytics: Track submit attempt
    analyticsApi.trackEvent({
      event_type: 'signup_workflow',
      event_name: 'signup_submit',
    });

    setIsLoading(true);
    try {
      const result = await authApi.register({
        username: data.username,
        password: data.password,
        email: data.email || '',
        first_name: data.firstName,
        last_name: data.lastName || '',
        age: data.age,
        gender: data.gender,
      });

      setIsSuccess(true);
      setSuccessMessage(
        result.message || 'Registration request received. Please check your email for next steps.'
      );

      // Analytics: Track success
      analyticsApi.trackEvent({
        event_type: 'signup_workflow',
        event_name: 'signup_success',
      });
    } catch (error) {
      if (error instanceof ApiError) {
        const result = error.data || {};

        // Check for Rate Limit Error first
        if (
          handleRateLimitError(result, (msg: string) => methods.setError('root', { message: msg }))
        ) {
          return;
        }

        // Pydantic validation error parsing
        let errorMessage = result.message;

        if (!errorMessage && result.detail) {
          if (Array.isArray(result.detail)) {
            // Standard Pydantic detail list: [{loc, msg, type}]
            errorMessage = result.detail[0]?.msg;
          } else if (typeof result.detail === 'string') {
            errorMessage = result.detail;
          } else if (result.detail.message) {
            errorMessage = result.detail.message;
          }
        }

        methods.setError('root', {
          message: errorMessage || 'Registration failed. Please try again or contact support.',
        });

        // Analytics: Track API error
        analyticsApi.trackEvent({
          event_type: 'signup_workflow',
          event_name: 'signup_error',
          event_data: { error: errorMessage || 'Registration failed' },
        });
      } else {
        methods.setError('root', {
          message: 'Network error. Please check your connection and try again.',
        });

        // Analytics: Track Network error
        analyticsApi.trackEvent({
          event_type: 'signup_workflow',
          event_name: 'signup_network_error',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const effectiveLoading = isLoading || isLocked;

  return (
    <AuthLayout
      title="Create an account"
      subtitle="Start your emotional intelligence journey today"
    >
      {isSuccess ? (
        <motion.div
          // ... (success view remains same)
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-4 py-8"
        >
          <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-semibold">Verify your email</h3>
          <p className="text-muted-foreground">{successMessage}</p>
          <Button onClick={() => router.push('/login')} className="mt-4">
            Back to Login
          </Button>
        </motion.div>
      ) : (
        <Form
          schema={registrationSchema}
          onSubmit={handleSubmit}
          className={`space-y-4 transition-opacity duration-200 ${effectiveLoading ? 'opacity-60 pointer-events-none' : ''}`}
        >
          {(methods) => (
            <>
              <RegisterFormContent
                methods={methods}
                isLoading={effectiveLoading}
                setShowPassword={setShowPassword}
                showPassword={showPassword}
                lockoutTime={lockoutTime}
              />
            </>
          )}
        </Form>
      )}
    </AuthLayout>
  );
}
