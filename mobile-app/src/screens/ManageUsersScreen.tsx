import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

export default function ManageUsersScreen({ navigation }: any) {
  const [users, setUsers] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const token = await SecureStore.getItemAsync('authToken');
      const response = await axios.get(`${API_BASE_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 30000,
      });
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error loading users:', error);
      Alert.alert('Error', 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUsers();
    setRefreshing(false);
  };

  const getSubscriptionColor = (subscription: string) => {
    switch (subscription?.toLowerCase()) {
      case 'enterprise': return '#10b981';
      case 'pro': return '#667eea';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading users...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Manage Users</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.statsCard}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{users.length}</Text>
          <Text style={styles.statLabel}>Total Users</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{users.filter(u => u.is_active).length}</Text>
          <Text style={styles.statLabel}>Active</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{users.filter(u => u.subscription !== 'free').length}</Text>
          <Text style={styles.statLabel}>Paid</Text>
        </View>
      </View>

      {users.map((user) => (
        <View key={user._id} style={styles.userCard}>
          <View style={styles.userHeader}>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                <Text style={styles.userName}>{user.full_name || user.email}</Text>
                {user.role === 'admin' && (
                  <View style={styles.adminBadge}>
                    <Text style={styles.adminBadgeText}>ADMIN</Text>
                  </View>
                )}
              </View>
              <Text style={styles.userEmail}>{user.email}</Text>
            </View>
            <View style={[styles.subscriptionBadge, { backgroundColor: getSubscriptionColor(user.subscription) }]}>
              <Text style={styles.subscriptionText}>{(user.subscription || 'FREE').toUpperCase()}</Text>
            </View>
          </View>

          <View style={styles.userStats}>
            <View style={styles.userStat}>
              <Ionicons name="cube-outline" size={16} color="#6b7280" />
              <Text style={styles.userStatText}>{user.bot_count} bots</Text>
            </View>
            {user.exchange_connected && (
              <View style={styles.userStat}>
                <Ionicons name="checkmark-circle" size={16} color="#10b981" />
                <Text style={styles.userStatText}>OKX Connected</Text>
              </View>
            )}
            <View style={styles.userStat}>
              <Ionicons name={user.is_active ? 'checkmark-circle' : 'close-circle'} size={16} color={user.is_active ? '#10b981' : '#ef4444'} />
              <Text style={styles.userStatText}>{user.is_active ? 'Active' : 'Inactive'}</Text>
            </View>
          </View>

          <Text style={styles.joinedText}>Joined: {new Date(user.created_at).toLocaleDateString()}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  loadingText: { textAlign: 'center', marginTop: 100, fontSize: 16, color: '#6b7280' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  backButton: { padding: 8 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  statsCard: { flexDirection: 'row', backgroundColor: '#fff', margin: 16, padding: 16, borderRadius: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  statLabel: { fontSize: 12, color: '#6b7280', marginTop: 4 },
  userCard: { backgroundColor: '#fff', margin: 16, marginTop: 0, padding: 16, borderRadius: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  userHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  userName: { fontSize: 16, fontWeight: '600', color: '#111827' },
  userEmail: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  adminBadge: { backgroundColor: '#ef4444', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4 },
  adminBadgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  subscriptionBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  subscriptionText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  userStats: { flexDirection: 'row', gap: 16, marginBottom: 8 },
  userStat: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  userStatText: { fontSize: 12, color: '#6b7280' },
  joinedText: { fontSize: 12, color: '#9ca3af', marginTop: 4 },
});
