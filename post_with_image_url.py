#!/usr/bin/env python3
"""
Post to Nostr with an image (from URL or file upload)
"""
from nostr_sdk import Keys, NostrSigner, EventBuilder, Client, RelayUrl, Tag
import asyncio
import sys
from pathlib import Path

async def post_with_image_url(message, image_url):
    """Post to Nostr with an image URL"""
    nsec = "nsec1kyk3607cfee5889ad5xgmz6g3309t6jyrr2kfk77h30q9j8yfz4qf4gvel"
    keys = Keys.parse(nsec)

    # Create client
    client = Client(NostrSigner.keys(keys))

    # Add relays
    relays = ["wss://relay.damus.io", "wss://nos.lol"]

    print(f"📡 Connecting to relays...")
    for relay in relays:
        await client.add_relay(RelayUrl.parse(relay))

    await client.connect()

    # Create tags with image URL (NIP-94)
    tags = [
        Tag.parse(["url", image_url]),
        Tag.parse(["m", "image/png"])
    ]

    # Build event with tags - prepend image URL to content
    full_message = f"{image_url}\n\n{message}"
    builder = EventBuilder.text_note(full_message).tags(tags)

    print(f"📤 Posting with image...")
    output = await client.send_event_builder(builder)

    print(f"✅ Post sent with image!")
    print(f"   Event ID: {output.id.to_hex()}")
    print(f"   Success: {len(output.success)} relays")
    print(f"   Image URL: {image_url}")

    if len(output.success) > 0:
        print(f"🔗 View on https://nostr.com/e/{output.id.to_hex()}")

    await client.disconnect()
    return output.id.to_hex()

if __name__ == "__main__":
    # Using a test image URL for the demo
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/2560px-Bitcoin.svg.png"
    message = sys.argv[1] if len(sys.argv) > 1 else "✅ Plebeian Scheduler - Bitcoin image test! 🪙 #plebeian #demo"

    print("=" * 50)
    print("🧪 Plebeian Scheduler - Post with Image URL")
    print("=" * 50)
    print(f"🖼️ Image URL: {test_image_url}")
    print(f"💬 Message: {message[:50]}...")
    print("=" * 50)

    event_id = asyncio.run(post_with_image_url(message, test_image_url))

    if event_id:
        print("\n✅ Demo complete!")
        print(f"Event ID: {event_id}")
    else:
        print("\n❌ Demo failed!")
