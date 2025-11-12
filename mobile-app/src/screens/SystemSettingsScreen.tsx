import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SystemSettingsScreen({ navigation }: any) {
  const handleAction = (action: string) => {
    Alert.alert('Coming Soon', `${action} will be available in the next update`);
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

      <Text style={styles.section}>TRADING CONFIGURATION</Text>
      <TouchableOpacity style={styles.item} onPress={() => handleAction('OKX Configuration')}>
        <Ionicons name="swap-horizontal" size={24} color="#667eea" />
        <Text style={styles.itemText}>OKX Configuration</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => handleAction('Trading Limits')}>
        <Ionicons name="shield-checkmark" size={24} color="#667eea" />
        <Text style={styles.itemText}>Trading Limits</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <Text style={styles.section}>SYSTEM MAINTENANCE</Text>
      <TouchableOpacity style={styles.item} onPress={() => handleAction('Database Backup')}>
        <Ionicons name="cloud-download" size={24} color="#667eea" />
        <Text style={styles.itemText}>Database Backup</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => handleAction('Clear Cache')}>
        <Ionicons name="trash" size={24} color="#ef4444" />
        <Text style={[styles.itemText, { color: '#ef4444' }]}>Clear Cache</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  section: { fontSize: 12, fontWeight: '600', color: '#6b7280', paddingHorizontal: 16, paddingVertical: 12 },
  item: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', padding: 16, marginTop: 1, gap: 12 },
  itemText: { flex: 1, fontSize: 16, color: '#111827' },
});
