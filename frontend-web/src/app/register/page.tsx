'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye,
  EyeOff,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  User,
  Mail,
  Shield,
} from 'lucide-react';
import { Form, FormField } from '@/components/forms';
import { Button, Input } from '@/components/ui';
import {
  AuthLayout,
  SocialLogin,
  PasswordStrengthIndicator,
  StepIndicator,
} from '@/components/auth';
import { registrationSchema } from '@/lib/validation';
import { useController, UseFormReturn } from 'react-hook-form';
import { useDebounce } from '@/hooks/useDebounce';
import { useEffect, useState, useMemo, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/errors';
import { useRateLimiter } from '@/hooks/useRateLimiter';
import { analyticsApi } from '@/lib/api/analytics';
import { useAuth } from '@/hooks/useAuth';
import { isValidCallbackUrl } from '@/lib/utils/url';

// step components and shared types have been moved to separate modules
import PersonalStep from './steps/PersonalStep';
import AccountStep from './steps/AccountStep';
import TermsStep from './steps/TermsStep';
import { RegisterFormData, StepContentProps, StepProps } from './registerTypes';

const steps = [
  { id: 'personal', label: 'Personal', description: 'Your info' },
  { id: 'account', label: 'Account', description: 'Credentials' },
  { id: 'terms', label: 'Complete', description: 'Review & submit' },
];


// PersonalStep moved to ./steps/PersonalStep.tsx

// AccountStep moved to ./steps/AccountStep.tsx

// TermsStep moved to ./steps/TermsStep.tsx

export default function RegisterPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/';
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();

  // Guard: Redirect if already logged in
  useEffect(() => {
    if (!authLoading && isAuthenticated && !isLoading) {
      const finalRedirect = isValidCallbackUrl(callbackUrl) ? callbackUrl : '/';
      router.push(finalRedirect);
    }
  }, [isAuthenticated, authLoading, isLoading, router, callbackUrl]);

  const { lockoutTime, isLocked, handleRateLimitError } = useRateLimiter();

  const availabilityCache = useMemo(
    () => new Map<string, { available: boolean; message: string }>(),
    []
  );

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

  // Analytics: Track page view
  useEffect(() => {
    analyticsApi.trackEvent({
      event_type: 'signup_workflow',
      event_name: 'signup_view',
    });
  }, []);

  const validateStep = useCallback(
    (step: number, methods: UseFormReturn<RegisterFormData>): boolean => {
      const values = methods.getValues();
      const errors = methods.formState.errors;

      switch (step) {
        case 0: // Personal
          return (
            !!values.firstName &&
            !!values.age &&
            !!values.gender &&
            !errors.firstName &&
            !errors.age &&
            !errors.gender
          );
        case 1: // Account
          return (
            !!values.username &&
            !!values.email &&
            !!values.password &&
            !!values.confirmPassword &&
            !errors.username &&
            !errors.email &&
            !errors.password &&
            !errors.confirmPassword
          );
        case 2: // Terms
          return !!values.acceptTerms;
        default:
          return false;
      }
    },
    []
  );

  const handleNext = useCallback((methods: UseFormReturn<RegisterFormData>) => {
    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  }, []);

  const handleBack = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
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

      setSuccessMessage(
        result.message || 'Registration request received. Please check your email for next steps.'
      );

      // Analytics: Track success
      analyticsApi.trackEvent({
        event_type: 'signup_workflow',
        event_name: 'signup_success',
      });

      // AUTOMATIC LOGIN
      try {
        await login(
          {
            username: data.username,
            password: data.password,
          },
          true, // rememberMe
          true, // shouldRedirect
          callbackUrl
        );
      } catch (loginError) {
        console.warn('Auto-login after registration failed:', loginError);
        setIsSuccess(true); // Only show success state if auto-login fails
      }
    } catch (error) {
      if (error instanceof ApiError) {
        const result = error.data || {};

        if (
          handleRateLimitError(result, (msg: string) => methods.setError('root', { message: msg }))
        ) {
          return;
        }

        let errorMessage = result.message;
        if (!errorMessage && result.detail) {
          if (Array.isArray(result.detail)) {
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

        analyticsApi.trackEvent({
          event_type: 'signup_workflow',
          event_name: 'signup_error',
          event_data: { error: errorMessage || 'Registration failed' },
        });
      } else {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        console.error('Registration non-api error:', error);
        methods.setError('root', {
          message: `Registration encountered an unexpected error: ${errorMsg}. Please try again or contact support.`,
        });

        analyticsApi.trackEvent({
          event_type: 'signup_workflow',
          event_name: 'signup_network_error',
          event_data: { error: errorMsg },
        });
        setCurrentStep(2);
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
          defaultValues={{
            firstName: '',
            lastName: '',
            age: 18,
            gender: undefined,
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
            acceptTerms: false,
          }}
          className={`space-y-6 transition-opacity duration-200 ${effectiveLoading ? 'opacity-60' : ''}`}
        >
          {(methods) => (
            <>
              <StepIndicator steps={steps} currentStep={currentStep} className="mb-6" />

              {methods.formState.errors.root && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-destructive/10 border border-destructive/20 text-destructive text-xs p-3 rounded-md flex items-center"
                >
                  <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                  {methods.formState.errors.root.message}
                </motion.div>
              )}

              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStep}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  {currentStep === 0 && (
                    <PersonalStep
                      methods={methods}
                      isLoading={effectiveLoading}
                      onNext={() => handleNext(methods)}
                      handleFocus={handleFocus}
                      canProceed={validateStep(0, methods)}
                    />
                  )}
                  {currentStep === 1 && (
                    <AccountStep
                      methods={methods}
                      isLoading={effectiveLoading}
                      showPassword={showPassword}
                      setShowPassword={setShowPassword}
                      availabilityCache={availabilityCache}
                      onNext={() => handleNext(methods)}
                      onBack={handleBack}
                      handleFocus={handleFocus}
                      canProceed={validateStep(1, methods)}
                    />
                  )}
                  {currentStep === 2 && (
                    <TermsStep
                      methods={methods}
                      isLoading={effectiveLoading}
                      onBack={handleBack}
                      handleFocus={handleFocus}
                      canProceed={validateStep(2, methods)}
                      lockoutTime={lockoutTime}
                    />
                  )}
                </motion.div>
              </AnimatePresence>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="text-center text-sm text-muted-foreground pt-4"
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
          )}
        </Form>
      )}
    </AuthLayout>
  );
}
