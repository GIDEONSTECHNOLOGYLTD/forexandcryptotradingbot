// Global type definitions for the app

export interface User {
  _id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'user';
  subscription: 'free' | 'pro' | 'enterprise';
  exchange_connected: boolean;
  created_at?: string;
}

export interface Bot {
  _id: string;
  user_id: string;
  config: BotConfig;
  status: 'running' | 'stopped' | 'error';
  created_at: string;
  started_at?: string;
  stopped_at?: string;
  is_my_bot?: boolean;
  owner_email?: string;
}

export interface BotConfig {
  bot_type: 'momentum' | 'grid' | 'dca' | 'arbitrage';
  symbol: string;
  capital: number;
  initial_capital: number;
  max_position_size: number;
  stop_loss_percent: number;
  take_profit_percent: number;
  max_open_positions: number;
  timeframe: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
  paper_trading: boolean;
}

export interface Trade {
  _id: string;
  bot_id: string;
  user_id: string;
  symbol: string;
  side: 'buy' | 'sell';
  amount: number;
  price: number;
  pnl_percent?: number;
  is_paper: boolean;
  timestamp: string;
}

export interface Subscription {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'inactive' | 'cancelled';
  expires_at?: string;
}

export interface PaymentMethod {
  type: 'crypto' | 'paystack';
  network?: string;
  address?: string;
}

export interface WebSocketMessage {
  type: 'trade' | 'bot_status' | 'error';
  data: any;
}
