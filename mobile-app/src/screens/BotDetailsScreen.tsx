import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function BotDetailsScreen({ route, navigation }: any) {
  const { botId } = route.params;
  const { isAdmin } = useUser();
  const [bot, setBot] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBotData();
  }, []);

  const loadBotData = async () => {
    try {
      setLoading(true);
      setError(null);
      await Promise.all([loadBot(), loadAnalytics()]);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load bot details';
      console.error('❌ Error loading bot details:', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const loadBot = async () => {
    console.log('📊 Loading bot details for:', botId);
    const data = await api.getBots();
    const bots = Array.isArray(data) ? data : (data.bots || []);
    const found = bots.find((b: any) => b._id === botId || b.id === botId);
    
    if (found) {
      console.log('✅ Bot found:', found);
      setBot(found);
    } else {
      console.error('❌ Bot not found in list');
      throw new Error('Bot not found');
    }
  };

  const loadAnalytics = async () => {
    try {
      console.log('📈 Loading analytics for bot:', botId);
      const data = await api.getBotAnalytics(botId);
      console.log('✅ Analytics loaded:', data);
      setAnalytics(data);
    } catch (error: any) {
      console.error('⚠️ Analytics not available:', error.message);
      // Analytics is optional, don't fail the whole screen
    }
  };

  // Show loading state
  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Ionicons name="sync" size={48} color="#667eea" />
        <Text style={styles.loadingText}>Loading bot details...</Text>
      </View>
    );
  }

  // Show error state
  if (error) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Ionicons name="alert-circle" size={48} color="#ef4444" />
        <Text style={styles.errorText}>Failed to Load</Text>
        <Text style={styles.errorSubtext}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadBotData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!bot) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Ionicons name="alert-circle" size={48} color="#ef4444" />
        <Text style={styles.errorText}>Bot Not Found</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const config = bot.config || {};

  return (
    <View style={styles.container}>
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminText}>ADMIN VIEW</Text>
        </View>
      )}

      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Bot Details</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Configuration</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Type:</Text>
            <Text style={styles.value}>{config.bot_type || 'momentum'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Symbol:</Text>
            <Text style={styles.value}>{config.symbol || 'BTC/USDT'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Capital:</Text>
            <Text style={styles.value}>${config.capital || 1000}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Mode:</Text>
            <Text style={styles.value}>{config.paper_trading ? 'Paper' : 'Real'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Status:</Text>
            <Text style={[styles.value, { color: bot.status === 'running' ? '#10b981' : '#ef4444' }]}>
              {bot.status}
            </Text>
          </View>
        </View>

        {analytics && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📊 Performance Analytics</Text>
            <View style={styles.row}>
              <Text style={styles.label}>Total Trades:</Text>
              <Text style={styles.value}>{analytics.total_trades}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Win Rate:</Text>
              <Text style={[styles.value, { color: analytics.win_rate > 50 ? '#10b981' : '#ef4444' }]}>
                {analytics.win_rate}%
              </Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Total P&L:</Text>
              <Text style={[styles.value, { color: analytics.total_pnl > 0 ? '#10b981' : '#ef4444' }]}>
                ${analytics.total_pnl}
              </Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Avg Profit:</Text>
              <Text style={styles.value}>${analytics.avg_profit}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Winning Trades:</Text>
              <Text style={[styles.value, { color: '#10b981' }]}>{analytics.winning_trades}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Losing Trades:</Text>
              <Text style={[styles.value, { color: '#ef4444' }]}>{analytics.losing_trades}</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  adminBadge: { backgroundColor: '#10b981', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, gap: 8 },
  adminText: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  content: { flex: 1, padding: 20 },
  card: { backgroundColor: '#fff', padding: 20, borderRadius: 12, marginBottom: 16 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  label: { fontSize: 14, color: '#6b7280' },
  value: { fontSize: 14, fontWeight: '600', color: '#111827' },
  centerContent: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#667eea',
  },
  errorText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#ef4444',
  },
  errorSubtext: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 10,
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  retryButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  backButton: {
    backgroundColor: '#6b7280',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 12,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
