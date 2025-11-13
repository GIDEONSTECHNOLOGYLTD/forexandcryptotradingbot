import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function TradingScreen({ navigation }: any) {
  const { user, isAdmin } = useUser();
  const [bots, setBots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [liveUpdates, setLiveUpdates] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadBots();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('wss://trading-bot-api-7xps.onrender.com/ws/trades');
      
      ws.onopen = () => {
        console.log('🔌 WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'trade') {
            console.log('📡 Live trade:', message.data);
            setLiveUpdates(prev => [message.data, ...prev].slice(0, 10));
          }
        } catch (e) {
          console.error('WebSocket message error:', e);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const loadBots = async () => {
    try {
      setLoading(true);
      console.log('🔍 Loading bots for user:', user?.email, 'isAdmin:', isAdmin);
      const data = await api.getBots();
      const botsList = Array.isArray(data) ? data : (data.bots || []);
      console.log('📊 Loaded', botsList.length, 'bots');
      console.log('🤖 Bot owners:', botsList.map(b => b.user_id).join(', '));
      setBots(botsList);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to load bots');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleStartBot = async (botId: string) => {
    try {
      console.log('Starting bot:', botId);
      const result = await api.startBot(botId);
      console.log('Start result:', result);
      Alert.alert('Success', 'Bot started successfully');
      loadBots();
    } catch (error: any) {
      console.error('Start bot error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to start bot';
      Alert.alert('Error', errorMsg);
    }
  };

  const handleStopBot = async (botId: string) => {
    try {
      console.log('Stopping bot:', botId);
      const result = await api.stopBot(botId);
      console.log('Stop result:', result);
      Alert.alert('Success', 'Bot stopped successfully');
      loadBots();
    } catch (error: any) {
      console.error('Stop bot error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to stop bot';
      Alert.alert('Error', errorMsg);
    }
  };

  const handleDeleteBot = (botId: string, botType: string) => {
    Alert.alert(
      'Delete Bot',
      `Are you sure you want to delete this ${botType} bot? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.deleteBot(botId);
              Alert.alert('Success', 'Bot deleted successfully');
              loadBots();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to delete bot');
            }
          },
        },
      ]
    );
  };

  const handleUpdateBot = (bot: any) => {
    // Navigate to BotConfig screen with bot data for editing
    navigation.navigate('BotConfig', { 
      bot: bot,
      isEditing: true 
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#10b981';
      case 'stopped':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <View style={styles.container}>
      {/* Admin Badge */}
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminBadgeText}>ADMIN - All Users' Bots</Text>
        </View>
      )}

      <View style={styles.header}>
        <Text style={styles.title}>{isAdmin ? 'All Trading Bots' : 'My Trading Bots'}</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('BotConfig')}
        >
          <Ionicons name="add-circle" size={32} color="#667eea" />
        </TouchableOpacity>
      </View>

      {/* Live Updates */}
      {liveUpdates.length > 0 && (
        <View style={styles.liveUpdates}>
          <View style={styles.liveHeader}>
            <View style={styles.liveDot} />
            <Text style={styles.liveTitle}>Live Trades</Text>
          </View>
          {liveUpdates.slice(0, 3).map((trade, index) => (
            <View key={index} style={styles.liveTradeCard}>
              <Text style={styles.liveTradeSymbol}>{trade.symbol}</Text>
              <Text style={[styles.liveTradeSide, trade.side === 'buy' ? styles.buyText : styles.sellText]}>
                {trade.side.toUpperCase()}
              </Text>
              <Text style={styles.liveTradePrice}>${trade.price?.toFixed(2)}</Text>
              {trade.pnl && (
                <Text style={[styles.liveTradePnl, trade.pnl > 0 ? styles.profitText : styles.lossText]}>
                  {trade.pnl > 0 ? '+' : ''}{trade.pnl.toFixed(2)}%
                </Text>
              )}
            </View>
          ))}
        </View>
      )}

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={loadBots} />
        }
      >
        {bots.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="construct-outline" size={64} color="#9ca3af" />
            <Text style={styles.emptyText}>No bots yet</Text>
            <Text style={styles.emptySubtext}>Create your first trading bot</Text>
            <TouchableOpacity
              style={styles.createButton}
              onPress={() => navigation.navigate('BotConfig')}
            >
              <Text style={styles.createButtonText}>Create Bot</Text>
            </TouchableOpacity>
          </View>
        ) : (
          bots.map((bot) => (
            <View key={bot._id} style={styles.botCard}>
              <View style={styles.botHeader}>
                <View style={{ flex: 1 }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                    <Text style={styles.botName}>{bot.config?.bot_type || 'Trading Bot'}</Text>
                    {isAdmin && !bot.is_my_bot && (
                      <View style={styles.userBadge}>
                        <Text style={styles.userBadgeText}>USER</Text>
                      </View>
                    )}
                    {isAdmin && bot.is_my_bot && (
                      <View style={styles.myBotBadge}>
                        <Text style={styles.myBotBadgeText}>MINE</Text>
                      </View>
                    )}
                  </View>
                  <Text style={styles.botSymbol}>{bot.config?.symbol || 'BTC/USDT'}</Text>
                  {isAdmin && bot.owner_email && (
                    <Text style={styles.ownerText}>👤 {bot.owner_email}</Text>
                  )}
                </View>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(bot.status) }]}>
                  <Text style={styles.statusText}>{bot.status}</Text>
                </View>
              </View>

              <View style={styles.botStats}>
                <View style={styles.stat}>
                  <Text style={styles.statLabel}>Capital</Text>
                  <Text style={styles.statValue}>${bot.config?.capital || 0}</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={styles.statLabel}>P&L</Text>
                  <Text style={[styles.statValue, { color: '#10b981' }]}>+$0.00</Text>
                </View>
                <View style={styles.stat}>
                  <Text style={styles.statLabel}>Trades</Text>
                  <Text style={styles.statValue}>0</Text>
                </View>
              </View>

              <View style={styles.botActions}>
                {bot.status === 'running' ? (
                  <TouchableOpacity
                    style={[styles.actionButton, styles.stopButton]}
                    onPress={() => handleStopBot(bot._id)}
                  >
                    <Ionicons name="stop-circle" size={20} color="#fff" />
                    <Text style={styles.actionButtonText}>Stop</Text>
                  </TouchableOpacity>
                ) : (
                  <TouchableOpacity
                    style={[styles.actionButton, styles.startButton]}
                    onPress={() => handleStartBot(bot._id)}
                  >
                    <Ionicons name="play-circle" size={20} color="#fff" />
                    <Text style={styles.actionButtonText}>Start</Text>
                  </TouchableOpacity>
                )}
                <TouchableOpacity 
                  style={[styles.actionButton, styles.detailsButton]}
                  onPress={() => navigation.navigate('BotDetails', { botId: bot._id })}
                >
                  <Ionicons name="stats-chart" size={20} color="#667eea" />
                  <Text style={[styles.actionButtonText, { color: '#667eea' }]}>Details</Text>
                </TouchableOpacity>
              </View>

              {/* Additional Actions */}
              <View style={styles.secondaryActions}>
                <TouchableOpacity 
                  style={styles.secondaryButton}
                  onPress={() => handleUpdateBot(bot)}
                >
                  <Ionicons name="create-outline" size={18} color="#667eea" />
                  <Text style={styles.secondaryButtonText}>Edit</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={styles.secondaryButton}
                  onPress={() => handleDeleteBot(bot._id, bot.config?.bot_type)}
                >
                  <Ionicons name="trash-outline" size={18} color="#ef4444" />
                  <Text style={[styles.secondaryButtonText, { color: '#ef4444' }]}>Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  adminBadge: {
    backgroundColor: '#10b981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 8,
  },
  adminBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  addButton: {
    padding: 5,
  },
  scrollView: {
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    marginTop: 60,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#6b7280',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 8,
  },
  createButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 24,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  botCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  botHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  botName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  botSymbol: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  ownerText: {
    fontSize: 12,
    color: '#667eea',
    marginTop: 4,
    fontWeight: '500',
  },
  userBadge: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  userBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  myBotBadge: {
    backgroundColor: '#10b981',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  myBotBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  liveUpdates: {
    backgroundColor: '#f0fdf4',
    padding: 16,
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#86efac',
  },
  liveHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22c55e',
    marginRight: 8,
  },
  liveTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#166534',
  },
  liveTradeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  liveTradeSymbol: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    flex: 1,
  },
  liveTradeSide: {
    fontSize: 12,
    fontWeight: '600',
    marginRight: 8,
  },
  buyText: {
    color: '#10b981',
  },
  sellText: {
    color: '#ef4444',
  },
  liveTradePrice: {
    fontSize: 14,
    color: '#6b7280',
    marginRight: 8,
  },
  liveTradePnl: {
    fontSize: 14,
    fontWeight: '600',
  },
  profitText: {
    color: '#10b981',
  },
  lossText: {
    color: '#ef4444',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  botStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#e5e7eb',
  },
  stat: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  botActions: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  startButton: {
    backgroundColor: '#10b981',
  },
  stopButton: {
    backgroundColor: '#ef4444',
  },
  detailsButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#667eea',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  secondaryActions: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  secondaryButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#f9fafb',
    gap: 6,
  },
  secondaryButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#667eea',
  },
});
