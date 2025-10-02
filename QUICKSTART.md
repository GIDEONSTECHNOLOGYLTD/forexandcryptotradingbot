# 🚀 Quick Start Guide

## Step-by-Step Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get OKX API Keys

**Important:** You need an OKX account first. Sign up at [okx.com](https://www.okx.com)

1. Log in to OKX
2. Go to: Profile → API → Create API Key
3. Set permissions: **Read** + **Trade** (NOT Withdraw)
4. Set IP restriction (optional but recommended)
5. Save these 3 values:
   - API Key
   - Secret Key
   - Passphrase

### 3. Configure Bot

```bash
# Copy example file
cp .env.example .env

# Edit with your favorite editor
nano .env
```

Add your credentials:
```
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here
```

### 4. Run the Bot

```bash
python advanced_trading_bot.py
```

That's it! The bot will:
- ✅ Scan OKX markets for opportunities
- ✅ Analyze top tokens with 5 strategies
- ✅ Simulate trades (paper trading mode)
- ✅ Show you performance statistics

## What You'll See

```
╔════════════════════════════════════════════════════════════════════╗
║                   ADVANCED TRADING BOT v2.0                        ║
║                    OKX Multi-Strategy System                       ║
╚════════════════════════════════════════════════════════════════════╝

🤖 Advanced Trading Bot Initialized
Exchange: OKX
Mode: PAPER TRADING
Initial Capital: $10,000.00
Timeframe: 1h
Max Positions: 3

🔍 Scanning markets for opportunities...

📊 Top Trading Opportunities:
Symbol          Price        24h Change   Volume (24h)     Score   
----------------------------------------------------------------------
BTC/USDT        $43,250.50   +2.34%       $1,234,567,890   8/10    
ETH/USDT        $2,280.75    +3.12%       $567,890,123     7/10    
SOL/USDT        $98.45       +5.67%       $234,567,890     7/10    

✅ Signal detected for BTC/USDT
Market Condition: trending_up

📝 PAPER TRADE
Symbol: BTC/USDT
Signal: BUY
Confidence: 75.0%
Entry Price: $43,250.50
Position Size: 0.0046
Stop Loss: $42,385.49
Take Profit: $44,980.52
```

## Understanding the Output

### 🔍 Market Scanner
- Runs every 15 minutes
- Shows top 5 opportunities
- Score based on volume, volatility, spread

### ✅ Trading Signals
- Only trades when confidence ≥ 60%
- Combines 5 technical strategies
- Shows entry, stop-loss, take-profit

### 📊 Statistics (shown every 5 iterations)
- Current capital and PnL
- Win rate and profit factor
- Number of trades
- Open positions

## Next Steps

### Test in Paper Trading (Recommended: 2+ weeks)
- Monitor performance
- Adjust settings in `config.py`
- Learn how strategies work

### Customize Settings
Edit `config.py`:
```python
# Risk Management
MAX_POSITION_SIZE_PERCENT = 2.0  # Lower = safer
STOP_LOSS_PERCENT = 2.0          # Adjust based on volatility
TAKE_PROFIT_PERCENT = 4.0        # 2:1 risk-reward ratio

# Scanner
MIN_VOLUME_USD = 1000000         # Filter low-volume tokens
SCAN_INTERVAL_MINUTES = 15       # How often to scan
```

### When Ready for Live Trading

⚠️ **ONLY after thorough testing!**

1. Change in `config.py`:
```python
PAPER_TRADING = False  # Enable live trading
```

2. Start with SMALL amounts:
```python
INITIAL_CAPITAL = 100  # Start with $100, not $10,000!
MAX_POSITION_SIZE_PERCENT = 1.0  # Use only 1% per trade
```

3. Monitor closely for first week

## Common Issues

### "Failed to connect to OKX"
- Check API credentials in `.env`
- Verify API key has correct permissions
- Make sure you copied all 3 values (key, secret, passphrase)

### "No opportunities found"
- Normal during low volatility
- Wait for next scan (15 min)
- Or lower `MIN_VOLUME_USD` in config

### Bot stops after error
- Check `trading_bot.log` for details
- Most errors are temporary (API rate limits)
- Bot will retry automatically

## Safety Reminders

✅ **DO:**
- Start with paper trading
- Test for at least 2 weeks
- Start small when going live
- Monitor regularly
- Adjust risk settings conservatively

❌ **DON'T:**
- Skip paper trading phase
- Invest more than you can lose
- Leave bot unmonitored
- Expect guaranteed profits
- Blame the bot for losses (you're responsible!)

## Getting Help

1. Check `trading_bot.log` for errors
2. Review configuration in `config.py`
3. Read full documentation in `README.md`
4. Understand that trading is risky

---

**Ready to start? Run:** `python advanced_trading_bot.py`
