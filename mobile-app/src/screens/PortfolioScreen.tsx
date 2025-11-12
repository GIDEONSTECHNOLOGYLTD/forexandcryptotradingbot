import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../context/UserContext';

export default function PortfolioScreen() {
  const { isAdmin } = useUser();

  return (
    <ScrollView style={styles.container}>
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminBadgeText}>ADMIN - System Portfolio</Text>
        </View>
      )}
      <View style={styles.header}>
        <Text style={styles.title}>{isAdmin ? 'System Portfolio' : 'Portfolio'}</Text>
      </View>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Total Balance</Text>
        <Text style={styles.balance}>$10,000.00</Text>
        <Text style={styles.pnl}>+$0.00 (0.00%)</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Performance</Text>
        <View style={styles.statRow}>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Win Rate</Text>
            <Text style={styles.statValue}>0%</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Total Trades</Text>
            <Text style={styles.statValue}>0</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  adminBadge: {
    backgroundColor: '#10b981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 8,
  },
  adminBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  header: { padding: 20, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold' },
  card: { backgroundColor: '#fff', margin: 16, padding: 20, borderRadius: 12 },
  cardTitle: { fontSize: 16, color: '#6b7280', marginBottom: 8 },
  balance: { fontSize: 32, fontWeight: 'bold', color: '#111827' },
  pnl: { fontSize: 16, color: '#10b981', marginTop: 4 },
  statRow: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 16 },
  stat: { alignItems: 'center' },
  statLabel: { fontSize: 12, color: '#6b7280' },
  statValue: { fontSize: 18, fontWeight: '600', marginTop: 4 },
});
