import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';

export default function SplashScreen({ navigation }: any) {
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if onboarding is complete
      const onboardingComplete = await SecureStore.getItemAsync('onboardingComplete');
      
      // Check if user is logged in (match the key used in LoginScreen)
      const token = await SecureStore.getItemAsync('token');

      // Wait minimum 2 seconds for splash screen
      await new Promise(resolve => setTimeout(resolve, 2000));

      if (!onboardingComplete) {
        navigation.replace('Onboarding');
      } else if (token) {
        // Check if biometric is enabled (must match BiometricService key!)
        const biometricEnabled = await SecureStore.getItemAsync('biometric_enabled');
        
        if (biometricEnabled === 'true') {
          // Trigger biometric authentication
          const hasHardware = await LocalAuthentication.hasHardwareAsync();
          const isEnrolled = await LocalAuthentication.isEnrolledAsync();
          
          if (hasHardware && isEnrolled) {
            const result = await LocalAuthentication.authenticateAsync({
              promptMessage: 'Authenticate to access Trading Bot',
              fallbackLabel: 'Use Passcode',
              cancelLabel: 'Cancel',
            });
            
            if (result.success) {
              navigation.replace('MainTabs');
            } else {
              Alert.alert('Authentication Failed', 'Please try again or use your password.');
              navigation.replace('Login');
            }
          } else {
            // Biometric not available, proceed without it
            navigation.replace('MainTabs');
          }
        } else {
          // Biometric not enabled, proceed normally
          navigation.replace('MainTabs');
        }
      } else {
        navigation.replace('Login');
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      navigation.replace('Login');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <Ionicons name="trending-up" size={80} color="#667eea" />
        <Text style={styles.title}>Trading Bot Pro</Text>
        <Text style={styles.subtitle}>AI-Powered Trading</Text>
      </View>
      
      <View style={styles.footer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 80,
  },
  logoContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 8,
  },
  footer: {
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#6b7280',
  },
});
