import { useMemo } from 'react';
import { startOfDay, differenceInCalendarDays, subDays, format } from 'date-fns';
import type { NostrEvent } from '@nostrify/nostrify';

export interface PostingStreakData {
  /** Current consecutive days with at least 1 post */
  currentStreak: number;
  /** Longest ever streak */
  longestStreak: number;
  /** Posts this week (Mon-Sun) */
  postsThisWeek: number;
  /** Weekly goal (default 5) */
  weeklyGoal: number;
  /** Whether the user posted today */
  postedToday: boolean;
  /** Whether the streak is at risk (posted yesterday but not today) */
  streakAtRisk: boolean;
  /** Last 14 days activity grid: true = posted, false = didn't */
  activityGrid: { date: string; posted: boolean; count: number }[];
  /** Total posts in the last 30 days */
  last30Days: number;
  /** Average posts per week (last 4 weeks) */
  avgPerWeek: number;
}

const WEEKLY_GOAL_KEY = 'plebeian-scheduler:weekly-goal';

export function getWeeklyGoal(): number {
  try {
    const stored = localStorage.getItem(WEEKLY_GOAL_KEY);
    return stored ? parseInt(stored) : 5;
  } catch {
    return 5;
  }
}

export function setWeeklyGoal(goal: number): void {
  localStorage.setItem(WEEKLY_GOAL_KEY, String(goal));
}

/**
 * Compute posting streak data from relay posts.
 * Only counts kind 1 and kind 30023 (not reposts).
 */
export function usePostingStreak(relayPosts: NostrEvent[] | undefined): PostingStreakData {
  return useMemo(() => {
    const weeklyGoal = getWeeklyGoal();

    if (!relayPosts || relayPosts.length === 0) {
      return {
        currentStreak: 0,
        longestStreak: 0,
        postsThisWeek: 0,
        weeklyGoal,
        postedToday: false,
        streakAtRisk: false,
        activityGrid: buildEmptyGrid(),
        last30Days: 0,
        avgPerWeek: 0,
      };
    }

    // Only count original posts (not reposts)
    const originalPosts = relayPosts.filter(e => e.kind === 1 || e.kind === 30023);

    // Build a set of days (YYYY-MM-DD) that had at least one post
    const postDays = new Set<string>();
    const dayPostCounts = new Map<string, number>();

    for (const event of originalPosts) {
      const dayKey = format(startOfDay(new Date(event.created_at * 1000)), 'yyyy-MM-dd');
      postDays.add(dayKey);
      dayPostCounts.set(dayKey, (dayPostCounts.get(dayKey) || 0) + 1);
    }

    const today = startOfDay(new Date());
    const todayKey = format(today, 'yyyy-MM-dd');
    const postedToday = postDays.has(todayKey);

    // Calculate current streak (consecutive days ending today or yesterday)
    let currentStreak = 0;
    let checkDay = postedToday ? today : subDays(today, 1);

    // If didn't post today AND didn't post yesterday, streak is 0
    if (!postedToday && !postDays.has(format(subDays(today, 1), 'yyyy-MM-dd'))) {
      currentStreak = 0;
    } else {
      while (postDays.has(format(checkDay, 'yyyy-MM-dd'))) {
        currentStreak++;
        checkDay = subDays(checkDay, 1);
      }
    }

    // Calculate longest streak
    let longestStreak = 0;
    const sortedDays = Array.from(postDays).sort();
    if (sortedDays.length > 0) {
      let streak = 1;
      for (let i = 1; i < sortedDays.length; i++) {
        const prev = new Date(sortedDays[i - 1]);
        const curr = new Date(sortedDays[i]);
        if (differenceInCalendarDays(curr, prev) === 1) {
          streak++;
        } else {
          longestStreak = Math.max(longestStreak, streak);
          streak = 1;
        }
      }
      longestStreak = Math.max(longestStreak, streak);
    }

    // Posts this week (Monday through Sunday)
    const dayOfWeek = today.getDay(); // 0=Sun, 1=Mon, ...
    const mondayOffset = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    const mondayStart = subDays(today, mondayOffset);
    let postsThisWeek = 0;
    for (let i = 0; i <= mondayOffset; i++) {
      const day = format(subDays(today, mondayOffset - i), 'yyyy-MM-dd');
      postsThisWeek += dayPostCounts.get(day) || 0;
    }

    // Streak at risk: posted yesterday but not today
    const yesterdayKey = format(subDays(today, 1), 'yyyy-MM-dd');
    const streakAtRisk = !postedToday && postDays.has(yesterdayKey);

    // Activity grid (last 14 days)
    const activityGrid: { date: string; posted: boolean; count: number }[] = [];
    for (let i = 13; i >= 0; i--) {
      const d = subDays(today, i);
      const key = format(d, 'yyyy-MM-dd');
      activityGrid.push({
        date: format(d, 'EEE'),
        posted: postDays.has(key),
        count: dayPostCounts.get(key) || 0,
      });
    }

    // Last 30 days count
    let last30Days = 0;
    for (let i = 0; i < 30; i++) {
      const key = format(subDays(today, i), 'yyyy-MM-dd');
      last30Days += dayPostCounts.get(key) || 0;
    }

    // Average per week (last 4 weeks)
    const avgPerWeek = Math.round((last30Days / 4) * 10) / 10;

    return {
      currentStreak,
      longestStreak,
      postsThisWeek,
      weeklyGoal,
      postedToday,
      streakAtRisk,
      activityGrid,
      last30Days,
      avgPerWeek,
    };
  }, [relayPosts]);
}

function buildEmptyGrid() {
  const today = startOfDay(new Date());
  const grid: { date: string; posted: boolean; count: number }[] = [];
  for (let i = 13; i >= 0; i--) {
    grid.push({ date: format(subDays(today, i), 'EEE'), posted: false, count: 0 });
  }
  return grid;
}
