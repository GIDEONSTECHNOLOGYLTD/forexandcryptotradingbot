import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function ExchangeConnectionScreen({ navigation }: any) {
  const [apiKey, setApiKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [passphrase, setPassphrase] = useState('');
  const [paperTrading, setPaperTrading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [showKeys, setShowKeys] = useState(false);

  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const status = await api.getExchangeStatus();
      setConnected(status.connected);
      setPaperTrading(status.paper_trading);
    } catch (error) {
      console.error('Failed to check connection status:', error);
    }
  };

  const handleConnect = async () => {
    if (!apiKey || !secretKey || !passphrase) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      await api.connectExchange({
        okx_api_key: apiKey,
        okx_secret_key: secretKey,
        okx_passphrase: passphrase,
        paper_trading: paperTrading,
      });
      
      Alert.alert(
        'Success',
        'Exchange connected successfully! You can now create real trading bots.',
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
      
      setConnected(true);
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to connect exchange'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    Alert.alert(
      'Disconnect Exchange',
      'Are you sure you want to disconnect your exchange? Your bots will stop trading.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disconnect',
          style: 'destructive',
          onPress: async () => {
            try {
              setLoading(true);
              await api.disconnectExchange();
              Alert.alert('Success', 'Exchange disconnected');
              setConnected(false);
              setApiKey('');
              setSecretKey('');
              setPassphrase('');
            } catch (error: any) {
              Alert.alert('Error', 'Failed to disconnect exchange');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="swap-horizontal" size={48} color="#667eea" />
        <Text style={styles.title}>OKX Exchange Connection</Text>
        <Text style={styles.subtitle}>
          {connected
            ? 'Your exchange is connected'
            : 'Connect your OKX account to enable real trading'}
        </Text>
      </View>

      {connected ? (
        <View style={styles.section}>
          <View style={styles.statusCard}>
            <Ionicons name="checkmark-circle" size={48} color="#10b981" />
            <Text style={styles.statusTitle}>Connected</Text>
            <Text style={styles.statusText}>
              Your OKX exchange is connected and ready for trading
            </Text>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Trading Mode:</Text>
              <Text style={styles.infoValue}>
                {paperTrading ? 'Paper Trading' : 'Live Trading'}
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.button, styles.dangerButton]}
            onPress={handleDisconnect}
            disabled={loading}
          >
            <Text style={styles.dangerButtonText}>
              {loading ? 'Disconnecting...' : 'Disconnect Exchange'}
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.section}>
          <View style={styles.infoBox}>
            <Ionicons name="information-circle" size={24} color="#667eea" />
            <Text style={styles.infoBoxText}>
              To get your OKX API credentials, visit OKX.com → Account → API Management
            </Text>
          </View>

          <View style={styles.form}>
            <Text style={styles.label}>API Key</Text>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.input}
                value={apiKey}
                onChangeText={setApiKey}
                placeholder="Enter your OKX API Key"
                autoCapitalize="none"
                secureTextEntry={!showKeys}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowKeys(!showKeys)}
              >
                <Ionicons
                  name={showKeys ? 'eye-off' : 'eye'}
                  size={24}
                  color="#9ca3af"
                />
              </TouchableOpacity>
            </View>

            <Text style={styles.label}>Secret Key</Text>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.input}
                value={secretKey}
                onChangeText={setSecretKey}
                placeholder="Enter your OKX Secret Key"
                autoCapitalize="none"
                secureTextEntry={!showKeys}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowKeys(!showKeys)}
              >
                <Ionicons
                  name={showKeys ? 'eye-off' : 'eye'}
                  size={24}
                  color="#9ca3af"
                />
              </TouchableOpacity>
            </View>

            <Text style={styles.label}>Passphrase</Text>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.input}
                value={passphrase}
                onChangeText={setPassphrase}
                placeholder="Enter your OKX Passphrase"
                autoCapitalize="none"
                secureTextEntry={!showKeys}
              />
              <TouchableOpacity
                style={styles.eyeButton}
                onPress={() => setShowKeys(!showKeys)}
              >
                <Ionicons
                  name={showKeys ? 'eye-off' : 'eye'}
                  size={24}
                  color="#9ca3af"
                />
              </TouchableOpacity>
            </View>

            <View style={styles.switchContainer}>
              <View>
                <Text style={styles.switchLabel}>Paper Trading Mode</Text>
                <Text style={styles.switchDescription}>
                  {paperTrading
                    ? 'Test with virtual money (recommended)'
                    : 'Trade with real money'}
                </Text>
              </View>
              <Switch
                value={paperTrading}
                onValueChange={setPaperTrading}
                trackColor={{ false: '#d1d5db', true: '#667eea' }}
                thumbColor="#fff"
              />
            </View>

            <TouchableOpacity
              style={styles.button}
              onPress={handleConnect}
              disabled={loading}
            >
              <Text style={styles.buttonText}>
                {loading ? 'Connecting...' : 'Connect Exchange'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.warningBox}>
            <Ionicons name="shield-checkmark" size={24} color="#f59e0b" />
            <Text style={styles.warningText}>
              Your API keys are encrypted and stored securely. We never have access to
              withdraw funds from your account.
            </Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    backgroundColor: '#fff',
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 16,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  section: {
    padding: 20,
  },
  statusCard: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  statusTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#10b981',
    marginTop: 12,
    marginBottom: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  infoLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  infoBox: {
    backgroundColor: '#eff6ff',
    padding: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 24,
  },
  infoBoxText: {
    flex: 1,
    fontSize: 14,
    color: '#1e40af',
  },
  form: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    gap: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  inputContainer: {
    position: 'relative',
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    paddingRight: 48,
    fontSize: 16,
  },
  eyeButton: {
    position: 'absolute',
    right: 12,
    top: 12,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  switchLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  switchDescription: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  button: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  dangerButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#ef4444',
  },
  dangerButtonText: {
    color: '#ef4444',
    fontSize: 16,
    fontWeight: '600',
  },
  warningBox: {
    backgroundColor: '#fffbeb',
    padding: 16,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginTop: 20,
  },
  warningText: {
    flex: 1,
    fontSize: 12,
    color: '#92400e',
  },
});
