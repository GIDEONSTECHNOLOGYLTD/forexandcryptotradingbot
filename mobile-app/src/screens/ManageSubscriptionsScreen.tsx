import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

export default function ManageSubscriptionsScreen({ navigation }: any) {
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

  const updateSubscription = async (userId: string, newPlan: string) => {
    try {
      const token = await SecureStore.getItemAsync('authToken');
      await axios.put(
        `${API_BASE_URL}/admin/users/${userId}/subscription`,
        { subscription: newPlan },
        {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 30000,
        }
      );
      Alert.alert('Success', `Subscription updated to ${newPlan.toUpperCase()}`);
      loadUsers();
    } catch (error) {
      Alert.alert('Error', 'Failed to update subscription');
    }
  };

  const showSubscriptionOptions = (user: any) => {
    Alert.alert(
      `Update Subscription: ${user.email}`,
      'Choose new subscription plan',
      [
        { text: 'Free', onPress: () => updateSubscription(user._id, 'free') },
        { text: 'Pro', onPress: () => updateSubscription(user._id, 'pro') },
        { text: 'Enterprise', onPress: () => updateSubscription(user._id, 'enterprise') },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const getSubscriptionColor = (subscription: string) => {
    switch (subscription?.toLowerCase()) {
      case 'enterprise': return '#8b5cf6';
      case 'pro': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Manage Subscriptions</Text>
        <TouchableOpacity onPress={loadUsers}>
          <Ionicons name="refresh" size={24} color="#667eea" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {users.map((user) => (
          <View key={user._id} style={styles.userCard}>
            <View style={styles.userHeader}>
              <View style={{ flex: 1 }}>
                <Text style={styles.userName}>{user.full_name || 'User'}</Text>
                <Text style={styles.userEmail}>{user.email}</Text>
              </View>
              <View style={[styles.subscriptionBadge, { backgroundColor: getSubscriptionColor(user.subscription) }]}>
                <Text style={styles.subscriptionText}>{(user.subscription || 'FREE').toUpperCase()}</Text>
              </View>
            </View>

            <View style={styles.userStats}>
              <View style={styles.userStat}>
                <Ionicons name="cube-outline" size={16} color="#6b7280" />
                <Text style={styles.userStatText}>{user.bot_count || 0} bots</Text>
              </View>
              {user.exchange_connected && (
                <View style={styles.userStat}>
                  <Ionicons name="checkmark-circle" size={16} color="#10b981" />
                  <Text style={styles.userStatText}>OKX Connected</Text>
                </View>
              )}
            </View>

            <TouchableOpacity
              style={styles.updateButton}
              onPress={() => showSubscriptionOptions(user)}
            >
              <Ionicons name="create-outline" size={20} color="#fff" />
              <Text style={styles.updateButtonText}>Update Subscription</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  backButton: { padding: 8 },
  title: { fontSize: 20, fontWeight: '600', color: '#111827', flex: 1, marginLeft: 16 },
  scrollView: { flex: 1 },
  userCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  userName: { fontSize: 16, fontWeight: '600', color: '#111827' },
  userEmail: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  subscriptionBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  subscriptionText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  userStats: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 12,
  },
  userStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  userStatText: { fontSize: 12, color: '#6b7280' },
  updateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#667eea',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  updateButtonText: { color: '#fff', fontSize: 14, fontWeight: '600' },
});
