/**
 * 予測APIハンドラー
 * 無料枠対応版（Durable Objects不使用）
 */

import { compressionUtils } from '../utils/compression.js';
import { calculateKellyBet } from '../utils/betting.js';

export async function handlePredict(request, env, ctx) {
  try {
    const { race_id, horses } = await request.json();
    
    if (!race_id || !horses || !Array.isArray(horses)) {
      return new Response(JSON.stringify({ 
        error: 'Invalid request',
        message: 'race_id and horses array are required' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // キャッシュチェック（無料枠最適化）
    const cacheKey = `pred:${race_id}`;
    const cachedPrediction = await env.PREDICTIONS.get(cacheKey, 'json');
    
    if (cachedPrediction) {
      // 圧縮データを展開
      const predictions = compressionUtils.decompressPredictions(cachedPrediction.p);
      
      return new Response(JSON.stringify({
        race_id,
        predictions,
        cached: true,
        model_version: cachedPrediction.v,
        timestamp: new Date(cachedPrediction.t).toISOString()
      }), {
        headers: { 
          'Content-Type': 'application/json',
          'X-Cache': 'HIT',
          'Cache-Control': 'public, max-age=300' // 5分キャッシュ
        }
      });
    }
    
    // 最新モデルメタデータ取得
    const modelMeta = await env.MODELS.get('latest_model_compressed', 'json');
    
    if (!modelMeta) {
      return new Response(JSON.stringify({ 
        error: 'Model not available',
        message: 'No trained model found. Please wait for model sync.' 
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // 予測実行（簡易版）
    const predictions = await performPrediction(horses, modelMeta);
    
    // 上位馬を選出
    const sortedPredictions = predictions
      .sort((a, b) => b.expected_value - a.expected_value);
    
    const recommended = sortedPredictions
      .slice(0, 3)
      .filter(p => p.expected_value > 1.2); // 期待値1.2以上
    
    // 結果を圧縮してキャッシュ
    const compressed = {
      v: modelMeta.v,
      t: Date.now(),
      p: compressionUtils.compressPredictions(predictions)
    };
    
    // 非同期でキャッシュ保存（レスポンスを遅延させない）
    ctx.waitUntil(
      env.PREDICTIONS.put(cacheKey, JSON.stringify(compressed), {
        expirationTtl: 3600 // 1時間
      })
    );
    
    // レスポンス
    const result = {
      race_id,
      predictions: sortedPredictions,
      recommended_bets: recommended.map(p => ({
        horse_num: p.horse_num,
        horse_name: p.horse_name,
        win_prob: p.win_prob,
        odds: p.odds,
        expected_value: p.expected_value,
        bet_fraction: p.recommended_bet,
        bet_amount: Math.floor(10000 * p.recommended_bet) // 1万円基準
      })),
      model_version: modelMeta.v,
      timestamp: new Date().toISOString()
    };
    
    return new Response(JSON.stringify(result), {
      headers: { 
        'Content-Type': 'application/json',
        'X-Cache': 'MISS'
      }
    });
    
  } catch (error) {
    console.error('Prediction error:', error);
    return new Response(JSON.stringify({ 
      error: 'Prediction failed',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * 予測実行（簡易版）
 * 実際のLightGBMモデルの代わりに、特徴量重要度に基づく簡易スコアリング
 */
async function performPrediction(horses, modelMeta) {
  const featureImportance = Object.fromEntries(modelMeta.fi);
  
  return horses.map(horse => {
    // 特徴量に基づくスコア計算
    let score = 0;
    
    // IDM（最重要特徴量と仮定）
    if (horse.idm && featureImportance['idm']) {
      score += (horse.idm / 100) * (featureImportance['idm'] / 100);
    }
    
    // その他の指数
    const indices = ['jockey_index', 'trainer_index', 'info_index'];
    indices.forEach(idx => {
      if (horse[idx] && featureImportance[idx.substring(0, 8)]) {
        score += (horse[idx] / 100) * (featureImportance[idx.substring(0, 8)] / 100);
      }
    });
    
    // オッズによる調整（人気馬は若干減点）
    const oddsAdjustment = horse.odds > 10 ? 1.1 : 0.95;
    score *= oddsAdjustment;
    
    // 正規化して勝率に変換（0-1の範囲）
    const winProb = Math.min(Math.max(score * 0.3, 0.01), 0.5);
    
    // 期待値計算
    const expectedValue = winProb * horse.odds;
    
    // ケリー基準でベット額計算
    const recommendedBet = calculateKellyBet(winProb, horse.odds);
    
    return {
      horse_num: horse.horse_num,
      horse_name: horse.horse_name,
      win_prob: winProb,
      odds: horse.odds,
      expected_value: expectedValue,
      recommended_bet: recommendedBet,
      score: score // デバッグ用
    };
  });
}