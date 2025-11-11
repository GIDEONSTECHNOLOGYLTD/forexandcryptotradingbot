import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import * as api from '../services/api';

export default function BotConfigScreen({ navigation }: any) {
  const [botType, setBotType] = useState('momentum');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [capital, setCapital] = useState('1000');
  const [paperTrading, setPaperTrading] = useState(true);

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

      <TouchableOpacity style={styles.button} onPress={handleCreate}>
        <Text style={styles.buttonText}>Create Bot</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' },
  label: { fontSize: 16, fontWeight: '600', marginTop: 16, marginBottom: 8 },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  picker: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 8 },
  button: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 32,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
