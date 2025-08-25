export interface Round {
  id: string;
  user_id: string;
  bet: number;
  payout: number;
  created_at: string;
}

export interface LedgerItem {
  id: string;
  user_id: string;
  amount: number;
  balance: number;
  meta: any;
  created_at: string;
}
