#!/usr/bin/env python3
"""
Test runner for the Plebeian Scheduler (no external dependencies required)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_queue(queue_path: str = "queue.json") -> dict:
    """Load the post queue"""
    with open(queue_path, 'r') as f:
        return json.load(f)


def save_queue(queue: dict, queue_path: str = "queue.json"):
    """Save the post queue"""
    with open(queue_path, 'w') as f:
        json.dump(queue, f, indent=2)


def simulate_post(post: dict):
    """Simulate posting to a platform"""
    platform = post.get('platform', 'both')
    content = post.get('content', '')
    post_type = post.get('type', 'short')

    print(f"\n{'='*60}")
    print(f"📤 SIMULATING POST")
    print(f"{'='*60}")
    print(f"ID: {post.get('id')}")
    print(f"Platform: {platform.upper()}")
    print(f"Type: {post_type}")
    print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")

    if post.get('title'):
        print(f"Title: {post.get('title')}")

    if post.get('tags'):
        print(f"Tags: {', '.join(post.get('tags'))}")

    return True


def process_due_posts(queue_path: str = "queue.json", dry_run: bool = True):
    """Process posts that are due"""
    queue = load_queue(queue_path)
    now = datetime.now(timezone.utc)

    print(f"\n🕐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"📋 Total posts in queue: {len(queue['posts'])}")

    due_count = 0
    for post in queue['posts']:
        if post.get('posted', False):
            continue

        scheduled_time_str = post.get('scheduled_at')
        if not scheduled_time_str:
            continue

        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            time_until = (scheduled_time - now).total_seconds() / 60  # minutes

            print(f"\n  • {post.get('id')}: {'✅ DUE' if time_until <= 0 else f'⏳ {int(time_until)} min away'}")

            if time_until <= 0:
                if dry_run:
                    simulate_post(post)
                    print(f"⚠️  DRY RUN: Would mark as posted")
                else:
                    simulate_post(post)
                    post['posted'] = True
                    post['posted_at'] = now.isoformat()
                    print(f"✅ Posted!")
                due_count += 1

        except Exception as e:
            print(f"  ❌ Error processing {post.get('id')}: {e}")

    if not dry_run and due_count > 0:
        save_queue(queue, queue_path)
        print(f"\n💾 Queue saved")

    print(f"\n📊 Processed {due_count} due posts")

    if dry_run:
        print(f"ℹ️  Dry run mode - no actual changes made")

    return due_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test runner for Plebeian Scheduler")
    parser.add_argument('--queue', '-q', default='queue.json', help='Path to queue file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--list', '-l', action='store_true', help='List all posts')

    args = parser.parse_args()

    if args.list:
        queue = load_queue(args.queue)
        print(f"\n📋 Queue Contents ({len(queue['posts'])} posts):\n")

        for i, post in enumerate(queue['posts'], 1):
            status = '✅ POSTED' if post.get('posted') else '⏳ SCHEDULED'
            platform = post.get('platform', 'both').upper()
            print(f"{i}. {status} | {platform}")
            print(f"   ID: {post.get('id')}")
            print(f"   Scheduled: {post.get('scheduled_at')}")
            print(f"   Content: {post.get('content', '')[:60]}...")
            print()
        return

    print("🚀 Plebeian Scheduler Test Runner")
    print("=" * 40)

    due = process_due_posts(args.queue, args.dry_run)

    if due == 0:
        print("\n✨ No posts due right now. Check back later!")


if __name__ == '__main__':
    main()
