import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { LineChart } from 'react-native-chart-kit';
import api from '../services/api';
import { useUser } from '../context/UserContext';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }: any) {
  const { user, isAdmin } = useUser();
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalBalance: 0,
    todayPnL: 0,
    totalTrades: 0,
    winRate: 0,
    activeBots: 0,
  });
  const [chartData, setChartData] = useState<number[]>([]);

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 5 seconds for real-time updates
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.getDashboard();
      
      // Map backend response to frontend structure
      const mappedStats = {
        totalBalance: response.stats?.total_capital || 0,
        todayPnL: response.stats?.total_pnl || 0,
        totalTrades: response.stats?.total_trades || 0,
        winRate: response.stats?.win_rate || 0,
        activeBots: response.stats?.active_bots || 0,
      };
      
      setStats(mappedStats);
      setChartData(response.chartData || [0, 0, 0, 0, 0, 0, 0]);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Admin Badge */}
      {isAdmin && (
        <View style={styles.adminBadge}>
          <Ionicons name="shield-checkmark" size={16} color="#fff" />
          <Text style={styles.adminBadgeText}>ADMIN - System Wide View</Text>
        </View>
      )}

      {/* Header Card */}
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.headerCard}
      >
        <View style={styles.balanceSection}>
          <Text style={styles.balanceLabel}>
            {isAdmin ? 'Total System Balance' : 'Total Balance'}
          </Text>
          <Text style={styles.balanceAmount}>
            ${stats.totalBalance.toLocaleString()}
          </Text>
          <View style={styles.pnlContainer}>
            <Ionicons
              name={stats.todayPnL >= 0 ? 'trending-up' : 'trending-down'}
              size={16}
              color="#fff"
            />
            <Text style={styles.pnlText}>
              ${Math.abs(stats.todayPnL).toFixed(2)} Today
            </Text>
          </View>
        </View>
      </LinearGradient>

      {/* Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>7-Day Performance</Text>
        <LineChart
          data={{
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{ data: chartData.length > 0 ? chartData : [0, 0, 0, 0, 0, 0, 0] }],
          }}
          width={width - 40}
          height={200}
          chartConfig={{
            backgroundColor: '#fff',
            backgroundGradientFrom: '#fff',
            backgroundGradientTo: '#fff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
            style: {
              borderRadius: 16,
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <StatCard
          icon="bar-chart"
          title="Total Trades"
          value={stats.totalTrades.toString()}
          color="#667eea"
        />
        <StatCard
          icon="trophy"
          title="Win Rate"
          value={`${stats.winRate.toFixed(1)}%`}
          color="#f093fb"
        />
        <StatCard
          icon="rocket"
          title="Active Bots"
          value={stats.activeBots.toString()}
          color="#4facfe"
        />
        <StatCard
          icon="flash"
          title="Status"
          value="Active"
          color="#43e97b"
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('BotConfig')}
        >
          <Ionicons name="settings-outline" size={24} color="#667eea" />
          <Text style={styles.actionText}>Configure Bot</Text>
          <Ionicons name="chevron-forward" size={20} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Payment')}
        >
          <Ionicons name="card-outline" size={24} color="#667eea" />
          <Text style={styles.actionText}>Upgrade Plan</Text>
          <Ionicons name="chevron-forward" size={20} color="#ccc" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

function StatCard({ icon, title, value, color }: any) {
  return (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <Ionicons name={icon} size={24} color={color} />
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  adminBadge: {
    backgroundColor: '#10b981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 8,
  },
  adminBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  headerCard: {
    padding: 30,
    margin: 20,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  balanceSection: {
    alignItems: 'center',
  },
  balanceLabel: {
    color: '#fff',
    fontSize: 16,
    opacity: 0.9,
  },
  balanceAmount: {
    color: '#fff',
    fontSize: 42,
    fontWeight: 'bold',
    marginTop: 10,
  },
  pnlContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  pnlText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 5,
  },
  chartContainer: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    marginBottom: 15,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 10,
  },
  statTitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  actionsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    flex: 1,
    marginLeft: 15,
    fontSize: 16,
    fontWeight: '500',
  },
});
