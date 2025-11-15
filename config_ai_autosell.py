"""
AI AUTO-SELL CONFIGURATION
Enable this to let AI Asset Manager automatically sell assets for profit
"""
import os

# AI Asset Manager - Auto-Sell Settings
ADMIN_ENABLE_ASSET_MANAGER = os.getenv('ADMIN_ENABLE_ASSET_MANAGER', 'true').lower() == 'true'
ADMIN_ASSET_MANAGER_AUTO_SELL = os.getenv('ADMIN_ASSET_MANAGER_AUTO_SELL', 'false').lower() == 'true'
ADMIN_ASSET_MANAGER_MIN_PROFIT = float(os.getenv('ADMIN_ASSET_MANAGER_MIN_PROFIT', '3'))  # Only sell if 3%+ profit

# Explanation:
# ADMIN_ENABLE_ASSET_MANAGER=true          → Enables AI Asset Manager (analyzes holdings)
# ADMIN_ASSET_MANAGER_AUTO_SELL=false      → Safe mode: Only recommendations (NO auto-sell)
# ADMIN_ASSET_MANAGER_AUTO_SELL=true       → Active mode: AI sells automatically
# ADMIN_ASSET_MANAGER_MIN_PROFIT=3         → Only auto-sell if profit >= 3%

print("="*70)
print("AI ASSET MANAGER CONFIGURATION")
print("="*70)
print(f"Enabled: {ADMIN_ENABLE_ASSET_MANAGER}")
print(f"Auto-Sell: {ADMIN_ASSET_MANAGER_AUTO_SELL}")
print(f"Min Profit for Auto-Sell: {ADMIN_ASSET_MANAGER_MIN_PROFIT}%")
print("="*70)
