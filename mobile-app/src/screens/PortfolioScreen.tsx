import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../context/UserContext';
import api from '../services/api';

export default function PortfolioScreen() {
  const { isAdmin } = useUser();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [balance, setBalance] = useState({
    total: 0,
    available: 0,
    locked: 0,
    unrealized_pnl: 0,
  });
  const [stats, setStats] = useState({
    totalTrades: 0,
    winRate: 0,
    totalPnL: 0,
    bestTrade: 0,
    worstTrade: 0,
  });

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch balance
      const balanceData = await api.getUserBalance();
      setBalance({
        total: balanceData.total || 0,
        available: balanceData.available || 0,
        locked: balanceData.locked || 0,
        unrealized_pnl: balanceData.unrealized_pnl || 0,
      });

      // Fetch dashboard stats
      const dashboardData = await api.getDashboard();
      setStats({
        totalTrades: dashboardData.stats?.total_trades || 0,
        winRate: dashboardData.stats?.win_rate || 0,
        totalPnL: dashboardData.stats?.total_pnl || 0,
        bestTrade: dashboardData.stats?.best_trade || 0,
        worstTrade: dashboardData.stats?.worst_trade || 0,
      });
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchPortfolioData();
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading portfolio...</Text>
      </View>
    );
  }

  const pnlPercent = balance.total > 0 ? (balance.unrealized_pnl / balance.total) * 100 : 0;

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminBadgeText}>ADMIN - System Portfolio</Text>
        </View>
      )}
      <View style={styles.header}>
        <Text style={styles.title}>{isAdmin ? 'System Portfolio' : 'Portfolio'}</Text>
      </View>
      
      {/* Total Balance Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Total Balance</Text>
        <Text style={styles.balance}>${balance.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Text>
        <Text style={[styles.pnl, balance.unrealized_pnl >= 0 ? styles.profitText : styles.lossText]}>
          {balance.unrealized_pnl >= 0 ? '+' : ''}${Math.abs(balance.unrealized_pnl).toFixed(2)} ({pnlPercent.toFixed(2)}%)
        </Text>
      </View>

      {/* Balance Breakdown */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Balance Breakdown</Text>
        <View style={styles.breakdownRow}>
          <Text style={styles.breakdownLabel}>Available</Text>
          <Text style={styles.breakdownValue}>${balance.available.toFixed(2)}</Text>
        </View>
        <View style={styles.breakdownRow}>
          <Text style={styles.breakdownLabel}>In Positions</Text>
          <Text style={styles.breakdownValue}>${balance.locked.toFixed(2)}</Text>
        </View>
        <View style={styles.breakdownRow}>
          <Text style={styles.breakdownLabel}>Unrealized P&L</Text>
          <Text style={[styles.breakdownValue, balance.unrealized_pnl >= 0 ? styles.profitText : styles.lossText]}>
            ${balance.unrealized_pnl.toFixed(2)}
          </Text>
        </View>
      </View>

      {/* Performance Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Performance</Text>
        <View style={styles.statRow}>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Win Rate</Text>
            <Text style={styles.statValue}>{stats.winRate.toFixed(1)}%</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Total Trades</Text>
            <Text style={styles.statValue}>{stats.totalTrades}</Text>
          </View>
        </View>
        <View style={styles.statRow}>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Total P&L</Text>
            <Text style={[styles.statValue, stats.totalPnL >= 0 ? styles.profitText : styles.lossText]}>
              ${stats.totalPnL.toFixed(2)}
            </Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Best Trade</Text>
            <Text style={[styles.statValue, styles.profitText]}>
              ${stats.bestTrade.toFixed(2)}
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  centerContent: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6b7280',
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
  header: { padding: 20, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold' },
  card: { 
    backgroundColor: '#fff', 
    margin: 16, 
    padding: 20, 
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: { fontSize: 16, color: '#6b7280', marginBottom: 12 },
  balance: { fontSize: 32, fontWeight: 'bold', color: '#111827' },
  pnl: { fontSize: 16, marginTop: 4 },
  profitText: { color: '#10b981' },
  lossText: { color: '#ef4444' },
  breakdownRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  breakdownLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  breakdownValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  statRow: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 16 },
  stat: { alignItems: 'center' },
  statLabel: { fontSize: 12, color: '#6b7280' },
  statValue: { fontSize: 18, fontWeight: '600', marginTop: 4 },
});
