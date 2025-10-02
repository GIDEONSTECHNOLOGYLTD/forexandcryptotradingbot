# 📦 Installation Guide

## System Requirements

### Minimum Requirements:
- **OS:** macOS, Linux, or Windows
- **Python:** 3.8 or higher
- **RAM:** 2GB minimum
- **Storage:** 500MB free space
- **Internet:** Stable connection required

### Recommended:
- **Python:** 3.9 or 3.10
- **RAM:** 4GB or more
- **Storage:** 1GB free space
- **Internet:** Broadband connection

---

## Installation Methods

### Method 1: Automated Setup (Recommended)

**For macOS/Linux:**
```bash
# Navigate to project directory
cd /Users/gideonaina/CascadeProjects/windsurf-project-2

# Run setup script
./setup.sh
```

**For Windows:**
```bash
# Navigate to project directory
cd C:\Users\YourName\CascadeProjects\windsurf-project-2

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
```

### Method 2: Manual Setup

**Step 1: Create Virtual Environment**
```bash
python3 -m venv venv
```

**Step 2: Activate Virtual Environment**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Step 3: Upgrade pip**
```bash
pip install --upgrade pip
```

**Step 4: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Create Environment File**
```bash
# macOS/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

---

## Dependency Details

### Core Dependencies:
```
ccxt==4.2.72          # Exchange connectivity
pandas==2.1.1         # Data manipulation
numpy==1.26.0         # Numerical computing
python-dotenv==1.0.0  # Environment variables
ta==0.11.0            # Technical analysis
requests==2.31.0      # HTTP requests
schedule==1.2.0       # Task scheduling
colorama==0.4.6       # Colored terminal output
tabulate==0.9.0       # Table formatting
```

### What Each Does:
- **ccxt** - Connects to OKX and other exchanges
- **pandas** - Handles market data and calculations
- **numpy** - Fast numerical operations
- **python-dotenv** - Loads API keys from .env
- **ta** - Calculates technical indicators (RSI, MACD, etc.)
- **requests** - Makes HTTP requests
- **schedule** - Schedules periodic tasks
- **colorama** - Colors the terminal output
- **tabulate** - Formats tables nicely

---

## OKX API Setup

### Step 1: Create OKX Account
1. Go to [okx.com](https://www.okx.com)
2. Click "Sign Up"
3. Complete registration
4. Verify your email
5. Complete KYC (if required)

### Step 2: Generate API Keys
1. Log in to OKX
2. Go to **Profile** → **API**
3. Click **Create API Key**
4. Set permissions:
   - ✅ **Read** (required)
   - ✅ **Trade** (required)
   - ❌ **Withdraw** (DO NOT enable)
5. Set API name (e.g., "Trading Bot")
6. Set passphrase (remember this!)
7. Complete 2FA verification
8. **Save these 3 values:**
   - API Key
   - Secret Key
   - Passphrase

### Step 3: Configure Bot
1. Open `.env` file:
   ```bash
   nano .env
   ```

2. Add your credentials:
   ```
   OKX_API_KEY=your_actual_api_key_here
   OKX_SECRET_KEY=your_actual_secret_key_here
   OKX_PASSPHRASE=your_actual_passphrase_here
   ```

3. Save and exit (Ctrl+O, Enter, Ctrl+X)

### Security Tips:
- ✅ Use strong passphrase
- ✅ Enable IP whitelist (optional)
- ✅ Keep credentials secret
- ✅ Never share API keys
- ❌ Never enable Withdraw permission
- ❌ Never commit .env to git

---

## Verification

### Test Installation:
```bash
# Check Python version
python3 --version
# Should show: Python 3.8.x or higher

# Check pip
pip --version
# Should show: pip 23.x or higher

# Check virtual environment
which python
# Should show: /path/to/venv/bin/python

# Check dependencies
pip list
# Should show all packages from requirements.txt
```

### Test Bot Connection:
```bash
# Run the bot
python advanced_trading_bot.py

# Expected output:
# ╔════════════════════════════════════════════════════════════════════╗
# ║                   ADVANCED TRADING BOT v2.0                        ║
# ║                    OKX Multi-Strategy System                       ║
# ╚════════════════════════════════════════════════════════════════════╝
# 
# 🤖 Advanced Trading Bot Initialized
# Exchange: OKX
# ...
```

### If Successful:
✅ Bot starts without errors
✅ Connects to OKX
✅ Displays market scan
✅ Shows top opportunities

### If Errors:
❌ Check API credentials in .env
❌ Verify internet connection
❌ Review error in trading_bot.log
❌ See Troubleshooting section below

---

## Troubleshooting

### Error: "ModuleNotFoundError"
**Problem:** Missing dependency

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "Failed to connect to OKX"
**Problem:** Invalid API credentials

**Solution:**
1. Check .env file has correct values
2. Verify API key is active on OKX
3. Check API permissions (Read + Trade)
4. Verify passphrase is correct

### Error: "Permission denied: ./setup.sh"
**Problem:** Setup script not executable

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Error: "python: command not found"
**Problem:** Python not installed or not in PATH

**Solution:**
```bash
# macOS
brew install python3

