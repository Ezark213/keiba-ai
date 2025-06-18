/**
 * パフォーマンス履歴APIハンドラー
 */

export async function handlePerformance(request, env) {
  try {
    const url = new URL(request.url);
    const days = parseInt(url.searchParams.get('days') || '30');
    const groupBy = url.searchParams.get('groupBy') || 'daily';
    
    // 履歴データ取得
    const performanceData = await getPerformanceHistory(env, days, groupBy);
    
    // 統計情報計算
    const stats = calculatePerformanceStats(performanceData);
    
    return new Response(JSON.stringify({
      history: performanceData,
      stats,
      period: {
        days,
        groupBy,
        start_date: getDateString(-days),
        end_date: getDateString(0)
      }
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=600' // 10分キャッシュ
      }
    });
    
  } catch (error) {
    console.error('Performance API error:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch performance',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * パフォーマンス履歴を取得
 */
async function getPerformanceHistory(env, days, groupBy) {
  const history = [];
  const today = new Date();
  
  if (groupBy === 'daily') {
    // 日次データ取得
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().slice(0, 10);
      
      const dailyStats = await env.MODELS.get(`stats:daily:${dateStr}`, 'json');
      
      if (dailyStats) {
        history.push({
          date: dateStr,
          return_rate: dailyStats.return_rate || 0,
          hit_rate: dailyStats.hit_rate || 0,
          bet_count: dailyStats.bet_count || 0,
          profit: dailyStats.profit || 0,
          roi: dailyStats.roi || 0
        });
      } else {
        // データがない日はゼロで埋める
        history.push({
          date: dateStr,
          return_rate: 0,
          hit_rate: 0,
          bet_count: 0,
          profit: 0,
          roi: 0
        });
      }
    }
  } else if (groupBy === 'weekly') {
    // 週次データ取得
    const weeks = Math.ceil(days / 7);
    for (let i = weeks - 1; i >= 0; i--) {
      const weekData = await getWeeklyStats(env, i);
      if (weekData) {
        history.push(weekData);
      }
    }
  }
  
  return history;
}

/**
 * 週次統計を取得
 */
async function getWeeklyStats(env, weeksAgo) {
  const endDate = new Date();
  endDate.setDate(endDate.getDate() - (weeksAgo * 7));
  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - 6);
  
  let totalProfit = 0;
  let totalBets = 0;
  let totalWins = 0;
  let daysWithData = 0;
  
  // 週の各日のデータを集計
  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const dateStr = date.toISOString().slice(0, 10);
    
    const dailyStats = await env.MODELS.get(`stats:daily:${dateStr}`, 'json');
    if (dailyStats) {
      totalProfit += dailyStats.profit || 0;
      totalBets += dailyStats.bet_count || 0;
      totalWins += dailyStats.win_count || 0;
      daysWithData++;
    }
  }
  
  if (daysWithData === 0) return null;
  
  return {
    week_start: startDate.toISOString().slice(0, 10),
    week_end: endDate.toISOString().slice(0, 10),
    return_rate: totalBets > 0 ? (totalProfit + totalBets) / totalBets : 0,
    hit_rate: totalBets > 0 ? totalWins / totalBets : 0,
    bet_count: totalBets,
    profit: totalProfit,
    roi: totalBets > 0 ? totalProfit / totalBets : 0
  };
}

/**
 * パフォーマンス統計を計算
 */
function calculatePerformanceStats(history) {
  if (history.length === 0) {
    return {
      average_return_rate: 0,
      average_hit_rate: 0,
      total_profit: 0,
      total_bets: 0,
      best_day: null,
      worst_day: null,
      winning_days: 0,
      losing_days: 0,
      max_drawdown: 0,
      sharpe_ratio: 0
    };
  }
  
  // 基本統計
  const totalProfit = history.reduce((sum, day) => sum + (day.profit || 0), 0);
  const totalBets = history.reduce((sum, day) => sum + (day.bet_count || 0), 0);
  const avgReturnRate = history.reduce((sum, day) => sum + day.return_rate, 0) / history.length;
  const avgHitRate = history.reduce((sum, day) => sum + day.hit_rate, 0) / history.length;
  
  // 最良・最悪の日
  const sortedByProfit = [...history].sort((a, b) => b.profit - a.profit);
  const bestDay = sortedByProfit[0];
  const worstDay = sortedByProfit[sortedByProfit.length - 1];
  
  // 勝敗日数
  const winningDays = history.filter(day => day.profit > 0).length;
  const losingDays = history.filter(day => day.profit < 0).length;
  
  // 最大ドローダウン計算
  let maxDrawdown = 0;
  let peak = 0;
  let cumulativeProfit = 0;
  
  history.forEach(day => {
    cumulativeProfit += day.profit;
    if (cumulativeProfit > peak) {
      peak = cumulativeProfit;
    }
    const drawdown = peak - cumulativeProfit;
    if (drawdown > maxDrawdown) {
      maxDrawdown = drawdown;
    }
  });
  
  // シャープレシオ（簡易版）
  const returns = history.map(day => day.roi || 0);
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);
  const sharpeRatio = stdDev > 0 ? avgReturn / stdDev : 0;
  
  return {
    average_return_rate: avgReturnRate,
    average_hit_rate: avgHitRate,
    total_profit: totalProfit,
    total_bets: totalBets,
    best_day: bestDay ? { date: bestDay.date, profit: bestDay.profit } : null,
    worst_day: worstDay ? { date: worstDay.date, profit: worstDay.profit } : null,
    winning_days: winningDays,
    losing_days: losingDays,
    max_drawdown: maxDrawdown,
    sharpe_ratio: sharpeRatio
  };
}

/**
 * 日付文字列取得ヘルパー
 */
function getDateString(daysOffset) {
  const date = new Date();
  date.setDate(date.getDate() + daysOffset);
  return date.toISOString().slice(0, 10);
}