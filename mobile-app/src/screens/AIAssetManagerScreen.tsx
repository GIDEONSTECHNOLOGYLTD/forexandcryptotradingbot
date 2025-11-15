import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  ActivityIndicator,
  RefreshControl,
  Alert,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { 
  getAIAssetManagerStatus,
  getHoldingsAnalysis,
  updateAssetManagerConfig,
  getAssetManagerAnalytics,
  executeManualSell,
} from '../services/api';

export default function AIAssetManagerScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Status & Config
  const [status, setStatus] = useState<any | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [autoSell, setAutoSell] = useState(false);
  const [minProfit, setMinProfit] = useState('3');
  
  // Holdings & Analytics
  const [holdings, setHoldings] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [expandedHolding, setExpandedHolding] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const [statusData, holdingsData, analyticsData] = await Promise.all([
        getAIAssetManagerStatus(),
        getHoldingsAnalysis(),
        getAssetManagerAnalytics(),
      ]);
      
      setStatus(statusData);
      setEnabled(statusData.enabled);
      setAutoSell(statusData.auto_sell);
      setMinProfit(statusData.min_profit_percent.toString());
      
      setHoldings(holdingsData.holdings || []);
      setAnalytics(analyticsData);
      
    } catch (error: any) {
      console.error('Error loading AI Asset Manager data:', error);
      Alert.alert('Error', error.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      
      const minProfitNum = parseFloat(minProfit);
      if (isNaN(minProfitNum) || minProfitNum < 0.1 || minProfitNum > 100) {
        Alert.alert('Invalid Input', 'Min profit must be between 0.1% and 100%');
        return;
      }
      
      await updateAssetManagerConfig({
        enabled,
        auto_sell: autoSell,
        min_profit_percent: minProfitNum,
      });
      
      Alert.alert('Success', 'Configuration saved successfully!');
      await loadData();
      
    } catch (error: any) {
      console.error('Error saving config:', error);
      Alert.alert('Error', error.message || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleManualSell = async (symbol: string, amount: number, price: number) => {
    Alert.alert(
      'Confirm Sell',
      `Sell ${amount.toFixed(6)} ${symbol} at $${price.toFixed(2)}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sell',
          style: 'destructive',
          onPress: async () => {
            try {
              await executeManualSell(symbol);
              Alert.alert('Success', `Sell order placed for ${symbol}`);
              await loadData();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'Failed to execute sell');
            }
          },
        },
      ]
    );
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_SELL': return '#DC2626';
      case 'SELL': return '#EF4444';
      case 'HOLD': return '#F59E0B';
      case 'BUY': return '#10B981';
      case 'STRONG_BUY': return '#059669';
      default: return '#6B7280';
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading AI Asset Manager...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Status Card */}
      <View style={styles.statusCard}>
        <View style={styles.statusHeader}>
          <Ionicons name="analytics" size={28} color="#667eea" />
          <Text style={styles.statusTitle}>AI Asset Manager</Text>
        </View>
        
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Status:</Text>
          <View style={[styles.statusBadge, { backgroundColor: enabled ? '#10B981' : '#6B7280' }]}>
            <Text style={styles.statusBadgeText}>
              {enabled ? '● Active' : '○ Inactive'}
            </Text>
          </View>
        </View>
        
        {status && (
          <>
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Holdings Analyzed:</Text>
              <Text style={styles.statusValue}>{status.holdings_analyzed}</Text>
            </View>
            
            <View style={styles.recommendationRow}>
              <Text style={[styles.recommendationText, { color: '#DC2626' }]}>
                {status.recommendations_count?.sell || 0} SELL
              </Text>
              <Text style={[styles.recommendationText, { color: '#F59E0B' }]}>
                {status.recommendations_count?.hold || 0} HOLD
              </Text>
              <Text style={[styles.recommendationText, { color: '#10B981' }]}>
                {status.recommendations_count?.buy || 0} BUY
              </Text>
            </View>
          </>
        )}
      </View>

      {/* Configuration Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚙️ Configuration</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Enable AI Analysis</Text>
            <Text style={styles.settingDescription}>
              Analyze all holdings hourly with 6 technical indicators
            </Text>
          </View>
          <Switch
            value={enabled}
            onValueChange={setEnabled}
            trackColor={{ false: '#D1D5DB', true: '#667eea' }}
            thumbColor="#FFFFFF"
          />
        </View>

        {enabled && (
          <>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Auto-Sell Mode</Text>
                <Text style={styles.settingDescription}>
                  Automatically sell profitable positions
                </Text>
                <Text style={[styles.settingDescription, { color: '#DC2626' }]}>
                  ⚠️ Never auto-sells at a loss!
                </Text>
              </View>
              <Switch
                value={autoSell}
                onValueChange={setAutoSell}
                trackColor={{ false: '#D1D5DB', true: '#667eea' }}
                thumbColor="#FFFFFF"
              />
            </View>

            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Min Profit % for Auto-Sell</Text>
              </View>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  value={minProfit}
                  onChangeText={setMinProfit}
                  keyboardType="decimal-pad"
                  placeholder="3.0"
                />
                <Text style={styles.inputSuffix}>%</Text>
              </View>
            </View>

            <TouchableOpacity
              style={[styles.saveButton, saving && styles.saveButtonDisabled]}
              onPress={handleSaveConfig}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <>
                  <Ionicons name="save" size={20} color="#FFFFFF" />
                  <Text style={styles.saveButtonText}>Save Configuration</Text>
                </>
              )}
            </TouchableOpacity>
          </>
        )}
      </View>

      {/* Holdings Section */}
      {holdings.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Your Holdings ({holdings.length})</Text>
          
          {holdings.map((holding) => (
            <View key={holding.symbol} style={styles.holdingCard}>
              <TouchableOpacity
                style={styles.holdingHeader}
                onPress={() => setExpandedHolding(
                  expandedHolding === holding.symbol ? null : holding.symbol
                )}
              >
                <View style={styles.holdingLeft}>
                  <Text style={styles.holdingSymbol}>{holding.symbol}</Text>
                  <View
                    style={[
                      styles.recommendationChip,
                      { backgroundColor: getRecommendationColor(holding.ai_recommendation) },
                    ]}
                  >
                    <Text style={styles.recommendationChipText}>
                      {holding.ai_recommendation}
                    </Text>
                  </View>
                </View>

                <View style={styles.holdingRight}>
                  <Text style={styles.holdingValue}>
                    ${holding.value_usd?.toFixed(2) || '0.00'}
                  </Text>
                  <Text
                    style={[
                      styles.holdingProfit,
                      { color: holding.estimated_profit_pct >= 0 ? '#10B981' : '#DC2626' },
                    ]}
                  >
                    {holding.estimated_profit_pct >= 0 ? '+' : ''}
                    {holding.estimated_profit_pct?.toFixed(2) || '0.00'}%
                  </Text>
                </View>
              </TouchableOpacity>

              {/* Expanded Details */}
              {expandedHolding === holding.symbol && holding.indicators && (
                <View style={styles.holdingExpanded}>
                  <View style={styles.indicatorsSection}>
                    <Text style={styles.indicatorsTitle}>📈 Technical Indicators:</Text>
                    <Text style={styles.indicatorText}>RSI: {holding.indicators.rsi?.toFixed(1) || 'N/A'}</Text>
                    <Text style={styles.indicatorText}>MACD: {holding.indicators.macd_trend || 'N/A'}</Text>
                    <Text style={styles.indicatorText}>Bollinger: {holding.indicators.bollinger_position?.toFixed(1) || 'N/A'}%</Text>
                    <Text style={styles.indicatorText}>Order Book: {holding.indicators.order_book_pressure || 'N/A'}</Text>
                  </View>

                  {holding.reasoning && holding.reasoning.length > 0 && (
                    <View style={styles.reasoningSection}>
                      <Text style={styles.reasoningTitle}>🤖 AI Reasoning:</Text>
                      {holding.reasoning.slice(0, 3).map((reason: string, index: number) => (
                        <Text key={index} style={styles.reasoningText}>• {reason}</Text>
                      ))}
                    </View>
                  )}

                  {(holding.ai_recommendation === 'SELL' || holding.ai_recommendation === 'STRONG_SELL') && (
                    <TouchableOpacity
                      style={styles.sellButton}
                      onPress={() => handleManualSell(holding.symbol, holding.amount, holding.current_price)}
                    >
                      <Ionicons name="cash" size={20} color="#FFFFFF" />
                      <Text style={styles.sellButtonText}>Execute Manual Sell</Text>
                    </TouchableOpacity>
                  )}
                </View>
              )}
            </View>
          ))}
        </View>
      )}

      {/* Analytics Section */}
      {analytics && analytics.total_sells > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Performance Analytics</Text>
          
          <View style={styles.analyticsGrid}>
            <View style={styles.analyticsCard}>
              <Text style={styles.analyticsLabel}>Total Sells</Text>
              <Text style={styles.analyticsValue}>{analytics.total_sells}</Text>
            </View>
            
            <View style={styles.analyticsCard}>
              <Text style={styles.analyticsLabel}>Total Profit</Text>
              <Text style={[styles.analyticsValue, { color: '#10B981' }]}>
                ${analytics.total_profit_usd?.toFixed(2) || '0.00'}
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Help Section */}
      <View style={styles.helpSection}>
        <Ionicons name="information-circle" size={24} color="#667eea" />
        <Text style={styles.helpText}>
          AI Asset Manager analyzes all your holdings hourly using 6 technical indicators. 
          Auto-sell only executes when profit ≥ your minimum threshold. 
          You are protected from selling at a loss! ✅
        </Text>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F3F4F6' },
  loadingText: { marginTop: 16, fontSize: 16, color: '#6B7280' },
  statusCard: { backgroundColor: '#FFFFFF', margin: 16, padding: 16, borderRadius: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  statusHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  statusTitle: { fontSize: 20, fontWeight: 'bold', color: '#1F2937', marginLeft: 8 },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  statusLabel: { fontSize: 14, color: '#6B7280' },
  statusValue: { fontSize: 14, fontWeight: '600', color: '#1F2937' },
  statusBadge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  statusBadgeText: { color: '#FFFFFF', fontSize: 12, fontWeight: '600' },
  recommendationRow: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#E5E7EB' },
  recommendationText: { fontSize: 13, fontWeight: '600' },
  section: { backgroundColor: '#FFFFFF', marginHorizontal: 16, marginBottom: 16, padding: 16, borderRadius: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1F2937', marginBottom: 16 },
  settingRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, paddingBottom: 20, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  settingInfo: { flex: 1, marginRight: 16 },
  settingLabel: { fontSize: 16, fontWeight: '600', color: '#1F2937', marginBottom: 4 },
  settingDescription: { fontSize: 13, color: '#6B7280', lineHeight: 18 },
  inputContainer: { flexDirection: 'row', alignItems: 'center' },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 8, width: 70, textAlign: 'center', fontSize: 16, fontWeight: '600' },
  inputSuffix: { fontSize: 16, fontWeight: '600', color: '#6B7280', marginLeft: 4 },
  saveButton: { backgroundColor: '#667eea', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 14, borderRadius: 10, marginTop: 8 },
  saveButtonDisabled: { opacity: 0.6 },
  saveButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '600', marginLeft: 8 },
  holdingCard: { backgroundColor: '#F9FAFB', borderRadius: 10, marginBottom: 12, overflow: 'hidden' },
  holdingHeader: { flexDirection: 'row', justifyContent: 'space-between', padding: 16 },
  holdingLeft: { flex: 1 },
  holdingSymbol: { fontSize: 16, fontWeight: 'bold', color: '#1F2937', marginBottom: 4 },
  recommendationChip: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12, alignSelf: 'flex-start' },
  recommendationChipText: { color: '#FFFFFF', fontSize: 10, fontWeight: 'bold' },
  holdingRight: { alignItems: 'flex-end' },
  holdingValue: { fontSize: 16, fontWeight: 'bold', color: '#1F2937', marginBottom: 4 },
  holdingProfit: { fontSize: 14, fontWeight: '600' },
  holdingExpanded: { padding: 16, paddingTop: 0, borderTopWidth: 1, borderTopColor: '#E5E7EB' },
  indicatorsSection: { backgroundColor: '#F3F4F6', padding: 12, borderRadius: 8, marginBottom: 12 },
  indicatorsTitle: { fontSize: 14, fontWeight: '600', color: '#1F2937', marginBottom: 8 },
  indicatorText: { fontSize: 13, color: '#4B5563', marginBottom: 4 },
  reasoningSection: { marginBottom: 12 },
  reasoningTitle: { fontSize: 14, fontWeight: '600', color: '#1F2937', marginBottom: 8 },
  reasoningText: { fontSize: 13, color: '#4B5563', marginBottom: 4, lineHeight: 18 },
  sellButton: { backgroundColor: '#DC2626', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 12, borderRadius: 8, marginTop: 8 },
  sellButtonText: { color: '#FFFFFF', fontSize: 14, fontWeight: '600', marginLeft: 8 },
  analyticsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  analyticsCard: { width: '48%', backgroundColor: '#F9FAFB', padding: 12, borderRadius: 8, marginBottom: 12 },
  analyticsLabel: { fontSize: 12, color: '#6B7280', marginBottom: 4 },
  analyticsValue: { fontSize: 18, fontWeight: 'bold', color: '#1F2937' },
  helpSection: { flexDirection: 'row', backgroundColor: '#EEF2FF', margin: 16, padding: 16, borderRadius: 12 },
  helpText: { flex: 1, fontSize: 13, color: '#4B5563', lineHeight: 20, marginLeft: 12 },
});
