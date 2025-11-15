"""
AI Asset Manager API Routes for Mobile App
Add these routes to web_dashboard.py or import this file
"""

from flask import jsonify, request
from datetime import datetime
from bson import ObjectId
from functools import wraps

# Assuming you have these imports from your existing code:
# from web_dashboard import app, db, token_required, get_current_user
# from ai_asset_manager import AIAssetManager

# ============================================================================
# AI ASSET MANAGER API ROUTES
# ============================================================================

@app.route('/api/ai-asset-manager/status', methods=['GET'])
@token_required
def get_asset_manager_status():
    """
    Get current AI Asset Manager status and configuration
    
    Returns:
        - enabled: bool
        - auto_sell: bool
        - min_profit_percent: float
        - last_check: ISO timestamp
        - holdings_analyzed: int
        - recommendations_count: {sell, hold, buy}
    """
    try:
        user = get_current_user()
        
        # Get user's asset manager configuration from database
        user_data = db.users.find_one(
            {'_id': ObjectId(user['_id'])},
            {'asset_manager_config': 1, 'okx_api_key': 1}
        )
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Get config or use defaults
        config = user_data.get('asset_manager_config', {})
        enabled = config.get('enabled', False)
        auto_sell = config.get('auto_sell', False)
        min_profit_percent = config.get('min_profit_percent', 3.0)
        
        # Get last analysis time (you may want to store this in DB)
        last_check = config.get('last_check', datetime.utcnow().isoformat() + 'Z')
        
        # Count holdings and recommendations
        # (You'll need to integrate with your AI Asset Manager instance)
        holdings_analyzed = 0
        recommendations = {'sell': 0, 'hold': 0, 'buy': 0}
        
        # If AI is enabled and user has OKX connected, get real data
        if enabled and user_data.get('okx_api_key'):
            try:
                # Get holdings analysis from AI Asset Manager
                # This depends on how you've structured your AIAssetManager
                # Example:
                # asset_manager = get_user_asset_manager(user['_id'])
                # if asset_manager:
                #     holdings_data = asset_manager.analyze_all_holdings()
                #     holdings_analyzed = len(holdings_data)
                #     for holding in holdings_data:
                #         rec = holding.get('ai_recommendation', 'HOLD')
                #         if rec in ['STRONG_SELL', 'SELL']:
                #             recommendations['sell'] += 1
                #         elif rec in ['BUY', 'STRONG_BUY']:
                #             recommendations['buy'] += 1
                #         else:
                #             recommendations['hold'] += 1
                pass
            except Exception as e:
                print(f"Error getting holdings data: {e}")
        
        return jsonify({
            'enabled': enabled,
            'auto_sell': auto_sell,
            'min_profit_percent': min_profit_percent,
            'last_check': last_check,
            'holdings_analyzed': holdings_analyzed,
            'recommendations_count': recommendations
        })
        
    except Exception as e:
        print(f"Error in get_asset_manager_status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-asset-manager/holdings', methods=['GET'])
@token_required
def get_holdings_analysis():
    """
    Get all holdings with AI analysis and recommendations
    
    Returns:
        holdings: Array of holding objects with AI analysis
    """
    try:
        user = get_current_user()
        
        # Get user config
        user_data = db.users.find_one(
            {'_id': ObjectId(user['_id'])},
            {'asset_manager_config': 1, 'okx_api_key': 1, 'okx_secret_key': 1, 'okx_passphrase': 1}
        )
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        config = user_data.get('asset_manager_config', {})
        enabled = config.get('enabled', False)
        
        if not enabled:
            return jsonify({
                'holdings': [],
                'message': 'AI Asset Manager is disabled'
            })
        
        # Check if user has OKX credentials
        if not user_data.get('okx_api_key'):
            return jsonify({
                'holdings': [],
                'message': 'OKX not connected'
            })
        
        holdings = []
        
        try:
            # INTEGRATE WITH YOUR AI ASSET MANAGER HERE
            # Example implementation:
            
            # 1. Get or create AIAssetManager instance for this user
            # from ai_asset_manager import AIAssetManager
            # asset_manager = AIAssetManager(
            #     exchange=user_exchange,  # Your OKX exchange instance
            #     db=db,
            #     telegram=None,  # Or user's telegram instance
            #     risk_manager=risk_manager
            # )
            
            # 2. Get holdings with AI analysis
            # holdings_data = asset_manager.get_all_holdings()
            # for holding in holdings_data:
            #     analysis = asset_manager.analyze_holding(holding)
            #     
            #     holdings.append({
            #         'symbol': holding['symbol'],
            #         'currency': holding['currency'],
            #         'amount': holding['total_amount'],
            #         'value_usd': holding['value_usd'],
            #         'current_price': holding['current_price'],
            #         'ai_recommendation': analysis.get('recommendation', 'HOLD'),
            #         'estimated_profit_pct': analysis.get('estimated_profit_pct', 0),
            #         'estimated_profit_usd': analysis.get('estimated_profit_usd', 0),
            #         'urgency': analysis.get('urgency', 'LOW'),
            #         'reasoning': analysis.get('reasoning', []),
            #         'indicators': {
            #             'rsi': analysis.get('rsi', 50),
            #             'macd_trend': analysis.get('macd_trend', 'NEUTRAL'),
            #             'bollinger_position': analysis.get('bollinger_position', 50),
            #             'order_book_pressure': analysis.get('order_book_pressure', 'NEUTRAL')
            #         }
            #     })
            
            # TEMPORARY: Return example data for testing
            holdings = []
            
        except Exception as e:
            print(f"Error analyzing holdings: {e}")
            return jsonify({'error': f'Failed to analyze holdings: {str(e)}'}), 500
        
        return jsonify({
            'holdings': holdings,
            'total_count': len(holdings),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        print(f"Error in get_holdings_analysis: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-asset-manager/config', methods=['PUT'])
@token_required
def update_asset_manager_config():
    """
    Update AI Asset Manager configuration
    
    Request Body:
        - enabled: bool
        - auto_sell: bool
        - min_profit_percent: float
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input
        enabled = data.get('enabled', False)
        auto_sell = data.get('auto_sell', False)
        min_profit_percent = data.get('min_profit_percent', 3.0)
        
        # Validate min_profit_percent
        if not isinstance(min_profit_percent, (int, float)):
            return jsonify({'error': 'min_profit_percent must be a number'}), 400
        
        if min_profit_percent < 0.1 or min_profit_percent > 100:
            return jsonify({'error': 'min_profit_percent must be between 0.1 and 100'}), 400
        
        # Update user configuration in database
        result = db.users.update_one(
            {'_id': ObjectId(user['_id'])},
            {
                '$set': {
                    'asset_manager_config': {
                        'enabled': bool(enabled),
                        'auto_sell': bool(auto_sell),
                        'min_profit_percent': float(min_profit_percent),
                        'last_updated': datetime.utcnow().isoformat() + 'Z'
                    }
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update configuration'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'config': {
                'enabled': enabled,
                'auto_sell': auto_sell,
                'min_profit_percent': min_profit_percent
            }
        })
        
    except Exception as e:
        print(f"Error in update_asset_manager_config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-asset-manager/analytics', methods=['GET'])
@token_required
def get_asset_manager_analytics():
    """
    Get AI Asset Manager performance analytics
    
    Returns:
        - total_sells: int
        - total_profit_usd: float
        - success_rate: float (%)
        - avg_profit_per_sell: float
        - recent_actions: Array of recent sell actions
    """
    try:
        user = get_current_user()
        
        # Get analytics from database
        # You should store AI sell actions in a collection
        # Example: db.ai_sells or add to trades collection with a flag
        
        # TEMPORARY: Return example data
        analytics = {
            'total_sells': 0,
            'total_profit_usd': 0.0,
            'success_rate': 0.0,
            'avg_profit_per_sell': 0.0,
            'recent_actions': []
        }
        
        # TODO: Query actual analytics from database
        # Example:
        # sells = db.ai_sells.find(
        #     {'user_id': ObjectId(user['_id'])},
        #     sort=[('timestamp', -1)],
        #     limit=10
        # )
        # 
        # total_sells = db.ai_sells.count_documents({'user_id': ObjectId(user['_id'])})
        # total_profit = db.ai_sells.aggregate([
        #     {'$match': {'user_id': ObjectId(user['_id'])}},
        #     {'$group': {'_id': None, 'total': {'$sum': '$profit_usd'}}}
        # ])
        
        return jsonify(analytics)
        
    except Exception as e:
        print(f"Error in get_asset_manager_analytics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-asset-manager/sell', methods=['POST'])
@token_required
def execute_manual_sell():
    """
    Manually execute a sell order for a holding
    
    Request Body:
        - symbol: str (e.g., "BTC/USDT")
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Symbol is required'}), 400
        
        symbol = data['symbol']
        
        # Get user's OKX credentials
        user_data = db.users.find_one(
            {'_id': ObjectId(user['_id'])},
            {'okx_api_key': 1, 'okx_secret_key': 1, 'okx_passphrase': 1}
        )
        
        if not user_data or not user_data.get('okx_api_key'):
            return jsonify({'error': 'OKX not connected'}), 400
        
        # INTEGRATE WITH YOUR AI ASSET MANAGER HERE
        # Example:
        # 1. Get holding information
        # 2. Execute sell via AIAssetManager.execute_smart_sell()
        # 3. Return result
        
        # TEMPORARY: Return example success
        return jsonify({
            'success': True,
            'message': f'Manual sell order placed for {symbol}',
            'order_id': 'TEMP_ORDER_ID',
            'price': 0.0,
            'amount': 0.0,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        print(f"Error in execute_manual_sell: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-asset-manager/asset/<symbol>', methods=['GET'])
@token_required
def get_asset_detail(symbol):
    """
    Get detailed analysis for a specific asset
    (Optional for v1 - can return same data as holdings endpoint)
    """
    try:
        user = get_current_user()
        
        # Get detailed analysis for this symbol
        # For now, can return same as holdings endpoint
        # In future, can add more detailed charts, history, etc.
        
        return jsonify({
            'symbol': symbol,
            'message': 'Detailed view coming soon'
        })
        
    except Exception as e:
        print(f"Error in get_asset_detail: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HELPER FUNCTIONS (Add these to your existing code)
# ============================================================================

def get_user_asset_manager(user_id):
    """
    Get or create AIAssetManager instance for a user
    
    This function should:
    1. Get user's OKX credentials
    2. Create exchange instance
    3. Create AIAssetManager instance
    4. Return it
    
    You may want to cache these instances to avoid recreating them
    """
    # TODO: Implement based on your architecture
    pass


# ============================================================================
# INTEGRATION NOTES
# ============================================================================
"""
To integrate these routes:

1. Add to web_dashboard.py:
   - Import this file: from ai_asset_manager_api_routes import *
   - OR copy the routes directly into web_dashboard.py

2. Connect to your AIAssetManager:
   - In get_holdings_analysis(), integrate with AIAssetManager.analyze_holding()
   - In execute_manual_sell(), use AIAssetManager.execute_smart_sell()
   - Store AI sell actions in database for analytics

3. Test each endpoint:
   curl http://localhost:8000/api/ai-asset-manager/status \\
     -H "Authorization: Bearer YOUR_TOKEN"

4. Deploy to production:
   git add .
   git commit -m "Add AI Asset Manager API routes"
   git push origin main
"""
