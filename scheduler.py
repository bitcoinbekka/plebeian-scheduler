#!/usr/bin/env python3
"""
Plebeian Social Media Scheduler
Posts scheduled content to Nostr and X/Twitter
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging

from dotenv import load_dotenv

# Try importing optional dependencies
try:
    from nostr.key import PrivateKey
    from nostr.event import Event, EventKind
    from nostr.relay_manager import RelayManager
    NOSTR_AVAILABLE = True
except ImportError:
    NOSTR_AVAILABLE = False
    print("Warning: nostr package not installed. Nostr posting disabled.")

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Warning: tweepy package not installed. X posting disabled.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests package not installed. Image upload disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration from environment variables"""

    def __init__(self):
        load_dotenv()

        self.nsec = os.getenv('NOSTR_PRIVATE_KEY', '')
        self.nostr_relays = os.getenv('NOSTR_RELAYS', '').split(',')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.schedule_interval = int(os.getenv('SCHEDULE_INTERVAL', '300'))

        # X/Twitter credentials
        self.x_api_key = os.getenv('X_API_KEY', '')
        self.x_api_secret = os.getenv('X_API_SECRET', '')
        self.x_access_token = os.getenv('X_ACCESS_TOKEN', '')
        self.x_access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET', '')
        self.x_bearer_token = os.getenv('X_BEARER_TOKEN', '')

        # Image hosting
        self.nostr_build_url = os.getenv('NOSTR_BUILD_URL', 'https://nostr.build')


class ImageUploader:
    """Upload images to Nostr-friendly hosts"""

    def __init__(self, config: Config):
        self.config = config

    def upload_to_nostr_build(self, image_path: str) -> Optional[str]:
        """Upload an image to nostr.build and return the URL"""
        if not REQUESTS_AVAILABLE:
            logger.warning("requests not available, cannot upload images")
            return None

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would upload image: {image_path}")
            return f"https://nostr.build/dummy-{os.path.basename(image_path)}"

        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None

        try:
            url = f"{self.config.nostr_build_url}/api/v2/upload/blossom"
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                response = requests.post(url, files=files, timeout=30)

            if response.status_code == 200:
                data = response.json()
                image_url = data.get('url') or data.get(0, {}).get('url')
                if image_url:
                    logger.info(f"Image uploaded to nostr.build: {image_url}")
                    return image_url
                else:
                    logger.error(f"Upload succeeded but no URL in response: {data}")
            else:
                logger.error(f"Failed to upload image: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Error uploading image: {e}")

        return None

    def resolve_image_url(self, image_input: str) -> Optional[str]:
        """Resolve an image to a URL

        If image_input is a URL, return it as-is.
        If it's a local file path, upload to nostr.build.
        """
        # Check if it's already a URL
        if image_input.startswith(('http://', 'https://')):
            return image_input

        # Otherwise, try to upload it
        return self.upload_to_nostr_build(image_input)


