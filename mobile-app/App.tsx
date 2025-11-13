// Polyfill for EventEmitter
import { EventEmitter } from 'events';
global.EventEmitter = EventEmitter;

// Polyfill for process if needed
if (typeof global.process === 'undefined') {
  global.process = { env: {} };
}

import React, { useState, useEffect } from 'react';
import { View, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import { UserProvider } from './src/context/UserContext';

// Screens
import SplashScreen from './src/screens/SplashScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import HomeScreen from './src/screens/HomeScreen';
import TradingScreen from './src/screens/TradingScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/LoginScreen';
import SignupScreen from './src/screens/SignupScreen';
import ForgotPasswordScreen from './src/screens/ForgotPasswordScreen';
import BotConfigScreen from './src/screens/BotConfigScreen';
import BotDetailsScreen from './src/screens/BotDetailsScreen';
import PaymentScreen from './src/screens/PaymentScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import AboutScreen from './src/screens/AboutScreen';
import ExchangeConnectionScreen from './src/screens/ExchangeConnectionScreen';
import ManageUsersScreen from './src/screens/ManageUsersScreen';
import SystemAnalyticsScreen from './src/screens/SystemAnalyticsScreen';
import SystemSettingsScreen from './src/screens/SystemSettingsScreen';
import SecurityScreen from './src/screens/SecurityScreen';
import ManageSubscriptionsScreen from './src/screens/ManageSubscriptionsScreen';
import AdminBotScreen from './src/screens/AdminBotScreen';
import TradeHistoryScreen from './src/screens/TradeHistoryScreen';
import AISuggestionsScreen from './src/screens/AISuggestionsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any = 'home-outline';

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Trading') {
            iconName = focused ? 'trending-up' : 'trending-up-outline';
          } else if (route.name === 'Portfolio') {
            iconName = focused ? 'wallet' : 'wallet-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#667eea',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#667eea',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: any }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('App Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>
            Something went wrong
          </Text>
          <Text style={{ color: '#666', textAlign: 'center' }}>
            {this.state.error?.message || 'Unknown error'}
          </Text>
        </View>
      );
    }

    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <UserProvider>
        <NavigationContainer>
          <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName="Splash">
          {/* Initial Screens */}
          <Stack.Screen name="Splash" component={SplashScreen} />
          <Stack.Screen name="Onboarding" component={OnboardingScreen} />
          
          {/* Auth Screens */}
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          
          {/* Main App */}
          <Stack.Screen name="MainTabs" component={MainTabs} />
          
          {/* Modal Screens */}
          <Stack.Screen 
            name="BotConfig" 
            component={BotConfigScreen}
            options={{ presentation: 'modal', headerShown: true, title: 'Create Bot' }}
          />
          <Stack.Screen 
            name="BotDetails" 
            component={BotDetailsScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="Payment" 
            component={PaymentScreen}
            options={{ presentation: 'modal', headerShown: true, title: 'Subscription' }}
          />
          <Stack.Screen 
            name="Profile" 
            component={ProfileScreen}
            options={{ headerShown: true, title: 'Profile' }}
          />
          <Stack.Screen 
            name="Notifications" 
            component={NotificationsScreen}
            options={{ headerShown: true, title: 'Notifications' }}
          />
          <Stack.Screen 
            name="About" 
            component={AboutScreen}
            options={{ headerShown: true, title: 'About & Credits' }}
          />
          <Stack.Screen 
            name="ExchangeConnection" 
            component={ExchangeConnectionScreen}
            options={{ headerShown: true, title: 'Exchange Connection' }}
          />
          <Stack.Screen 
            name="ManageUsers" 
            component={ManageUsersScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="SystemAnalytics" 
            component={SystemAnalyticsScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="SystemSettings" 
            component={SystemSettingsScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="Security" 
            component={SecurityScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="ManageSubscriptions" 
            component={ManageSubscriptionsScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="AdminBot" 
            component={AdminBotScreen}
            options={{ headerShown: true, title: '🚀 Admin Auto-Trader' }}
          />
          <Stack.Screen 
            name="TradeHistory" 
            component={TradeHistoryScreen}
            options={{ headerShown: true, title: '📊 Trade History' }}
          />
          <Stack.Screen 
            name="AISuggestions" 
            component={AISuggestionsScreen}
            options={{ headerShown: true, title: '✨ AI Suggestions' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="auto" />
    </UserProvider>
    </ErrorBoundary>
  );
}
