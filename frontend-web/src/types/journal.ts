export interface JournalEntry {
    id: number;
    content: string;
    sentiment_score?: number;
    entry_date: string;
    tags?: string[];
    sleep_hours?: number;
    sleep_quality?: number;
    energy_level?: number;
    stress_level?: number;
    mood_score?: number; // 1-10 rating
}

export type TimeRange = '7d' | '14d' | '30d';
