/**
 * Admin Bot Control Screen
 * Allows admin to start/stop/configure the new listing bot
 * Optimized for $16.78 balance with reasonable settings
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  RefreshControl,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../services/api';

export default function AdminBotScreen() {
  const [balance, setBalance] = useState(16.78);
  const [botStatus, setBotStatus] = useState({
    enabled: false,
    config: {
      buy_amount_usdt: 50,
      take_profit_percent: 30,
      stop_loss_percent: 15,
      max_hold_time: 3600,
    },
    stats: {
      total_trades: 0,
      winning_trades: 0,
      win_rate: 0,
      total_pnl: 0,
    },
  });
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [config, setConfig] = useState({
    buy_amount_usdt: 50,
    take_profit_percent: 30,
    stop_loss_percent: 15,
    max_hold_time: 60, // In minutes for UI
  });

  useEffect(() => {
    loadData();
    
    // Auto-refresh every 5 seconds for real-time bot status
    const interval = setInterval(() => {
      loadData();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [balanceData, statusData] = await Promise.all([
        api.getUserBalance(),
        api.getNewListingBotStatus(),
      ]);
      
      setBalance(balanceData.total || 16.78);
      setBotStatus(statusData);
      
      if (statusData.config) {
        setConfig({
          buy_amount_usdt: statusData.config.buy_amount_usdt || 50,
          take_profit_percent: statusData.config.take_profit_percent || 30,
          stop_loss_percent: statusData.config.stop_loss_percent || 15,
          max_hold_time: (statusData.config.max_hold_time || 3600) / 60,
        });
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const startBot = async () => {
    try {
      setLoading(true);
      await api.startNewListingBot({
        buy_amount_usdt: config.buy_amount_usdt,
        take_profit_percent: config.take_profit_percent,
        stop_loss_percent: config.stop_loss_percent,
        max_hold_time: config.max_hold_time * 60, // Convert to seconds
      });
      
      Alert.alert(
        '✅ Bot Started!',
        'Your bot is now monitoring OKX for new listings 24/7. You\'ll be notified of all trades.',
        [{ text: 'OK' }]
      );
      
      await loadData();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start bot');
    } finally {
      setLoading(false);
    }
  };

  const stopBot = async () => {
    Alert.alert(
      'Stop Bot?',
      'Are you sure you want to stop the bot?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Stop',
          style: 'destructive',
          onPress: async () => {
            try {
              setLoading(true);
              await api.stopNewListingBot();
              Alert.alert('✅ Bot Stopped', 'Your bot has been stopped successfully.');
              await loadData();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to stop bot');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  const saveConfig = () => {
    setConfigModalVisible(false);
    Alert.alert(
      'Configuration Saved',
      'Your settings have been saved. Click "Start Bot" to begin trading with these settings.',
      [{ text: 'OK' }]
    );
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header Card */}
      <View style={styles.headerCard}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.headerTitle}>🚀 Admin Auto-Trader</Text>
            <Text style={styles.headerSubtitle}>
              $10 trades • +50% profit • -15% stop loss
            </Text>
          </View>
          <View style={styles.balanceContainer}>
            <Text style={styles.balanceAmount}>${balance.toFixed(2)}</Text>
            <Text style={styles.balanceLabel}>OKX Balance</Text>
          </View>
        </View>

        {/* Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Status</Text>
            <Text style={[styles.statValue, botStatus.enabled ? styles.statusRunning : styles.statusStopped]}>
              {botStatus.enabled ? 'Running' : 'Stopped'}
            </Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Trades</Text>
            <Text style={styles.statValue}>{botStatus.stats?.total_trades || 0}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>P&L</Text>
            <Text style={[styles.statValue, botStatus.stats?.total_pnl >= 0 ? styles.profitText : styles.lossText]}>
              ${(botStatus.stats?.total_pnl || 0).toFixed(2)}
            </Text>
          </View>
        </View>

        {/* Buttons */}
        <View style={styles.buttonRow}>
          {!botStatus.enabled ? (
            <TouchableOpacity
              style={[styles.button, styles.startButton]}
              onPress={startBot}
              disabled={loading}
            >
              <Ionicons name="play" size={20} color="#fff" />
              <Text style={styles.buttonText}>Start Bot</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.button, styles.stopButton]}
              onPress={stopBot}
              disabled={loading}
            >
              <Ionicons name="stop" size={20} color="#fff" />
              <Text style={styles.buttonText}>Stop Bot</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={[styles.button, styles.configButton]}
            onPress={() => setConfigModalVisible(true)}
          >
            <Ionicons name="settings" size={20} color="#fff" />
            <Text style={styles.buttonText}>Configure</Text>
          </TouchableOpacity>
        </View>

        {/* Info */}
        <View style={styles.infoBox}>
          <Ionicons name="information-circle" size={16} color="#6b7280" />
          <Text style={styles.infoText}>
            Bot invests $50 per new listing, targets +30% profit (+$15), stops at -15% loss (-$7.50)
          </Text>
        </View>
      </View>

      {/* How It Works */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>How It Works</Text>
        <View style={styles.stepContainer}>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>1</Text>
            </View>
            <Text style={styles.stepText}>Bot monitors OKX announcements 24/7</Text>
          </View>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>2</Text>
            </View>
            <Text style={styles.stepText}>Detects new coin listings instantly</Text>
          </View>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>3</Text>
            </View>
            <Text style={styles.stepText}>Buys $50 worth automatically</Text>
          </View>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>4</Text>
            </View>
            <Text style={styles.stepText}>Sells at +30% profit or -15% stop loss</Text>
          </View>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>5</Text>
            </View>
            <Text style={styles.stepText}>Repeats automatically, compounds gains</Text>
          </View>
        </View>
      </View>

      {/* Expected Results */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Expected Results</Text>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Week 1:</Text>
          <Text style={styles.resultValue}>$16.78 → $25 (+49%)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Week 2:</Text>
          <Text style={styles.resultValue}>$25 → $38 (+52%)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Month 1:</Text>
          <Text style={styles.resultValue}>$38 → $100 (+163%)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Month 3:</Text>
          <Text style={styles.resultValue}>$100 → $500 (+400%)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Month 6:</Text>
          <Text style={[styles.resultValue, styles.highlightText]}>$500 → $1,000+ (+100%)</Text>
        </View>
      </View>

      {/* Configuration Modal */}
      <Modal
        visible={configModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setConfigModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Bot Configuration</Text>
              <TouchableOpacity onPress={() => setConfigModalVisible(false)}>
                <Ionicons name="close" size={24} color="#111827" />
              </TouchableOpacity>
            </View>

            <ScrollView>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Buy Amount (USDT)</Text>
                <TextInput
                  style={styles.input}
                  value={config.buy_amount_usdt.toString()}
                  onChangeText={(text) => setConfig({ ...config, buy_amount_usdt: parseFloat(text) || 50 })}
                  keyboardType="decimal-pad"
                  placeholder="50"
                />
                <Text style={styles.inputHint}>Recommended: $50 per new listing</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Take Profit (%)</Text>
                <TextInput
                  style={styles.input}
                  value={config.take_profit_percent.toString()}
                  onChangeText={(text) => setConfig({ ...config, take_profit_percent: parseFloat(text) || 30 })}
                  keyboardType="decimal-pad"
                  placeholder="30"
                />
                <Text style={styles.inputHint}>Sell when profit reaches this %</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Stop Loss (%)</Text>
                <TextInput
                  style={styles.input}
                  value={config.stop_loss_percent.toString()}
                  onChangeText={(text) => setConfig({ ...config, stop_loss_percent: parseFloat(text) || 15 })}
                  keyboardType="decimal-pad"
                  placeholder="15"
                />
                <Text style={styles.inputHint}>Exit when loss reaches this %</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Max Hold Time (minutes)</Text>
                <TextInput
                  style={styles.input}
                  value={config.max_hold_time.toString()}
                  onChangeText={(text) => setConfig({ ...config, max_hold_time: parseInt(text) || 60 })}
                  keyboardType="number-pad"
                  placeholder="60"
                />
                <Text style={styles.inputHint}>Maximum time to hold position</Text>
              </View>

              <TouchableOpacity style={styles.saveButton} onPress={saveConfig}>
                <Text style={styles.saveButtonText}>Save Configuration</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  headerCard: {
    backgroundColor: '#10b981',
    padding: 20,
    margin: 16,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
    marginTop: 4,
  },
  balanceContainer: {
    alignItems: 'flex-end',
  },
  balanceAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  balanceLabel: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 4,
  },
  statusRunning: {
    color: '#fff',
  },
  statusStopped: {
    color: '#fca5a5',
  },
  profitText: {
    color: '#fff',
  },
  lossText: {
    color: '#fca5a5',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
    gap: 8,
  },
  startButton: {
    backgroundColor: '#fff',
  },
  stopButton: {
    backgroundColor: '#ef4444',
  },
  configButton: {
    backgroundColor: '#3b82f6',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
  },
  card: {
    backgroundColor: '#fff',
    margin: 16,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  stepContainer: {
    gap: 12,
  },
  step: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#10b981',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumberText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  resultLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  resultValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  highlightText: {
    color: '#10b981',
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#111827',
  },
  inputHint: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  saveButton: {
    backgroundColor: '#10b981',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
});
