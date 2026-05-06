import { useMemo } from 'react';
import type { NostrEvent } from '@nostrify/nostrify';
import type { PostEngagement } from './usePostEngagement';

export interface SmartHashtag {
  /** Hashtag without # prefix */
  tag: string;
  /** Number of posts that used this hashtag */
  postCount: number;
  /** Average engagement score per post with this hashtag */
  avgEngagement: number;
  /** Total sats earned from posts with this hashtag */
  totalSats: number;
  /** Composite ranking score */
  score: number;
}

/**
 * Analyze user's published posts and their engagement to suggest
 * hashtags that correlate with the highest engagement.
 */
export function useSmartHashtags(
  relayPosts: NostrEvent[] | undefined,
  engagementMap: Map<string, PostEngagement> | undefined,
): SmartHashtag[] {
  return useMemo(() => {
    if (!relayPosts || !engagementMap || relayPosts.length === 0) return [];

    // Extract hashtags from post content and track engagement
    const hashtagStats = new Map<string, {
      posts: number;
      totalReactions: number;
      totalZaps: number;
      totalSats: number;
    }>();

    for (const event of relayPosts) {
      // Only analyze kind 1 posts (not reposts or articles)
      if (event.kind !== 1) continue;

      // Extract hashtags from content
      const hashtags = new Set<string>();
      const matches = event.content.match(/#(\w{2,})/g);
      if (matches) {
        for (const m of matches) {
          hashtags.add(m.slice(1).toLowerCase());
        }
      }

      // Also check t tags
      for (const tag of event.tags) {
        if (tag[0] === 't' && tag[1]) {
          hashtags.add(tag[1].toLowerCase());
        }
      }

      if (hashtags.size === 0) continue;

      const eng = engagementMap.get(event.id);
      const reactions = eng?.reactionCount || 0;
      const zaps = eng?.zapCount || 0;
      const sats = eng?.totalSats || 0;

      for (const tag of hashtags) {
        const existing = hashtagStats.get(tag) || { posts: 0, totalReactions: 0, totalZaps: 0, totalSats: 0 };
        existing.posts++;
        existing.totalReactions += reactions;
        existing.totalZaps += zaps;
        existing.totalSats += sats;
        hashtagStats.set(tag, existing);
      }
    }

    // Calculate scores and sort
    const results: SmartHashtag[] = [];
    for (const [tag, stats] of hashtagStats) {
      const avgEngagement = stats.posts > 0
        ? (stats.totalReactions + stats.totalZaps * 3) / stats.posts
        : 0;

      // Score: combination of frequency, engagement, and sats
      const score = (avgEngagement * 2) + (stats.posts * 0.5) + (stats.totalSats * 0.01);

      results.push({
        tag,
        postCount: stats.posts,
        avgEngagement: Math.round(avgEngagement * 10) / 10,
        totalSats: stats.totalSats,
        score,
      });
    }

    // Sort by score descending, take top 20
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, 20);
  }, [relayPosts, engagementMap]);
}
