import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView, Switch } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function BotConfigScreen({ navigation }: any) {
  const { user, isAdmin } = useUser();
  const [botType, setBotType] = useState('momentum');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [capital, setCapital] = useState('1000');
  // Default to real trading if user has OKX connected, otherwise paper trading
  const [paperTrading, setPaperTrading] = useState(!user?.exchange_connected && !isAdmin);

  const handleCreate = async () => {
    try {
      const config = {
        bot_type: botType,
        symbol,
        capital: parseFloat(capital),
        paper_trading: paperTrading,
      };
      await api.createBot(config);
      Alert.alert('Success', 'Bot created successfully!');
      navigation.goBack();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create bot');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Bot Type</Text>
      <Picker selectedValue={botType} onValueChange={setBotType} style={styles.picker}>
        <Picker.Item label="Momentum" value="momentum" />
        <Picker.Item label="Grid Trading" value="grid" />
        <Picker.Item label="DCA" value="dca" />
      </Picker>

      <Text style={styles.label}>Symbol</Text>
      <TextInput style={styles.input} value={symbol} onChangeText={setSymbol} />

      <Text style={styles.label}>Capital ($)</Text>
      <TextInput
        style={styles.input}
        value={capital}
        onChangeText={setCapital}
        keyboardType="numeric"
      />

      <View style={styles.switchContainer}>
        <View>
          <Text style={styles.label}>Trading Mode</Text>
          <Text style={styles.sublabel}>
            {paperTrading ? 'Paper Trading (Simulated)' : 'Real Trading (Live)'}
          </Text>
          {!user?.exchange_connected && !isAdmin && !paperTrading && (
            <Text style={styles.warning}>⚠️ Connect OKX in Settings for real trading</Text>
          )}
        </View>
        <Switch
          value={!paperTrading}
          onValueChange={(value) => setPaperTrading(!value)}
          trackColor={{ false: '#d1d5db', true: '#10b981' }}
          thumbColor={!paperTrading ? '#fff' : '#f4f3f4'}
        />
      </View>

      <TouchableOpacity style={styles.button} onPress={handleCreate}>
        <Text style={styles.buttonText}>Create Bot</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' },
  label: { fontSize: 16, fontWeight: '600', marginTop: 16, marginBottom: 8 },
  sublabel: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  warning: { fontSize: 12, color: '#ef4444', marginTop: 4 },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  picker: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 8 },
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
