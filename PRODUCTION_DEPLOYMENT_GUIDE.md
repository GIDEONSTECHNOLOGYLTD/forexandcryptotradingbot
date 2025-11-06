# 🚀 Production Deployment Guide - Complete Setup

This guide will take you from development to a production-ready trading bot platform that can handle thousands of users.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Testing](#testing)
4. [Payment Setup (Stripe)](#payment-setup)
5. [Security Configuration](#security-configuration)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Monitoring Setup](#monitoring-setup)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Go Live Checklist](#go-live-checklist)

---

## 1. Prerequisites

### Required Accounts
- ✅ GitHub account (for code & CI/CD)
- ✅ MongoDB Atlas (free tier available)
- ✅ Stripe account (for payments)
- ✅ OKX exchange account + API keys
- ✅ Domain name (for production)
- ✅ Cloud provider (AWS/DigitalOcean/Heroku)

### Local Development Tools
```bash
# Install Docker
brew install docker docker-compose  # macOS
# or download from https://www.docker.com/

# Install Python 3.11+
brew install python@3.11

# Install git
brew install git
```

---

## 2. Development Setup

### Step 1: Clone and Install
```bash
# Clone repository
git clone https://github.com/yourusername/forexandcryptotradingbot.git
cd forexandcryptotradingbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables:**
```env
# OKX API (Get from https://www.okx.com/account/my-api)
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase

# MongoDB (Get from https://cloud.mongodb.com)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/trading_bot

# JWT Secret (Generate random string)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Stripe (Get from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Gmail or SendGrid)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram (Optional, from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Environment
ENVIRONMENT=development
PAPER_TRADING=true
```

### Step 3: Setup MongoDB
```bash
# Option 1: MongoDB Atlas (Recommended - Free)
1. Go to https://cloud.mongodb.com
2. Create free cluster
3. Create database user
4. Whitelist your IP (0.0.0.0/0 for now)
5. Get connection string
6. Add to .env as MONGODB_URI

# Option 2: Local MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0
MONGODB_URI=mongodb://localhost:27017/trading_bot
```

---

## 3. Testing

### Run All Tests
```bash
# Run unit tests
pytest tests/unit -v

# Run with coverage
pytest tests/unit --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Manual Testing
```bash
# Test web dashboard
python web_dashboard.py
# Open http://localhost:8000/docs

# Test trading bot (paper trading)
python advanced_trading_bot.py
```

---

## 4. Payment Setup (Stripe)

### Step 1: Create Stripe Account
1. Go to https://stripe.com
2. Sign up for free account
3. Activate account (test mode first)

### Step 2: Create Products & Prices
```bash
# In Stripe Dashboard:
1. Go to Products
2. Create 3 products:
   
   Product 1: Pro Plan
   - Price: $29/month
   - Recurring billing
   - Copy Price ID → STRIPE_PRO_PRICE_ID
   
   Product 2: Enterprise Plan
   - Price: $99/month
   - Recurring billing
   - Copy Price ID → STRIPE_ENTERPRISE_PRICE_ID
```

### Step 3: Setup Webhooks
```bash
# In Stripe Dashboard:
1. Go to Developers > Webhooks
2. Add endpoint: https://yourdomain.com/api/webhooks/stripe
3. Select events:
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.paid
   - invoice.payment_failed
4. Copy webhook secret → STRIPE_WEBHOOK_SECRET
```

### Step 4: Test Payment Integration
```bash
# Use Stripe test cards
python -c "
from payment_integration import PaymentProcessor
processor = PaymentProcessor()

# Test card: 4242 4242 4242 4242
print('Payment system ready!')
"
```

---

## 5. Security Configuration

### Step 1: Generate Secure Keys
```bash
# Generate JWT secret
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Generate API keys for users
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Enable Security Features
```python
# In web_dashboard.py, add middleware:
from security import rate_limit_middleware, security_headers_middleware

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(security_headers_middleware)
```

### Step 3: Setup Email Verification
```bash
# For Gmail, enable 2FA and create App Password:
1. Go to Google Account settings
2. Security > 2-Step Verification
3. App passwords > Generate
4. Copy password to .env as SMTP_PASSWORD
```

### Step 4: SSL Certificate (Production)
```bash
# Use Let's Encrypt (free)
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

---

## 6. Docker Deployment

### Step 1: Build Docker Image
```bash
# Build image
docker build -t trading-bot:latest .

# Test locally
docker run -p 8000:8000 --env-file .env trading-bot:latest
```

### Step 2: Docker Compose (Complete Stack)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web

# Stop all services
docker-compose down
```

### Services Running:
- **mongodb**: Database (port 27017)
- **redis**: Caching (port 6379)
- **web**: Dashboard API (port 8000)
- **bot**: Trading bot
- **nginx**: Reverse proxy (port 80/443)

---

## 7. Cloud Deployment

### Option A: DigitalOcean (Recommended - Easy)

**1. Create Droplet**
```bash
# Size: $12/month (2GB RAM, 1 CPU)
# Image: Ubuntu 22.04
# Options: Enable monitoring, backups
```

**2. Initial Setup**
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Clone repository
git clone https://github.com/yourusername/forexandcryptotradingbot.git
cd forexandcryptotradingbot
```

**3. Configure & Deploy**
```bash
# Create .env file
nano .env
# (Add all production credentials)

# Start services
docker-compose up -d

# Setup firewall
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

**4. Domain Setup**
```bash
# Point your domain to droplet IP
# A record: @ → your-droplet-ip
# A record: www → your-droplet-ip

# Update nginx.conf with your domain
nano nginx.conf
# Change server_name to yourdomain.com

# Restart nginx
docker-compose restart nginx
```

### Option B: AWS (Scalable)

**Using AWS ECS (Elastic Container Service):**
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name trading-bot

# 2. Build and push image
docker build -t trading-bot .
docker tag trading-bot:latest YOUR_ECR_URI/trading-bot:latest
docker push YOUR_ECR_URI/trading-bot:latest

# 3. Create ECS cluster & service
# Follow AWS ECS wizard or use Terraform
```

### Option C: Heroku (Simplest)

```bash
# 1. Install Heroku CLI
brew install heroku/brew/heroku

# 2. Login
heroku login

# 3. Create app
heroku create trading-bot-platform

# 4. Add MongoDB addon
heroku addons:create mongolab:sandbox

# 5. Set environment variables
heroku config:set OKX_API_KEY=xxx
heroku config:set JWT_SECRET_KEY=xxx
# ... (all other vars)

# 6. Deploy
git push heroku main

# 7. Scale
heroku ps:scale web=1 bot=1
```

---

## 8. Monitoring Setup

### Step 1: Prometheus + Grafana
```bash
# Add to docker-compose.yml:
# (Already included in the file)

# Access Grafana
open http://localhost:3000
# Default: admin/admin

# Add Prometheus data source
# URL: http://prometheus:9090

# Import dashboard
# Use ID: 1860 (Node Exporter)
```

### Step 2: Sentry (Error Tracking)
```bash
# 1. Create account at sentry.io
# 2. Create project (Python/FastAPI)
# 3. Get DSN

# Add to .env
SENTRY_DSN=https://xxx@sentry.io/xxx

# Initialize in code:
import sentry_sdk
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
```

### Step 3: Uptime Monitoring
```bash
# Use free services:
# - UptimeRobot (https://uptimerobot.com)
# - Pingdom
# - StatusCake

# Monitor:
# - https://yourdomain.com/health
# - Alert via email/SMS if down
```

---

## 9. CI/CD Pipeline

### GitHub Actions (Already Set Up)

**Workflow File:** `.github/workflows/ci-cd.yml`

**What It Does:**
1. ✅ Runs tests on every push
2. ✅ Checks code quality (linting)
3. ✅ Scans for security vulnerabilities
4. ✅ Builds Docker image
5. ✅ Deploys to staging (develop branch)
6. ✅ Deploys to production (main branch)

**Setup Secrets:**
```bash
# In GitHub: Settings > Secrets > Actions

# Add these secrets:
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
STAGING_HOST
STAGING_USER
STAGING_SSH_KEY
PRODUCTION_HOST
PRODUCTION_USER
PRODUCTION_SSH_KEY
SLACK_WEBHOOK (optional)
```

---

## 10. Go Live Checklist

### Pre-Launch (Development → Staging)
- [ ] All tests passing (100+ tests)
- [ ] Code coverage > 70%
- [ ] Security scan passed
- [ ] MongoDB Atlas configured
- [ ] Stripe test mode working
- [ ] Email system working
- [ ] Rate limiting enabled
- [ ] Docker build successful
- [ ] Deploy to staging
- [ ] Test on staging for 1 week

### Launch Preparation
- [ ] Switch Stripe to live mode
- [ ] Update API keys to production
- [ ] Enable HTTPS/SSL
- [ ] Set PAPER_TRADING=false (carefully!)
- [ ] Configure backups (MongoDB)
- [ ] Setup monitoring alerts
- [ ] Configure error tracking
- [ ] Enable firewall rules
- [ ] Update CORS origins
- [ ] Setup CDN (CloudFlare)

### Launch Day
- [ ] Final backup of database
- [ ] Deploy to production
- [ ] Smoke test all features
- [ ] Monitor for 24 hours
- [ ] Have rollback plan ready

### Post-Launch (Week 1)
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review user feedback
- [ ] Optimize slow queries
- [ ] Scale if needed
- [ ] Update documentation

---

## 🎯 Quick Start Commands

### Development
```bash
# Install
pip install -r requirements.txt

# Test
pytest

# Run
python web_dashboard.py
```

### Production (Docker)
```bash
# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f

# Update
git pull
docker-compose up -d --build
```

---

## 📊 Expected Costs (Monthly)

### Minimal Setup (~$25/month)
- DigitalOcean Droplet: $12/month
- MongoDB Atlas: Free
- Stripe: Free (2.9% + $0.30 per transaction)
- Domain: ~$10/year
- Email: Free (Gmail)

### Scaling (100+ users) (~$100/month)
- DigitalOcean: $48/month (4GB RAM)
- MongoDB Atlas: $57/month (M10)
- Cloudflare: Free
- Monitoring: Free (Grafana Cloud)

### Enterprise (1000+ users) (~$500/month)
- AWS ECS: ~$200/month
- MongoDB Atlas: ~$200/month
- Redis Cache: ~$50/month
- Load Balancer: ~$20/month
- Monitoring: ~$30/month

---

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check MongoDB URI
echo $MONGODB_URI

# Test connection
mongosh "$MONGODB_URI"

# Whitelist IP in MongoDB Atlas
```

**2. Docker Build Failed**
```bash
# Clear cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

**3. Rate Limiting Too Strict**
```python
# In security.py, adjust limits:
rate_limiter = RateLimiter(
    requests_per_minute=120,  # Increase
    requests_per_hour=2000
)
```

**4. Memory Issues**
```bash
# Increase Docker memory
# Docker Desktop > Settings > Resources > Memory: 4GB

# Or optimize code
# Add pagination, caching, cleanup
```

---

## 📞 Support & Resources

- **Documentation**: See all MD files in repo
- **Issues**: GitHub Issues page
- **Community**: Discord server (create one)
- **Email**: your-support@email.com

---

## 🎉 Success Metrics

After going live, track:
- ✅ Users registered
- ✅ Active subscriptions
- ✅ Monthly Recurring Revenue (MRR)
- ✅ Trading volume
- ✅ System uptime (target: 99.9%)
- ✅ Response time (target: <200ms)
- ✅ Error rate (target: <0.1%)

---

**You're ready to launch! 🚀**

Start with development setup, test thoroughly, then deploy to production. Good luck!
