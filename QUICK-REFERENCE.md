# Quick Reference - Plebeian Scheduler

## After Installation

### Configure
```bash
nano .env
```
Add: `NOSTR_PRIVATE_KEY=nsec1...`
Save: Ctrl+X → Y → Enter

---

### Test Commands

```bash
# Test without posting
python scheduler.py --dry-run

# Add a post
python add_post.py --platform nostr --content "Hello!" --schedule "+2h"

# View queue
python manage_queue.py list

# View specific post
python manage_queue.py view post-ID
```

---

### Go Live

Edit `.env`: Change `DRY_RUN=false`

```bash
# Run once
python scheduler.py

# Run continuously
python scheduler.py --daemon
```

---

### Time Formats

```bash
# ISO format
python add_post.py --content "..." --schedule "2026-03-12T10:00:00Z"

# Relative
python add_post.py --content "..." --schedule "+2h"    # 2 hours
python add_post.py --content "..." --schedule "+30m"   # 30 minutes
python add_post.py --content "..." --schedule "+1d"    # 1 day

# Natural language
python add_post.py --content "..." --schedule "tomorrow 9am"
```

---

### Platform Options

```bash
--platform nostr    # Nostr only
--platform x        # X/Twitter only
--platform both     # Both platforms
```

---

### Post Types (Nostr only)

```bash
--type short    # Short note (kind 1)
--type long     # Long-form article (kind 30023)
```

---

### Queue Management

```bash
# List all
python manage_queue.py list

# View post
python manage_queue.py view post-ID

# Delete post
python manage_queue.py delete post-ID

# Reschedule
python manage_queue.py reschedule post-ID "2026-03-12T10:00:00Z"

# Mark as posted manually
python manage_queue.py mark-posted post-ID
```

---

## Your Nostr Key

Find your Nostr private key:
- **Damus app:** Settings → Private Key
- **Amethyst app:** Settings → Private Key
- **Primal app:** Settings → Private Key
- **Web:** Your Nostr extension/wallet settings

It should start with: `nsec1...`

---

## Deactivate Virtual Environment

When done:
```bash
deactivate
```

To reactivate later:
```bash
cd ~/.openclaw/workspace/plebeian-scheduler
source venv/bin/activate
```
