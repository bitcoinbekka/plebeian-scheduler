# Quick Start Guide - Plebeian Scheduler

Get up and running in 5 minutes.

## 1. Installation

```bash
cd plebeian-scheduler
pip install -r requirements.txt
```

## 2. Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### For Nostr Only (Easiest)

You only need:
- `NOSTR_PRIVATE_KEY` - Your Nostr private key (starts with `nsec1...`)

### For X/Twitter Also

You need:
- Create an app at https://developer.twitter.com/
- Get API keys and access tokens
- Add to `.env`

## 3. Test with Dry Run

```bash
# List current queue
python manage_queue.py list

# Run scheduler (won't actually post)
python scheduler.py --dry-run
```

## 4. Add Your First Post

```bash
# Add a simple Nostr note
python add_post.py \
  --platform nostr \
  --content "Hello from Plebeian! 🚀" \
  --schedule "+2h"

# Add an X post
python add_post.py \
  --platform x \
  --content "Check out Plebeian Market! #Bitcoin" \
  --schedule "+3h"

# Add to both
python add_post.py \
  --platform both \
  --content "Cross-platform test post" \
  --schedule "+4h"
```

## 5. Go Live!

Edit `.env`:
```env
DRY_RUN=false
```

Then run:
```bash
# Run once
python scheduler.py

# Or run as daemon
python scheduler.py --daemon
```

## Schedule Time Formats

```bash
# Absolute time
python add_post.py --content "..." --schedule "2026-03-12T10:00:00Z"

# Relative (hours)
python add_post.py --content "..." --schedule "+2h"
python add_post.py --content "..." --schedule "+24h"

# Relative (minutes, days)
python add_post.py --content "..." --schedule "+30m"
python add_post.py --content "..." --schedule "+3d"

# Natural language
python add_post.py --content "..." --schedule "tomorrow 9am"
```

## Common Tasks

```bash
# List scheduled posts
python manage_queue.py list

# View a post
python manage_queue.py view post-001

# Delete a post
python manage_queue.py delete post-001

# Mark as posted manually
python manage_queue.py mark-posted post-001
```

## Long-form Nostr Posts

```bash
python add_post.py \
  --platform nostr \
  --type long \
  --title "My Article Title" \
  --content "Full article content here..." \
  --tags bitcoin nostr freedom \
  --schedule "tomorrow 10am"
```

## Systemd Service (Auto-start)

Create `/etc/systemd/system/plebeian-scheduler.service`:

```ini
[Unit]
Description=Plebeian Social Media Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/plebeian-scheduler
ExecStart=/usr/bin/python3 /home/your_username/plebeian-scheduler/scheduler.py --daemon
Restart=always
RestartSec=60
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable plebeian-scheduler
sudo systemctl start plebeian-scheduler
sudo systemctl status plebeian-scheduler
```

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"Nostr private key not found"**
- Check `.env` file has `NOSTR_PRIVATE_KEY=nsec1...`

**Posts not appearing on Nostr**
- Check relay URLs are correct
- Some relays are slow
- Check logs with `-v` flag

**X API errors**
- Verify API keys in `.env`
- Check rate limits (300 tweets/3 hours)

## Next Steps

1. ✏️ Plan your weekly content
2. 📅 Schedule posts ahead of time
3. 📊 Monitor engagement
4. 🔄 Iterate on what works

Happy posting! 🚀
