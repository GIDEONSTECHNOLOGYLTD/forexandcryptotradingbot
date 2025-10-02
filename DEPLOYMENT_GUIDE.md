# 🚀 Deployment Guide - Free & Paid Options

## Free Deployment Options

### 1. Railway.app (Recommended - Free Tier)

**Pros:**
- ✅ Free tier: $5 credit/month (enough for 24/7 bot)
- ✅ Easy deployment
- ✅ Auto-restart on crash
- ✅ Environment variables support
- ✅ Logs and monitoring

**Setup:**
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set OKX_API_KEY=your_key
railway variables set OKX_SECRET_KEY=your_secret
railway variables set OKX_PASSPHRASE=your_passphrase

# 5. Deploy
railway up
```

**Create `railway.json`:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python advanced_trading_bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### 2. Render.com (Free Tier)

**Pros:**
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ SSL certificates
- ✅ Easy to use

**Setup:**
1. Push code to GitHub
2. Go to render.com
3. Create new "Background Worker"
4. Connect GitHub repo
5. Set start command: `python advanced_trading_bot.py`
6. Add environment variables
7. Deploy

---

### 3. Fly.io (Free Tier)

**Pros:**
- ✅ Free tier: 3 VMs
- ✅ Global deployment
- ✅ Good performance

**Setup:**
```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app
flyctl launch

# 4. Set secrets
flyctl secrets set OKX_API_KEY=your_key
flyctl secrets set OKX_SECRET_KEY=your_secret
flyctl secrets set OKX_PASSPHRASE=your_passphrase

# 5. Deploy
flyctl deploy
```

**Create `fly.toml`:**
```toml
app = "trading-bot"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  internal_port = 8080
  protocol = "tcp"
```

---

### 4. Google Cloud Platform (Free Tier)

**Pros:**
- ✅ $300 free credit for 90 days
- ✅ Always-free tier after
- ✅ Professional infrastructure

**Setup (Cloud Run):**
```bash
# 1. Create Dockerfile
# 2. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/trading-bot

# 3. Deploy
gcloud run deploy trading-bot \
  --image gcr.io/PROJECT_ID/trading-bot \
  --platform managed \
  --set-env-vars OKX_API_KEY=your_key
```

---

### 5. Oracle Cloud (Always Free)

**Pros:**
- ✅ Always free tier
- ✅ 2 VMs with 1GB RAM each
- ✅ No credit card required initially

**Setup:**
1. Create Oracle Cloud account
2. Launch VM instance (Ubuntu)
3. SSH into instance
4. Clone repo and setup
5. Run with systemd or screen

---

### 6. AWS Free Tier (12 Months)

**Pros:**
- ✅ Free for 12 months
- ✅ Professional infrastructure
- ✅ EC2 t2.micro instance

**Setup (EC2):**
1. Launch EC2 t2.micro instance
2. SSH into instance
3. Install Python and dependencies
4. Clone repo
5. Setup systemd service
6. Run bot

---

## Recommended: Railway.app

**Why Railway:**
- Easiest setup (5 minutes)
- Free tier sufficient for bot
- Auto-restart on crash
- Built-in monitoring
- Environment variables
- No credit card needed initially

**Quick Deploy:**
```bash
# 1. Install Railway
npm i -g @railway/cli

# 2. Deploy
railway login
railway init
railway up

# 3. Set environment variables in Railway dashboard
# 4. Bot runs 24/7!
```

---

## Production Deployment Checklist

### Before Deployment:
- [ ] Tested in paper trading mode for 2+ weeks
- [ ] Verified positive performance
- [ ] Reviewed all settings in config.py
- [ ] Set PAPER_TRADING = False (if going live)
- [ ] Reduced INITIAL_CAPITAL to small amount
- [ ] API keys secured in environment variables
- [ ] Logs configured properly

### Security:
- [ ] Never commit .env to git
- [ ] Use environment variables for secrets
- [ ] Enable IP whitelist on OKX API
- [ ] Set API permissions to Read + Trade only
- [ ] Monitor logs regularly
- [ ] Set up alerts for errors

### Monitoring:
- [ ] Check logs daily
- [ ] Monitor performance metrics
- [ ] Set up uptime monitoring (UptimeRobot)
- [ ] Configure error notifications
- [ ] Track capital changes

---

## Running 24/7 on Your Computer (Free)

### macOS/Linux:

**Using screen:**
```bash
# Start screen session
screen -S tradingbot

