import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function AboutScreen({ navigation }: any) {
  const openWebsite = () => {
    Linking.openURL('https://gideonstechnology.com');
  };

  const openEmail = () => {
    Linking.openURL('mailto:ceo@gideonstechnology.com');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="rocket" size={80} color="#667eea" />
        <Text style={styles.title}>Trading Bot Pro</Text>
        <Text style={styles.version}>Version 1.0.0</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Built By</Text>
        <View style={styles.card}>
          <Text style={styles.companyName}>Gideon's Technology Ltd</Text>
          <Text style={styles.tagline}>Innovative AI & Trading Solutions</Text>
          
          <TouchableOpacity style={styles.linkButton} onPress={openWebsite}>
            <Ionicons name="globe-outline" size={20} color="#667eea" />
            <Text style={styles.linkText}>gideonstechnology.com</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.linkButton} onPress={openEmail}>
            <Ionicons name="mail-outline" size={20} color="#667eea" />
            <Text style={styles.linkText}>ceo@gideonstechnology.com</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About This App</Text>
        <View style={styles.card}>
          <Text style={styles.description}>
            Trading Bot Pro is an AI-powered automated trading platform that helps you trade 
            cryptocurrencies and forex markets 24/7. Built with cutting-edge technology and 
            advanced algorithms.
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Features</Text>
        <View style={styles.card}>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>8 AI Trading Strategies</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>Forex + Crypto Support</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>Real-time Trading</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>Advanced Analytics</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>P2P Copy Trading</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <Text style={styles.featureText}>Secure & Encrypted</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Technology Stack</Text>
        <View style={styles.card}>
          <Text style={styles.tech}>• React Native + Expo</Text>
          <Text style={styles.tech}>• FastAPI Backend</Text>
          <Text style={styles.tech}>• MongoDB Database</Text>
          <Text style={styles.tech}>• OKX Exchange Integration</Text>
          <Text style={styles.tech}>• AI/ML Algorithms</Text>
          <Text style={styles.tech}>• Real-time WebSockets</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.copyright}>© 2025 Gideon's Technology Ltd</Text>
        <Text style={styles.rights}>All Rights Reserved</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    alignItems: 'center',
    paddingVertical: 40,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
  },
  version: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  companyName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 20,
  },
  linkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 12,
  },
  linkText: {
    fontSize: 16,
    color: '#667eea',
  },
  description: {
    fontSize: 15,
    color: '#4b5563',
    lineHeight: 24,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 8,
    gap: 12,
  },
  featureText: {
    fontSize: 15,
    color: '#4b5563',
  },
  tech: {
    fontSize: 15,
    color: '#4b5563',
    marginVertical: 4,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingBottom: 60,
  },
  copyright: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '600',
  },
  rights: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 4,
  },
});
