import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

export default function SettingsScreen({ navigation }: any) {
  const { user, isAdmin } = useUser();
  
  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await api.logout();
          navigation.replace('Login');
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Admin Badge */}
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={20} color="#fff" />
          <Text style={styles.adminBadgeText}>ADMIN SETTINGS</Text>
        </View>
      )}

      {/* User Info Card */}
      <View style={styles.userCard}>
        <View style={styles.userIconContainer}>
          <Ionicons name="person" size={40} color="#667eea" />
        </View>
        <Text style={styles.userName}>{user?.full_name || user?.email}</Text>
        <Text style={styles.userEmail}>{user?.email}</Text>
        <View style={[styles.subscriptionBadge, isAdmin && styles.adminSubscriptionBadge]}>
          <Text style={styles.subscriptionText}>
            {isAdmin ? '👑 ADMIN - ENTERPRISE' : (user?.subscription || 'FREE').toUpperCase()}
          </Text>
        </View>
      </View>

      {/* Admin-Only Section */}
      {isAdmin && (
        <>
          <Text style={styles.sectionTitle}>ADMIN TOOLS</Text>
          <TouchableOpacity style={styles.adminToolButton} onPress={() => navigation.navigate('ManageUsers')}>
            <Ionicons name="people-outline" size={24} color="#667eea" />
            <Text style={styles.adminToolText}>Manage Users</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminToolButton} onPress={() => navigation.navigate('ManageSubscriptions')}>
            <Ionicons name="card-outline" size={24} color="#667eea" />
            <Text style={styles.adminToolText}>Manage Subscriptions</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminToolButton} onPress={() => navigation.navigate('SystemAnalytics')}>
            <Ionicons name="analytics-outline" size={24} color="#667eea" />
            <Text style={styles.adminToolText}>System Analytics</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminToolButton} onPress={() => navigation.navigate('SystemSettings')}>
            <Ionicons name="settings-outline" size={24} color="#667eea" />
            <Text style={styles.adminToolText}>System Settings</Text>
          </TouchableOpacity>
        </>
      )}

      {/* Regular Settings */}
      <Text style={styles.sectionTitle}>{isAdmin ? 'PERSONAL SETTINGS' : 'SETTINGS'}</Text>
      
      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('AISuggestions')}>
        <Ionicons name="sparkles" size={24} color="#667eea" />
        <Text style={styles.itemText}>AI Suggestions</Text>
        <Text style={styles.itemBadge}>NEW</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('Payment')}>
        <Ionicons name="card-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Subscription</Text>
        {!isAdmin && <Text style={styles.itemBadge}>{user?.subscription || 'FREE'}</Text>}
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('ExchangeConnection')}>
        <Ionicons name="swap-horizontal-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Exchange Connection</Text>
        {user?.exchange_connected && <Ionicons name="checkmark-circle" size={20} color="#10b981" />}
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('Profile')}>
        <Ionicons name="person-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Profile</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('Security')}>
        <Ionicons name="shield-checkmark-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Security</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('About')}>
        <Ionicons name="information-circle-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>About & Credits</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#ef4444" />
        <Text style={[styles.itemText, { color: '#ef4444' }]}>Logout</Text>
      </TouchableOpacity>
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
    padding: 16,
    gap: 8,
  },
  adminBadgeText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  userCard: {
    backgroundColor: '#fff',
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  userIconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#eff6ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 12,
  },
  subscriptionBadge: {
    backgroundColor: '#eff6ff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  adminSubscriptionBadge: {
    backgroundColor: '#d1fae5',
  },
  subscriptionText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#667eea',
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f9fafb',
  },
  adminToolButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 1,
    gap: 12,
  },
  adminToolText: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
    fontWeight: '500',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 1,
    gap: 12,
  },
  itemText: { flex: 1, fontSize: 16, color: '#111827' },
  itemBadge: {
    fontSize: 12,
    fontWeight: '600',
    color: '#667eea',
    backgroundColor: '#eff6ff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
});
