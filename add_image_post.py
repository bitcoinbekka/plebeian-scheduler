#!/usr/bin/env python3
"""
Add an image post to the queue
"""
import json
from datetime import datetime, timedelta, timezone

# Load queue
with open('queue.json', 'r') as f:
    queue = json.load(f)

# Create image post
image_post = {
    "id": f"post-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
    "platform": "nostr",
    "content": "🖼️ Demo Post 3/3: With image! The scheduler posts images too. Check out this Bitcoin logo! 🪙 #plebeian #demo",
    "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/2560px-Bitcoin.svg.png",
    "scheduled_at": (datetime.now(timezone.utc) + timedelta(minutes=6, seconds=10)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    "posted": False,
    "posted_at": None,
    "tags": ["demo", "plebeian", "image"]
}

# Add to queue
queue["posts"].append(image_post)

# Save
with open('queue.json', 'w') as f:
    json.dump(queue, f, indent=2)

print("✓ Image post added to queue:")
print(f"  ID: {image_post['id']}")
print(f"  Scheduled: {image_post['scheduled_at']}")
print(f"  Image: {image_post['image'][:60]}...")
