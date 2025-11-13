import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function ActiveSessionsScreen({ navigation }: any) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await api.getActiveSessions();
      setSessions(data.sessions || []);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRevokeSession = (sessionId: string) => {
    Alert.alert(
      'Revoke Session',
      'This will log out this device. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Revoke',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.revokeSession(sessionId);
              Alert.alert('Success', 'Session revoked successfully');
              loadSessions();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to revoke session');
            }
          },
        },
      ]
    );
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType?.toLowerCase()) {
      case 'mobile':
      case 'ios':
      case 'android':
        return 'phone-portrait';
      case 'tablet':
        return 'tablet-portrait';
      case 'desktop':
        return 'desktop';
      default:
        return 'phone-portrait';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Active Sessions</Text>
        <TouchableOpacity onPress={loadSessions}>
          <Ionicons name="refresh" size={24} color="#667eea" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadSessions} />}
      >
        {loading ? (
          <View style={styles.centerContent}>
            <Ionicons name="sync" size={48} color="#667eea" />
            <Text style={styles.loadingText}>Loading sessions...</Text>
          </View>
        ) : sessions.length === 0 ? (
          <View style={styles.centerContent}>
            <Ionicons name="phone-portrait-outline" size={64} color="#9ca3af" />
            <Text style={styles.emptyText}>No active sessions</Text>
            <Text style={styles.emptySubtext}>You'll see all devices logged into your account here</Text>
          </View>
        ) : (
          sessions.map((session, index) => (
            <View key={session.id || index} style={styles.sessionCard}>
              <View style={styles.sessionHeader}>
                <View style={styles.deviceIconContainer}>
                  <Ionicons
                    name={getDeviceIcon(session.device_type)}
                    size={24}
                    color="#667eea"
                  />
                </View>
                <View style={styles.sessionInfo}>
                  <Text style={styles.deviceName}>{session.device_name || 'Unknown Device'}</Text>
                  <Text style={styles.deviceType}>{session.device_type || 'Unknown'}</Text>
                </View>
                {session.is_current && (
                  <View style={styles.currentBadge}>
                    <Text style={styles.currentText}>Current</Text>
                  </View>
                )}
              </View>

              <View style={styles.sessionDetails}>
                <View style={styles.detailRow}>
                  <Ionicons name="location" size={16} color="#6b7280" />
                  <Text style={styles.detailText}>{session.location || 'Unknown Location'}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Ionicons name="time" size={16} color="#6b7280" />
                  <Text style={styles.detailText}>
                    Last active: {new Date(session.last_active).toLocaleDateString()}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Ionicons name="globe" size={16} color="#6b7280" />
                  <Text style={styles.detailText}>{session.ip_address || 'Unknown IP'}</Text>
                </View>
              </View>

              {!session.is_current && (
                <TouchableOpacity
                  style={styles.revokeButton}
                  onPress={() => handleRevokeSession(session.id)}
                >
                  <Text style={styles.revokeButtonText}>Revoke Session</Text>
                </TouchableOpacity>
              )}
            </View>
          ))
        )}

        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#667eea" />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.infoTitle}>Session Security</Text>
            <Text style={styles.infoText}>
              These are all devices currently logged into your account. If you see an unfamiliar device, revoke it immediately and change your password.
            </Text>
          </View>
        </View>
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
  sessionCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
  },
  sessionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  deviceIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sessionInfo: { flex: 1, marginLeft: 12 },
  deviceName: { fontSize: 16, fontWeight: '600', color: '#111827' },
  deviceType: { fontSize: 14, color: '#6b7280', marginTop: 2 },
  currentBadge: {
    backgroundColor: '#10b981',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  currentText: { fontSize: 12, fontWeight: '600', color: '#fff' },
  sessionDetails: { marginTop: 8 },
  detailRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8, gap: 8 },
  detailText: { fontSize: 14, color: '#6b7280' },
  revokeButton: {
    marginTop: 16,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#fef2f2',
    borderWidth: 1,
    borderColor: '#fecaca',
  },
  revokeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ef4444',
    textAlign: 'center',
  },
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
