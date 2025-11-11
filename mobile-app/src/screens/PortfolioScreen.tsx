import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function PortfolioScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Portfolio</Text>
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
