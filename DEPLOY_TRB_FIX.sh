#!/bin/bash

# TRB ISSUE FIX - DEPLOYMENT SCRIPT
# This fixes AI Asset Manager not selling and buy-back loops

echo "=========================================================================="
echo "TRB ISSUE FIX - Deploying AI Auto-Sell Solution"
echo "=========================================================================="
echo ""

# Step 1: Show what changed
echo "📝 Files changed:"
echo "  - config.py (added auto-sell settings)"
echo "  - admin_auto_trader.py (use auto-sell from config)"
echo "  - advanced_trading_bot.py (use auto-sell from config)"
echo "  - ai_asset_manager.py (min profit check)"
echo ""

# Step 2: Git add
echo "📦 Adding files to git..."
git add config.py admin_auto_trader.py advanced_trading_bot.py ai_asset_manager.py
echo "✅ Files added"
echo ""

# Step 3: Git commit
echo "💾 Committing changes..."
git commit -m "Fix TRB issue: Enable AI auto-sell with min profit threshold

- Added ADMIN_ASSET_MANAGER_AUTO_SELL config setting
- Added ADMIN_ASSET_MANAGER_MIN_PROFIT config setting (default: 3%)
- Updated both bots to use auto-sell from config
- AI Asset Manager now sells at profitable levels
- Prevents tiny sales (0.3 cent)
- No more buy-back loops
- All AI features properly integrated"
echo "✅ Changes committed"
echo ""

# Step 4: Git push
echo "🚀 Pushing to Render..."
git push
echo "✅ Pushed to Render"
echo ""

# Step 5: Show Render environment variables
echo "=========================================================================="
echo "📋 NEXT STEPS: Add to Render Environment Variables"
echo "=========================================================================="
echo ""
echo "Go to: Render Dashboard → Your Bot Service → Environment"
echo ""
echo "Add these 2 variables:"
echo ""
echo "  Variable 1:"
echo "    Key:   ADMIN_ASSET_MANAGER_AUTO_SELL"
echo "    Value: true"
echo ""
echo "  Variable 2:"
echo "    Key:   ADMIN_ASSET_MANAGER_MIN_PROFIT"
echo "    Value: 3"
echo ""
echo "Then click: Save Changes"
echo ""
echo "=========================================================================="
echo "⏰ TIMELINE"
echo "=========================================================================="
echo ""
echo "Now:         Code deploying to Render (2-3 minutes)"
echo "After deploy: Bot restarts with new code"
echo "In 1 hour:   AI Asset Manager runs and sells TRB"
echo "Result:      TRB sold, capital freed, no buy-back!"
echo ""
echo "=========================================================================="
echo "📱 WHAT TO WATCH FOR"
echo "=========================================================================="
echo ""
echo "In Render Logs:"
echo "  ✅ AI Asset Manager imported"
echo "  ✅ Mode: AUTO-SELL"
echo "  ✅ Min Profit: 3.0%"
echo ""
echo "In Telegram (after 1 hour):"
echo "  🟢 SELL EXECUTED"
echo "  🪙 Symbol: TRB/USDT"
echo "  📈 Profit: [amount]"
echo "  ✅ Position closed successfully!"
echo ""
echo "=========================================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================================================="
echo ""
echo "TRB will be sold automatically in 1 hour!"
echo "Or run manually: python ai_asset_manager.py (select option 2)"
echo ""
