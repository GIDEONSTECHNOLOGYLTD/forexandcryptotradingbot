/**
 * Trade History Screen
 * Shows complete trade history for admin and user bots
 * Includes filtering and detailed trade information
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  FlatList,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../services/api';

interface Trade {
  _id: string;
  timestamp: string;
  entry_time?: string;
  bot_name: string;
  bot_id?: string;
  bot_type?: string;
  symbol: string;
  side: string;
  entry_price: number;
  exit_price: number;
  amount: number;
  pnl: number;
  status: string;
  is_paper?: boolean;
}

export default function TradeHistoryScreen() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [openPositions, setOpenPositions] = useState<Trade[]>([]);
  const [filteredTrades, setFilteredTrades] = useState<Trade[]>([]);
  const [filter, setFilter] = useState<'all' | 'admin' | 'users'>('all');
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    winning: 0,
    losing: 0,
    totalPnL: 0,
    openPositions: 0,
  });

  useEffect(() => {
    loadTrades();
    
    // Auto-refresh every 5 seconds for real-time trade updates
    const interval = setInterval(() => {
      loadTrades();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    applyFilter();
  }, [filter, trades, openPositions]);

  const loadTrades = async () => {
    try {
      // Load both closed trades and open positions
      const [historyResponse, positionsResponse] = await Promise.all([
        api.getTradeHistory(),
        api.getOpenPositions().catch(() => ({ positions: [], count: 0 }))
      ]);
      
      const tradeData = historyResponse.trades || [];
      const positionData = positionsResponse.positions || [];
      
      setTrades(tradeData);
      setOpenPositions(positionData);
      calculateStats(tradeData, positionData);
    } catch (error) {
      console.error('Error loading trades:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTrades();
    setRefreshing(false);
  };

  const applyFilter = () => {
    let filtered = trades;
    
    if (filter === 'admin') {
      filtered = trades.filter(t => 
        t.bot_type === 'admin' || 
        t.bot_id === 'admin_auto_trader' ||
        t.bot_id === 'new_listing_bot' ||
        (t.bot_name && t.bot_name.includes('Admin'))
      );
    } else if (filter === 'users') {
      filtered = trades.filter(t => 
        t.bot_type === 'user' || 
        (t.bot_id !== 'admin_auto_trader' && 
         t.bot_id !== 'new_listing_bot' && 
         (!t.bot_name || !t.bot_name.includes('Admin')))
      );
    }
    
    setFilteredTrades(filtered);
    calculateStats(filtered, openPositions);
  };

  const calculateStats = (tradeList: Trade[], positions: Trade[] = []) => {
    const total = tradeList.length;
    const winning = tradeList.filter(t => (t.pnl || 0) > 0).length;
    const losing = tradeList.filter(t => (t.pnl || 0) < 0).length;
    const totalPnL = tradeList.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const openPositions = positions.length;

    setStats({ total, winning, losing, totalPnL, openPositions });
  };

  const renderTrade = ({ item }: { item: Trade }) => {
    const pnl = item.pnl || 0;
    const isProfitable = pnl >= 0;
    const tradeTime = new Date(item.timestamp || item.entry_time || '').toLocaleString();

    return (
      <View style={styles.tradeCard}>
        <View style={styles.tradeHeader}>
          <View style={styles.tradeHeaderLeft}>
            <Text style={styles.tradeBotName}>{item.bot_name || 'Unknown Bot'}</Text>
            <Text style={styles.tradeTime}>{tradeTime}</Text>
          </View>
          <View style={[styles.pnlBadge, isProfitable ? styles.pnlPositive : styles.pnlNegative]}>
            <Text style={styles.pnlText}>
              {isProfitable ? '+' : ''}${pnl.toFixed(2)}
            </Text>
          </View>
        </View>

        <View style={styles.tradeDetails}>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Symbol:</Text>
            <Text style={styles.tradeValue}>{item.symbol}</Text>
          </View>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Type:</Text>
            <View style={[styles.typeBadge, item.side === 'buy' ? styles.buyBadge : styles.sellBadge]}>
              <Text style={styles.typeBadgeText}>{(item.side || 'buy').toUpperCase()}</Text>
            </View>
          </View>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Entry:</Text>
            <Text style={styles.tradeValue}>${(item.entry_price || 0).toFixed(4)}</Text>
          </View>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Exit:</Text>
            <Text style={styles.tradeValue}>${(item.exit_price || 0).toFixed(4)}</Text>
          </View>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Amount:</Text>
            <Text style={styles.tradeValue}>${(item.amount || 0).toFixed(2)}</Text>
          </View>
          <View style={styles.tradeRow}>
            <Text style={styles.tradeLabel}>Status:</Text>
            <View style={[styles.statusBadge, item.status === 'closed' ? styles.closedBadge : styles.openBadge]}>
              <Text style={styles.statusBadgeText}>{(item.status || 'open').toUpperCase()}</Text>
            </View>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Compact Stats Row */}
      <View style={styles.statsRow}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Open</Text>
          <Text style={[styles.statValue, { color: '#3b82f6' }]}>{stats.openPositions}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Closed</Text>
          <Text style={styles.statValue}>{stats.total}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Win</Text>
          <Text style={[styles.statValue, styles.winningText]}>{stats.winning}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>Loss</Text>
          <Text style={[styles.statValue, styles.losingText]}>{stats.losing}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>P&L</Text>
          <Text style={[styles.statValue, stats.totalPnL >= 0 ? styles.winningText : styles.losingText]}>
            ${stats.totalPnL.toFixed(2)}
          </Text>
        </View>
      </View>

      {/* Compact Filter Buttons */}
      <View style={styles.filterContainer}>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'all' && styles.filterButtonActive]}
          onPress={() => setFilter('all')}
        >
          <Text style={[styles.filterButtonText, filter === 'all' && styles.filterButtonTextActive]}>All</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'admin' && styles.filterButtonActive]}
          onPress={() => setFilter('admin')}
        >
          <Text style={[styles.filterButtonText, filter === 'admin' && styles.filterButtonTextActive]}>Admin</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'users' && styles.filterButtonActive]}
          onPress={() => setFilter('users')}
        >
          <Text style={[styles.filterButtonText, filter === 'users' && styles.filterButtonTextActive]}>Users</Text>
        </TouchableOpacity>
        <View style={styles.okxBadge}>
          <Ionicons name="information-circle" size={14} color="#3b82f6" />
          <Text style={styles.okxBadgeText}>View in OKX</Text>
        </View>
      </View>

      {/* Open Positions Section */}
      {openPositions.length > 0 && (
        <View style={styles.sectionContainer}>
          <View style={styles.sectionHeader}>
            <Ionicons name="pulse" size={18} color="#3b82f6" />
            <Text style={styles.sectionTitle}>Open Positions ({openPositions.length})</Text>
          </View>
          {openPositions.map((position) => (
            <View key={position._id} style={[styles.tradeCard, styles.openPositionCard]}>
              <View style={styles.openPositionBadge}>
                <Text style={styles.openPositionBadgeText}>LIVE</Text>
              </View>
              <View style={styles.tradeHeader}>
                <View style={styles.tradeHeaderLeft}>
                  <Text style={styles.tradeBotName}>{position.bot_name || 'Unknown Bot'}</Text>
                  <Text style={styles.tradeTime}>{new Date(position.timestamp || '').toLocaleString()}</Text>
                </View>
                {!position.is_paper && (
                  <View style={styles.okxRealBadge}>
                    <Text style={styles.okxRealBadgeText}>OKX</Text>
                  </View>
                )}
              </View>
              <View style={styles.tradeDetails}>
                <View style={styles.tradeRow}>
                  <Text style={styles.tradeLabel}>Symbol:</Text>
                  <Text style={styles.tradeValue}>{position.symbol}</Text>
                </View>
                <View style={styles.tradeRow}>
                  <Text style={styles.tradeLabel}>Entry:</Text>
                  <Text style={styles.tradeValue}>${Number(position.entry_price || 0).toFixed(4)}</Text>
                </View>
                <View style={styles.tradeRow}>
                  <Text style={styles.tradeLabel}>Amount:</Text>
                  <Text style={styles.tradeValue}>{Number(position.amount || 0).toFixed(6)}</Text>
                </View>
                <View style={styles.tradeRow}>
                  <Text style={styles.tradeLabel}>Mode:</Text>
                  <Text style={[styles.tradeValue, position.is_paper ? { color: '#f59e0b' } : { color: '#10b981' }]}>
                    {position.is_paper ? 'PAPER' : 'REAL'}
                  </Text>
                </View>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Closed Trades Section */}
      {filteredTrades.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="bar-chart-outline" size={64} color="#d1d5db" />
          <Text style={styles.emptyStateText}>No trades yet</Text>
          <Text style={styles.emptyStateSubtext}>Start the bot to begin trading!</Text>
        </View>
      ) : (
        <FlatList
          data={filteredTrades}
          renderItem={renderTrade}
          keyExtractor={(item) => item._id}
          contentContainerStyle={styles.tradeList}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  statsRow: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 10,
    color: '#6b7280',
    marginBottom: 2,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  winningText: {
    color: '#10b981',
  },
  losingText: {
    color: '#ef4444',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 6,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  filterButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#3b82f6',
  },
  filterButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
  },
  okxBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#eff6ff',
    gap: 4,
  },
  okxBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#3b82f6',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  tradeList: {
    padding: 12,
  },
  tradeCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  tradeHeaderLeft: {
    flex: 1,
  },
  tradeBotName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  tradeTime: {
    fontSize: 12,
    color: '#6b7280',
  },
  pnlBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  pnlPositive: {
    backgroundColor: '#d1fae5',
  },
  pnlNegative: {
    backgroundColor: '#fee2e2',
  },
  pnlText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  tradeDetails: {
    gap: 8,
  },
  tradeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tradeLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  tradeValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  buyBadge: {
    backgroundColor: '#d1fae5',
  },
  sellBadge: {
    backgroundColor: '#fee2e2',
  },
  typeBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#111827',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  closedBadge: {
    backgroundColor: '#e5e7eb',
  },
  openBadge: {
    backgroundColor: '#dbeafe',
  },
  statusBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#111827',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#6b7280',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 8,
  },
  sectionContainer: {
    backgroundColor: '#fff',
    marginVertical: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  openPositionCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  openPositionBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#3b82f6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    zIndex: 1,
  },
  openPositionBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
  },
  okxRealBadge: {
    backgroundColor: '#10b981',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  okxRealBadgeText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#fff',
  },
});
