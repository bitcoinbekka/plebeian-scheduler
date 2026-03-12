#!/usr/bin/env python3
"""
Add a new post to the scheduling queue
"""

import json
import sys
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid


def load_queue(queue_path: Path) -> dict:
    """Load the post queue"""
    if not queue_path.exists():
        return {"posts": []}

    try:
        with open(queue_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading queue: {e}")
        return {"posts": []}


def save_queue(queue: dict, queue_path: Path):
    """Save the post queue"""
    try:
        with open(queue_path, 'w') as f:
            json.dump(queue, f, indent=2)
        print(f"Queue saved to {queue_path}")
    except Exception as e:
        print(f"Error saving queue: {e}")


def parse_schedule_time(schedule_str: str) -> str:
    """Parse schedule time string to ISO format

    Supports:
    - ISO format: 2026-03-12T10:00:00Z
    - Relative: "2 hours", "1 day", "tomorrow 9am"
    """
    # If already ISO format, return as-is
    if 'T' in schedule_str:
        return schedule_str

    # Handle relative times
    schedule_str = schedule_str.lower().strip()

    if schedule_str.startswith('+'):
        # +2h, +30m, +1d format
        try:
            amount = int(schedule_str[1:-1])
            unit = schedule_str[-1]

            if unit == 'h':
                dt = datetime.now(timezone.utc) + timedelta(hours=amount)
            elif unit == 'm':
                dt = datetime.now(timezone.utc) + timedelta(minutes=amount)
            elif unit == 'd':
                dt = datetime.now(timezone.utc) + timedelta(days=amount)
            else:
                raise ValueError(f"Unknown unit: {unit}")

            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            print(f"Error parsing relative time: {e}")
            sys.exit(1)

    # Try parsing natural language (simple cases)
    now = datetime.now(timezone.utc)

    if 'tomorrow' in schedule_str:
        dt = now + timedelta(days=1)
        if 'am' in schedule_str:
            hour = int(schedule_str.split()[1].replace('am', ''))
            dt = dt.replace(hour=hour % 12, minute=0)
        elif 'pm' in schedule_str:
            hour = int(schedule_str.split()[1].replace('pm', ''))
            dt = dt.replace(hour=(hour % 12) + 12, minute=0)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Default: try parsing as-is
    try:
        dt = datetime.fromisoformat(schedule_str)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        print(f"Could not parse schedule time: {schedule_str}")
        print("Use format like: 2026-03-12T10:00:00Z or +2h")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Add a post to the scheduling queue")
    parser.add_argument('--platform', '-p', choices=['nostr', 'x', 'both'],
                       default='both', help='Platform to post to')
    parser.add_argument('--type', '-t', choices=['short', 'long'],
                       default='short', help='Post type (for Nostr)')
    parser.add_argument('--content', '-c', required=True, help='Post content')
    parser.add_argument('--title', help='Post title (for long-form)')
    parser.add_argument('--schedule', '-s', required=True,
                       help='Schedule time (ISO format or relative like +2h)')
    parser.add_argument('--tags', nargs='*', help='Hashtags for Nostr')
    parser.add_argument('--image', '-i', help='Path to image file or URL')
    parser.add_argument('--queue', '-q', default='queue.json', help='Path to queue file')
    parser.add_argument('--id', help='Custom post ID (auto-generated if not provided)')

    args = parser.parse_args()

    # Parse schedule time
    scheduled_at = parse_schedule_time(args.schedule)

    # Generate post ID
    post_id = args.id or f"post-{uuid.uuid4().hex[:8]}"

    # Build post object
    post = {
        "id": post_id,
        "platform": args.platform,
        "content": args.content,
        "scheduled_at": scheduled_at,
        "posted": False,
        "posted_at": None
    }

    # Add optional fields
    if args.type == 'long':
        post['type'] = 'long-form'  # Convert 'long' to 'long-form' for consistency
        if args.title:
            post['title'] = args.title
        elif not args.title and args.platform == 'nostr':
            print("Warning: Long-form post should have a title")

    if args.tags:
        post['tags'] = args.tags

    if args.image:
        post['image'] = args.image

    # Load, add, save
    queue_path = Path(args.queue)
    queue = load_queue(queue_path)
    queue['posts'].append(post)
    save_queue(queue, queue_path)

    # Show confirmation
    print(f"\n✓ Post added to queue:")
    print(f"  ID: {post_id}")
    print(f"  Platform: {args.platform}")
    print(f"  Scheduled: {scheduled_at}")
    print(f"  Content preview: {args.content[:60]}{'...' if len(args.content) > 60 else ''}")

    if args.type == 'long':
        print(f"  Title: {args.title or '(no title)'}")
    if args.tags:
        print(f"  Tags: {', '.join(args.tags)}")
    if args.image:
        print(f"  Image: {args.image}")


if __name__ == '__main__':
    main()
