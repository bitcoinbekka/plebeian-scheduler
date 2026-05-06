import { useMemo } from 'react';
import { useCurrentUser } from './useCurrentUser';
import { useMyPublishedPosts } from './useMyPublishedPosts';
import { useBatchEngagement } from './usePostEngagement';
import type { Lead, LeadInteraction } from '@/lib/leadTypes';
import { calculateLeadScore } from '@/lib/leadTypes';

/**
 * Build a ranked lead list from the shared engagement data.
 *
 * Uses the same useBatchEngagement hook as Dashboard and Analytics,
 * ensuring consistent numbers across all pages.
 */
export function useLeadTracker() {
  const { user } = useCurrentUser();
  const { data: myPosts, isLoading: postsLoading } = useMyPublishedPosts();

  const postIds = useMemo(
    () => (myPosts || []).map(e => e.id),
    [myPosts],
  );

  // Use the same shared engagement query as Dashboard and Analytics
  const { data: engagementMap, isLoading: engagementLoading } = useBatchEngagement(postIds);

  // Build leads from the shared engagement data
  const leads = useMemo(() => {
    if (!user || !engagementMap || engagementMap.size === 0) return [];

    // Build a map of pubkey -> interactions from the raw events in engagementMap
    const leadMap = new Map<string, {
      reactions: number;
      zaps: number;
      sats: number;
      postIds: Set<string>;
      firstSeen: number;
      lastSeen: number;
      interactions: LeadInteraction[];
    }>();

    const ensureLead = (pubkey: string) => {
      if (!leadMap.has(pubkey)) {
        leadMap.set(pubkey, {
          reactions: 0,
          zaps: 0,
          sats: 0,
          postIds: new Set(),
          firstSeen: Infinity,
          lastSeen: 0,
          interactions: [],
        });
      }
      return leadMap.get(pubkey)!;
    };

    // Process all engagement events from the shared map
    for (const [eventId, eng] of engagementMap) {
      // Process reactions
      for (const event of eng.reactionEvents) {
        if (event.pubkey === user.pubkey) continue;
        const lead = ensureLead(event.pubkey);
        lead.reactions++;
        lead.postIds.add(eventId);
        lead.firstSeen = Math.min(lead.firstSeen, event.created_at);
        lead.lastSeen = Math.max(lead.lastSeen, event.created_at);
        lead.interactions.push({
          eventId: event.id,
          type: 'reaction',
          emoji: event.content === '' || event.content === '+' ? '❤️' : event.content,
          targetEventId: eventId,
          timestamp: event.created_at,
        });
      }

      // Process zaps
      for (const zap of eng.zapEvents) {
        const descTag = zap.tags.find(([n]) => n === 'description')?.[1];
        if (!descTag) continue;
        let zapperPubkey: string | null = null;
        try {
          const zapReq = JSON.parse(descTag);
          zapperPubkey = zapReq.pubkey;
        } catch { continue; }
        if (!zapperPubkey || zapperPubkey === user.pubkey) continue;

        let sats = 0;
        const amountTag = zap.tags.find(([n]) => n === 'amount')?.[1];
        if (amountTag) {
          sats = Math.floor(parseInt(amountTag) / 1000);
        }

        const lead = ensureLead(zapperPubkey);
        lead.zaps++;
        lead.sats += sats;
        lead.postIds.add(eventId);
        lead.firstSeen = Math.min(lead.firstSeen, zap.created_at);
        lead.lastSeen = Math.max(lead.lastSeen, zap.created_at);
        lead.interactions.push({
          eventId: zap.id,
          type: 'zap',
          sats,
          targetEventId: eventId,
          timestamp: zap.created_at,
        });
      }
    }

    // Convert map to sorted Lead array
    const now = Math.floor(Date.now() / 1000);
    const twoWeeksAgo = now - (14 * 86400);
    const fourWeeksAgo = now - (28 * 86400);

    const result: Lead[] = [];
    for (const [pubkey, data] of leadMap) {
      const postsInteracted = data.postIds.size;
      const daysSinceLastSeen = Math.floor((now - data.lastSeen) / 86400);

      const recentInteractions = data.interactions.filter(i => i.timestamp > twoWeeksAgo).length;
      const olderInteractions = data.interactions.filter(i => i.timestamp > fourWeeksAgo && i.timestamp <= twoWeeksAgo).length;
      let trend: Lead['trend'] = 'stable';
      if (recentInteractions > olderInteractions + 1) trend = 'rising';
      else if (recentInteractions < olderInteractions - 1) trend = 'cooling';

      const lead: Lead = {
        pubkey,
        totalReactions: data.reactions,
        totalZaps: data.zaps,
        totalSats: data.sats,
        postsInteracted,
        firstSeen: data.firstSeen === Infinity ? now : data.firstSeen,
        lastSeen: data.lastSeen || now,
        interactions: data.interactions.sort((a, b) => b.timestamp - a.timestamp),
        daysSinceLastSeen,
        isRepeatEngager: postsInteracted >= 3,
        trend,
        score: 0,
      };
      lead.score = calculateLeadScore(lead);
      result.push(lead);
    }

    result.sort((a, b) => b.score - a.score);
    return result;
  }, [user, engagementMap]);

  return {
    leads,
    isLoading: postsLoading || engagementLoading,
    postCount: postIds.length,
  };
}
