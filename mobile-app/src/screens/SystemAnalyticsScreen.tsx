import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

export default function SystemAnalyticsScreen({ navigation }: any) {
  const [analytics, setAnalytics] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const token = await SecureStore.getItemAsync('authToken');
      const response = await axios.get(`${API_BASE_URL}/admin/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 30000,
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAnalytics();
    setRefreshing(false);
  };

  if (!analytics) return <View style={styles.container}><Text style={styles.loading}>Loading...</Text></View>;

  const { overview } = analytics;

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="arrow-back" size={24} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>System Analytics</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.card}>
        <View style={styles.row}>
          <View style={styles.stat}>
            <Ionicons name="people" size={24} color="#667eea" />
            <Text style={styles.value}>{overview.users.total}</Text>
            <Text style={styles.label}>Users</Text>
          </View>
          <View style={styles.stat}>
            <Ionicons name="robot" size={24} color="#667eea" />
            <Text style={styles.value}>{overview.bots.total}</Text>
            <Text style={styles.label}>Bots</Text>
          </View>
        </View>
        <View style={styles.row}>
          <View style={styles.stat}>
            <Ionicons name="swap-horizontal" size={24} color="#10b981" />
            <Text style={styles.value}>{overview.trading.total_trades}</Text>
            <Text style={styles.label}>Trades</Text>
          </View>
          <View style={styles.stat}>
            <Ionicons name="cash" size={24} color="#10b981" />
            <Text style={styles.value}>${overview.revenue.total.toFixed(0)}</Text>
            <Text style={styles.label}>Revenue</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  loading: { textAlign: 'center', marginTop: 100, fontSize: 16, color: '#6b7280' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  card: { backgroundColor: '#fff', margin: 16, padding: 16, borderRadius: 12 },
  row: { flexDirection: 'row', marginBottom: 16 },
  stat: { flex: 1, alignItems: 'center' },
  value: { fontSize: 24, fontWeight: 'bold', color: '#111827', marginTop: 8 },
  label: { fontSize: 12, color: '#6b7280', marginTop: 4 },
});
