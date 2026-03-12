#!/usr/bin/env python3
"""
Manage the post scheduling queue
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def load_queue(queue_path: Path) -> dict:
    """Load the post queue"""
    if not queue_path.exists():
        print("Queue file does not exist")
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
    except Exception as e:
        print(f"Error saving queue: {e}")


def list_posts(queue: dict, show_all: bool = False):
    """List all posts in the queue"""
    posts = queue['posts']

    if not posts:
        print("Queue is empty")
        return

    print(f"\n{'='*70}")
    print(f"Post Queue ({len(posts)} total)")
    print(f"{'='*70}\n")

    for post in posts:
        if not show_all and post.get('posted'):
            continue

        status = "✓ POSTED" if post.get('posted') else "⏳ SCHEDULED"
        platform = post.get('platform', 'both').upper()
        post_type = post.get('type', 'short')
        scheduled = post.get('scheduled_at', 'N/A')
        posted_at = post.get('posted_at', '')

        print(f"{status} | {platform} | {post_type}")
        print(f"  ID: {post.get('id')}")
        print(f"  Scheduled: {scheduled}")
        if posted_at:
            print(f"  Posted: {posted_at}")

        content = post.get('content', '')
        preview = content[:80] + '...' if len(content) > 80 else content
        print(f"  Content: {preview}")

        if post.get('title'):
            print(f"  Title: {post.get('title')}")

        if post.get('tags'):
            print(f"  Tags: {', '.join(post.get('tags'))}")

        print()


def view_post(queue: dict, post_id: str):
    """View details of a specific post"""
    for post in queue['posts']:
        if post.get('id') == post_id:
            print(f"\n{'='*70}")
            print(f"Post Details: {post_id}")
            print(f"{'='*70}\n")
            print(f"Platform: {post.get('platform')}")
            print(f"Type: {post.get('type', 'short')}")
            print(f"Scheduled: {post.get('scheduled_at')}")
            print(f"Status: {'POSTED' if post.get('posted') else 'SCHEDULED'}")

            if post.get('title'):
                print(f"\nTitle: {post.get('title')}")

            print(f"\nContent:\n{post.get('content')}")

            if post.get('tags'):
                print(f"\nTags: {', '.join(post.get('tags'))}")

            if post.get('posted_at'):
                print(f"\nPosted at: {post.get('posted_at')}")
            return

    print(f"Post not found: {post_id}")


def delete_post(queue: dict, post_id: str, queue_path: Path):
    """Delete a post from the queue"""
    original_count = len(queue['posts'])
    queue['posts'] = [p for p in queue['posts'] if p.get('id') != post_id]

    if len(queue['posts']) < original_count:
        save_queue(queue, queue_path)
        print(f"Post deleted: {post_id}")
    else:
        print(f"Post not found: {post_id}")


def reschedule_post(queue: dict, post_id: str, new_time: str, queue_path: Path):
    """Reschedule a post"""
    found = False

    for post in queue['posts']:
        if post.get('id') == post_id:
            post['scheduled_at'] = new_time
            found = True
            break

    if found:
        save_queue(queue, queue_path)
        print(f"Post rescheduled: {post_id} -> {new_time}")
    else:
        print(f"Post not found: {post_id}")


def mark_posted(queue: dict, post_id: str, queue_path: Path):
    """Manually mark a post as posted"""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    found = False

    for post in queue['posts']:
        if post.get('id') == post_id:
            post['posted'] = True
            post['posted_at'] = now
            found = True
            break

    if found:
        save_queue(queue, queue_path)
        print(f"Post marked as posted: {post_id}")
    else:
        print(f"Post not found: {post_id}")


def main():
    parser = argparse.ArgumentParser(description="Manage the post scheduling queue")
    parser.add_argument('--queue', '-q', default='queue.json', help='Path to queue file')

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # List command
    list_parser = subparsers.add_parser('list', help='List posts in queue')
    list_parser.add_argument('--all', '-a', action='store_true', help='Show all posts including posted')

    # View command
    view_parser = subparsers.add_parser('view', help='View a specific post')
    view_parser.add_argument('post_id', help='Post ID to view')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a post')
    delete_parser.add_argument('post_id', help='Post ID to delete')

    # Reschedule command
    reschedule_parser = subparsers.add_parser('reschedule', help='Reschedule a post')
    reschedule_parser.add_argument('post_id', help='Post ID to reschedule')
    reschedule_parser.add_argument('time', help='New scheduled time (ISO format)')

    # Mark posted command
    mark_parser = subparsers.add_parser('mark-posted', help='Mark a post as posted')
    mark_parser.add_argument('post_id', help='Post ID to mark')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    queue_path = Path(args.queue)
    queue = load_queue(queue_path)

    if args.action == 'list':
        list_posts(queue, show_all=args.all)
    elif args.action == 'view':
        view_post(queue, args.post_id)
    elif args.action == 'delete':
        delete_post(queue, args.post_id, queue_path)
    elif args.action == 'reschedule':
        reschedule_post(queue, args.post_id, args.time, queue_path)
    elif args.action == 'mark-posted':
        mark_posted(queue, args.post_id, queue_path)


if __name__ == '__main__':
    main()