class NostrPoster:
    """Post content to Nostr"""

    def __init__(self, config: Config, image_uploader: ImageUploader = None):
        self.config = config
        self.private_key = None
        self.relay_manager = None
        self.image_uploader = image_uploader or ImageUploader(config)

        if NOSTR_AVAILABLE and config.nsec:
            try:
                self.private_key = PrivateKey.from_nsec(config.nsec)
                self.relay_manager = RelayManager()
                for relay_url in config.nostr_relays:
                    relay_url = relay_url.strip()
                    if relay_url:
                        self.relay_manager.add_relay(relay_url)
                logger.info("Nostr configured successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Nostr: {e}")
                self.private_key = None

    def post_note(self, content: str, tags: List[str] = None, image: str = None) -> Optional[str]:
        """Post a short-form note (kind 1)

        Args:
            content: The text content of the note
            tags: Hashtag tags
            image: Path to local image or URL (will be uploaded if local)
        """
        if not self.private_key:
            logger.warning("Nostr not configured, skipping post")
            return None

        # Handle image upload
        image_url = None
        if image:
            image_url = self.image_uploader.resolve_image_url(image)
            if image_url:
                # Prepend image to content
                content = f"{image_url}\n\n{content}"
                logger.info(f"Image attached: {image_url}")

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Nostr note: {content[:100]}...")
            if image_url:
                logger.info(f"[DRY RUN] Image: {image_url}")
            return "dry-run-id"

        try:
            event = Event(
                content=content,
                kind=EventKind.TEXT_NOTE,
                public_key=self.private_key.public_key.hex()
            )

            if tags:
                for tag in tags:
                    event.tags.append(['t', tag])

            # Add NIP-94 tags for image if present
            if image_url:
                # Add url tag pointing to the image
                event.tags.append(['url', image_url])
                # Add mime type tag (assuming common formats)
                if image_url.lower().endswith(('.png', '.PNG')):
                    event.tags.append(['m', 'image/png'])
                elif image_url.lower().endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                    event.tags.append(['m', 'image/jpeg'])
                elif image_url.lower().endswith(('.gif', '.GIF')):
                    event.tags.append(['m', 'image/gif'])
                elif image_url.lower().endswith(('.webp', '.WEBP')):
                    event.tags.append(['m', 'image/webp'])

            self.private_key.sign_event(event)

            # Publish to relays
            event_ids = []
            for relay in self.relay_manager.relays.values():
                relay.publish_event(event)
                event_ids.append(event.id)

            logger.info(f"Nostr note posted: {event.id}")
            return event.id

        except Exception as e:
            logger.error(f"Failed to post Nostr note: {e}")
            return None

    def post_long_form(self, title: str, content: str, tags: List[str] = None, image: str = None) -> Optional[str]:
        """Post a long-form article (kind 30023)

        Args:
            title: Article title
            content: Article content
            tags: Hashtag tags
            image: Path to local image or URL (will be uploaded if local)
        """
        if not self.private_key:
            logger.warning("Nostr not configured, skipping long-form post")
            return None

        # Handle image upload
        image_url = None
        if image:
            image_url = self.image_uploader.resolve_image_url(image)
            if image_url:
                # Add image at top of content
                content = f"\n\n![{title or 'Image'}]({image_url})\n\n{content}"
                logger.info(f"Image attached to long-form: {image_url}")

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Nostr long-form: {title}")
            if image_url:
                logger.info(f"[DRY RUN] Image: {image_url}")
            return "dry-run-id"

        try:
            # Format as Markdown with title
            formatted_content = f"# {title}\n\n{content}"

            event = Event(
                content=formatted_content,
                kind=EventKind.LONG_FORM,
                public_key=self.private_key.public_key.hex()
            )

            # Add title tag
            event.tags.append(['title', title])
            event.tags.append(['published_at', str(int(datetime.now().timestamp()))])

            # Add NIP-94 tags for image if present
            if image_url:
                event.tags.append(['url', image_url])
                if image_url.lower().endswith(('.png', '.PNG')):
                    event.tags.append(['m', 'image/png'])
                elif image_url.lower().endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                    event.tags.append(['m', 'image/jpeg'])
                elif image_url.lower().endswith(('.gif', '.GIF')):
                    event.tags.append(['m', 'image/gif'])
                elif image_url.lower().endswith(('.webp', '.WEBP')):
                    event.tags.append(['m', 'image/webp'])

            if tags:
                for tag in tags:
                    event.tags.append(['t', tag])

            self.private_key.sign_event(event)

            # Publish to relays
            for relay in self.relay_manager.relays.values():
                relay.publish_event(event)

            logger.info(f"Nostr long-form posted: {event.id}")
            return event.id

        except Exception as e:
            logger.error(f"Failed to post Nostr long-form: {e}")
            return None


