/**
 * ベッティング戦略ユーティリティ
 */

/**
 * ケリー基準でベット額を計算
 * @param {number} winProb - 勝率（0-1）
 * @param {number} odds - オッズ
 * @param {number} kellyFraction - ケリー係数（デフォルト1/4）
 * @returns {number} - ベット割合（0-0.05）
 */
export function calculateKellyBet(winProb, odds, kellyFraction = 0.25) {
  // エッジ計算（期待値 - 1）
  const edge = winProb * odds - 1;
  
  // エッジがマイナスならベットしない
  if (edge <= 0) return 0;
  
  // ケリー基準の計算
  // f = (p * b - q) / b
  // p: 勝率, q: 負け率(1-p), b: ネットオッズ(odds-1)
  const q = 1 - winProb;
  const b = odds - 1;
  const fullKelly = (winProb * b - q) / b;
  
  // 保守的なケリー（1/4ケリー）
  const conservativeKelly = fullKelly * kellyFraction;
  
  // 最大5%に制限
  return Math.min(Math.max(conservativeKelly, 0), 0.05);
}

/**
 * 複数ベットの最適配分を計算
 * @param {Array} bets - ベット候補配列
 * @param {number} totalBankroll - 総資金
 * @returns {Array} - 最適化されたベット配列
 */
export function optimizeBetAllocation(bets, totalBankroll = 10000) {
  // 期待値でソート
  const sortedBets = [...bets].sort((a, b) => b.expected_value - a.expected_value);
  
  let remainingBankroll = totalBankroll;
  const optimizedBets = [];
  
  for (const bet of sortedBets) {
    if (bet.recommended_bet <= 0) continue;
    
    // ベット額計算
    const betAmount = Math.floor(totalBankroll * bet.recommended_bet);
    
    // 残資金チェック
    if (betAmount > remainingBankroll) continue;
    
    optimizedBets.push({
      ...bet,
      bet_amount: betAmount,
      bet_percentage: bet.recommended_bet
    });
    
    remainingBankroll -= betAmount;
    
    // 最大3点買いまで
    if (optimizedBets.length >= 3) break;
  }
  
  return optimizedBets;
}

/**
 * リスク調整後のベット額を計算
 * @param {number} baseBet - 基本ベット額
 * @param {number} confidence - 信頼度（0-1）
 * @param {number} volatility - ボラティリティ
 * @returns {number} - 調整後ベット額
 */
export function adjustBetForRisk(baseBet, confidence, volatility) {
  // 信頼度による調整
  const confidenceMultiplier = 0.5 + (confidence * 0.5);
  
  // ボラティリティによる調整（高ボラティリティは減額）
  const volatilityMultiplier = 1 / (1 + volatility);
  
  return baseBet * confidenceMultiplier * volatilityMultiplier;
}