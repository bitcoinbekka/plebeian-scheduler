# Plebeian Social Media Scheduler

A tool to schedule posts to Nostr and X (Twitter) for the Plebeian Market accounts.

## Features

- Schedule posts to Nostr (long-form and short-form)
- Schedule posts to X/Twitter
- **Image support** for both Nostr and X (local files or URLs)
- JSON-based post queue
- Cron-compatible scheduling
- Automatic posting from queue
- Dry-run mode for testing

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Nostr Configuration
NOSTR_PRIVATE_KEY=nsec1...  # Your Nostr private key
NOSTR_RELAYS=wss://relay.damus.io,wss://nos.lol,wss://relay.nostr.band

# X/Twitter Configuration
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_BEARER_TOKEN=your_bearer_token

# Scheduler Configuration
SCHEDULE_INTERVAL=300  # Check queue every 300 seconds (5 minutes)
DRY_RUN=true  # Set to false to actually post
```

### Getting X API Credentials

1. Go to https://developer.twitter.com/
2. Create a project/app
3. Get your API keys and access tokens
4. Add them to `.env`

## Usage

### Adding Posts

Create a JSON file with your posts (e.g., `queue.json`):

```json
{
  "posts": [
    {
      "id": "post-001",
      "platform": "nostr",
      "type": "long-form",
      "title": "Building the Mycelium of Free Commerce",
      "content": "Full article content here...\n\nCan include markdown-like formatting.",
      "image": "/path/to/cover-image.jpg",
      "tags": ["plebeian", "bitcoin", "nostr", "freedom"],
      "scheduled_at": "2026-03-12T10:00:00Z",
      "posted": false,
      "posted_at": null
    },
    {
      "id": "post-002",
      "platform": "x",
      "content": "🚀 New merchant spotlight on Plebeian Market! Meet @farmer_bob selling organic produce directly with Bitcoin. No fees, no middlemen. Just fresh food and freedom. ⚡🌽\n\n#Bitcoin #Nostr #LocalFood",
      "image": "/path/to/merchant-photo.png",
      "scheduled_at": "2026-03-12T14:00:00Z",
      "posted": false,
      "posted_at": null
    },
    {
      "id": "post-003",
      "platform": "both",
      "content": "Quick tip: You can self-host your entire Plebeian marketplace on a $5 VPS or even at home on Umbrel/Start9. Your data, your rules. 🏠⚡",
      "image": "https://example.com/image.jpg",
      "scheduled_at": "2026-03-13T09:00:00Z",
      "posted": false,
      "posted_at": null
    }
  ]
}
```

See `example-queue-with-images.json` for more examples with images.

### Running the Scheduler

```bash
# Run once (process all due posts)
python scheduler.py

# Run in daemon mode (continuously check for due posts)
python scheduler.py --daemon

# Dry run (don't actually post, just show what would happen)
python scheduler.py --dry-run

# Specify a different queue file
python scheduler.py --queue custom_queue.json
```

### Adding Individual Posts

```bash
# Add a Nostr post
python add_post.py --platform nostr \
  --content "Your post here" \
  --schedule "2026-03-12T10:00:00Z" \
  --tags bitcoin nostr

# Add a Nostr post with an image
python add_post.py --platform nostr \
  --content "Check out this new merchant! 🌾" \
  --image /path/to/image.jpg \
  --schedule "2026-03-12T10:00:00Z" \
  --tags bitcoin nostr

# Add an X post
python add_post.py --platform x \
  --content "Your X post here" \
  --schedule "2026-03-12T14:00:00Z"

# Add an X post with an image
python add_post.py --platform x \
  --content "New merchant spotlight!" \
  --image /path/to/photo.png \
  --schedule "2026-03-12T14:00:00Z"

# Add to both platforms with image
python add_post.py --platform both \
  --content "Cross-platform post" \
  --image https://example.com/image.jpg \
  --schedule "2026-03-13T09:00:00Z"
