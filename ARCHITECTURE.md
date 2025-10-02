# 🏗️ Trading Bot Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADVANCED TRADING BOT v2.0                     │
│                         (Main Controller)                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌──────────────────┐     ┌─────────────────┐
│ Token Scanner │      │ Strategy Engine  │     │  Risk Manager   │
│               │      │                  │     │                 │
│ • Scan markets│      │ • 5 Strategies   │     │ • Position size │
│ • Filter      │      │ • Indicators     │     │ • Stop-loss     │
│ • Score       │      │ • Confidence     │     │ • Take-profit   │
│ • Rank top 5  │      │ • Market analysis│     │ • Daily limits  │
└───────┬───────┘      └────────┬─────────┘     └────────┬────────┘
        │                       │                        │
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    OKX Exchange API   │
                    │                       │
                    │ • Market data         │
                    │ • Order execution     │
                    │ • Account info        │
                    └───────────────────────┘
```

## Component Details

### 1. Main Controller (`advanced_trading_bot.py`)

**Responsibilities:**
- Initialize all components
- Run main trading loop
- Coordinate between modules
- Handle errors and logging
- Display statistics

**Flow:**
```
START
  ↓
Initialize Exchange
  ↓
Create Risk Manager
  ↓
Create Token Scanner
  ↓
Create Strategy Engine
  ↓
LOOP:
  ├─ Scan Markets (every 15 min)
  ├─ Check Open Positions
  ├─ Analyze Active Tokens
  ├─ Generate Signals
  ├─ Execute Trades
  ├─ Display Stats (every 5 iterations)
  └─ Wait 60 seconds
```

### 2. Token Scanner (`token_scanner.py`)

**Purpose:** Find the best trading opportunities

**Process:**
```
Fetch All Tickers
  ↓
Filter by Quote Currency (USDT, USDC, USD)
  ↓
Filter by Volume (> $1M)
  ↓
Calculate Opportunity Score:
  ├─ Volume Score (0-3 points)
  ├─ Price Change Score (0-3 points)
  └─ Spread Score (0-2 points)
  ↓
Sort by Score
  ↓
Return Top 5 Opportunities
```

**Scoring System:**
```
Volume Score:
  > $10M  → 3 points
  > $5M   → 2 points
  > $1M   → 1 point

Price Change Score:
  2-5%    → 3 points (ideal)
  5-10%   → 2 points (good)
  > 10%   → 1 point (too volatile)

Spread Score:
  < 0.1%  → 2 points (tight)
  < 0.5%  → 1 point (acceptable)
```

### 3. Strategy Engine (`strategy.py`)

**Purpose:** Analyze tokens and generate trading signals

**Technical Indicators:**
```
Price Data
  ↓
Calculate Indicators:
  ├─ SMA (20, 50)
  ├─ EMA (12, 26)
  ├─ RSI (14)
  ├─ MACD (12, 26, 9)
  ├─ Bollinger Bands (20, 2)
  ├─ OBV
  └─ Momentum
  ↓
Apply 5 Strategies:
  ├─ MA Crossover (2 points)
  ├─ RSI (1 point)
  ├─ MACD (2 points)
  ├─ Bollinger Bands (1 point)
  └─ Momentum (1 point)
  ↓
Calculate Confidence:
  Buy Signals / Total Signals × 100%
  ↓
Return Signal if Confidence ≥ 60%
```

**Strategy Details:**

1. **Moving Average Crossover** (Weight: 2)
   - Golden Cross: SMA20 crosses above SMA50 → BUY
   - Death Cross: SMA20 crosses below SMA50 → SELL

2. **RSI** (Weight: 1)
   - RSI < 30 → BUY (oversold)
   - RSI > 70 → SELL (overbought)

3. **MACD** (Weight: 2)
   - MACD crosses above signal → BUY
   - MACD crosses below signal → SELL

4. **Bollinger Bands** (Weight: 1)
   - Price touches lower band → BUY
   - Price touches upper band → SELL

5. **Momentum** (Weight: 1)
   - Momentum > 3% → BUY
   - Momentum < -3% → SELL

**Confidence Calculation Example:**
```
Buy Signals: 5 (MA=2, RSI=1, MACD=2)
Sell Signals: 2 (BB=1, Momentum=1)
Total: 7

Confidence = 5/7 × 100% = 71.4%
Result: BUY signal (≥ 60%)
```

### 4. Risk Manager (`risk_manager.py`)

**Purpose:** Protect capital and manage positions

**Position Sizing:**
```
Current Capital: $10,000
Max Position %: 2%
Entry Price: $100

Position Value = $10,000 × 2% = $200
Position Size = $200 / $100 = 2 units
```

**Stop-Loss Calculation:**
```
Entry Price: $100
Stop-Loss %: 2%

Long Position:
  Stop-Loss = $100 × (1 - 0.02) = $98

Short Position:
  Stop-Loss = $100 × (1 + 0.02) = $102
```

**Take-Profit Calculation:**
```
Entry Price: $100
Take-Profit %: 4%

Long Position:
  Take-Profit = $100 × (1 + 0.04) = $104

Short Position:
  Take-Profit = $100 × (1 - 0.04) = $96
```

**Risk Checks:**
```
Before Each Trade:
  ├─ Daily Loss < 5%? ✓
  ├─ Open Positions < 3? ✓
  └─ Capital Available? ✓
    ↓
  ALLOW TRADE
