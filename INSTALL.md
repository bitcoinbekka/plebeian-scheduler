# Install Plebeian Scheduler

## Quick Install (5 minutes)

### Step 1: Install pip (one-time system setup)

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
```

*Or use the install script:*
```bash
cd ~/.openclaw/workspace/plebeian-scheduler
sudo bash install.sh
```

---

### Step 2: Go to scheduler directory

```bash
cd ~/.openclaw/workspace/plebeian-scheduler
```

---

### Step 3: Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

*You should see `(venv)` in your prompt now.*

---

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

This will install:
- nostr (for Nostr posting)
- tweepy (for X/Twitter posting)
- python-dotenv (for config)
- schedule (for cron-like scheduling)
- pytz (for timezone handling)

---

### Step 5: Configure

```bash
cp .env.example .env
nano .env
```

Add your credentials:

**For Nostr only:**
```env
NOSTR_PRIVATE_KEY=nsec1...your_key_here
NOSTR_RELAYS=wss://relay.damus.io,wss://nos.lol,wss://relay.nostr.band
DRY_RUN=true  # Set to false to actually post
```

**For X/Twitter also:**
```env
# Add to the above:
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_BEARER_TOKEN=your_bearer_token
```

**Get X API keys:**
1. Go to https://developer.twitter.com/
2. Create a new project/app
3. Get API keys and access tokens
4. Paste them into `.env`

---

### Step 6: Test

```bash
# Test with dry run (won't actually post)
python scheduler.py --dry-run

# Test adding a post
python add_post.py --platform nostr --content "Test!" --schedule "+2h"

# View queue
python manage_queue.py list
```

---

### Step 7: Go Live

Edit `.env`:
```env
DRY_RUN=false
```

Then run:
```bash
# Run once (processes all due posts)
python scheduler.py

# Or run continuously (daemon mode)
python scheduler.py --daemon
```

---

## Using Without Dependencies (Testing Only)

If you just want to test the queue logic without installing dependencies:

```bash
cd ~/.openclaw/workspace/plebeian-scheduler

# Add posts (works without dependencies)
python3 add_post.py --platform nostr --content "Hello!" --schedule "+2h"

# Manage queue (works without dependencies)
python3 manage_queue.py list
python3 manage_queue.py view post-ID

# Test queue processing (works without dependencies)
python3 test_scheduler.py --dry-run
```

---

## Troubleshooting

### "pip: command not found"
- Install pip3 first: `sudo apt install python3-pip`

### "ModuleNotFoundError: No module named 'dotenv'"
- Install dependencies: `pip install -r requirements.txt`
- Make sure virtual environment is activated: `source venv/bin/activate`

### "Nostr private key not found"
- Check `.env` file exists
- Verify `NOSTR_PRIVATE_KEY=nsec1...` is set
- Key should start with `nsec1...`

### "X API rate limit exceeded"
- X has limits: 300 tweets/3-hour window
- Reduce posting frequency
- Wait before trying again

### Posts not appearing on Nostr
- Check relay URLs are correct
- Some relays are slow to propagate
- Verify your private key is correct

---

## Auto-Start with Systemd (Optional)

To have the scheduler start automatically on boot:

### Create service file

```bash
sudo nano /etc/systemd/system/plebeian-scheduler.service
```

Paste this:

```ini
[Unit]
Description=Plebeian Social Media Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/.openclaw/workspace/plebeian-scheduler
ExecStart=/home/your_username/.openclaw/workspace/plebeian-scheduler/venv/bin/python /home/your_username/.openclaw/workspace/plebeian-scheduler/scheduler.py --daemon
Restart=always
RestartSec=60
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

*Replace `your_username` with your actual username.*

### Enable and start

```bash
sudo systemctl enable plebeian-scheduler
sudo systemctl start plebeian-scheduler
sudo systemctl status plebeian-scheduler
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python scheduler.py --dry-run` | Test without posting |
| `python scheduler.py` | Run once, process due posts |
| `python scheduler.py --daemon` | Run continuously |
| `python add_post.py -p nostr -c "..." -s "+2h"` | Add post |
| `python manage_queue.py list` | List all posts |
| `python manage_queue.py view post-ID` | View post details |
| `python manage_queue.py delete post-ID` | Delete post |
| `python manage_queue.py reschedule post-ID "2026-03-12T10:00:00Z"` | Change time |
| `python manage_queue.py mark-posted post-ID` | Mark as posted |

---

## Need Help?

- Full docs: `README.md`
- Quick start: `QUICKSTART.md`
- Test results: `TEST-RESULTS.md`
