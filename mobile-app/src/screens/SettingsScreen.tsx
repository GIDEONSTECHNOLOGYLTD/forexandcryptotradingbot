import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function SettingsScreen({ navigation }: any) {
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
    <View style={styles.container}>
      <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('Payment')}>
        <Ionicons name="card-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Subscription</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item}>
        <Ionicons name="key-outline" size={24} color="#667eea" />
        <Text style={styles.itemText}>Exchange Connection</Text>
        <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
      </TouchableOpacity>

      <TouchableOpacity style={styles.item} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#ef4444" />
        <Text style={[styles.itemText, { color: '#ef4444' }]}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 1,
    gap: 12,
  },
  itemText: { flex: 1, fontSize: 16, color: '#111827' },
});