# Linux (Ubuntu/Debian)
sudo apt-get install python3 python3-pip

# Windows
# Download from python.org
```

### Error: "ccxt.NetworkError"
**Problem:** Internet connection issue

**Solution:**
1. Check internet connection
2. Try again in a few minutes
3. Check if OKX is down (status.okx.com)

### Error: "RateLimitExceeded"
**Problem:** Too many API requests

**Solution:**
- Bot handles this automatically
- Wait a few seconds
- Bot will retry

### Bot runs but no trades
**This is NORMAL!**
- Bot only trades when confidence ≥ 60%
- May take hours to find good signals
- Check logs to see analysis

---

## Platform-Specific Instructions

### macOS

**Install Python:**
```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
```

**Install Bot:**
```bash
cd /path/to/windsurf-project-2
./setup.sh
```

**Run Bot:**
```bash
source venv/bin/activate
python advanced_trading_bot.py
```

### Linux (Ubuntu/Debian)

**Install Python:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

**Install Bot:**
```bash
cd /path/to/windsurf-project-2
chmod +x setup.sh
./setup.sh
```

**Run Bot:**
```bash
source venv/bin/activate
python advanced_trading_bot.py
```

### Windows

**Install Python:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Complete installation

**Install Bot:**
```cmd
cd C:\path\to\windsurf-project-2
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**Run Bot:**
```cmd
venv\Scripts\activate
python advanced_trading_bot.py
```

---

## Post-Installation

### Configure Settings:
Edit `config.py` to customize:
```python
# Risk Management
MAX_POSITION_SIZE_PERCENT = 2.0
STOP_LOSS_PERCENT = 2.0
TAKE_PROFIT_PERCENT = 4.0

# Trading
TIMEFRAME = '1h'
PAPER_TRADING = True  # Keep True for testing!

# Scanner
MIN_VOLUME_USD = 1000000
SCAN_INTERVAL_MINUTES = 15
```

### First Run Checklist:
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] OKX API keys added
- [ ] PAPER_TRADING = True
- [ ] Bot starts without errors
- [ ] Market scan displays
- [ ] Ready to test!

---

## Updating

### Update Dependencies:
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update pip
pip install --upgrade pip

# Update packages
pip install -r requirements.txt --upgrade
```

### Update Bot Code:
```bash
# If using git
git pull origin main

# Or manually download new files
# and replace old ones
```

---

## Uninstallation

### Remove Bot:
```bash
# Deactivate virtual environment
deactivate

# Remove project directory
rm -rf /path/to/windsurf-project-2

# Or on Windows
rmdir /s windsurf-project-2
```

### Revoke API Keys:
1. Log in to OKX
2. Go to Profile → API
3. Find your API key
4. Click "Delete"
5. Confirm deletion

---

## Running as a Service (Advanced)

### macOS (launchd):
Create `~/Library/LaunchAgents/com.tradingbot.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tradingbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/advanced_trading_bot.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.tradingbot.plist
```

### Linux (systemd):
Create `/etc/systemd/system/tradingbot.service`:
```ini
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/windsurf-project-2
ExecStart=/path/to/venv/bin/python advanced_trading_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
```

### Windows (Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Trading Bot"
4. Trigger: At startup
5. Action: Start a program
6. Program: `C:\path\to\venv\Scripts\python.exe`
7. Arguments: `advanced_trading_bot.py`
8. Start in: `C:\path\to\windsurf-project-2`
9. Finish

---

## Getting Help

### Check These First:
1. **trading_bot.log** - Error details
2. **README.md** - Full documentation
3. **QUICKSTART.md** - Setup guide
4. **TROUBLESHOOTING** section above

### Common Issues:
- API credentials → Check .env file
- Connection errors → Check internet
- No trades → Normal, be patient
- Errors in log → Read error message

---

## Next Steps

After successful installation:

1. **Read Documentation:**
   - START_HERE.md
   - QUICKSTART.md
   - README.md

2. **Test the Bot:**
   - Run in paper trading mode
   - Watch for 1-2 hours
   - Observe market scans
   - See signal generation

3. **Learn the System:**
   - Understand strategies
   - Review risk management
   - Check configuration options

4. **Monitor Performance:**
   - Track statistics
   - Review trade history
   - Analyze results

5. **Optimize Settings:**
   - Adjust risk parameters
   - Test different timeframes
   - Fine-tune strategies

---

**Installation complete! Ready to run:**
```bash
python advanced_trading_bot.py
```

Good luck! 🚀
