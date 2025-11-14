import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, Switch } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

// Trading pairs - Crypto + Forex
const TRADING_PAIRS = {
  crypto: [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
    'SOL/USDT', 'DOT/USDT', 'DOGE/USDT', 'MATIC/USDT', 'LTC/USDT',
    'AVAX/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'TON/USDT'
  ],
  forex: [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD',
    'USD/CAD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY'
  ]
};

export default function BotConfigScreen({ route, navigation }: any) {
  const { user, isAdmin } = useUser();
  const { bot, isEditing } = route.params || {};
  
  // Basic Config - Pre-fill if editing (INSTANT, NO API CALLS)
  const [botType, setBotType] = useState(bot?.config?.bot_type || 'momentum');
  const [strategy, setStrategy] = useState(bot?.config?.strategy || 'momentum');
  const [pairCategory, setPairCategory] = useState('crypto'); // Default to crypto for speed
  const [symbol, setSymbol] = useState(bot?.config?.symbol || 'BTC/USDT');
  const [capital, setCapital] = useState(bot?.config?.capital?.toString() || '20');
  const [paperTrading, setPaperTrading] = useState(bot?.config?.paper_trading ?? (!user?.exchange_connected && !isAdmin));
  
  // Advanced Config (matching backend) - OPTIMIZED DEFAULTS
  const [initialCapital, setInitialCapital] = useState(bot?.config?.initial_capital?.toString() || '10000');
  const [maxPositionSize, setMaxPositionSize] = useState(bot?.config?.max_position_size?.toString() || '2.0');
  const [stopLoss, setStopLoss] = useState(bot?.config?.stop_loss_percent?.toString() || '2.0');
  const [takeProfit, setTakeProfit] = useState(bot?.config?.take_profit_percent?.toString() || '4.0');
  const [maxOpenPositions, setMaxOpenPositions] = useState(bot?.config?.max_open_positions?.toString() || '3');
  const [timeframe, setTimeframe] = useState(bot?.config?.timeframe || '1h');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleCreate = async () => {
    // Validation
    if (!symbol.trim()) {
      Alert.alert('Error', 'Please enter a trading symbol (e.g., BTC/USDT)');
      return;
    }
    const capitalAmount = parseFloat(capital);
    if (!capital || capitalAmount <= 0) {
      Alert.alert('Error', 'Please enter a valid capital amount');
      return;
    }
    // Check minimum for real trading (OKX requires min $5-10 order depending on pair)
    if (!paperTrading && capitalAmount < 15) {
      Alert.alert('Error', 'For real trading, minimum capital is $15 to meet exchange order requirements');
      return;
    }

    // Skip trial check if editing
    if (isEditing) {
      await saveBotNow();
      return;
    }

    // Check trial limits for free users (only for new bots)
    if (!paperTrading && user?.subscription === 'free' && !isAdmin) {
      Alert.alert(
        '🎁 Free Trial',
        'You have 1 free real trade as trial. After that, upgrade to Pro ($29/mo) for 5 trades/month or Enterprise ($99/mo) for unlimited trading!',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Continue', onPress: () => createBotNow() }
        ]
      );
      return;
    }
    
    await createBotNow();
  };

  const createBotNow = async () => {
    try {
      const config = {
        bot_type: botType,
        strategy: strategy,
        symbol: (symbol || 'BTC/USDT').toUpperCase().trim(),
        capital: parseFloat(capital),
        initial_capital: parseFloat(initialCapital),
        max_position_size: parseFloat(maxPositionSize),
        stop_loss_percent: parseFloat(stopLoss),
        take_profit_percent: parseFloat(takeProfit),
        max_open_positions: parseInt(maxOpenPositions),
        timeframe: timeframe,
        paper_trading: paperTrading,
      };
      
      await api.createBot(config);
      
      Alert.alert(
        '✅ Bot Created Successfully!',
        `${(botType || 'momentum').toUpperCase()} bot for ${(symbol || 'BTC/USDT').toUpperCase()}\nCapital: $${capital}\nMode: ${paperTrading ? 'Paper Trading' : 'Real Trading'}\nStop Loss: ${stopLoss}% | Take Profit: ${takeProfit}%\n\nGo to Trading screen to start it!`,
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to create bot';
      
      // Check if trial limit reached
      if (errorMsg.includes('Trial limit') || errorMsg.includes('Upgrade')) {
        Alert.alert(
          '🔒 Trial Ended',
          errorMsg + '\n\nWould you like to upgrade now?',
          [
            { text: 'Maybe Later', style: 'cancel' },
            { text: 'Upgrade', onPress: () => navigation.navigate('Payment') }
          ]
        );
      } else {
        Alert.alert('Error', errorMsg);
      }
    }
  };

  const saveBotNow = async () => {
    try {
      const config = {
        bot_type: botType,
        strategy: strategy,
        symbol: (symbol || 'BTC/USDT').toUpperCase().trim(),
        capital: parseFloat(capital),
        initial_capital: parseFloat(initialCapital),
        max_position_size: parseFloat(maxPositionSize),
        stop_loss_percent: parseFloat(stopLoss),
        take_profit_percent: parseFloat(takeProfit),
        max_open_positions: parseInt(maxOpenPositions),
        timeframe: timeframe,
        paper_trading: paperTrading,
      };
      
      // Update bot via API (you'll need to add this endpoint)
      await api.updateBot(bot._id || bot.id, config);
      
      Alert.alert(
        '✅ Bot Updated Successfully!',
        `${(botType || 'momentum').toUpperCase()} bot for ${(symbol || 'BTC/USDT').toUpperCase()}\nCapital: $${capital}\nMode: ${paperTrading ? 'Paper Trading' : 'Real Trading'}\nStop Loss: ${stopLoss}% | Take Profit: ${takeProfit}%`,
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update bot');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Bot Type</Text>
      <Picker 
        selectedValue={botType} 
        onValueChange={setBotType} 
        style={styles.picker}
        itemStyle={styles.pickerItem}
      >
        <Picker.Item label="Momentum" value="momentum" />
        <Picker.Item label="Grid Trading" value="grid" />
        <Picker.Item label="DCA (Dollar Cost Average)" value="dca" />
      </Picker>

      <Text style={styles.label}>Trading Strategy</Text>
      <Text style={styles.sublabel}>
        Choose the strategy that fits your goals
      </Text>
      <Picker 
        selectedValue={strategy} 
        onValueChange={setStrategy} 
        style={styles.picker}
        itemStyle={styles.pickerItem}
      >
        <Picker.Item label="🚀 Momentum - Trend Following (60% win rate)" value="momentum" />
        <Picker.Item label="📊 Grid Trading - Range Markets (80% win rate)" value="grid" />
        <Picker.Item label="💎 DCA - Buy Dips (85% win rate)" value="dca" />
        <Picker.Item label="🤖 AI Enhanced - ML Predictions (75% win rate)" value="ml_enhanced" />
        {(user?.subscription === 'enterprise' || isAdmin) && (
          <Picker.Item label="⚡ Arbitrage - Risk-Free (95% win rate)" value="arbitrage" />
        )}
      </Picker>
      <Text style={styles.hint}>
        {strategy === 'momentum' && '✓ Best for trending markets, follows price momentum'}
        {strategy === 'grid' && '✓ Best for ranging markets, profits from oscillations'}
        {strategy === 'dca' && '✓ Best for dips, averages down then sells at profit'}
        {strategy === 'ml_enhanced' && '✓ Uses AI predictions and multi-timeframe analysis'}
        {strategy === 'arbitrage' && '✓ Risk-free profits between exchanges (Enterprise only)'}
      </Text>

      <Text style={styles.label}>Market Type</Text>
      <Picker 
        selectedValue={pairCategory} 
        onValueChange={(value) => {
          setPairCategory(value);
          setSymbol(TRADING_PAIRS[value][0]);
        }} 
        style={styles.picker}
        itemStyle={styles.pickerItem}
      >
        <Picker.Item label="Cryptocurrency" value="crypto" />
        <Picker.Item label="Forex" value="forex" />
      </Picker>

      <Text style={styles.label}>Trading Pair</Text>
      <Picker 
        selectedValue={symbol} 
        onValueChange={setSymbol} 
        style={styles.picker}
        itemStyle={styles.pickerItem}
      >
        {TRADING_PAIRS[pairCategory].map(pair => (
          <Picker.Item key={pair} label={pair} value={pair} />
        ))}
      </Picker>

      <Text style={styles.label}>Capital ($)</Text>
      <TextInput
        style={styles.input}
        value={capital}
        onChangeText={setCapital}
        keyboardType="numeric"
        placeholder="Minimum $15 for real trading"
      />
      {!paperTrading && (
        <Text style={styles.hint}>💡 Minimum $15 required for real trading (exchange limits)</Text>
      )}

      <View style={styles.switchContainer}>
        <View>
          <Text style={styles.label}>Trading Mode</Text>
          <Text style={styles.sublabel}>
            {paperTrading ? 'Paper Trading (Simulated)' : 'Real Trading (Live)'}
          </Text>
          {!user?.exchange_connected && !isAdmin && !paperTrading && (
            <Text style={styles.warning}>⚠️ Connect OKX in Settings for real trading</Text>
          )}
          {!paperTrading && user?.subscription === 'free' && !isAdmin && (
            <Text style={styles.trial}>🎁 1 free real trade available</Text>
          )}
        </View>
        <Switch
          value={!paperTrading}
          onValueChange={(value) => setPaperTrading(!value)}
          trackColor={{ false: '#d1d5db', true: '#10b981' }}
          thumbColor={!paperTrading ? '#fff' : '#f4f3f4'}
        />
      </View>

      {/* Advanced Settings */}
      <TouchableOpacity 
        style={styles.advancedToggle} 
        onPress={() => setShowAdvanced(!showAdvanced)}
      >
        <Text style={styles.advancedText}>⚙️ Advanced Settings</Text>
        <Text style={styles.advancedIcon}>{showAdvanced ? '▼' : '▶'}</Text>
      </TouchableOpacity>

      {showAdvanced && (
        <View style={styles.advancedSection}>
          <Text style={styles.label}>Initial Capital ($)</Text>
          <TextInput
            style={styles.input}
            value={initialCapital}
            onChangeText={setInitialCapital}
            keyboardType="numeric"
          />

          <Text style={styles.label}>Max Position Size (x)</Text>
          <TextInput
            style={styles.input}
            value={maxPositionSize}
            onChangeText={setMaxPositionSize}
            keyboardType="numeric"
          />

          <Text style={styles.label}>Stop Loss (%)</Text>
          <TextInput
            style={styles.input}
            value={stopLoss}
            onChangeText={setStopLoss}
            keyboardType="numeric"
          />

          <Text style={styles.label}>Take Profit (%)</Text>
          <TextInput
            style={styles.input}
            value={takeProfit}
            onChangeText={setTakeProfit}
            keyboardType="numeric"
          />

          <Text style={styles.label}>Max Open Positions</Text>
          <TextInput
            style={styles.input}
            value={maxOpenPositions}
            onChangeText={setMaxOpenPositions}
            keyboardType="numeric"
          />

          <Text style={styles.label}>Timeframe</Text>
          <Picker 
            selectedValue={timeframe} 
            onValueChange={setTimeframe} 
            style={styles.picker}
            itemStyle={styles.pickerItem}
          >
            <Picker.Item label="1 Minute" value="1m" />
            <Picker.Item label="5 Minutes" value="5m" />
            <Picker.Item label="15 Minutes" value="15m" />
            <Picker.Item label="1 Hour" value="1h" />
            <Picker.Item label="4 Hours" value="4h" />
            <Picker.Item label="1 Day" value="1d" />
          </Picker>
        </View>
      )}

      <TouchableOpacity style={styles.button} onPress={handleCreate}>
        <Text style={styles.buttonText}>{isEditing ? 'Update Bot' : 'Create Bot'}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' },
  label: { fontSize: 16, fontWeight: '600', marginTop: 16, marginBottom: 8 },
  sublabel: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  warning: { fontSize: 12, color: '#ef4444', marginTop: 4 },
  trial: { fontSize: 12, color: '#10b981', marginTop: 4, fontWeight: '600' },
  hint: { fontSize: 12, color: '#667eea', marginTop: 4, fontStyle: 'italic' },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  advancedToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    marginTop: 20,
  },
  advancedText: { fontSize: 16, fontWeight: '600', color: '#667eea' },
  advancedIcon: { fontSize: 16, color: '#667eea' },
  advancedSection: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 8,
    marginTop: 8,
  },
  picker: { 
    borderWidth: 1, 
    borderColor: '#d1d5db', 
    borderRadius: 8,
    backgroundColor: '#fff',
    minHeight: 50,
    paddingHorizontal: 10,
  },
  pickerItem: {
    fontSize: 16,
    height: 50,
    color: '#111827',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
  },
  button: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 32,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
