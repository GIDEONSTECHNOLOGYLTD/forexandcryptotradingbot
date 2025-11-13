import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';
import { BiometricService } from '../services/biometrics';

export default function SecurityScreen({ navigation }: any) {
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkBiometricStatus();
  }, []);

  const checkBiometricStatus = async () => {
    const enabled = await BiometricService.isBiometricLoginEnabled();
    setBiometricEnabled(enabled);
  };

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
      setLoading(true);
      // Call API to change password
      await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      });
      Alert.alert('✅ Success', 'Password changed successfully! Please log in again with your new password.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to change password. Make sure current password is correct.');
    } finally {
      setLoading(false);
    }
  };

  const toggleTwoFactor = async (value: boolean) => {
    if (value) {
      // Enable 2FA
      Alert.alert(
        '🔐 Enable 2FA',
        'Two-factor authentication adds an extra layer of security.\n\nWe\'ll send a verification code to your email every time you log in.',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Enable', 
            onPress: async () => {
              try {
                setLoading(true);
                // Call API to enable 2FA
                await api.enableTwoFactor();
                setTwoFactorEnabled(true);
                Alert.alert('✅ Success', '2FA enabled! You\'ll receive a code on your next login.');
              } catch (error: any) {
                Alert.alert('Error', error.response?.data?.detail || 'Failed to enable 2FA');
              } finally {
                setLoading(false);
              }
            }
          },
        ]
      );
    } else {
      // Disable 2FA
      Alert.alert(
        '⚠️ Disable 2FA',
        'This will reduce your account security. Are you sure?',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Disable', 
            style: 'destructive',
            onPress: async () => {
              try {
                setLoading(true);
                await api.disableTwoFactor();
                setTwoFactorEnabled(false);
                Alert.alert('Success', '2FA disabled');
              } catch (error: any) {
                Alert.alert('Error', error.response?.data?.detail || 'Failed to disable 2FA');
              } finally {
                setLoading(false);
              }
            }
          },
        ]
      );
    }
  };

  const toggleBiometric = async (value: boolean) => {
    try {
      if (value) {
        const success = await BiometricService.enableBiometricLogin();
        if (success) {
          setBiometricEnabled(true);
          Alert.alert('Success', 'Biometric login enabled');
        }
      } else {
        await BiometricService.disableBiometricLogin();
        setBiometricEnabled(false);
        Alert.alert('Success', 'Biometric login disabled');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to toggle biometric login');
    }
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
          placeholderTextColor="#9ca3af"
          secureTextEntry
          value={currentPassword}
          onChangeText={setCurrentPassword}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TextInput
          style={styles.input}
          placeholder="New Password"
          placeholderTextColor="#9ca3af"
          secureTextEntry
          value={newPassword}
          onChangeText={setNewPassword}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TextInput
          style={styles.input}
          placeholder="Confirm New Password"
          placeholderTextColor="#9ca3af"
          secureTextEntry
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TouchableOpacity 
          style={[styles.button, loading && styles.buttonDisabled]} 
          onPress={handleChangePassword}
          disabled={loading}
        >
          <Text style={styles.buttonText}>{loading ? 'Changing...' : 'Change Password'}</Text>
        </TouchableOpacity>
      </View>

      {/* Session Management */}
      <Text style={styles.section}>SESSION MANAGEMENT</Text>
      <View style={styles.card}>
        <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('ActiveSessions')}>
          <Ionicons name="phone-portrait" size={24} color="#667eea" />
          <Text style={styles.itemText}>Active Sessions</Text>
          <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.item} onPress={() => navigation.navigate('LoginHistory')}>
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
                { 
                  text: 'Delete', 
                  style: 'destructive', 
                  onPress: async () => {
                    try {
                      setLoading(true);
                      await api.deleteAccount();
                      Alert.alert(
                        'Account Deleted',
                        'Your account has been permanently deleted. All your data has been removed.',
                        [{ text: 'OK', onPress: () => navigation.replace('Login') }]
                      );
                    } catch (error: any) {
                      Alert.alert('Error', error.response?.data?.detail || 'Failed to delete account');
                    } finally {
                      setLoading(false);
                    }
                  }
                },
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
  input: { 
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#d1d5db',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    fontSize: 16,
    color: '#111827',
  },
  button: { backgroundColor: '#667eea', padding: 16, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
