"""
ADD THESE ROUTES TO web_dashboard.py
Copy everything below and paste at the end of web_dashboard.py (before if __name__ == "__main__")
"""

# ============================================================================
# AI ASSET MANAGER ENDPOINTS - ADD TO web_dashboard.py
# ============================================================================

from pydantic import BaseModel

class AssetManagerConfig(BaseModel):
    enabled: bool
    auto_sell: bool
    min_profit_percent: float

class ManualSell(BaseModel):
    symbol: str

@app.get("/api/ai-asset-manager/status")
async def get_asset_manager_status(user: dict = Depends(get_current_user)):
    """
    Get AI Asset Manager status and configuration
    
    Returns current settings and analysis statistics
    """
    try:
        # Get user's asset manager config from database
        config = user.get('asset_manager_config', {})
        
        # Get last check time
        last_check = config.get('last_check', datetime.utcnow().isoformat() + 'Z')
        
        # TODO: Calculate real holdings analyzed and recommendations
        # For now, return defaults
        holdings_analyzed = 0
        recommendations = {'sell': 0, 'hold': 0, 'buy': 0}
        
        return {
            "enabled": config.get('enabled', False),
            "auto_sell": config.get('auto_sell', False),
            "min_profit_percent": config.get('min_profit_percent', 3.0),
            "last_check": last_check,
            "holdings_analyzed": holdings_analyzed,
            "recommendations_count": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error in get_asset_manager_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-asset-manager/holdings")
async def get_holdings_analysis(user: dict = Depends(get_current_user)):
    """
    Get all holdings with AI analysis and recommendations
    
    Returns holdings with technical indicators and AI recommendations
    """
    try:
        # Get user's asset manager config
        config = user.get('asset_manager_config', {})
        enabled = config.get('enabled', False)
        
        if not enabled:
            return {
                "holdings": [],
                "total_count": 0,
                "message": "AI Asset Manager is disabled",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        
        # Check if OKX is connected
        if not user.get('okx_api_key'):
            return {
                "holdings": [],
                "total_count": 0,
                "message": "OKX not connected. Please connect your exchange first.",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        
        holdings = []
        
        # TODO: INTEGRATE WITH AIAssetManager HERE
        # Example integration:
        # try:
        #     from ai_asset_manager import AIAssetManager
        #     from cryptography.fernet import Fernet
        #     import ccxt
        #     
        #     # Decrypt OKX credentials
        #     cipher_suite = Fernet(config.ENCRYPTION_KEY.encode())
        #     api_key = cipher_suite.decrypt(user['okx_api_key'].encode()).decode()
        #     secret_key = cipher_suite.decrypt(user['okx_secret_key'].encode()).decode()
        #     passphrase = cipher_suite.decrypt(user['okx_passphrase'].encode()).decode()
        #     
        #     # Create exchange instance
        #     exchange = ccxt.okx({
        #         'apiKey': api_key,
        #         'secret': secret_key,
        #         'password': passphrase,
        #         'enableRateLimit': True
        #     })
        #     
        #     # Create AIAssetManager instance
        #     asset_manager = AIAssetManager(
        #         exchange=exchange,
        #         db=db,
        #         telegram=None,  # Or user's telegram if configured
        #         risk_manager=None  # Or create risk manager instance
        #     )
        #     
        #     # Get all holdings
        #     holdings_data = asset_manager.get_all_holdings()
        #     
        #     # Analyze each holding
        #     for holding in holdings_data:
        #         analysis = asset_manager.analyze_holding(holding)
        #         
        #         holdings.append({
        #             'symbol': holding['symbol'],
        #             'currency': holding['currency'],
        #             'amount': holding['total_amount'],
        #             'value_usd': holding['value_usd'],
        #             'current_price': holding['current_price'],
        #             'ai_recommendation': analysis.get('recommendation', 'HOLD'),
        #             'estimated_profit_pct': analysis.get('estimated_profit_pct', 0),
        #             'estimated_profit_usd': analysis.get('estimated_profit_usd', 0),
        #             'urgency': analysis.get('urgency', 'LOW'),
        #             'reasoning': analysis.get('reasoning', []),
        #             'indicators': {
        #                 'rsi': analysis.get('rsi', 50),
        #                 'macd_trend': analysis.get('macd_trend', 'NEUTRAL'),
        #                 'bollinger_position': analysis.get('bollinger_position', 50),
        #                 'order_book_pressure': analysis.get('order_book_pressure', 'NEUTRAL')
        #             }
        #         })
        # 
        # except Exception as e:
        #     logger.error(f"Error analyzing holdings: {e}")
        #     raise HTTPException(status_code=500, detail=f"Failed to analyze holdings: {str(e)}")
        
        return {
            "holdings": holdings,
            "total_count": len(holdings),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_holdings_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/ai-asset-manager/config")
async def update_asset_manager_config(
    config: AssetManagerConfig,
    user: dict = Depends(get_current_user)
):
    """
    Update AI Asset Manager configuration
    
    Allows users to enable/disable AI analysis and configure auto-sell settings
    """
    try:
        from bson import ObjectId
        
        # Validate min_profit_percent
        if config.min_profit_percent < 0.1 or config.min_profit_percent > 100:
            raise HTTPException(
                status_code=400,
                detail="min_profit_percent must be between 0.1 and 100"
            )
        
        # Update user configuration in database
        result = users_collection.update_one(
            {'_id': ObjectId(user['_id'])},
            {
                '$set': {
                    'asset_manager_config': {
                        'enabled': config.enabled,
                        'auto_sell': config.auto_sell,
                        'min_profit_percent': config.min_profit_percent,
                        'last_updated': datetime.utcnow().isoformat() + 'Z',
                        'last_check': datetime.utcnow().isoformat() + 'Z'
                    }
                }
            }
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to update configuration"
            )
        
        logger.info(f"✅ AI Asset Manager config updated for user {user['email']}")
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": {
                "enabled": config.enabled,
                "auto_sell": config.auto_sell,
                "min_profit_percent": config.min_profit_percent
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_asset_manager_config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-asset-manager/analytics")
async def get_asset_manager_analytics(user: dict = Depends(get_current_user)):
    """
    Get AI Asset Manager performance analytics
    
    Returns historical performance metrics and recent actions
    """
    try:
        # TODO: Query analytics from database
        # You should store AI sell actions in a collection like:
        # db.ai_asset_sells or add to trades with a flag
        
        # Example query:
        # from bson import ObjectId
        # 
        # sells = list(db.db['ai_asset_sells'].find(
        #     {'user_id': ObjectId(user['_id'])},
        #     sort=[('timestamp', -1)],
        #     limit=10
        # ))
        # 
        # total_sells = db.db['ai_asset_sells'].count_documents(
        #     {'user_id': ObjectId(user['_id'])}
        # )
        # 
        # profit_result = list(db.db['ai_asset_sells'].aggregate([
        #     {'$match': {'user_id': ObjectId(user['_id'])}},
        #     {'$group': {
        #         '_id': None,
        #         'total': {'$sum': '$profit_usd'},
        #         'count': {'$sum': 1},
        #         'successful': {
        #             '$sum': {'$cond': [{'$gt': ['$profit_usd', 0]}, 1, 0]}
        #         }
        #     }}
        # ]))
        
        # For now, return empty analytics
        return {
            "total_sells": 0,
            "total_profit_usd": 0.0,
            "success_rate": 0.0,
            "avg_profit_per_sell": 0.0,
            "recent_actions": []
        }
        
    except Exception as e:
        logger.error(f"Error in get_asset_manager_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai-asset-manager/sell")
async def execute_manual_sell(
    data: ManualSell,
    user: dict = Depends(get_current_user)
):
    """
    Manually execute a sell order for a holding
    
    Allows user to manually trigger AI-recommended sell
    """
    try:
        # Check if OKX is connected
        if not user.get('okx_api_key'):
            raise HTTPException(
                status_code=400,
                detail="OKX not connected. Please connect your exchange first."
            )
        
        logger.info(f"📤 Manual sell requested for {data.symbol} by user {user['email']}")
        
        # TODO: INTEGRATE WITH AIAssetManager.execute_smart_sell()
        # Example:
        # from ai_asset_manager import AIAssetManager
        # from cryptography.fernet import Fernet
        # import ccxt
        # 
        # # Decrypt credentials and create exchange instance
        # cipher_suite = Fernet(config.ENCRYPTION_KEY.encode())
        # api_key = cipher_suite.decrypt(user['okx_api_key'].encode()).decode()
        # secret_key = cipher_suite.decrypt(user['okx_secret_key'].encode()).decode()
        # passphrase = cipher_suite.decrypt(user['okx_passphrase'].encode()).decode()
        # 
        # exchange = ccxt.okx({
        #     'apiKey': api_key,
        #     'secret': secret_key,
        #     'password': passphrase,
        #     'enableRateLimit': True
        # })
        # 
        # asset_manager = AIAssetManager(exchange, db, None, None)
        # 
        # # Find holding
        # holdings = asset_manager.get_all_holdings()
        # holding = next((h for h in holdings if h['symbol'] == data.symbol), None)
        # 
        # if not holding:
        #     raise HTTPException(status_code=404, detail=f"Holding {data.symbol} not found")
        # 
        # # Execute sell
        # analysis = asset_manager.analyze_holding(holding)
        # result = asset_manager.execute_smart_sell(holding, analysis)
        # 
        # if result:
        #     # Store in database for analytics
        #     db.db['ai_asset_sells'].insert_one({
        #         'user_id': ObjectId(user['_id']),
        #         'symbol': data.symbol,
        #         'price': holding['current_price'],
        #         'amount': holding['total_amount'],
        #         'profit_usd': analysis.get('estimated_profit_usd', 0),
        #         'profit_pct': analysis.get('estimated_profit_pct', 0),
        #         'timestamp': datetime.utcnow()
        #     })
        #     
        #     return {
        #         "success": True,
        #         "message": f"Successfully sold {data.symbol}",
        #         "order_id": "ORDER_ID_FROM_EXCHANGE",
        #         "price": holding['current_price'],
        #         "amount": holding['total_amount'],
        #         "timestamp": datetime.utcnow().isoformat() + 'Z'
        #     }
        # else:
        #     raise HTTPException(status_code=500, detail="Failed to execute sell order")
        
        # TEMPORARY: Return success for testing
        return {
            "success": True,
            "message": f"Manual sell order placed for {data.symbol}",
            "note": "This is a test response. Full integration pending.",
            "order_id": "TEMP_ORDER_ID",
            "price": 0.0,
            "amount": 0.0,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in execute_manual_sell: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai-asset-manager/asset/{symbol}")
async def get_asset_detail(
    symbol: str,
    user: dict = Depends(get_current_user)
):
    """
    Get detailed analysis for a specific asset
    
    Returns in-depth information about a single holding (v1: basic info)
    """
    try:
        # For v1, return basic info
        # In future, can add detailed charts, historical analysis, etc.
        
        return {
            "symbol": symbol,
            "message": "Detailed asset view coming soon",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        logger.error(f"Error in get_asset_detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# END OF AI ASSET MANAGER ENDPOINTS
# ============================================================================

"""
INTEGRATION NOTES:

1. Copy everything above this comment block
2. Paste at the end of web_dashboard.py (before if __name__ == "__main__")
3. The endpoints will work immediately with basic responses
4. To enable full functionality, uncomment the TODO sections and:
   - Import AIAssetManager from ai_asset_manager.py
   - Decrypt user's OKX credentials
   - Create exchange and asset manager instances
   - Call asset manager methods
   - Store results in database

5. Test the endpoints:
   curl http://localhost:8000/api/ai-asset-manager/status \\
     -H "Authorization: Bearer YOUR_TOKEN"

6. Deploy to Render:
   git add web_dashboard.py
   git commit -m "Add AI Asset Manager API endpoints for iOS"
   git push origin main
"""
