import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, Linking, Modal, Clipboard } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import QRCode from 'react-native-qrcode-svg';
import * as api from '../services/api';
import { useUser } from '../context/UserContext';

const PRODUCT_IDS = {
  pro: 'com.gtechldt.tradingbot.pro.monthly',
  enterprise: 'com.gtechldt.tradingbot.enterprise.monthly'
};

export default function PaymentScreen({ navigation }: any) {
  const { user, refreshUser } = useUser();
  const [selectedPlan, setSelectedPlan] = useState('pro');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<'card' | 'crypto' | 'iap'>('card');
  const [purchasing, setPurchasing] = useState(false);
  const [cryptoAddress, setCryptoAddress] = useState('');
  const [cryptoCurrency, setCryptoCurrency] = useState('USDT');
  const [showCryptoModal, setShowCryptoModal] = useState(false);
  const [cryptoAmount, setCryptoAmount] = useState(0);

  useEffect(() => {
    // No initialization needed - IAP will be loaded on demand
  }, [selectedPaymentMethod]);

  const handlePaystackPayment = async (plan: string) => {
    try {
      setPurchasing(true);
      const response = await api.initializePaystackPayment({
        email: user?.email || '',
        amount: plan === 'pro' ? 29 : 99,
        plan: plan
      });
      
      // Open Paystack payment page
      await Linking.openURL(response.authorization_url);
      
      Alert.alert(
        'Payment Initiated',
        'Complete payment in browser. Return here after payment.',
        [
          {
            text: 'I\'ve Paid',
            onPress: async () => {
              await refreshUser();
              navigation.goBack();
            }
          }
        ]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Payment failed');
    } finally {
      setPurchasing(false);
    }
  };

  const handleCryptoPayment = async (plan: string) => {
    try {
      setPurchasing(true);
      const response = await api.initializeCryptoPayment({
        plan: plan,
        crypto_currency: cryptoCurrency,
        amount: plan === 'pro' ? 29 : 99
      });
      
      const address = response.deposit_address || response.address || 'Address generation failed';
      const amount = response.crypto_amount || response.amount || (plan === 'pro' ? 29 : 99);
      
      setCryptoAddress(address);
      setCryptoAmount(amount);
      setShowCryptoModal(true);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Crypto payment not configured yet. Please use Card payment.');
    } finally {
      setPurchasing(false);
    }
  };

  const copyToClipboard = () => {
    Clipboard.setString(cryptoAddress);
    Alert.alert('Copied!', 'Address copied to clipboard');
  };

  const handleInAppPurchase = async (plan: string) => {
    // IAP not available - show message
    Alert.alert(
      'Coming Soon',
      'In-app purchases are being configured.\n\nPlease use Card (Paystack) or Crypto payment for now.',
      [{ text: 'OK', onPress: () => setSelectedPaymentMethod('card') }]
    );
  };

  const handleSubscribe = async (plan: string) => {
    if (plan === 'free') {
      Alert.alert('Free Plan', 'You are already on the free plan!');
      return;
    }

    switch (selectedPaymentMethod) {
      case 'card':
        await handlePaystackPayment(plan);
        break;
      case 'crypto':
        await handleCryptoPayment(plan);
        break;
      case 'iap':
        await handleInAppPurchase(plan);
        break;
    }
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

      {/* Crypto Payment Modal */}
      <Modal
        visible={showCryptoModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowCryptoModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Crypto Payment</Text>
              <TouchableOpacity onPress={() => setShowCryptoModal(false)}>
                <Ionicons name="close" size={24} color="#111827" />
              </TouchableOpacity>
            </View>

            <View style={styles.qrCodeContainer}>
              {cryptoAddress && cryptoAddress !== 'Address generation failed' ? (
                <QRCode
                  value={cryptoAddress}
                  size={200}
                  backgroundColor="white"
                />
              ) : (
                <View style={styles.qrPlaceholder}>
                  <Ionicons name="alert-circle" size={64} color="#ef4444" />
                  <Text style={styles.qrErrorText}>Failed to generate address</Text>
                </View>
              )}
            </View>

            <View style={styles.paymentInfo}>
              <Text style={styles.paymentLabel}>Amount</Text>
              <Text style={styles.paymentValue}>{cryptoAmount} {cryptoCurrency}</Text>
            </View>

            <View style={styles.paymentInfo}>
              <Text style={styles.paymentLabel}>Address</Text>
              <Text style={styles.paymentAddress} numberOfLines={2}>{cryptoAddress}</Text>
            </View>

            <TouchableOpacity style={styles.copyButton} onPress={copyToClipboard}>
              <Ionicons name="copy" size={20} color="#fff" />
              <Text style={styles.copyButtonText}>Copy Address</Text>
            </TouchableOpacity>

            <Text style={styles.paymentInstructions}>
              Send exactly {cryptoAmount} {cryptoCurrency} to the address above.{'\n\n'}
              Payment will be confirmed automatically within 10-30 minutes.
            </Text>
          </View>
        </View>
      </Modal>
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  qrCodeContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    marginBottom: 20,
  },
  qrPlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  qrErrorText: {
    marginTop: 12,
    fontSize: 14,
    color: '#ef4444',
    textAlign: 'center',
  },
  paymentInfo: {
    marginBottom: 16,
  },
  paymentLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
    fontWeight: '600',
  },
  paymentValue: {
    fontSize: 18,
    color: '#111827',
    fontWeight: 'bold',
  },
  paymentAddress: {
    fontSize: 12,
    color: '#111827',
    fontFamily: 'monospace',
  },
  copyButton: {
    backgroundColor: '#667eea',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    gap: 8,
  },
  copyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  paymentInstructions: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
});
