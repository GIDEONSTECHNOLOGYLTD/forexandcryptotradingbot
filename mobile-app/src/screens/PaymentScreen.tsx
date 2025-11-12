import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

export default function PaymentScreen({ navigation }: any) {
  const [selectedPlan, setSelectedPlan] = useState('pro');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<'card' | 'crypto' | 'iap'>('card');
  const [purchasing, setPurchasing] = useState(false);

  const handleSubscribe = async (plan: string) => {
    if (plan === 'free') {
      Alert.alert('Free Plan', 'You are already on the free plan!');
      return;
    }

    // Show payment method specific instructions
    const paymentInstructions = {
      card: 'Card payment integration coming soon! For now, contact support to upgrade.',
      crypto: 'Crypto payment integration coming soon! For now, contact support to upgrade.',
      iap: 'In-app purchases only work in production builds from App Store.'
    };

    Alert.alert(
      'Payment Required',
      paymentInstructions[selectedPaymentMethod],
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Contact Support',
          onPress: () => {
            Alert.alert(
              'Contact Support',
              'Email: support@gideonstechnology.com\nOr use the chat in the app.'
            );
          }
        }
      ]
    );

    // TODO: Implement actual payment processing
    // For now, don't activate subscription without payment
  };

  const plans = [
    { name: 'Free', price: '$0', features: ['Paper trading', '1 bot', 'Basic strategies'] },
    { name: 'Pro', price: '$29', features: ['Real trading', '3 bots', 'All strategies', 'Priority support'] },
    { name: 'Enterprise', price: '$99', features: ['Unlimited bots', 'API access', 'Custom strategies', '24/7 support'] },
  ];

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Choose Your Plan</Text>
      
      {/* Payment Method Selection */}
      <View style={styles.paymentMethodSection}>
        <Text style={styles.sectionTitle}>Payment Method</Text>
        <View style={styles.paymentMethods}>
          <TouchableOpacity
            style={[
              styles.paymentMethod,
              selectedPaymentMethod === 'card' && styles.paymentMethodSelected
            ]}
            onPress={() => setSelectedPaymentMethod('card')}
          >
            <Ionicons name="card" size={24} color={selectedPaymentMethod === 'card' ? '#667eea' : '#9ca3af'} />
            <Text style={[
              styles.paymentMethodText,
              selectedPaymentMethod === 'card' && styles.paymentMethodTextSelected
            ]}>Card</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.paymentMethod,
              selectedPaymentMethod === 'crypto' && styles.paymentMethodSelected
            ]}
            onPress={() => setSelectedPaymentMethod('crypto')}
          >
            <Ionicons name="logo-bitcoin" size={24} color={selectedPaymentMethod === 'crypto' ? '#667eea' : '#9ca3af'} />
            <Text style={[
              styles.paymentMethodText,
              selectedPaymentMethod === 'crypto' && styles.paymentMethodTextSelected
            ]}>Crypto</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.paymentMethod,
              selectedPaymentMethod === 'iap' && styles.paymentMethodSelected
            ]}
            onPress={() => setSelectedPaymentMethod('iap')}
          >
            <Ionicons name="phone-portrait" size={24} color={selectedPaymentMethod === 'iap' ? '#667eea' : '#9ca3af'} />
            <Text style={[
              styles.paymentMethodText,
              selectedPaymentMethod === 'iap' && styles.paymentMethodTextSelected
            ]}>App Store</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Plans */}
      {plans.map((plan, index) => (
        <View key={index} style={styles.planCard}>
          <Text style={styles.planName}>{plan.name}</Text>
          <Text style={styles.planPrice}>{plan.price}/month</Text>
          {plan.features.map((feature, i) => (
            <View key={i} style={styles.feature}>
              <Ionicons name="checkmark-circle" size={20} color="#10b981" />
              <Text style={styles.featureText}>{feature}</Text>
            </View>
          ))}
          <TouchableOpacity 
            style={[styles.button, purchasing && styles.buttonDisabled]}
            onPress={() => handleSubscribe(plan.name.toLowerCase())}
            disabled={purchasing}
          >
            <Text style={styles.buttonText}>
              {purchasing ? 'Processing...' : plan.name === 'Free' ? 'Current Plan' : 'Select Plan'}
            </Text>
          </TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#f9fafb' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  paymentMethodSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
    color: '#111827',
  },
  paymentMethods: {
    flexDirection: 'row',
    gap: 12,
  },
  paymentMethod: {
    flex: 1,
    padding: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    alignItems: 'center',
    gap: 8,
  },
  paymentMethodSelected: {
    borderColor: '#667eea',
    backgroundColor: '#eff6ff',
  },
  paymentMethodText: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '600',
  },
  paymentMethodTextSelected: {
    color: '#667eea',
  },
  planCard: { backgroundColor: '#fff', padding: 20, borderRadius: 12, marginBottom: 16 },
  planName: { fontSize: 20, fontWeight: 'bold' },
  planPrice: { fontSize: 32, fontWeight: 'bold', color: '#667eea', marginVertical: 8 },
  feature: { flexDirection: 'row', alignItems: 'center', marginVertical: 4, gap: 8 },
  featureText: { fontSize: 14, color: '#6b7280' },
  button: {
    backgroundColor: '#667eea',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  buttonDisabled: { opacity: 0.5 },
});
