import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  TextInput,
  Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function CopyTradingScreen({ navigation }: any) {
  const [topTraders, setTopTraders] = useState<any[]>([]);
  const [mySubscriptions, setMySubscriptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [subscribeModalVisible, setSubscribeModalVisible] = useState(false);
  const [selectedTrader, setSelectedTrader] = useState<any>(null);
  const [capital, setCapital] = useState('100');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [traders, subscriptions] = await Promise.all([
        api.getTopTraders(20),
        api.getMyCopySubscriptions()
      ]);
      
      setTopTraders(traders.traders || []);
      setMySubscriptions(subscriptions.subscriptions || []);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load copy trading data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleSubscribe = (trader: any) => {
    setSelectedTrader(trader);
    setSubscribeModalVisible(true);
  };

  const confirmSubscribe = async () => {
    if (!selectedTrader || !capital) return;
    
    const capitalNum = parseFloat(capital);
    if (isNaN(capitalNum) || capitalNum < 50) {
      Alert.alert('Error', 'Minimum capital is $50');
      return;
    }

    try {
      await api.subscribeToTrader(selectedTrader._id, capitalNum);
      Alert.alert(
        'Success!',
        `You're now copying ${selectedTrader.name}'s strategy with $${capitalNum} capital`,
        [{ text: 'OK', onPress: () => {
          setSubscribeModalVisible(false);
          loadData();
        }}]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to subscribe');
    }
  };

  const handleUnsubscribe = (subscription: any) => {
    Alert.alert(
      'Unsubscribe',
      `Stop copying this strategy? Open positions will remain active.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Unsubscribe',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.unsubscribeFromTrader(subscription.strategy_id);
              Alert.alert('Success', 'Unsubscribed successfully');
              loadData();
            } catch (error: any) {
              Alert.alert('Error', 'Failed to unsubscribe');
            }
          }
        }
      ]
    );
  };

  const renderTraderCard = (trader: any) => {
    const isSubscribed = mySubscriptions.some(s => s.strategy_id === trader._id && s.status === 'active');
    
    return (
      <View key={trader._id} style={styles.traderCard}>
        <View style={styles.traderHeader}>
          <View style={styles.traderAvatar}>
            <Ionicons name="person" size={32} color="#667eea" />
          </View>
          <View style={styles.traderInfo}>
            <Text style={styles.traderName}>{trader.name}</Text>
            <Text style={styles.traderDescription} numberOfLines={2}>
              {trader.description}
            </Text>
          </View>
        </View>

        <View style={styles.statsGrid}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Win Rate</Text>
            <Text style={[styles.statValue, { color: '#10b981' }]}>
              {trader.win_rate.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Monthly Return</Text>
            <Text style={[styles.statValue, { color: '#667eea' }]}>
              +{trader.monthly_return.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Total Trades</Text>
            <Text style={styles.statValue}>{trader.total_trades}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Subscribers</Text>
            <Text style={styles.statValue}>{trader.subscribers}</Text>
          </View>
        </View>

        <View style={styles.detailsRow}>
          <View style={styles.detailItem}>
            <Ionicons name="trending-up" size={16} color="#667eea" />
            <Text style={styles.detailText}>
              Total Return: {trader.total_return.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.detailItem}>
            <Ionicons name="shield" size={16} color="#ef4444" />
            <Text style={styles.detailText}>
              Max Drawdown: {trader.max_drawdown.toFixed(1)}%
            </Text>
          </View>
        </View>

        <View style={styles.profitShareBox}>
          <Ionicons name="cash" size={16} color="#f59e0b" />
          <Text style={styles.profitShareText}>
            Profit Share: {trader.profit_share}% of your profits
          </Text>
        </View>

        {isSubscribed ? (
          <View style={styles.subscribedBadge}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.subscribedText}>Subscribed</Text>
          </View>
        ) : (
          <TouchableOpacity
            style={styles.copyButton}
            onPress={() => handleSubscribe(trader)}
          >
            <Ionicons name="copy" size={20} color="#fff" />
            <Text style={styles.copyButtonText}>Copy Strategy</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  const renderMySubscription = (subscription: any) => (
    <View key={subscription._id} style={styles.subscriptionCard}>
      <View style={styles.subscriptionHeader}>
        <View>
          <Text style={styles.subscriptionName}>{subscription.strategy_name}</Text>
          <Text style={styles.subscriptionDetail}>
            Capital: ${subscription.capital.toFixed(2)}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.unsubscribeButton}
          onPress={() => handleUnsubscribe(subscription)}
        >
          <Text style={styles.unsubscribeButtonText}>Unsubscribe</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.subscriptionStats}>
        <View style={styles.subscriptionStat}>
          <Text style={styles.subscriptionStatLabel}>Total Profit</Text>
          <Text style={[
            styles.subscriptionStatValue,
            { color: subscription.total_profit >= 0 ? '#10b981' : '#ef4444' }
          ]}>
            {subscription.total_profit >= 0 ? '+' : ''}${subscription.total_profit.toFixed(2)}
          </Text>
        </View>
        <View style={styles.subscriptionStat}>
          <Text style={styles.subscriptionStatLabel}>Copied Trades</Text>
          <Text style={styles.subscriptionStatValue}>{subscription.total_trades}</Text>
        </View>
        <View style={styles.subscriptionStat}>
          <Text style={styles.subscriptionStatLabel}>Leader Win Rate</Text>
          <Text style={styles.subscriptionStatValue}>
            {subscription.leader_win_rate?.toFixed(1)}%
          </Text>
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Copy Trading</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} />}
      >
        {mySubscriptions.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>My Subscriptions</Text>
            {mySubscriptions.map(renderMySubscription)}
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Top Performing Traders</Text>
          <Text style={styles.sectionSubtitle}>
            Copy successful traders and earn automatically
          </Text>

          {loading ? (
            <View style={styles.centerContent}>
              <Ionicons name="sync" size={48} color="#667eea" />
              <Text style={styles.loadingText}>Loading traders...</Text>
            </View>
          ) : topTraders.length === 0 ? (
            <View style={styles.centerContent}>
              <Ionicons name="people-outline" size={64} color="#9ca3af" />
              <Text style={styles.emptyText}>No traders available yet</Text>
            </View>
          ) : (
            topTraders.map(renderTraderCard)
          )}
        </View>

        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#667eea" />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.infoTitle}>How Copy Trading Works</Text>
            <Text style={styles.infoText}>
              1. Choose a profitable trader to copy{'\n'}
              2. Set your capital amount{'\n'}
              3. Their trades are automatically copied to your account{'\n'}
              4. You earn profits proportional to your capital{'\n'}
              5. Leader earns a small % of your profits
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Subscribe Modal */}
      <Modal
        visible={subscribeModalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setSubscribeModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Subscribe to Strategy</Text>
            
            {selectedTrader && (
              <View style={styles.modalTraderInfo}>
                <Text style={styles.modalTraderName}>{selectedTrader.name}</Text>
                <Text style={styles.modalTraderStats}>
                  Win Rate: {selectedTrader.win_rate.toFixed(1)}% | 
                  Monthly Return: +{selectedTrader.monthly_return.toFixed(1)}%
                </Text>
              </View>
            )}

            <Text style={styles.modalLabel}>Capital to Allocate</Text>
            <TextInput
              style={styles.modalInput}
              value={capital}
              onChangeText={setCapital}
              keyboardType="numeric"
              placeholder="Minimum $50"
            />

            <Text style={styles.modalHint}>
              Your trades will be proportional to the leader's capital.
              You keep 90% of profits, leader earns 10%.
            </Text>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.modalCancelButton}
                onPress={() => setSubscribeModalVisible(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalConfirmButton}
                onPress={confirmSubscribe}
              >
                <Text style={styles.modalConfirmText}>Subscribe</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  content: { flex: 1 },
  section: { padding: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '600', color: '#111827', marginBottom: 4 },
  sectionSubtitle: { fontSize: 14, color: '#6b7280', marginBottom: 16 },
  traderCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  traderHeader: { flexDirection: 'row', marginBottom: 16 },
  traderAvatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  traderInfo: { flex: 1, marginLeft: 12, justifyContent: 'center' },
  traderName: { fontSize: 18, fontWeight: '600', color: '#111827' },
  traderDescription: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  statBox: {
    width: '50%',
    padding: 8,
  },
  statLabel: { fontSize: 12, color: '#6b7280', marginBottom: 4 },
  statValue: { fontSize: 20, fontWeight: '600', color: '#111827' },
  detailsRow: { marginBottom: 12 },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 8,
  },
  detailText: { fontSize: 14, color: '#6b7280' },
  profitShareBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef3c7',
    padding: 8,
    borderRadius: 8,
    marginBottom: 12,
    gap: 8,
  },
  profitShareText: { fontSize: 14, color: '#92400e', fontWeight: '500' },
  copyButton: {
    flexDirection: 'row',
    backgroundColor: '#667eea',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  copyButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  subscribedBadge: {
    flexDirection: 'row',
    backgroundColor: '#d1fae5',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  subscribedText: { color: '#065f46', fontSize: 16, fontWeight: '600' },
  subscriptionCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  subscriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  subscriptionName: { fontSize: 16, fontWeight: '600', color: '#111827' },
  subscriptionDetail: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  unsubscribeButton: {
    backgroundColor: '#fee2e2',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  unsubscribeButtonText: { color: '#dc2626', fontSize: 12, fontWeight: '600' },
  subscriptionStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  subscriptionStat: { flex: 1 },
  subscriptionStatLabel: { fontSize: 12, color: '#6b7280', marginBottom: 4 },
  subscriptionStatValue: { fontSize: 16, fontWeight: '600', color: '#111827' },
  centerContent: { alignItems: 'center', justifyContent: 'center', padding: 40 },
  loadingText: { fontSize: 16, color: '#6b7280', marginTop: 12 },
  emptyText: { fontSize: 18, fontWeight: '600', color: '#111827', marginTop: 12 },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#eff6ff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
  },
  infoTitle: { fontSize: 16, fontWeight: '600', color: '#1e40af', marginBottom: 8 },
  infoText: { fontSize: 14, color: '#1e40af', lineHeight: 20 },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '90%',
    maxWidth: 400,
  },
  modalTitle: { fontSize: 20, fontWeight: '600', color: '#111827', marginBottom: 16 },
  modalTraderInfo: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  modalTraderName: { fontSize: 16, fontWeight: '600', color: '#111827', marginBottom: 4 },
  modalTraderStats: { fontSize: 14, color: '#6b7280' },
  modalLabel: { fontSize: 14, fontWeight: '600', color: '#111827', marginBottom: 8 },
  modalInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 8,
  },
  modalHint: { fontSize: 12, color: '#6b7280', marginBottom: 24, lineHeight: 18 },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalCancelButton: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
  },
  modalCancelText: { fontSize: 16, fontWeight: '600', color: '#6b7280' },
  modalConfirmButton: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    backgroundColor: '#667eea',
    alignItems: 'center',
  },
  modalConfirmText: { fontSize: 16, fontWeight: '600', color: '#fff' },
});
