import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as InAppPurchases from 'expo-in-app-purchases';

// Product IDs - These need to be created in App Store Connect
const PRODUCT_IDS = {
  pro: 'com.gtechldt.tradingbot.pro.monthly',
  enterprise: 'com.gtechldt.tradingbot.enterprise.monthly'
};

export default function PaymentScreen({ navigation }: any) {
  const [selectedPlan, setSelectedPlan] = useState('pro');
  const [products, setProducts] = useState<any[]>([]);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    initializeIAP();
    return () => {
      InAppPurchases.disconnectAsync();
    };
  }, []);

  const initializeIAP = async () => {
    try {
      await InAppPurchases.connectAsync();
      const { results } = await InAppPurchases.getProductsAsync([
        PRODUCT_IDS.pro,
        PRODUCT_IDS.enterprise
      ]);
      setProducts(results);
    } catch (error) {
      console.error('IAP initialization error:', error);
    }
  };

  const handlePurchase = async (productId: string) => {
    try {
      setPurchasing(true);
      await InAppPurchases.purchaseItemAsync(productId);
      Alert.alert('Success', 'Subscription activated!', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error: any) {
      if (error.code !== 'E_USER_CANCELLED') {
        Alert.alert('Error', 'Purchase failed. Please try again.');
      }
    } finally {
      setPurchasing(false);
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
            onPress={() => {
              if (plan.name === 'Free') {
                Alert.alert('Free Plan', 'You are already on the free plan!');
              } else if (plan.name === 'Pro') {
                handlePurchase(PRODUCT_IDS.pro);
              } else if (plan.name === 'Enterprise') {
                handlePurchase(PRODUCT_IDS.enterprise);
              }
            }}
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
