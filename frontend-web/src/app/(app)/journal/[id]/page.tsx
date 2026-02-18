'use client';

import { useParams, useRouter } from 'next/navigation';
import { useApi } from '@/hooks/useApi';
import { journalApi, JournalEntry } from '@/lib/api/journal';
import { ErrorDisplay, Skeleton } from '@/components/common';
import { Button, Card, CardContent } from '@/components/ui';
import {
  ArrowLeft,
  Calendar,
  Tag,
  Edit,
  Trash2,
  Smile,
  Meh,
  Frown,
} from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';

const MOOD_ICONS = {
  positive: { icon: Smile, color: 'text-green-500', bg: 'bg-green-500/10' },
  neutral: { icon: Meh, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  negative: { icon: Frown, color: 'text-red-500', bg: 'bg-red-500/10' },
};

function getMoodCategory(score?: number) {
  if (score == null) return 'neutral';
  if (score >= 60) return 'positive';
  if (score >= 40) return 'neutral';
  return 'negative';
}

export default function JournalEntryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string);

  const {
    data: entry,
    loading,
    error,
    refetch,
  } = useApi({
    apiFn: () => journalApi.getEntry(id),
    deps: [id],
  });

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this entry?')) {
      try {
        await journalApi.deleteEntry(id);
        router.push('/journal');
      } catch {
        // TODO: toast
      }
    }
  };

  const formatDate = (value: string) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card className="rounded-[2rem]">
          <CardContent className="p-8 space-y-4">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return <ErrorDisplay message={error} onRetry={refetch} />;
  }

  if (!entry) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <h1 className="text-2xl font-bold">Entry not found</h1>
        <Link href="/journal">
          <Button className="mt-4">Back to Journal</Button>
        </Link>
      </div>
    );
  }

  const mood = getMoodCategory(entry.sentiment_score ?? entry.mood_score);
  const MoodIcon = MOOD_ICONS[mood].icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link href="/journal">
          <Button variant="ghost" className="rounded-full">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Journal
          </Button>
        </Link>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-full">
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button
            variant="outline"
            onClick={handleDelete}
            className="rounded-full text-red-500 hover:text-red-600"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Entry Card */}
      <Card className="rounded-[2rem] border-none bg-background/60 backdrop-blur-xl shadow-xl shadow-black/5">
        <CardContent className="p-8 space-y-6">
          {/* Title & Mood */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold mb-2">
                {entry.title || 'Untitled Entry'}
              </h1>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <div className={`p-2 rounded-xl ${MOOD_ICONS[mood].bg}`}>
                  <MoodIcon className={`w-4 h-4 ${MOOD_ICONS[mood].color}`} />
                </div>
                <Calendar className="w-4 h-4" />
                {formatDate(entry.timestamp)}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="prose prose-lg max-w-none">
            <p className="text-foreground leading-relaxed whitespace-pre-wrap">
              {entry.content}
            </p>
          </div>

          {/* Tags */}
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-4 border-t">
              {entry.tags.map((tag) => (
                <span
                  key={tag}
                  className="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium"
                >
                  <Tag className="w-3 h-3" />
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}