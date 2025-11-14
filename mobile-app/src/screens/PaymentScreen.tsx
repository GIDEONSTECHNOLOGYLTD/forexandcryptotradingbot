import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, Linking, Modal, Clipboard, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import QRCode from 'react-native-qrcode-svg';
import * as InAppPurchases from 'expo-in-app-purchases';
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
  const [cryptoNetwork, setCryptoNetwork] = useState('TRC20');
  const [availableNetworks, setAvailableNetworks] = useState<string[]>([]);
  const [showCryptoModal, setShowCryptoModal] = useState(false);
  const [showNetworkSelector, setShowNetworkSelector] = useState(false);
  const [cryptoAmount, setCryptoAmount] = useState(0);
  const [isLoadingNetworks, setIsLoadingNetworks] = useState(false);
  const [isInitializingIAP, setIsInitializingIAP] = useState(false);

  useEffect(() => {
    if (selectedPaymentMethod === 'crypto' && !isLoadingNetworks) {
      loadCryptoNetworks();
    } else if (selectedPaymentMethod === 'iap' && !isInitializingIAP) {
      initializeIAP();
    }
  }, [selectedPaymentMethod]);

  const initializeIAP = async () => {
    if (isInitializingIAP) return; // Prevent double initialization
    
    try {
      setIsInitializingIAP(true);
      await InAppPurchases.connectAsync();
      const { responseCode, results } = await InAppPurchases.getProductsAsync([
        PRODUCT_IDS.pro,
        PRODUCT_IDS.enterprise
      ]);
      if (responseCode === InAppPurchases.IAPResponseCode.OK) {
        console.log('IAP products loaded:', results);
      }
    } catch (error) {
      console.error('IAP initialization error:', error);
    } finally {
      setIsInitializingIAP(false);
    }
  };

  const loadCryptoNetworks = async () => {
    if (isLoadingNetworks) return; // Prevent double loading
    
    try {
      setIsLoadingNetworks(true);
      const response = await api.getCryptoNetworks();
      
      // Handle both string arrays and object arrays
      let networks = response.networks || ['TRC20', 'ERC20', 'BEP20', 'Polygon', 'Arbitrum', 'Optimism'];
      
      // If networks is array of objects, extract network names
      if (Array.isArray(networks) && networks.length > 0 && typeof networks[0] === 'object') {
        networks = networks.map((n: any) => n.network || n.name || String(n));
      }
      
      setAvailableNetworks(networks);
    } catch (error) {
      console.error('Failed to load networks:', error);
      setAvailableNetworks(['TRC20', 'ERC20', 'BEP20']);
    } finally {
      setIsLoadingNetworks(false);
    }
  };

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
              // Grant subscription after payment
              try {
                await api.verifySubscriptionPayment({
                  plan,
                  payment_method: 'card'
                });
              } catch (error) {
                console.error('Subscription grant error:', error);
              }
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
      
      console.log('🔐 Initializing REAL crypto payment...');
      console.log('Network:', cryptoNetwork);
      console.log('Currency:', cryptoCurrency);
      console.log('Plan:', plan);
      
      const response = await api.initializeCryptoPayment({
        plan: plan,
        crypto_currency: cryptoCurrency,
        network: cryptoNetwork,
        amount: plan === 'pro' ? 29 : 99
      });
      
      console.log('✅ Real OKX address received:', response);
      
      const address = response.deposit_address || response.address;
      const amount = response.crypto_amount || response.amount || (plan === 'pro' ? 29 : 99);
      
      setCryptoAddress(address);
      setCryptoAmount(amount);
      setShowCryptoModal(true);
      
      Alert.alert(
        'Payment Address Generated',
        `Send exactly ${amount} ${cryptoCurrency} to the address shown. Payment will be confirmed automatically.`,
        [{ text: 'OK' }]
      );
    } catch (error: any) {
      console.error('❌ Crypto payment error:', error);
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to generate payment address. Please try again or contact support.',
        [{ text: 'OK' }]
      );
    } finally {
      setPurchasing(false);
    }
  };

  const copyToClipboard = () => {
    Clipboard.setString(cryptoAddress);
    Alert.alert('Copied!', 'Address copied to clipboard');
  };

  const handleInAppPurchase = async (plan: string) => {
    if (Platform.OS !== 'ios' && Platform.OS !== 'android') {
      Alert.alert('Mobile Only', 'In-app purchases are only available on iOS and Android. Please use Card or Crypto payment.');
      return;
    }
    
    // Show coming soon alert for now
    Alert.alert(
      'Coming Soon',
      'In-app purchases are being configured. Please use Card or Crypto payment.',
      [
        { text: 'Use Card', onPress: () => setSelectedPaymentMethod('card') },
        { text: 'Use Crypto', onPress: () => setSelectedPaymentMethod('crypto') },
        { text: 'OK', style: 'cancel' }
      ]
    );
    return;

    try {
      setPurchasing(true);
      const productId = plan === 'pro' ? PRODUCT_IDS.pro : PRODUCT_IDS.enterprise;
      
      // Query products (already connected from initializeIAP)
      const { responseCode, results } = await InAppPurchases.getProductsAsync([productId]);
      
      if (responseCode !== InAppPurchases.IAPResponseCode.OK || !results || results.length === 0) {
        Alert.alert(
          'In-App Purchase Unavailable', 
          'iOS subscriptions are currently being set up. Please use Card or Crypto payment instead.',
          [
            { text: 'Use Card Payment', onPress: () => setSelectedPaymentMethod('card') },
            { text: 'Use Crypto Payment', onPress: () => setSelectedPaymentMethod('crypto') },
            { text: 'Cancel', style: 'cancel' }
          ]
        );
        setPurchasing(false);
        return;
      }
      
      await InAppPurchases.purchaseItemAsync(productId);
      
      // Listen for purchase updates
      InAppPurchases.setPurchaseListener(({ responseCode, results, errorCode }) => {
        if (responseCode === InAppPurchases.IAPResponseCode.OK) {
          results?.forEach(async (purchase) => {
            if (!purchase.acknowledged) {
              // Verify with backend and grant subscription
              try {
                await api.verifyInAppPurchase({
                  plan,
                  receipt_data: purchase.transactionReceipt || '',
                  platform: 'ios'
                });
                
                // Grant subscription
                await api.verifySubscriptionPayment({
                  plan,
                  payment_method: 'in_app_purchase'
                });
                
                // Finish transaction
                await InAppPurchases.finishTransactionAsync(purchase, true);
                
                Alert.alert('Success', 'Subscription activated!');
                await refreshUser();
                navigation.goBack();
              } catch (error) {
                Alert.alert('Error', 'Failed to verify purchase');
              }
            }
          });
        } else if (responseCode === InAppPurchases.IAPResponseCode.USER_CANCELED) {
          Alert.alert('Cancelled', 'Purchase was cancelled');
        } else {
          Alert.alert('Error', 'Purchase failed');
        }
        setPurchasing(false);
      });
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Purchase failed');
      setPurchasing(false);
    }
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
      default:
        Alert.alert('Error', 'Please select a payment method');
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
        
        {/* Crypto Network Selector */}
        {selectedPaymentMethod === 'crypto' && availableNetworks.length > 0 && (
          <View style={styles.networkSelector}>
            <Text style={styles.networkLabel}>Select Network:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.networkScroll}>
              {availableNetworks.map((network) => {
                // Ensure network is a string
                const networkStr = typeof network === 'string' ? network : String(network);
                return (
                  <TouchableOpacity
                    key={networkStr}
                    style={[
                      styles.networkChip,
                      cryptoNetwork === networkStr && styles.networkChipSelected
                    ]}
                    onPress={() => setCryptoNetwork(networkStr)}
                  >
                    <Text style={[
                      styles.networkChipText,
                      cryptoNetwork === networkStr && styles.networkChipTextSelected
                    ]}>{networkStr}</Text>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </View>
        )}
        
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
  networkSelector: {
    marginBottom: 16,
  },
  networkLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  networkScroll: {
    flexDirection: 'row',
  },
  networkChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    marginRight: 8,
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  networkChipSelected: {
    backgroundColor: '#eff6ff',
    borderColor: '#667eea',
  },
  networkChipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  networkChipTextSelected: {
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
