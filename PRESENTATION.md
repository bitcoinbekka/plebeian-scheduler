# Plebeian Social Media Scheduler

---

## 🚀 Overview

A powerful tool to **schedule posts** to **Nostr** and **X (Twitter)** for Plebeian Market accounts.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📝 **Schedule Posts** | Plan content days or weeks in advance |
| 🌐 **Nostr Integration** | Post to public relays (Damus, Nos.lol, etc.) |
| 🐦 **X/Twitter Support** | Cross-post to social media |
| 🖼️ **Image Support** | Upload and attach images to posts |
| ⏰ **Automatic Posting** | Runs on schedule, no manual work needed |
| 🧪 **Dry-Run Mode** | Test before going live |

---

## 🎯 Use Cases

- **Product Announcements** — Schedule new features, merchant spotlights
- **Content Marketing** — Cross-post from Substack, blog posts
- **Weekly Updates** — Regular updates on project progress
- **Community Engagement** — Tips, memes, Bitcoin education

---

## 📋 How It Works

```
1. Plan Content → 2. Add to Queue → 3. Scheduler Runs → 4. Posts Go Live
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │ Write posts │ → │ JSON queue   │ → │ Cron job    │ → │ Nostr + X    │
   │ with images │   │ with times   │   │ processes   │   │ relays       │
   └─────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

---

## 💻 Quick Demo

**Step 1: Add a post**
```bash
python add_post.py --platform nostr \
  --content "New merchant joined! 🌾" \
  --schedule "2026-03-15T09:00:00Z" \
  --tags bitcoin nostr
```

**Step 2: The scheduler posts automatically**
```bash
python scheduler.py
```

**Step 3: Post appears on Nostr!**
```
🔗 https://nostr.com/e/[event-id]
```

---

## 🎬 Demo Results

| Post | Type | Status |
|------|------|--------|
| Welcome Post | Text | ✅ Live |
| Feature Announcement | Text | ✅ Live |
| Image Post | 🖼️ Image | ✅ Live |

**View all demo posts:** Search for `npub19yjcp6m5ucpvx20e5knqspnwc44n94f4ynu0qkfxhlz6erm7klpq9senx6`

---

## 🔐 Security & Privacy

- ✅ **Self-hosted** — Run on your own infrastructure
- ✅ **FOSS** — Free and open source forever
- ✅ **Private keys** — Never exposed or stored in code
- ✅ **No platform fees** — Keep 100% of your control

---

## 🌐 GitHub Repository

**Code:** https://github.com/bitcoinbekka/plebeian-scheduler

- Full source code
- Documentation
- Installation guide
- Example queues

---

## 💡 Next Steps

1. ✅ **Deploy to production** — Set up as a systemd service
2. ✅ **Configure production keys** — Use production Nostr key
3. ✅ **Add X/Twitter API** — Enable cross-posting
4. ✅ **Schedule content** — Plan your weekly calendar
5. ✅ **Monitor posts** — Track engagement and reach

---

## 🙌 Thank You

**Questions?**

- GitHub: `https://github.com/bitcoinbekka/plebeian-scheduler`
- Nostr: `npub19yjcp6m5ucpvx20e5knqspnwc44n94f4ynu0qkfxhlz6erm7klpq9senx6`

---

*Powered by Bitcoin & Nostr* ⚡🌐