class XPoster:
    """Post content to X/Twitter"""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.api = None  # For media uploads (v1.1)

        if TWEEPY_AVAILABLE and all([config.x_api_key, config.x_access_token]):
            try:
                # API v2 client
                self.client = tweepy.Client(
                    consumer_key=config.x_api_key,
                    consumer_secret=config.x_api_secret,
                    access_token=config.x_access_token,
                    access_token_secret=config.x_access_token_secret,
                    bearer_token=config.x_bearer_token,
                    wait_on_rate_limit=True
                )

                # API v1.1 client for media uploads
                auth = tweepy.OAuth1UserHandler(
                    config.x_api_key,
                    config.x_api_secret,
                    config.x_access_token,
                    config.x_access_token_secret
                )
                self.api = tweepy.API(auth)

                logger.info("X/Twitter configured successfully")
            except Exception as e:
                logger.error(f"Failed to initialize X client: {e}")
                self.client = None
                self.api = None

    def upload_media(self, media_path: str) -> Optional[str]:
        """Upload media and return media_id"""
        if not self.api:
            logger.warning("X not configured, cannot upload media")
            return None

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would upload media: {media_path}")
            return "dry-run-media-id"

        if not os.path.exists(media_path):
            logger.error(f"Media file not found: {media_path}")
            return None

        try:
            media = self.api.media_upload(filename=media_path)
            logger.info(f"Media uploaded: {media.media_id}")
            return str(media.media_id)
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            return None

    def post_tweet(self, content: str, media: str = None) -> Optional[str]:
        """Post a tweet

        Args:
            content: Tweet text
            media: Path to local image/video file
        """
        if not self.client:
            logger.warning("X not configured, skipping tweet")
            return None

        # Handle media upload
        media_id = None
        if media:
            media_id = self.upload_media(media)

        if self.config.dry_run:
            logger.info(f"[DRY RUN] X tweet: {content[:100]}...")
            if media_id:
                logger.info(f"[DRY RUN] Media ID: {media_id}")
            return "dry-run-id"

        try:
            kwargs = {'text': content}
            if media_id:
                kwargs['media_ids'] = [media_id]

            response = self.client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            logger.info(f"Tweet posted: {tweet_id}")
            return tweet_id

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None


class PostScheduler:
    """Manage and execute scheduled posts"""

    def __init__(self, queue_path: str = "queue.json"):
        self.queue_path = Path(queue_path)
        self.config = Config()
        self.image_uploader = ImageUploader(self.config)
        self.nostr = NostrPoster(self.config, self.image_uploader)
        self.x = XPoster(self.config)

    def load_queue(self) -> Dict[str, Any]:
        """Load the post queue from JSON file"""
        if not self.queue_path.exists():
            return {"posts": []}

        try:
            with open(self.queue_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load queue: {e}")
            return {"posts": []}

    def save_queue(self, queue: Dict[str, Any]):
        """Save the post queue to JSON file"""
        try:
            with open(self.queue_path, 'w') as f:
                json.dump(queue, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")

    def process_due_posts(self):
        """Process all posts that are due to be posted"""
        queue = self.load_queue()
        now = datetime.now(timezone.utc)

        for post in queue['posts']:
            if post.get('posted', False):
                continue

            scheduled_time_str = post.get('scheduled_at')
            if not scheduled_time_str:
                continue

            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))

                if now >= scheduled_time:
                    logger.info(f"Processing post {post.get('id')}: {post.get('content', '')[:50]}...")
                    self.execute_post(post)
                    post['posted'] = True
                    post['posted_at'] = now.isoformat()

            except Exception as e:
                logger.error(f"Error processing post {post.get('id')}: {e}")

        self.save_queue(queue)

    def execute_post(self, post: Dict[str, Any]):
        """Execute a single post"""
        platform = post.get('platform', 'both')
        content = post.get('content', '')
        tags = post.get('tags', [])
        image = post.get('image') or post.get('media')

        if platform in ['nostr', 'both']:
            post_type = post.get('type', 'short')

            if post_type == 'long-form':
                title = post.get('title', 'Untitled')
                self.nostr.post_long_form(title, content, tags, image)
            else:
                self.nostr.post_note(content, tags, image)

        if platform in ['x', 'both']:
            self.x.post_tweet(content, image)

    def run_once(self):
        """Run once and exit"""
        logger.info("Processing scheduled posts...")
        self.process_due_posts()
        logger.info("Done")

    def run_daemon(self):
        """Run continuously, checking for due posts"""
        logger.info(f"Starting scheduler daemon (interval: {self.config.schedule_interval}s)")
        logger.info(f"Dry run: {self.config.dry_run}")

        try:
            while True:
                self.process_due_posts()
                time.sleep(self.config.schedule_interval)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Plebeian Social Media Scheduler")
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    parser.add_argument('--queue', '-q', default='queue.json', help='Path to queue JSON file')
    parser.add_argument('--dry-run', action='store_true', help='Force dry run mode')

    args = parser.parse_args()

    scheduler = PostScheduler(args.queue)

    if args.dry_run:
        scheduler.config.dry_run = True
        logger.info("Dry run mode enabled")

    if args.daemon:
        scheduler.run_daemon()
    else:
        scheduler.run_once()


if __name__ == '__main__':
    main()
