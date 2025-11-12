import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function TradingScreen({ navigation }: any) {
  const { user, isAdmin } = useUser();
  const [bots, setBots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    try {
      setLoading(true);
      const data = await api.getBots();
      // Backend returns array directly now
      setBots(Array.isArray(data) ? data : (data.bots || []));
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
                <View>
                  <Text style={styles.botName}>{bot.config?.bot_type || 'Trading Bot'}</Text>
                  <Text style={styles.botSymbol}>{bot.config?.symbol || 'BTC/USDT'}</Text>
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
                <TouchableOpacity style={[styles.actionButton, styles.detailsButton]}>
                  <Ionicons name="stats-chart" size={20} color="#667eea" />
                  <Text style={[styles.actionButtonText, { color: '#667eea' }]}>Details</Text>
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
});
