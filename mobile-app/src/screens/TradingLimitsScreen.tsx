import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function TradingLimitsScreen({ navigation }: any) {
  const [limits, setLimits] = useState({
    max_position_size: 1000,
    max_daily_trades: 50,
    max_loss_per_trade: 100,
    max_daily_loss: 500,
    max_leverage: 3,
    require_confirmation: false,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadLimits();
  }, []);

  const loadLimits = async () => {
    try {
      const response = await api.getSystemSettings();
      if (response.trading_limits) {
        setLimits(response.trading_limits);
      }
    } catch (error) {
      console.error('Error loading limits:', error);
    }
  };

  const saveLimits = async () => {
    try {
      setLoading(true);
      await api.updateSystemSettings({
        trading_limits: limits,
      });
      Alert.alert('Success', 'Trading limits updated successfully');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update limits');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Trading Limits</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.infoBox}>
          <Ionicons name="shield-checkmark" size={20} color="#10b981" />
          <Text style={styles.infoText}>
            Set system-wide trading limits to protect against excessive losses and manage risk.
          </Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Position Size (USDT)</Text>
          <TextInput
            style={styles.input}
            value={limits.max_position_size.toString()}
            onChangeText={(text) => setLimits({ ...limits, max_position_size: parseFloat(text) || 0 })}
            keyboardType="decimal-pad"
            placeholder="1000"
          />
          <Text style={styles.hint}>Maximum amount per single trade</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Daily Trades</Text>
          <TextInput
            style={styles.input}
            value={limits.max_daily_trades.toString()}
            onChangeText={(text) => setLimits({ ...limits, max_daily_trades: parseInt(text) || 0 })}
            keyboardType="number-pad"
            placeholder="50"
          />
          <Text style={styles.hint}>Maximum number of trades per day</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Loss Per Trade (USDT)</Text>
          <TextInput
            style={styles.input}
            value={limits.max_loss_per_trade.toString()}
            onChangeText={(text) => setLimits({ ...limits, max_loss_per_trade: parseFloat(text) || 0 })}
            keyboardType="decimal-pad"
            placeholder="100"
          />
          <Text style={styles.hint}>Maximum loss allowed on a single trade</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Daily Loss (USDT)</Text>
          <TextInput
            style={styles.input}
            value={limits.max_daily_loss.toString()}
            onChangeText={(text) => setLimits({ ...limits, max_daily_loss: parseFloat(text) || 0 })}
            keyboardType="decimal-pad"
            placeholder="500"
          />
          <Text style={styles.hint}>Maximum total loss per day</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Leverage</Text>
          <TextInput
            style={styles.input}
            value={limits.max_leverage.toString()}
            onChangeText={(text) => setLimits({ ...limits, max_leverage: parseFloat(text) || 1 })}
            keyboardType="decimal-pad"
            placeholder="3"
          />
          <Text style={styles.hint}>Maximum leverage multiplier (1-10x)</Text>
        </View>

        <View style={styles.toggleContainer}>
          <View style={styles.toggleInfo}>
            <Text style={styles.toggleLabel}>Require Trade Confirmation</Text>
            <Text style={styles.toggleHint}>Ask for confirmation before executing trades</Text>
          </View>
          <Switch
            value={limits.require_confirmation}
            onValueChange={(value) => setLimits({ ...limits, require_confirmation: value })}
            trackColor={{ false: '#d1d5db', true: '#667eea' }}
            thumbColor="#fff"
          />
        </View>

        <TouchableOpacity
          style={[styles.saveButton, loading && styles.buttonDisabled]}
          onPress={saveLimits}
          disabled={loading}
        >
          <Text style={styles.saveButtonText}>
            {loading ? 'Saving...' : 'Save Limits'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Risk Management Tips</Text>
        <View style={styles.tip}>
          <Ionicons name="bulb" size={20} color="#f59e0b" />
          <Text style={styles.tipText}>
            <Text style={styles.tipBold}>Start Conservative:</Text> Begin with lower limits and increase gradually as you gain confidence.
          </Text>
        </View>
        <View style={styles.tip}>
          <Ionicons name="bulb" size={20} color="#f59e0b" />
          <Text style={styles.tipText}>
            <Text style={styles.tipBold}>2% Rule:</Text> Never risk more than 2% of your total capital on a single trade.
          </Text>
        </View>
        <View style={styles.tip}>
          <Ionicons name="bulb" size={20} color="#f59e0b" />
          <Text style={styles.tipText}>
            <Text style={styles.tipBold}>Daily Loss Limit:</Text> Set to 5-10% of total capital to protect your account.
          </Text>
        </View>
        <View style={styles.tip}>
          <Ionicons name="bulb" size={20} color="#f59e0b" />
          <Text style={styles.tipText}>
            <Text style={styles.tipBold}>Leverage Caution:</Text> Higher leverage = higher risk. Use 1-3x for safer trading.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  backButton: {
    marginRight: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
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
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#d1fae5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  infoText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#065f46',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
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
  hint: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    marginBottom: 20,
  },
  toggleInfo: {
    flex: 1,
    marginRight: 16,
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  toggleHint: {
    fontSize: 12,
    color: '#6b7280',
  },
  saveButton: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  tipText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  tipBold: {
    fontWeight: '600',
    color: '#111827',
  },
});
