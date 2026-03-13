#!/bin/bash
# Demo setup script - Creates a fresh demo queue with 3 posts

cd /home/ada/.openclaw/workspace/plebeian-scheduler

echo "=============================================="
echo "🧪 Setting up Plebeian Scheduler Demo"
echo "=============================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Calculate times (start in 10 seconds, then every 3 minutes)
TIME1=$(date -u -d "10 seconds" +"%Y-%m-%dT%H:%M:%SZ")
TIME2=$(date -u -d "3 minutes 10 seconds" +"%Y-%m-%dT%H:%M:%SZ")
TIME3=$(date -u -d "6 minutes 10 seconds" +"%Y-%m-%dT%H:%M:%SZ")

echo "Scheduling demo posts:"
echo "  Post 1: $TIME1 (10 seconds from now)"
echo "  Post 2: $TIME2 (3 minutes later)"
echo "  Post 3: $TIME3 (6 minutes later)"
echo ""

# Create fresh queue
echo '{"posts": []}' > queue.json

# Add Post 1 (text)
python3 add_post.py --platform nostr \
  --content "📢 Demo Post 1/3: Welcome to the Plebeian Scheduler demo! This post goes first. #plebeian #demo" \
  --schedule "$TIME1" \
  --tags demo plebeian

# Add Post 2 (text)
python3 add_post.py --platform nostr \
  --content "⏱️ Demo Post 2/3: 3 minutes later! The scheduler waits and posts automatically. This is text-only. #plebeian #demo" \
  --schedule "$TIME2" \
  --tags demo plebeian scheduler

# Add Post 3 (image)
python3 add_image_post.py

echo ""
echo "=============================================="
echo "✅ Demo queue ready!"
echo "=============================================="
echo ""
echo "📋 Demo Posts:"
python3 manage_queue.py list | grep -A4 "Demo Post"
echo ""
echo "🚀 To run the demo, type:"
echo "   python3 demo_runner.py"
echo ""
