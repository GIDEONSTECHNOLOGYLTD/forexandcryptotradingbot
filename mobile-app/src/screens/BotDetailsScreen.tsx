import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function BotDetailsScreen({ route, navigation }: any) {
  const { botId } = route.params;
  const { isAdmin } = useUser();
  const [bot, setBot] = useState<any>(null);

  useEffect(() => {
    loadBot();
  }, []);

  const loadBot = async () => {
    try {
      const data = await api.getBots();
      const bots = Array.isArray(data) ? data : (data.bots || []);
      const found = bots.find((b: any) => b._id === botId);
      if (found) setBot(found);
      else navigation.goBack();
    } catch (error) {
      navigation.goBack();
    }
  };

  if (!bot) return <View style={styles.container}><Text>Loading...</Text></View>;

  const config = bot.config || {};

  return (
    <View style={styles.container}>
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminText}>ADMIN VIEW</Text>
        </View>
      )}

      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Bot Details</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Configuration</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Type:</Text>
            <Text style={styles.value}>{config.bot_type || 'momentum'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Symbol:</Text>
            <Text style={styles.value}>{config.symbol || 'BTC/USDT'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Capital:</Text>
            <Text style={styles.value}>${config.capital || 1000}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Mode:</Text>
            <Text style={styles.value}>{config.paper_trading ? 'Paper' : 'Real'}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Status:</Text>
            <Text style={[styles.value, { color: bot.status === 'running' ? '#10b981' : '#ef4444' }]}>
              {bot.status}
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  adminBadge: { backgroundColor: '#10b981', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, gap: 8 },
  adminText: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  content: { flex: 1, padding: 20 },
  card: { backgroundColor: '#fff', padding: 20, borderRadius: 12, marginBottom: 16 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  label: { fontSize: 14, color: '#6b7280' },
  value: { fontSize: 14, fontWeight: '600', color: '#111827' },
});