```

### Image Support

Images can be added to posts using the `--image` or `-i` flag:

- **Local files:** Provide a path to a local image file (JPG, PNG, GIF, WebP). The scheduler will automatically upload it to nostr.build for Nostr posts, or to X for Twitter posts.
- **URLs:** Provide a full HTTPS URL. The scheduler will use it directly (for Nostr) or will need it as a local file for X.

**Supported formats:**
- JPG/JPEG
- PNG
- GIF
- WebP

**Nostr image handling:**
- Local images are uploaded to nostr.build
- URLs are embedded directly
- NIP-94 metadata tags are added for proper image display

**X/Twitter image handling:**
- Only local files are supported (X API limitation)
- Images are uploaded via X's media upload API
- First 4 images are attached to tweets

### Managing the Queue

```bash
# List all scheduled posts
python manage_queue.py --list

# View post details
python manage_queue.py --view post-001

# Delete a post
python manage_queue.py --delete post-002

# Reschedule a post
python manage_queue.py --reschedule post-001 "2026-03-15T10:00:00Z"

# Mark as posted (manual override)
python manage_queue.py --mark-posted post-001
```

## Post Types

### Nostr

**Short-form (kind 1):**
- Plain text notes
- Up to 1400+ characters
- Great for announcements, tips, engagement

**Long-form (kind 30023):**
- Articles, blog posts, guides
- Markdown support
- Best for Substack cross-posts, educational content

### X/Twitter

- Standard tweets (280 chars)
- Can include hashtags, mentions
- Images/media support (add `media` field in JSON)

## Setting Up as a Systemd Service (Linux)

Create `/etc/systemd/system/plebeian-scheduler.service`:

```ini
[Unit]
Description=Plebeian Social Media Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/plebeian-scheduler
ExecStart=/usr/bin/python3 /path/to/plebeian-scheduler/scheduler.py --daemon
Restart=always
RestartSec=60
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable plebeian-scheduler
sudo systemctl start plebeian-scheduler
sudo systemctl status plebeian-scheduler
```

## Integration with Substack

To auto-schedule Substack posts to Nostr:

```bash
python substack_to_nostr.py \
  --substack-url https://plebeian.substack.com \
  --schedule-delay "2 hours"
```

This will:
1. Fetch your latest Substack posts
2. Convert them to Nostr long-form format
3. Schedule them to Nostr after a delay
4. Add links back to Substack for comments

## Security Notes

- Never commit `.env` or your private keys
- Use environment-specific .env files (.env.production, .env.staging)
- For production, use secrets management or environment variables
- X API tokens have rate limits — schedule accordingly

## Troubleshooting

**"Nostr private key not found"**
- Ensure NOSTR_PRIVATE_KEY is set in .env
- Format should start with `nsec1...`

**"X API rate limit exceeded"**
- Reduce posting frequency
- X has limits: 300 tweets/3-hour window for basic tier

**"Post not appearing on Nostr"**
- Check relay connectivity
- Verify relays are online
- Some relays may be slow to propagate

## Example Workflow

```bash
# 1. Plan your weekly content (Monday)
python add_post.py --platform both \
  --content "Weekly update: 5 new merchants joined Plebeian this week! 🎉" \
  --schedule "2026-03-17T09:00:00Z"

# 2. Add merchant spotlight (Tuesday)
python add_post.py --platform nostr --type long-form \
  --title "Meet Farmer Bob: Organic Food, Bitcoin Payments" \
  --content "Full article..." \
  --schedule "2026-03-18T10:00:00Z"

# 3. Cross-post summary to X (Tuesday afternoon)
python add_post.py --platform x \
  --content "🌾 New spotlight: How Farmer Bob uses Plebeian to sell organic produce for Bitcoin. Read the full story on our Nostr! 📖\n\n#Bitcoin #Nostr #LocalFood" \
  --schedule "2026-03-18T15:00:00Z"

# 4. Start the scheduler
python scheduler.py --daemon
```

## Contributing

This is a FOSS project. Feel free to submit issues and PRs!

## License

Same as Plebeian Market - GPL-3.0
