#!/usr/bin/env python3
"""
Simple live posting demo for Plebeian Scheduler
"""
from nostr_sdk import Keys, NostrSigner, EventBuilder, Client, RelayUrl
import asyncio
from datetime import datetime, timezone
import sys

async def post_to_nostr(message):
    """Post a message to Nostr"""
    # Your private key
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

    print(f"📤 Posting: {message[:50]}...")
    builder = EventBuilder.text_note(message)
    output = await client.send_event_builder(builder)

    print(f"✅ Post sent!")
    print(f"   Event ID: {output.id.to_hex()}")
    print(f"   Success: {len(output.success)} relays")

    if len(output.success) > 0:
        print(f"🔗 View on https://nostr.com/e/{output.id.to_hex()}")

    await client.disconnect()
    return output.id.to_hex()

if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "✅ Plebeian Scheduler Live Demo! 🚀 #plebeian"

    print("=" * 50)
    print("🧪 Plebeian Scheduler - Live Posting")
    print("=" * 50)

    event_id = asyncio.run(post_to_nostr(message))

    print("\n✅ Demo complete!")
    print(f"Event ID: {event_id}")
