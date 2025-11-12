import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'https://trading-bot-api-7xps.onrender.com/api';

export default function SecurityScreen({ navigation }: any) {
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      Alert.alert('Error', 'Please fill all password fields');
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert('Error', 'New passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    try {
      const token = await SecureStore.getItemAsync('authToken');
      await axios.put(`${API_BASE_URL}/users/me/password`, {
        old_password: currentPassword,
        new_password: newPassword,
      }, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 30000,
      });
      Alert.alert('Success', 'Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to change password');
    }
  };

  const toggleTwoFactor = async (value: boolean) => {
    if (value) {
      Alert.alert('Coming Soon', '2FA will be available in the next update');
    } else {
      setTwoFactorEnabled(value);
    }
  };

  const toggleBiometric = async (value: boolean) => {
    setBiometricEnabled(value);
    Alert.alert('Success', value ? 'Biometric login enabled' : 'Biometric login disabled');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Security Settings</Text>
        <View style={{ width: 24 }} />
      </View>

      {/* Authentication */}
      <Text style={styles.section}>AUTHENTICATION</Text>
      <View style={styles.card}>
        <View style={styles.item}>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemTitle}>Two-Factor Authentication</Text>
            <Text style={styles.itemSubtitle}>Add extra security to your account</Text>
          </View>
          <Switch
            value={twoFactorEnabled}
            onValueChange={toggleTwoFactor}
            trackColor={{ false: '#d1d5db', true: '#10b981' }}
          />
        </View>

        <View style={styles.item}>
          <View style={{ flex: 1 }}>
            <Text style={styles.itemTitle}>Biometric Login</Text>
            <Text style={styles.itemSubtitle}>Use fingerprint or Face ID</Text>
          </View>
          <Switch
            value={biometricEnabled}
            onValueChange={toggleBiometric}
            trackColor={{ false: '#d1d5db', true: '#10b981' }}
          />
        </View>
      </View>

      {/* Change Password */}
      <Text style={styles.section}>CHANGE PASSWORD</Text>
      <View style={styles.card}>
        <TextInput
          style={styles.input}
          placeholder="Current Password"
          secureTextEntry
          value={currentPassword}
          onChangeText={setCurrentPassword}
        />
        <TextInput
          style={styles.input}
          placeholder="New Password"
          secureTextEntry
          value={newPassword}
          onChangeText={setNewPassword}
        />
        <TextInput
          style={styles.input}
          placeholder="Confirm New Password"
          secureTextEntry
          value={confirmPassword}
          onChangeText={setConfirmPassword}
        />
        <TouchableOpacity style={styles.button} onPress={handleChangePassword}>
          <Text style={styles.buttonText}>Change Password</Text>
        </TouchableOpacity>
      </View>

      {/* Session Management */}
      <Text style={styles.section}>SESSION MANAGEMENT</Text>
      <View style={styles.card}>
        <TouchableOpacity style={styles.item} onPress={() => Alert.alert('Coming Soon', 'Active sessions management')}>
          <Ionicons name="phone-portrait" size={24} color="#667eea" />
          <Text style={styles.itemText}>Active Sessions</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item} onPress={() => Alert.alert('Coming Soon', 'Login history')}>
          <Ionicons name="time" size={24} color="#667eea" />
          <Text style={styles.itemText}>Login History</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
      </View>

      {/* Danger Zone */}
      <Text style={styles.section}>DANGER ZONE</Text>
      <View style={styles.card}>
        <TouchableOpacity
          style={styles.item}
          onPress={() =>
            Alert.alert(
              'Delete Account',
              'Are you sure? This action cannot be undone.',
              [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Delete', style: 'destructive', onPress: () => Alert.alert('Coming Soon') },
              ]
            )
          }
        >
          <Ionicons name="trash" size={24} color="#ef4444" />
          <Text style={[styles.itemText, { color: '#ef4444' }]}>Delete Account</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  section: { fontSize: 12, fontWeight: '600', color: '#6b7280', paddingHorizontal: 16, paddingVertical: 12 },
  card: { backgroundColor: '#fff', marginHorizontal: 16, marginBottom: 16, padding: 16, borderRadius: 12 },
  item: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, gap: 12 },
  itemTitle: { fontSize: 16, fontWeight: '600', color: '#111827' },
  itemSubtitle: { fontSize: 14, color: '#6b7280', marginTop: 2 },
  itemText: { flex: 1, fontSize: 16, color: '#111827' },
  input: { backgroundColor: '#f9fafb', padding: 12, borderRadius: 8, marginBottom: 12, fontSize: 16 },
  button: { backgroundColor: '#667eea', padding: 16, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