```

**Position Monitoring:**
```
Every Iteration:
  For Each Open Position:
    ├─ Get Current Price
    ├─ Check Stop-Loss
    ├─ Check Take-Profit
    └─ Close if Hit
```

## Data Flow

### Trade Execution Flow

```
1. SCAN PHASE
   Token Scanner → Top 5 Opportunities
   
2. ANALYSIS PHASE
   For each opportunity:
     Fetch OHLCV Data
       ↓
     Add Technical Indicators
       ↓
     Run 5 Strategies
       ↓
     Calculate Confidence
       ↓
     Generate Signal (if ≥ 60%)

3. RISK CHECK PHASE
   Signal Generated
     ↓
   Check Trading Allowed?
     ├─ Daily loss OK?
     ├─ Position slots available?
     └─ Capital sufficient?
       ↓
   Calculate Position Size
     ↓
   Calculate Stop-Loss
     ↓
   Calculate Take-Profit

4. EXECUTION PHASE
   Paper Trading:
     ├─ Log trade details
     ├─ Update risk manager
     └─ Display notification
   
   Live Trading:
     ├─ Submit order to OKX
     ├─ Wait for confirmation
     ├─ Update risk manager
     └─ Log execution

5. MONITORING PHASE
   Every iteration:
     ├─ Check current price
     ├─ Compare to stop-loss
     ├─ Compare to take-profit
     └─ Close if triggered
```

## Configuration Hierarchy

```
config.py (Global Settings)
  ├─ Exchange Settings
  │   ├─ EXCHANGE = 'okx'
  │   ├─ API credentials
  │   └─ TIMEFRAME = '1h'
  │
  ├─ Risk Management
  │   ├─ MAX_POSITION_SIZE_PERCENT = 2.0
  │   ├─ STOP_LOSS_PERCENT = 2.0
  │   ├─ TAKE_PROFIT_PERCENT = 4.0
  │   ├─ MAX_DAILY_LOSS_PERCENT = 5.0
  │   └─ MAX_OPEN_POSITIONS = 3
  │
  ├─ Scanner Settings
  │   ├─ MIN_VOLUME_USD = 1000000
  │   ├─ MIN_PRICE_CHANGE_PERCENT = 2.0
  │   └─ SCAN_INTERVAL_MINUTES = 15
  │
  └─ Strategy Parameters
      ├─ RSI_OVERSOLD = 30
      ├─ RSI_OVERBOUGHT = 70
      ├─ SMA_FAST = 20
      ├─ SMA_SLOW = 50
      └─ ... (more indicators)
```

## Error Handling

```
Try-Catch Hierarchy:

Main Loop
  ├─ Try: Run iteration
  ├─ Catch KeyboardInterrupt: Clean shutdown
  └─ Catch Exception: Log error, continue

Exchange Operations
  ├─ Try: API call
  ├─ Catch RateLimitError: Wait and retry
  ├─ Catch NetworkError: Retry with backoff
  └─ Catch Exception: Log and skip

Trade Execution
  ├─ Try: Execute order
  ├─ Catch InsufficientFunds: Log warning
  ├─ Catch InvalidOrder: Log error
  └─ Catch Exception: Log critical error
```

## Performance Tracking

```
Risk Manager Statistics:
  ├─ Total Trades
  ├─ Winning Trades
  ├─ Losing Trades
  ├─ Win Rate (%)
  ├─ Total PnL ($)
  ├─ Total PnL (%)
  ├─ Average Win ($)
  ├─ Average Loss ($)
  ├─ Profit Factor
  ├─ Current Capital
  ├─ Daily PnL
  └─ Open Positions

Trade Record:
  ├─ Symbol
  ├─ Side (long/short)
  ├─ Entry Price
  ├─ Exit Price
  ├─ Amount
  ├─ Entry Time
  ├─ Exit Time
  ├─ Duration
  ├─ PnL ($)
  ├─ PnL (%)
  ├─ Stop-Loss Price
  └─ Take-Profit Price
```

## Security Measures

```
API Key Protection:
  ├─ Stored in .env file
  ├─ .env in .gitignore
  ├─ Never logged
  └─ Never displayed

Rate Limiting:
  ├─ enableRateLimit: True
  ├─ Automatic throttling
  └─ Retry with backoff

Paper Trading:
  ├─ Default mode
  ├─ No real orders
  └─ Safe testing

Risk Limits:
  ├─ Position size caps
  ├─ Daily loss limits
  ├─ Stop-loss protection
  └─ Position count limits
```

## Logging System

```
Log Levels:
  ├─ INFO: Normal operations
  ├─ WARNING: Potential issues
  ├─ ERROR: Recoverable errors
  └─ CRITICAL: System failures

Log Destinations:
  ├─ Console (colored output)
  └─ File (trading_bot.log)

Logged Events:
  ├─ Bot start/stop
  ├─ Market scans
  ├─ Signal generation
  ├─ Trade execution
  ├─ Position closures
  ├─ Errors and warnings
  └─ Performance statistics
```

## Scalability Considerations

**Current Design:**
- Single exchange (OKX)
- Single timeframe (1h)
- Max 5 active symbols
- Max 3 positions

**Future Expansion:**
- Multi-exchange support
- Multi-timeframe analysis
- Unlimited symbols
- Portfolio optimization
- Machine learning integration
- Web dashboard
- Mobile notifications

---

This architecture prioritizes **safety, reliability, and transparency** over complexity. Every component is designed to protect your capital while seeking profitable opportunities.
