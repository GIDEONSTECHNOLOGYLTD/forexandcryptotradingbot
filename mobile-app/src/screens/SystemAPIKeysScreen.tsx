import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function SystemAPIKeysScreen({ navigation }: any) {
  const [apiKeys, setApiKeys] = useState({
    okx_api_key: '',
    okx_secret_key: '',
    okx_passphrase: '',
  });
  const [showKeys, setShowKeys] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAPIKeys();
  }, []);

  const loadAPIKeys = async () => {
    try {
      // Load masked API keys from backend
      const response = await api.getSystemSettings();
      if (response.api_keys) {
        setApiKeys({
          okx_api_key: response.api_keys.okx_api_key || '',
          okx_secret_key: response.api_keys.okx_secret_key || '',
          okx_passphrase: response.api_keys.okx_passphrase || '',
        });
      }
    } catch (error) {
      console.error('Error loading API keys:', error);
    }
  };

  const saveAPIKeys = async () => {
    try {
      setLoading(true);
      await api.updateSystemSettings({
        api_keys: apiKeys,
      });
      Alert.alert('Success', 'System API keys updated successfully');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update API keys');
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
        <Text style={styles.title}>System API Keys</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.warningBox}>
          <Ionicons name="warning" size={20} color="#f59e0b" />
          <Text style={styles.warningText}>
            These are the master API keys used by the admin bot. Keep them secure!
          </Text>
        </View>

        <View style={styles.toggleContainer}>
          <Text style={styles.toggleLabel}>Show Keys</Text>
          <Switch
            value={showKeys}
            onValueChange={setShowKeys}
            trackColor={{ false: '#d1d5db', true: '#667eea' }}
            thumbColor="#fff"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>OKX API Key</Text>
          <TextInput
            style={styles.input}
            value={apiKeys.okx_api_key}
            onChangeText={(text) => setApiKeys({ ...apiKeys, okx_api_key: text })}
            placeholder="Enter OKX API Key"
            secureTextEntry={!showKeys}
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>OKX Secret Key</Text>
          <TextInput
            style={styles.input}
            value={apiKeys.okx_secret_key}
            onChangeText={(text) => setApiKeys({ ...apiKeys, okx_secret_key: text })}
            placeholder="Enter OKX Secret Key"
            secureTextEntry={!showKeys}
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>OKX Passphrase</Text>
          <TextInput
            style={styles.input}
            value={apiKeys.okx_passphrase}
            onChangeText={(text) => setApiKeys({ ...apiKeys, okx_passphrase: text })}
            placeholder="Enter OKX Passphrase"
            secureTextEntry={!showKeys}
            autoCapitalize="none"
          />
        </View>

        <TouchableOpacity
          style={[styles.saveButton, loading && styles.buttonDisabled]}
          onPress={saveAPIKeys}
          disabled={loading}
        >
          <Text style={styles.saveButtonText}>
            {loading ? 'Saving...' : 'Save API Keys'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>How to Get OKX API Keys</Text>
        <View style={styles.step}>
          <Text style={styles.stepNumber}>1</Text>
          <Text style={styles.stepText}>Log in to OKX.com</Text>
        </View>
        <View style={styles.step}>
          <Text style={styles.stepNumber}>2</Text>
          <Text style={styles.stepText}>Go to Profile → API Management</Text>
        </View>
        <View style={styles.step}>
          <Text style={styles.stepNumber}>3</Text>
          <Text style={styles.stepText}>Create API Key with Trading permissions</Text>
        </View>
        <View style={styles.step}>
          <Text style={styles.stepNumber}>4</Text>
          <Text style={styles.stepText}>Copy API Key, Secret, and Passphrase</Text>
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
  warningBox: {
    flexDirection: 'row',
    backgroundColor: '#fef3c7',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  warningText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    color: '#92400e',
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  inputGroup: {
    marginBottom: 16,
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
    fontSize: 14,
    color: '#111827',
  },
  saveButton: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
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
  step: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stepNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#667eea',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 24,
    fontWeight: 'bold',
    marginRight: 12,
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
  },
});
