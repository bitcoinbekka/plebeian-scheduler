#!/usr/bin/env python3
"""
Demo runner: Process scheduled posts and post to Nostr
"""
import json
import sys
from datetime import datetime, timezone
from nostr_sdk import Keys, NostrSigner, EventBuilder, Client, RelayUrl, Tag
import asyncio

# Configuration
NSEC = "nsec1kyk3607cfee5889ad5xgmz6g3309t6jyrr2kfk77h30q9j8yfz4qf4gvel"
RELAYS = ["wss://relay.damus.io", "wss://nos.lol"]

async def post_to_nostr(content, image_url=None, tags=None):
    """Post to Nostr (with optional image)"""
    keys = Keys.parse(NSEC)
    client = Client(NostrSigner.keys(keys))

    # Add relays
    for relay in RELAYS:
        await client.add_relay(RelayUrl.parse(relay))

    await client.connect()

    # Build content
    final_content = content

    # Add image URL if present
    nostr_tags = []
    if image_url:
        final_content = f"{image_url}\n\n{content}"
        nostr_tags = [
            Tag.parse(["url", image_url]),
            Tag.parse(["m", "image/png"])
        ]

    # Create event
    builder = EventBuilder.text_note(final_content)
    if nostr_tags:
        builder = builder.tags(nostr_tags)

    output = await client.send_event_builder(builder)

    await client.disconnect()
    return output.id.to_hex(), len(output.success)

async def run_demo():
    """Process scheduled posts"""
    # Load queue
    with open('queue.json', 'r') as f:
        queue = json.load(f)

    now = datetime.now(timezone.utc)

    print("=" * 60)
    print("🧪 PLEBEIAN SCHEDULER DEMO")
    print("=" * 60)
    print(f"Current time: {now.strftime('%H:%M:%S')} UTC")
    print()

    for post in queue['posts']:
        if post.get('posted', False):
            continue

        scheduled_time = datetime.fromisoformat(post['scheduled_at'].replace('Z', '+00:00'))
        time_until = (scheduled_time - now).total_seconds()

        if time_until > 0:
            print(f"⏳ Waiting {int(time_until)}s for: {post.get('id')}")

            # Wait with countdown
            while time_until > 0:
                print(f"   ⏰ {int(time_until)}s remaining...    ", end='\r')
                await asyncio.sleep(1)
                time_until -= 1
            print()  # New line

        # Post to Nostr
        content = post.get('content', '')
        image_url = post.get('image')
        tags = post.get('tags', [])

        print(f"📤 Posting: {content[:50]}...")

        if image_url:
            print(f"   🖼️ Image: {image_url[:50]}...")

        event_id, success_count = await post_to_nostr(content, image_url, tags)

        print(f"   ✅ Posted! Event ID: {event_id}")
        print(f"   📡 Success on {success_count} relays")
        print(f"   🔗 https://nostr.com/e/{event_id}")
        print()

        # Mark as posted
        post['posted'] = True
        post['posted_at'] = datetime.now(timezone.utc).isoformat()

        # Save queue
        with open('queue.json', 'w') as f:
            json.dump(queue, f, indent=2)

    print("=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_demo())
