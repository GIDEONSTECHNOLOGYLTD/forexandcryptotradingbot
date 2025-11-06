# Advanced Trading Bot v2.0 🤖

A professional-grade Python trading bot with OKX integration, featuring multi-strategy analysis, automatic token scanning, comprehensive risk management, and support for both cryptocurrency and forex markets.

## 🌟 Features

- **OKX Exchange Integration** - Direct connection to OKX spot markets
- **Automatic Token Scanner** - Finds high-potential trading opportunities
- **Multi-Strategy System** - Combines 5+ technical strategies with confidence scoring
- **Advanced Risk Management** - Stop-loss, take-profit, position sizing, daily loss limits
- **Paper Trading Mode** - Test strategies without risking real money
- **Real-time Monitoring** - Live statistics and performance tracking
- **Technical Indicators** - RSI, MACD, Bollinger Bands, Moving Averages, OBV, Momentum
- **Forex Support** - Ready for forex trading (requires appropriate OKX account)

## 📋 Prerequisites

- Python 3.8 or higher
- OKX account with API access
- Basic understanding of trading concepts

## 🚀 Quick Start

### Option 1: Docker (Recommended - Production Ready)

```bash
# Clone and setup
git clone https://github.com/yourusername/forexandcryptotradingbot.git
cd forexandcryptotradingbot

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start all services (MongoDB, Redis, Web, Bot)
docker-compose up -d

# Access dashboard
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get OKX API Keys

1. Go to [OKX API Management](https://www.okx.com/account/my-api)
2. Create a new API key with **Read** and **Trade** permissions
3. Save your API Key, Secret Key, and Passphrase securely

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OKX credentials
nano .env  # or use any text editor
```

Add your credentials:
```
OKX_API_KEY=your_actual_api_key
OKX_SECRET_KEY=your_actual_secret_key
OKX_PASSPHRASE=your_actual_passphrase
```

### 4. Run the Bot

```bash
# Start in paper trading mode (SAFE - no real money)
python advanced_trading_bot.py
```

## ⚙️ Configuration

Edit `config.py` to customize:

### Risk Management
- `MAX_POSITION_SIZE_PERCENT` - Max % of portfolio per trade (default: 2%)
- `STOP_LOSS_PERCENT` - Stop loss percentage (default: 2%)
- `TAKE_PROFIT_PERCENT` - Take profit percentage (default: 4%)
- `MAX_DAILY_LOSS_PERCENT` - Daily loss limit (default: 5%)
- `MAX_OPEN_POSITIONS` - Max concurrent positions (default: 3)

### Trading Parameters
- `TIMEFRAME` - Candle timeframe (default: '1h')
- `PAPER_TRADING` - Enable paper trading (default: True)
- `MIN_VOLUME_USD` - Minimum 24h volume filter (default: $1M)

### Strategy Settings
- `RSI_OVERSOLD` / `RSI_OVERBOUGHT` - RSI thresholds
- `SMA_FAST` / `SMA_SLOW` - Moving average periods
- Technical indicator parameters

## 📊 How It Works

### 1. Token Scanner
- Scans all OKX markets every 15 minutes
- Filters by volume, price change, and liquidity
- Scores opportunities based on multiple factors
- Selects top 5 tokens for monitoring

### 2. Multi-Strategy Analysis
Combines 5 strategies with confidence scoring:
- **Moving Average Crossover** - Trend following
- **RSI** - Oversold/overbought detection
- **MACD** - Momentum and trend
- **Bollinger Bands** - Volatility breakouts
- **Momentum** - Price momentum analysis

Only trades when confidence ≥ 60%

### 3. Risk Management
- Calculates optimal position size (2% of capital)
- Sets automatic stop-loss (2% below entry)
- Sets take-profit target (4% above entry)
- Monitors daily loss limits
- Limits concurrent positions

### 4. Execution
- **Paper Trading**: Simulates trades, tracks performance
- **Live Trading**: Executes real orders on OKX

## 📈 Monitoring

The bot displays:
- 🔍 Market scan results with top opportunities
- 📝 Trade executions with entry/exit prices
- 🔔 Position closures (stop-loss/take-profit)
- 📊 Performance statistics (win rate, PnL, profit factor)

## 🛡️ Safety Features

- **Paper Trading Default** - No real money at risk initially
- **Stop-Loss Protection** - Automatic loss limiting
- **Daily Loss Limits** - Stops trading if daily loss exceeds 5%
- **Position Limits** - Maximum 3 concurrent positions
- **Rate Limiting** - Respects exchange API limits
- **Error Handling** - Graceful error recovery

## ⚠️ CRITICAL WARNINGS

### Before Live Trading:
1. ✅ Test in paper trading mode for AT LEAST 2 weeks
2. ✅ Verify strategies are profitable in backtests
3. ✅ Start with SMALL amounts (1-5% of capital)
4. ✅ Never invest more than you can afford to lose
5. ✅ Monitor the bot regularly
6. ✅ Understand that past performance ≠ future results

### Risk Disclosure:
- Trading cryptocurrencies carries significant risk
- You can lose your entire investment
- This bot is provided "as-is" without guarantees
- The creator is not responsible for any losses
- Always do your own research (DYOR)

## 🔧 Troubleshooting

### "Failed to connect to OKX"
- Check API credentials in `.env`
- Verify API has correct permissions
- Check internet connection

### "Daily loss limit reached"
- Bot stops trading to protect capital
- Will resume next day
- Review strategy performance

### No opportunities found
- Market conditions may not be favorable
- Adjust `MIN_VOLUME_USD` or `MIN_PRICE_CHANGE_PERCENT` in config
- Wait for next scan cycle

## 📚 Project Structure

```
├── advanced_trading_bot.py  # Main bot with trading loop
├── config.py                # Configuration settings
├── risk_manager.py          # Risk management system
├── token_scanner.py         # Market opportunity scanner
├── strategy.py              # Trading strategies
├── requirements.txt         # Python dependencies
├── .env                     # API credentials (create from .env.example)
└── trading_bot.log          # Log file
```

## 🎯 What's New (Just Added!)

- ✅ **Comprehensive Testing** - 60+ automated tests
- ✅ **Payment Integration** - Stripe subscriptions ($29-$99/month)
- ✅ **Production Infrastructure** - Docker, CI/CD, monitoring
- ✅ **Advanced Security** - 2FA, rate limiting, email verification
- ✅ **Monitoring System** - Prometheus metrics, health checks, alerts
- ✅ **Complete Deployment** - One-command cloud deployment

## 🎯 Roadmap

- ✅ Backtesting framework (COMPLETE)
- ✅ Web dashboard for monitoring (COMPLETE)
- ✅ Telegram notifications (COMPLETE)
- ✅ Payment processing (COMPLETE - Stripe)
- ✅ Production deployment (COMPLETE - Docker)
- [ ] React frontend (in progress)
- [ ] Machine learning strategy optimization
- [ ] Multi-exchange support
- [ ] Mobile apps (iOS/Android)

## 📝 License

MIT License - Use at your own risk

## 🤝 Contributing

Contributions welcome! Please test thoroughly before submitting PRs.

---

**Remember: This is a tool, not a money-printing machine. Use responsibly and never risk more than you can afford to lose.**
# forexandcryptotradingbot
