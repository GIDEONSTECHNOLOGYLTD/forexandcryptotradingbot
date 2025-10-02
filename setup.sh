#!/bin/bash

# Advanced Trading Bot Setup Script
# This script automates the initial setup process

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           Advanced Trading Bot v2.0 - Setup Script                 ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.8 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
echo "⚙️  Setting up configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env and add your OKX API credentials!"
    echo "   Run: nano .env"
fi
echo ""

# Display next steps
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                        Setup Complete! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Get OKX API Keys:"
echo "   → Visit: https://www.okx.com/account/my-api"
echo "   → Create API with 'Read' and 'Trade' permissions"
echo "   → Save: API Key, Secret Key, and Passphrase"
echo ""
echo "2. Configure the bot:"
echo "   → Run: nano .env"
echo "   → Add your OKX credentials"
echo ""
echo "3. Start the bot:"
echo "   → Run: python advanced_trading_bot.py"
echo ""
echo "📚 Documentation:"
echo "   → Quick Start: QUICKSTART.md"
echo "   → Full Guide: README.md"
echo "   → Architecture: ARCHITECTURE.md"
echo ""
echo "⚠️  IMPORTANT: The bot starts in PAPER TRADING mode (safe)"
echo "   Test for at least 2 weeks before considering live trading!"
echo ""
echo "Good luck and trade safely! 🚀"
echo ""