# Run bot
python advanced_trading_bot.py

# Detach: Ctrl+A, then D
# Reattach: screen -r tradingbot
```

**Using systemd (Linux):**
```bash
# Create service file
sudo nano /etc/systemd/system/tradingbot.service

# Add:
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

# Enable and start
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
```

### Windows:

**Using Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `advanced_trading_bot.py`
7. Start in: `C:\path\to\windsurf-project-2`

---

## Docker Deployment (Advanced)

**Create `Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "advanced_trading_bot.py"]
```

**Build and run:**
```bash
# Build
docker build -t trading-bot .

# Run
docker run -d \
  --name trading-bot \
  --restart unless-stopped \
  -e OKX_API_KEY=your_key \
  -e OKX_SECRET_KEY=your_secret \
  -e OKX_PASSPHRASE=your_passphrase \
  trading-bot
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  trading-bot:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./logs:/app/logs
```

---

## Cost Comparison

| Platform | Free Tier | Cost After Free | Best For |
|----------|-----------|-----------------|----------|
| Railway | $5/month credit | ~$5-10/month | Beginners |
| Render | 750 hours/month | $7/month | Simple deploy |
| Fly.io | 3 VMs free | $0-5/month | Global deploy |
| GCP | $300 credit | Pay as you go | Professional |
| Oracle | Always free | $0 | Long-term free |
| AWS | 12 months free | Pay as you go | Enterprise |
| Your PC | Free | Electricity | Testing |

---

## Monitoring & Alerts

### UptimeRobot (Free)
- Monitor bot uptime
- Email alerts when down
- Free for 50 monitors

### Better Stack (Free Tier)
- Log management
- Error tracking
- Alerts

### Sentry (Free Tier)
- Error tracking
- Performance monitoring
- Alerts

---

## Best Practice Deployment

**Recommended Setup:**
1. **Development:** Run on your computer
2. **Testing:** Deploy to Railway (free)
3. **Production:** Railway or Oracle Cloud

**Why:**
- Free or very cheap
- Easy to manage
- Auto-restart on crash
- Good monitoring
- Scalable

---

## Post-Deployment

### Daily Tasks:
- [ ] Check bot status
- [ ] Review logs
- [ ] Monitor performance
- [ ] Check for errors

### Weekly Tasks:
- [ ] Review statistics
- [ ] Analyze trades
- [ ] Adjust settings if needed
- [ ] Update documentation

### Monthly Tasks:
- [ ] Performance review
- [ ] Strategy optimization
- [ ] Cost analysis
- [ ] Backup data

---

## Emergency Procedures

### If Bot Crashes:
1. Check logs for error
2. Restart bot
3. Verify API connection
4. Check OKX status
5. Review recent trades

### If Losing Money:
1. Stop the bot immediately
2. Review trade history
3. Analyze what went wrong
4. Adjust strategy or settings
5. Test in paper mode again

### If API Issues:
1. Check OKX status
2. Verify API keys
3. Check rate limits
4. Review permissions
5. Regenerate keys if needed

---

## Scaling Up

### When to Scale:
- Bot profitable for 3+ months
- Want to trade more pairs
- Need better performance
- Want redundancy

### How to Scale:
1. **Multiple Instances:** Run separate bots for different strategies
2. **Better Infrastructure:** Move to dedicated server
3. **Database:** Add PostgreSQL for trade history
4. **Monitoring:** Professional monitoring tools
5. **Backup:** Redundant deployments

---

## Summary

**Best Free Option:** Railway.app
- Easy setup
- Free tier sufficient
- Good monitoring
- Auto-restart

**Best Always-Free:** Oracle Cloud
- Truly free forever
- More control
- Better for long-term

**Best for Testing:** Your computer
- No cost
- Easy debugging
- Full control

**Start with Railway, scale as needed!**
