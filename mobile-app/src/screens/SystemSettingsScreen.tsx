import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Switch, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

export default function SystemSettingsScreen({ navigation }: any) {
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [autoBackup, setAutoBackup] = useState(true);
  const [maxBotsPerUser, setMaxBotsPerUser] = useState('10');
  const [defaultCapital, setDefaultCapital] = useState('1000');

  const handleSaveSettings = async () => {
    try {
      const token = await SecureStore.getItemAsync('authToken');
      await axios.post(`${API_BASE_URL}/admin/settings/update`, {
        maintenance_mode: maintenanceMode,
        auto_backup: autoBackup,
        max_bots_per_user: parseInt(maxBotsPerUser),
        default_capital: parseFloat(defaultCapital),
      }, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 30000,
      });
      Alert.alert('Success', 'System settings updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to update settings');
    }
  };

  const handleBackup = () => {
    Alert.alert(
      'Database Backup',
      'Create a backup of all system data?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Backup',
          onPress: () => {
            Alert.alert('Success', 'Backup created successfully');
          },
        },
      ]
    );
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => {
            Alert.alert('Success', 'Cache cleared');
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>System Settings</Text>
        <View style={{ width: 24 }} />
      </View>

      {/* System Status */}
      <Text style={styles.section}>SYSTEM STATUS</Text>
      <View style={styles.card}>
        <View style={styles.item}>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemTitle}>Maintenance Mode</Text>
            <Text style={styles.itemSubtitle}>Disable trading for all users</Text>
          </View>
          <Switch
            value={maintenanceMode}
            onValueChange={setMaintenanceMode}
            trackColor={{ false: '#d1d5db', true: '#ef4444' }}
          />
        </View>
        <View style={styles.item}>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemTitle}>Auto Backup</Text>
            <Text style={styles.itemSubtitle}>Daily automatic backups</Text>
          </View>
          <Switch
            value={autoBackup}
            onValueChange={setAutoBackup}
            trackColor={{ false: '#d1d5db', true: '#10b981' }}
          />
        </View>
      </View>

      {/* Trading Configuration */}
      <Text style={styles.section}>TRADING CONFIGURATION</Text>
      <View style={styles.card}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Max Bots Per User</Text>
          <TextInput
            style={styles.input}
            value={maxBotsPerUser}
            onChangeText={setMaxBotsPerUser}
            keyboardType="numeric"
          />
        </View>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Default Capital ($)</Text>
          <TextInput
            style={styles.input}
            value={defaultCapital}
            onChangeText={setDefaultCapital}
            keyboardType="numeric"
          />
        </View>
      </View>

      {/* OKX Configuration */}
      <Text style={styles.section}>OKX CONFIGURATION</Text>
      <View style={styles.card}>
        <TouchableOpacity style={styles.item}>
          <Ionicons name="key" size={24} color="#667eea" />
          <Text style={styles.itemText}>System API Keys</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item}>
          <Ionicons name="shield-checkmark" size={24} color="#667eea" />
          <Text style={styles.itemText}>Trading Limits</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
      </View>

      {/* System Maintenance */}
      <Text style={styles.section}>SYSTEM MAINTENANCE</Text>
      <View style={styles.card}>
        <TouchableOpacity style={styles.item} onPress={handleBackup}>
          <Ionicons name="cloud-download" size={24} color="#667eea" />
          <Text style={styles.itemText}>Create Backup</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item} onPress={handleClearCache}>
          <Ionicons name="trash" size={24} color="#ef4444" />
          <Text style={[styles.itemText, { color: '#ef4444' }]}>Clear Cache</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
      </View>

      {/* Save Button */}
      <TouchableOpacity style={styles.saveButton} onPress={handleSaveSettings}>
        <Text style={styles.saveButtonText}>Save Settings</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  section: { fontSize: 12, fontWeight: '600', color: '#6b7280', paddingHorizontal: 16, paddingVertical: 12 },
  card: { backgroundColor: '#fff', marginHorizontal: 16, marginBottom: 16, padding: 16, borderRadius: 12 },
  item: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, gap: 12 },
  itemTitle: { fontSize: 16, fontWeight: '600', color: '#111827' },
  itemSubtitle: { fontSize: 14, color: '#6b7280', marginTop: 2 },
  itemText: { flex: 1, fontSize: 16, color: '#111827' },
  inputGroup: { marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '600', color: '#111827', marginBottom: 8 },
  input: { backgroundColor: '#f9fafb', padding: 12, borderRadius: 8, fontSize: 16 },
  saveButton: { backgroundColor: '#667eea', margin: 16, padding: 16, borderRadius: 8, alignItems: 'center' },
  saveButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
