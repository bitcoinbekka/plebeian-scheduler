#!/bin/bash
# Quick install script for Plebeian Scheduler

set -e

echo "🚀 Plebeian Scheduler Installation"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run with sudo: sudo bash install.sh"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
apt update
apt install -y python3-pip python3-venv

echo ""
echo "✅ System dependencies installed!"
echo ""
echo "Next steps:"
echo "1. cd ~/.openclaw/workspace/plebeian-scheduler"
echo "2. python3 -m venv venv"
echo "3. source venv/bin/activate"
echo "4. pip install -r requirements.txt"
echo "5. cp .env.example .env"
echo "6. nano .env  # Add your credentials"
echo "7. python scheduler.py --dry-run"
echo ""
