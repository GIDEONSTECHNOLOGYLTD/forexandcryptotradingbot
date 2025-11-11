import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function PaymentScreen() {
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
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Select Plan</Text>
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
});
