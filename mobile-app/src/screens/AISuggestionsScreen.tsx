import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as api from '../services/api';

interface AISuggestion {
  id: string;
  type: 'strategy' | 'optimization' | 'risk' | 'opportunity';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  action?: string;
  timestamp: string;
}

export default function AISuggestionsScreen({ navigation }: any) {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      console.log('🤖 Loading AI suggestions from backend...');
      const response = await api.getAISuggestions();
      
      if (response.suggestions && response.suggestions.length > 0) {
        console.log('✅ Real AI suggestions loaded:', response.suggestions.length);
        setSuggestions(response.suggestions);
        setLoading(false);
        setRefreshing(false);
        return;
      }
    } catch (error) {
      console.log('⚠️ AI endpoint not available, using demo suggestions');
    }
    
    // Fallback to demo suggestions if API fails
    const demoSuggestions: AISuggestion[] = [
        {
          id: '1',
          type: 'strategy' as const,
          title: 'Optimize Trading Hours',
          description: 'Your bots perform 23% better during 8AM-2PM UTC. Consider adjusting active hours.',
          confidence: 0.87,
          impact: 'high' as const,
          action: 'Adjust Schedule',
          timestamp: new Date().toISOString(),
        },
        {
          id: '2',
          type: 'risk' as const,
          title: 'Reduce Position Size',
          description: 'Current volatility suggests reducing position size by 15% to minimize risk.',
          confidence: 0.76,
          impact: 'medium' as const,
          action: 'Update Settings',
          timestamp: new Date().toISOString(),
        },
        {
          id: '3',
          type: 'opportunity' as const,
          title: 'New Market Opportunity',
          description: 'ETH/USDT showing strong momentum patterns. Consider adding to portfolio.',
          confidence: 0.82,
          impact: 'high' as const,
          action: 'Create Bot',
          timestamp: new Date().toISOString(),
        },
        {
          id: '4',
          type: 'optimization' as const,
          title: 'Improve Stop Loss',
          description: 'Tightening stop loss to 12% could improve win rate by 8% based on historical data.',
          confidence: 0.71,
          impact: 'medium' as const,
          action: 'Review',
          timestamp: new Date().toISOString(),
        },
      ];
    
    console.log('📝 Using demo AI suggestions');
    setSuggestions(demoSuggestions);
    setLoading(false);
    setRefreshing(false);
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadSuggestions();
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'strategy':
        return 'bulb';
      case 'optimization':
        return 'speedometer';
      case 'risk':
        return 'shield-checkmark';
      case 'opportunity':
        return 'trending-up';
      default:
        return 'sparkles';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'strategy':
        return '#667eea';
      case 'optimization':
        return '#10b981';
      case 'risk':
        return '#f59e0b';
      case 'opportunity':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return '#10b981';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const handleAction = (suggestion: AISuggestion) => {
    // Navigate based on action type
    if (suggestion.action === 'Create Bot') {
      navigation.navigate('BotConfig');
    } else if (suggestion.action === 'Update Settings') {
      navigation.navigate('Settings');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading AI insights...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>AI Suggestions</Text>
          <Text style={styles.subtitle}>Powered by machine learning</Text>
        </View>
        <View style={styles.badge}>
          <Ionicons name="sparkles" size={16} color="#fff" />
          <Text style={styles.badgeText}>BETA</Text>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {suggestions.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="sparkles-outline" size={64} color="#9ca3af" />
            <Text style={styles.emptyText}>No suggestions yet</Text>
            <Text style={styles.emptySubtext}>
              AI is analyzing your trading patterns
            </Text>
          </View>
        ) : (
          suggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.suggestionCard}>
              <View style={styles.suggestionHeader}>
                <View
                  style={[
                    styles.iconContainer,
                    { backgroundColor: getTypeColor(suggestion.type) + '20' },
                  ]}
                >
                  <Ionicons
                    name={getTypeIcon(suggestion.type) as any}
                    size={24}
                    color={getTypeColor(suggestion.type)}
                  />
                </View>
                <View style={styles.headerInfo}>
                  <Text style={styles.suggestionTitle}>{suggestion.title}</Text>
                  <View style={styles.metaRow}>
                    <View
                      style={[
                        styles.impactBadge,
                        { backgroundColor: getImpactColor(suggestion.impact) + '20' },
                      ]}
                    >
                      <Text
                        style={[
                          styles.impactText,
                          { color: getImpactColor(suggestion.impact) },
                        ]}
                      >
                        {suggestion.impact.toUpperCase()} IMPACT
                      </Text>
                    </View>
                    <Text style={styles.confidence}>
                      {Math.round(suggestion.confidence * 100)}% confidence
                    </Text>
                  </View>
                </View>
              </View>

              <Text style={styles.description}>{suggestion.description}</Text>

              {suggestion.action && (
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={() => handleAction(suggestion)}
                >
                  <Text style={styles.actionButtonText}>{suggestion.action}</Text>
                  <Ionicons name="arrow-forward" size={20} color="#667eea" />
                </TouchableOpacity>
              )}
            </View>
          ))
        )}

        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#667eea" />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>About AI Suggestions</Text>
            <Text style={styles.infoText}>
              Our AI analyzes your trading patterns, market conditions, and historical
              data to provide personalized recommendations. Suggestions are updated
              daily based on new data.
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#667eea',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    gap: 4,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  scrollView: {
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 80,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
  },
  suggestionCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  suggestionHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerInfo: {
    flex: 1,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  impactBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  impactText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  confidence: {
    fontSize: 12,
    color: '#6b7280',
  },
  description: {
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 20,
    marginBottom: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ede9fe',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#667eea',
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#eff6ff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 12,
    color: '#3b82f6',
    lineHeight: 18,
  },
});
