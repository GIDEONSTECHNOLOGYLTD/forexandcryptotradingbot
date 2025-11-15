"""
Profit Protector V2 - AGGRESSIVE PROFIT LOCKING
Never let profits turn into losses!
Sell immediately when in profit before it disappears
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class AggressiveProfitProtector:
    """
    Aggressive profit protection strategy:
    1. Lock in profits FAST (at 1%, 2%, 3% - don't wait!)
    2. Move stop to break-even immediately when in profit
    3. Trail very tight (0.5% below current) to lock gains
    4. Never let profits turn into losses
    """
    
    def __init__(self):
        self.positions = {}
        
    def add_position(self, symbol: str, entry_price: float, amount: float, 
                    side: str = 'long', stop_loss_pct: float = 0.01):
        """
        Add position with TIGHT stop loss (1% default)
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            amount: Position size
            side: 'long' or 'short'
            stop_loss_pct: Stop loss % (default 1% - tight!)
        """
        position_id = f"{symbol}_{datetime.now().timestamp()}"
        
        # Calculate initial stop loss (1% default - TIGHT!)
        if side == 'long':
            stop_loss = entry_price * (1 - stop_loss_pct)
        else:
            stop_loss = entry_price * (1 + stop_loss_pct)
        
        self.positions[position_id] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'amount': amount,
            'side': side,
            'stop_loss': stop_loss,
            'highest_price': entry_price,  # Track peak
            'break_even_activated': False,
            'profit_locked': False,
            'entry_time': datetime.now()
        }
        
        logger.info(f"✅ Position added with TIGHT 1% stop: {symbol} @ ${entry_price:.2f}")
        
        return position_id
    
    def check_position(self, position_id: str, current_price: float) -> List[Dict]:
        """
        Check position and return actions to take
        
        STRATEGY:
        1. If ANY profit (even 0.5%) → Move stop to break-even
        2. If profit >= 1% → Take profit immediately OR trail tight
        3. If profit >= 2% → SELL IMMEDIATELY (lock gains!)
        4. If profit >= 3% → SELL IMMEDIATELY (excellent gains!)
        
        Returns:
            list: Actions to take [{'action': 'exit', 'reason': '...'}]
        """
        if position_id not in self.positions:
            return []
        
        position = self.positions[position_id]
        actions = []
        
        entry_price = position['entry_price']
        side = position['side']
        
        # Calculate profit
        if side == 'long':
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100
        
        profit_usd = (current_price - entry_price) * position['amount'] if side == 'long' else \
                     (entry_price - current_price) * position['amount']
        
        # Update highest price (for trailing)
        if side == 'long' and current_price > position['highest_price']:
            position['highest_price'] = current_price
        elif side == 'short' and current_price < position['highest_price']:
            position['highest_price'] = current_price
        
        # ═══════════════════════════════════════════════════════════
        # AGGRESSIVE PROFIT PROTECTION LOGIC
        # ═══════════════════════════════════════════════════════════
        
        # 1. CHECK STOP LOSS FIRST (prevent losses!)
        if side == 'long':
            if current_price <= position['stop_loss']:
                actions.append({
                    'action': 'exit',
                    'reason': f'STOP_LOSS (${profit_usd:+.2f})',
                    'profit_pct': profit_pct,
                    'profit_usd': profit_usd
                })
                logger.warning(f"🛑 Stop loss hit: {position['symbol']} - {profit_pct:+.2f}%")
                return actions
        else:
            if current_price >= position['stop_loss']:
                actions.append({
                    'action': 'exit',
                    'reason': f'STOP_LOSS (${profit_usd:+.2f})',
                    'profit_pct': profit_pct,
                    'profit_usd': profit_usd
                })
                logger.warning(f"🛑 Stop loss hit: {position['symbol']} - {profit_pct:+.2f}%")
                return actions
        
        # 2. IN PROFIT? (Even 0.5% counts!)
        if profit_pct > 0.5:  # ANY profit above 0.5%
            
            # A. Move stop to break-even immediately (PROTECT GAINS!)
            if not position['break_even_activated']:
                position['stop_loss'] = entry_price
                position['break_even_activated'] = True
                logger.info(f"🎯 BREAK-EVEN ACTIVATED! {position['symbol']} @ {profit_pct:.2f}% - Can't lose now!")
            
            # B. AGGRESSIVE PROFIT TAKING
            
            # If 3%+ profit → SELL IMMEDIATELY (excellent gains!)
            if profit_pct >= 3.0 and not position.get('profit_locked'):
                actions.append({
                    'action': 'exit',
                    'reason': f'PROFIT_3_PCT (+${profit_usd:.2f})',
                    'profit_pct': profit_pct,
                    'profit_usd': profit_usd
                })
                position['profit_locked'] = True
                logger.info(f"💰 TAKING 3% PROFIT! {position['symbol']} = +${profit_usd:.2f}")
                return actions
            
            # If 2%+ profit → SELL IMMEDIATELY (good gains!)
            elif profit_pct >= 2.0 and not position.get('profit_locked'):
                actions.append({
                    'action': 'exit',
                    'reason': f'PROFIT_2_PCT (+${profit_usd:.2f})',
                    'profit_pct': profit_pct,
                    'profit_usd': profit_usd
                })
                position['profit_locked'] = True
                logger.info(f"💰 TAKING 2% PROFIT! {position['symbol']} = +${profit_usd:.2f}")
                return actions
            
            # If 1%+ profit → Trail VERY tight (0.5% below current)
            elif profit_pct >= 1.0:
                if side == 'long':
                    tight_trailing_stop = current_price * 0.995  # 0.5% below current
                    if tight_trailing_stop > position['stop_loss']:
                        position['stop_loss'] = tight_trailing_stop
                        logger.info(f"🛡️ Tight trailing @ {profit_pct:.2f}%: ${tight_trailing_stop:.2f}")
                else:
                    tight_trailing_stop = current_price * 1.005
                    if tight_trailing_stop < position['stop_loss']:
                        position['stop_loss'] = tight_trailing_stop
                        logger.info(f"🛡️ Tight trailing @ {profit_pct:.2f}%: ${tight_trailing_stop:.2f}")
            
            # If 0.5-1% profit → Trail tight (1% below current)
            else:  # 0.5% - 1% profit
                if side == 'long':
                    trailing_stop = current_price * 0.99  # 1% below current
                    if trailing_stop > position['stop_loss']:
                        position['stop_loss'] = trailing_stop
                        logger.info(f"🛡️ Trailing @ {profit_pct:.2f}%: ${trailing_stop:.2f}")
                else:
                    trailing_stop = current_price * 1.01
                    if trailing_stop < position['stop_loss']:
                        position['stop_loss'] = trailing_stop
                        logger.info(f"🛡️ Trailing @ {profit_pct:.2f}%: ${trailing_stop:.2f}")
        
        # 3. CHECK IF PROFIT DISAPPEARED (price dropped from peak)
        if profit_pct < 0:  # In loss now
            # Already at stop loss, will trigger in next check
            pass
        elif profit_pct > 0 and position['break_even_activated']:
            # We're in profit with break-even protection
            # Check if price dropped significantly from peak
            peak = position['highest_price']
            if side == 'long':
                drop_from_peak = ((peak - current_price) / peak) * 100
                if drop_from_peak >= 1.0:  # Dropped 1% from peak
                    # Price is falling - lock in whatever profit we have!
                    actions.append({
                        'action': 'exit',
                        'reason': f'PROFIT_PROTECTION (peak drop, +${profit_usd:.2f})',
                        'profit_pct': profit_pct,
                        'profit_usd': profit_usd
                    })
                    logger.info(f"💰 Profit protection! Dropped {drop_from_peak:.1f}% from peak - selling @ +{profit_pct:.2f}%")
                    return actions
        
        return actions
    
    def remove_position(self, position_id: str):
        """Remove position after closing"""
        if position_id in self.positions:
            del self.positions[position_id]
            logger.info(f"✅ Position removed: {position_id}")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛡️ AGGRESSIVE PROFIT PROTECTOR V2")
    print("   Never let profits turn into losses!")
    print("="*70 + "\n")
    
    protector = AggressiveProfitProtector()
    
    # Scenario 1: Quick profit
    print("📊 Scenario 1: Quick 2% profit\n")
    pos_id = protector.add_position('BTC/USDT', 45000, 0.01, 'long')
    
    prices = [45000, 45450, 45900]  # 0%, +1%, +2%
    for price in prices:
        profit_pct = ((price - 45000) / 45000) * 100
        print(f"Price: ${price:,} (+{profit_pct:.1f}%)")
        actions = protector.check_position(pos_id, price)
        if actions:
            print(f"  → ACTION: {actions[0]['action']} - {actions[0]['reason']}")
            print(f"  → PROFIT: ${actions[0]['profit_usd']:.2f}")
            break
        else:
            pos = protector.positions[pos_id]
            print(f"  → Stop Loss: ${pos['stop_loss']:,.2f}")
            if pos['break_even_activated']:
                print(f"  → ✅ Break-even protected!")
    
    print("\n" + "="*70)
    print("✅ Strategy: Lock in profits FAST, never let them disappear!")
    print("="*70 + "\n")
