/**
 * システムステータスAPIハンドラー
 */

import { compressionUtils } from '../utils/compression.js';

export async function handleStatus(request, env) {
  try {
    // モデル情報取得
    const modelMetaCompressed = await env.MODELS.get('latest_model_compressed', 'json');
    
    if (!modelMetaCompressed) {
      return new Response(JSON.stringify({
        status: 'no_model',
        message: 'No model available',
        timestamp: new Date().toISOString()
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // 圧縮データを展開
    const modelMeta = compressionUtils.decompressModel(modelMetaCompressed);
    
    // パフォーマンス統計を取得
    const perfStats = await getPerformanceStats(env);
    
    // ステータス情報構築
    const status = {
      status: 'operational',
      model_version: modelMeta.version,
      current_return_rate: modelMeta.return_rate,
      hit_rate: modelMeta.hit_rate,
      model_accuracy: modelMeta.accuracy,
      feature_importance: modelMeta.feature_importance,
      
      // パフォーマンス統計
      total_bets: perfStats.total_bets,
      monthly_bets: perfStats.monthly_bets,
      daily_bets: perfStats.daily_bets,
      
      // 変化率（前日比）
      return_rate_change: perfStats.return_rate_change,
      hit_rate_change: perfStats.hit_rate_change,
      
      // システム情報
      last_model_update: modelMeta.timestamp,
      cache_hit_rate: perfStats.cache_hit_rate,
      
      // 予測パフォーマンス
      recent_predictions: perfStats.recent_predictions,
      winning_streak: perfStats.winning_streak,
      
      timestamp: new Date().toISOString()
    };
    
    return new Response(JSON.stringify(status), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=30' // 30秒キャッシュ
      }
    });
    
  } catch (error) {
    console.error('Status error:', error);
    return new Response(JSON.stringify({
      status: 'error',
      message: error.message,
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * パフォーマンス統計を取得
 */
async function getPerformanceStats(env) {
  // 今日の日付キー
  const today = new Date().toISOString().slice(0, 10);
  const month = today.slice(0, 7);
  
  try {
    // 統計情報を取得（バッチで保存されたもの）
    const dailyStats = await env.MODELS.get(`stats:daily:${today}`, 'json') || {};
    const monthlyStats = await env.MODELS.get(`stats:monthly:${month}`, 'json') || {};
    const yesterdayStats = await env.MODELS.get(`stats:daily:${getYesterday()}`, 'json') || {};
    
    // 変化率計算
    const return_rate_change = yesterdayStats.return_rate 
      ? ((dailyStats.return_rate || 0) - yesterdayStats.return_rate) / yesterdayStats.return_rate
      : 0;
      
    const hit_rate_change = yesterdayStats.hit_rate
      ? ((dailyStats.hit_rate || 0) - yesterdayStats.hit_rate) / yesterdayStats.hit_rate
      : 0;
    
    return {
      total_bets: monthlyStats.total_bets || 0,
      monthly_bets: monthlyStats.bets_count || 0,
      daily_bets: dailyStats.bets_count || 0,
      return_rate_change,
      hit_rate_change,
      cache_hit_rate: dailyStats.cache_hit_rate || 0,
      recent_predictions: dailyStats.recent_predictions || [],
      winning_streak: dailyStats.winning_streak || 0
    };
    
  } catch (error) {
    console.error('Failed to get performance stats:', error);
    return {
      total_bets: 0,
      monthly_bets: 0,
      daily_bets: 0,
      return_rate_change: 0,
      hit_rate_change: 0,
      cache_hit_rate: 0,
      recent_predictions: [],
      winning_streak: 0
    };
  }
}

function getYesterday() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return yesterday.toISOString().slice(0, 10);
}