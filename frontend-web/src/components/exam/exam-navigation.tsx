'use client';

import * as React from 'react';
import { ArrowLeft, ArrowRight, Check, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExamNavigationProps {
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
  canGoPrevious: boolean;
  canGoNext: boolean;
  isLastQuestion: boolean;
  isSubmitting?: boolean;
  className?: string;
}

export function ExamNavigation({
  onPrevious,
  onNext,
  onSubmit,
  canGoPrevious,
  canGoNext,
  isLastQuestion,
  isSubmitting = false,
  className,
}: ExamNavigationProps) {

  // Keyboard Shortcuts
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      if (e.key === 'ArrowLeft' && canGoPrevious) {
        onPrevious();
      }
      if (e.key === 'ArrowRight' && canGoNext && !isLastQuestion) {
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canGoPrevious, canGoNext, isLastQuestion, onPrevious, onNext]);

  return (
    <div className={cn("flex w-full items-center justify-between py-4", className)}>
      <button
        onClick={onPrevious}
        disabled={!canGoPrevious || isSubmitting}
        className={cn(
          "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
          "border border-slate-200 bg-white hover:bg-slate-100 text-slate-900",
          "dark:border-slate-800 dark:bg-slate-950 dark:hover:bg-slate-800 dark:text-slate-100",
          "disabled:opacity-50 disabled:pointer-events-none"
        )}
      >
        <ArrowLeft className="h-4 w-4" />
        Previous
      </button>

      {isLastQuestion ? (
        <button
          onClick={onSubmit}
          disabled={isSubmitting}
          className={cn(
            "flex items-center gap-2 rounded-lg px-6 py-2 text-sm font-medium text-white transition-colors",
            "bg-green-600 hover:bg-green-700",
            "disabled:opacity-50 disabled:pointer-events-none"
          )}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              Submit Exam
              <Check className="h-4 w-4" />
            </>
          )}
        </button>
      ) : (
        <button
          onClick={onNext}
          disabled={!canGoNext || isSubmitting}
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors",
            "bg-blue-600 hover:bg-blue-700",
            "disabled:opacity-50 disabled:pointer-events-none"
          )}
        >
          Next
          <ArrowRight className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}