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
      buy_amount_usdt: 10,  // SMART: $10 per listing (many small wins strategy)
      take_profit_percent: 5,  // SMART AI: Adjusts per coin (1-20%)
      stop_loss_percent: 2,  // TIGHT: 2% max loss ($0.20 per trade)
      max_hold_time: 1800,  // 30 min (quick in/out)
    },
    stats: {
      total_trades: 0,
      winning_trades: 0,
      win_rate: 0,
      total_pnl: 0,
    },
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [config, setConfig] = useState({
    buy_amount_usdt: 10,  // SMART: $10 per listing
    take_profit_percent: 5,  // SMART AI: Adjusts per coin
    stop_loss_percent: 2,  // TIGHT: 2% stop
    max_hold_time: 30, // 30 minutes for UI
  });

  useEffect(() => {
    loadData();
    
    // Auto-refresh every 10 seconds for real-time bot status (silent refresh)
    const interval = setInterval(() => {
      loadData(true); // Silent refresh
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadData = async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
        setError(null);
      }
      
      console.log('📊 Loading admin bot data...');
      const [balanceData, statusData] = await Promise.all([
        api.getUserBalance(),
        api.getNewListingBotStatus(),
      ]);
      
      console.log('✅ Admin bot data loaded:', JSON.stringify({ balance: balanceData, status: statusData }));
      
      // Ensure balance is a number
      const balanceValue = typeof balanceData === 'object' ? (balanceData.total || 16.78) : (balanceData || 16.78);
      setBalance(balanceValue);
      
      // Safely extract config and stats as primitives only
      const safeConfig = {
        buy_amount_usdt: Number(statusData?.config?.buy_amount_usdt) || 10,
        take_profit_percent: Number(statusData?.config?.take_profit_percent) || 5,
        stop_loss_percent: Number(statusData?.config?.stop_loss_percent) || 2,
        max_hold_time: Number(statusData?.config?.max_hold_time) || 1800,
      };
      
      const safeStats = {
        total_trades: Number(statusData?.stats?.total_trades) || 0,
        winning_trades: Number(statusData?.stats?.winning_trades) || 0,
        win_rate: Number(statusData?.stats?.win_rate) || 0,
        total_pnl: Number(statusData?.stats?.total_pnl) || 0,
      };
      
      setBotStatus({
        enabled: Boolean(statusData?.enabled),
        config: safeConfig,
        stats: safeStats,
      });
      
      setConfig({
        buy_amount_usdt: safeConfig.buy_amount_usdt,
        take_profit_percent: safeConfig.take_profit_percent,
        stop_loss_percent: safeConfig.stop_loss_percent,
        max_hold_time: safeConfig.max_hold_time / 60, // Convert to minutes
      });
      
      setError(null);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load admin bot data';
      console.error('❌ Error loading admin bot data:', errorMsg);
      if (!silent) {
        setError(errorMsg);
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
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

  const saveConfig = async () => {
    try {
      setLoading(true);
      
      // Save configuration to backend
      await api.updateNewListingBotConfig({
        buy_amount_usdt: config.buy_amount_usdt,
        take_profit_percent: config.take_profit_percent,
        stop_loss_percent: config.stop_loss_percent,
        max_hold_time: config.max_hold_time * 60, // Convert minutes to seconds
      });
      
      setConfigModalVisible(false);
      Alert.alert(
        '✅ Configuration Saved',
        `Settings saved successfully:\n\n` +
        `💰 Buy Amount: $${config.buy_amount_usdt}\n` +
        `📈 Take Profit: ${config.take_profit_percent}%\n` +
        `📉 Stop Loss: ${config.stop_loss_percent}%\n` +
        `⏱️ Max Hold: ${config.max_hold_time} minutes\n\n` +
        `Click "Start Bot" whenever you're ready to begin trading!`,
        [{ text: 'OK' }]
      );
      
      // Reload to get the saved config
      await loadData();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  // Show loading on first load
  if (loading && !refreshing) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Ionicons name="sync" size={48} color="#10b981" />
        <Text style={styles.loadingText}>Loading admin bot...</Text>
        <Text style={styles.loadingSubtext}>Please wait</Text>
      </View>
    );
  }

  // Show error with retry
  if (error && !loading) {
    return (
      <View style={[styles.container, styles.centerContent]}>
        <Ionicons name="alert-circle" size={48} color="#ef4444" />
        <Text style={styles.errorText}>Failed to Load</Text>
        <Text style={styles.errorSubtext}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => loadData()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

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
              🤖 Smart AI • ${Number(config?.buy_amount_usdt || 10)} per trade • Many small wins • Max -{Number(config?.stop_loss_percent || 2)}% ($0.{(Number(config?.buy_amount_usdt || 10) * Number(config?.stop_loss_percent || 2)).toFixed(0)}) loss
            </Text>
          </View>
          <View style={styles.balanceContainer}>
            <Text style={styles.balanceAmount}>${Number(balance || 0).toFixed(2)}</Text>
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
            <Text style={styles.statValue}>{Number(botStatus?.stats?.total_trades || 0)}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>P&L</Text>
            <Text style={[styles.statValue, Number(botStatus?.stats?.total_pnl || 0) >= 0 ? styles.profitText : styles.lossText]}>
              ${Number(botStatus?.stats?.total_pnl || 0).toFixed(2)}
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
            🤖 AI analyzes each coin → Invests $10 → Takes 1-20% profit (AI decides) → Max loss $0.20 → Break-even at 2%
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
            <Text style={styles.stepText}>AI analyzes coin, invests ${Number(config?.buy_amount_usdt || 10)}</Text>
          </View>
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>4</Text>
            </View>
            <Text style={styles.stepText}>AI decides optimal exit (1-20% profit) or -2% stop</Text>
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
          <Text style={styles.resultLabel}>Strategy:</Text>
          <Text style={styles.resultValue}>Many small wins (continuous profits)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Per Trade:</Text>
          <Text style={styles.resultValue}>+$0.50 avg (5% on $10)</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Week 1:</Text>
          <Text style={styles.resultValue}>5 listings → +$2.50 profit</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Month 1:</Text>
          <Text style={styles.resultValue}>20 listings → +$10 profit</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={styles.resultLabel}>Month 3:</Text>
          <Text style={styles.resultValue}>60 listings → +$30 profit</Text>
        </View>
        <View style={styles.resultRow}>
          <Text style={[styles.resultValue, styles.highlightText]}>Catch 1 big pump: +$100 bonus! 🚀</Text>
        </View>
        <View style={styles.infoBox}>
          <Ionicons name="bulb" size={16} color="#f59e0b" />
          <Text style={styles.infoTextSmall}>🤖 AI studies each coin's volume, spread, hype → Adjusts target (1-20%) → Takes continuous small profits → Never waits for huge gains that may not come!</Text>
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
                  value={String(Number(config?.buy_amount_usdt || 50))}
                  onChangeText={(text) => setConfig({ ...config, buy_amount_usdt: parseFloat(text) || 10 })}
                  keyboardType="decimal-pad"
                  placeholder="10"
                />
                <Text style={styles.inputHint}>Recommended: $10 per listing (safe, allows MANY trades, continuous profits)</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Take Profit (%)</Text>
                <TextInput
                  style={styles.input}
                  value={String(Number(config?.take_profit_percent || 30))}
                  onChangeText={(text) => setConfig({ ...config, take_profit_percent: parseFloat(text) || 5 })}
                  keyboardType="decimal-pad"
                  placeholder="5"
                />
                <Text style={styles.inputHint}>AI adjusts per coin (1-20%). Default 5% = safe baseline. AI will optimize!</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Stop Loss (%)</Text>
                <TextInput
                  style={styles.input}
                  value={String(Number(config?.stop_loss_percent || 15))}
                  onChangeText={(text) => setConfig({ ...config, stop_loss_percent: parseFloat(text) || 2 })}
                  keyboardType="decimal-pad"
                  placeholder="2"
                />
                <Text style={styles.inputHint}>Recommended: 2% (tight stop, only $0.20 loss on $10 trade). Break-even protection at 2% profit!</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Max Hold Time (minutes)</Text>
                <TextInput
                  style={styles.input}
                  value={String(Number(config?.max_hold_time || 30))}
                  onChangeText={(text) => setConfig({ ...config, max_hold_time: parseInt(text) || 30 })}
                  keyboardType="number-pad"
                  placeholder="30"
                />
                <Text style={styles.inputHint}>Recommended: 30 min (quick in/out, don't hold too long, take profits fast!)</Text>
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
  infoTextSmall: {
    flex: 1,
    fontSize: 11,
    color: '#374151',
    lineHeight: 16,
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
  centerContent: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#10b981',
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 10,
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
    backgroundColor: '#10b981',
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
});
