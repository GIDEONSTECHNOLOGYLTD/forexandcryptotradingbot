import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function LoginHistoryScreen({ navigation }: any) {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getLoginHistory();
      setHistory(data.history || []);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to load login history');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusColor = (success: boolean) => {
    return success ? '#10b981' : '#ef4444';
  };

  const getStatusIcon = (success: boolean) => {
    return success ? 'checkmark-circle' : 'close-circle';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Login History</Text>
        <TouchableOpacity onPress={loadHistory}>
          <Ionicons name="refresh" size={24} color="#667eea" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadHistory} />}
      >
        {loading ? (
          <View style={styles.centerContent}>
            <Ionicons name="sync" size={48} color="#667eea" />
            <Text style={styles.loadingText}>Loading history...</Text>
          </View>
        ) : history.length === 0 ? (
          <View style={styles.centerContent}>
            <Ionicons name="time-outline" size={64} color="#9ca3af" />
            <Text style={styles.emptyText}>No login history</Text>
            <Text style={styles.emptySubtext}>Your login attempts will appear here</Text>
          </View>
        ) : (
          <>
            {history.map((item, index) => (
              <View key={item.id || index} style={styles.historyCard}>
                <View style={styles.historyHeader}>
                  <View style={[styles.statusIcon, { backgroundColor: getStatusColor(item.success) + '20' }]}>
                    <Ionicons
                      name={getStatusIcon(item.success)}
                      size={24}
                      color={getStatusColor(item.success)}
                    />
                  </View>
                  <View style={styles.historyInfo}>
                    <View style={styles.statusRow}>
                      <Text style={[styles.statusText, { color: getStatusColor(item.success) }]}>
                        {item.success ? 'Successful Login' : 'Failed Login'}
                      </Text>
                      <Text style={styles.timeText}>{formatDate(item.timestamp)}</Text>
                    </View>
                    <Text style={styles.dateText}>
                      {new Date(item.timestamp).toLocaleString()}
                    </Text>
                  </View>
                </View>

                <View style={styles.detailsContainer}>
                  <View style={styles.detailRow}>
                    <Ionicons name="phone-portrait" size={16} color="#6b7280" />
                    <Text style={styles.detailText}>{item.device || 'Unknown Device'}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Ionicons name="location" size={16} color="#6b7280" />
                    <Text style={styles.detailText}>{item.location || 'Unknown Location'}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Ionicons name="globe" size={16} color="#6b7280" />
                    <Text style={styles.detailText}>{item.ip_address || 'Unknown IP'}</Text>
                  </View>
                  {!item.success && item.reason && (
                    <View style={[styles.detailRow, { marginTop: 8 }]}>
                      <Ionicons name="alert-circle" size={16} color="#ef4444" />
                      <Text style={[styles.detailText, { color: '#ef4444' }]}>
                        Reason: {item.reason}
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            ))}

            <View style={styles.infoCard}>
              <Ionicons name="shield-checkmark" size={24} color="#667eea" />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={styles.infoTitle}>Security Tip</Text>
                <Text style={styles.infoText}>
                  Review your login history regularly. If you see suspicious activity, change your password immediately and enable 2FA.
                </Text>
              </View>
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  content: { flex: 1 },
  centerContent: { alignItems: 'center', justifyContent: 'center', padding: 40 },
  loadingText: { fontSize: 16, color: '#6b7280', marginTop: 12 },
  emptyText: { fontSize: 18, fontWeight: '600', color: '#111827', marginTop: 12 },
  emptySubtext: { fontSize: 14, color: '#6b7280', marginTop: 8, textAlign: 'center' },
  historyCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
  },
  historyHeader: { flexDirection: 'row', alignItems: 'flex-start' },
  statusIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  historyInfo: { flex: 1, marginLeft: 12 },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  statusText: { fontSize: 16, fontWeight: '600' },
  timeText: { fontSize: 12, color: '#6b7280', fontWeight: '500' },
  dateText: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  detailsContainer: { marginTop: 16, paddingTop: 16, borderTopWidth: 1, borderTopColor: '#f3f4f6' },
  detailRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8, gap: 8 },
  detailText: { fontSize: 14, color: '#6b7280' },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#eff6ff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
  },
  infoTitle: { fontSize: 16, fontWeight: '600', color: '#1e40af', marginBottom: 4 },
  infoText: { fontSize: 14, color: '#1e40af', lineHeight: 20 },
});
