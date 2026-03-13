# Plebeian Scheduler — One-Pager

---

## What It Is

A self-hosted tool that **automatically posts** scheduled content to Nostr and X (Twitter) for Plebeian Market.

---

## Why It Matters

- **Save time** — Schedule posts weeks in advance
- **Consistent presence** — Regular updates even when you're busy
- **Image support** — Upload and attach images automatically
- **Cross-platform** — Post to Nostr + X simultaneously
- **Free & open source** — No fees, full control

---

## How It Works

```
You add post → JSON queue → Scheduler runs → Post goes live
  (planning)   (schedule)    (automatic)     (Nostr + X)
```

**Example:**
```bash
# Schedule a post for next Tuesday at 9am
python add_post.py --platform nostr \
  --content "Weekly update: 5 new merchants! 🎉" \
  --schedule "2026-03-18T09:00:00Z" \
  --tags plebeian bitcoin
```

The scheduler automatically posts it at the right time!

---

## Demo Results

| Post | Type | Status |
|------|------|--------|
| Welcome message | Text | ✅ Posted |
| Feature update | Text | ✅ Posted |
| Image post | 🖼️ Image | ✅ Posted with Bitcoin logo |

**View live on Nostr:** Search `npub19yjcp6m5ucpvx20e5knqspnwc44n94f4ynu0qkfxhlz6erm7klpq9senx6`

---

## Technical Details

- **Language:** Python 3
- **Storage:** JSON queue
- **Posting:** Nostr SDK library
- **Scheduling:** Cron-compatible timestamps
- **Deployment:** Systemd service (Linux)

---

## Get Started

```bash
# 1. Clone the repo
git clone https://github.com/bitcoinbekka/plebeian-scheduler.git
cd plebeian-scheduler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (add your Nostr key)
cp .env.example .env
# Edit .env with your keys

# 4. Add posts
python add_post.py --platform nostr --content "Test" --schedule "now"

# 5. Run
python scheduler.py
```

---

## GitHub

**https://github.com/bitcoinbekka/plebeian-scheduler**

Full documentation, examples, and contribution guide.

---

*Built for the self-sovereign future of commerce* ⚡🌐
