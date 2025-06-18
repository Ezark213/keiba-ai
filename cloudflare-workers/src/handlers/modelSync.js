/**
 * モデル同期APIハンドラー
 * M4 Macから呼び出される
 */

import { compressionUtils } from '../utils/compression.js';

export async function handleModelSync(request, env, ctx) {
  try {
    // multipart/form-dataの処理
    const formData = await request.formData();
    const modelFile = formData.get('model');
    const metadata = JSON.parse(formData.get('metadata'));
    
    if (!modelFile || !metadata) {
      return new Response(JSON.stringify({ 
        error: 'Invalid request',
        message: 'Model file and metadata are required' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // メタデータ検証
    const requiredFields = ['version', 'return_rate', 'hit_rate', 'feature_importance'];
    for (const field of requiredFields) {
      if (!(field in metadata)) {
        return new Response(JSON.stringify({ 
          error: 'Invalid metadata',
          message: `Missing required field: ${field}` 
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
    
    // 還元率チェック（前のモデルより悪化していないか）
    const currentModel = await env.MODELS.get('latest_model_compressed', 'json');
    if (currentModel && currentModel.rr > metadata.return_rate * 1000) {
      console.warn('New model has lower return rate than current model');
      // 警告するが、アップロードは続行（実験的な変更の可能性）
    }
    
    // R2にモデルファイル保存
    const modelKey = `models/${metadata.version}/${metadata.filename || 'model.lgb'}`;
    await env.MODEL_STORAGE.put(modelKey, modelFile, {
      httpMetadata: {
        contentType: 'application/octet-stream',
      },
      customMetadata: {
        version: metadata.version,
        return_rate: String(metadata.return_rate),
        uploaded_at: new Date().toISOString()
      }
    });
    
    // メタデータを圧縮してKVに保存
    const compressedMeta = compressionUtils.compressModel({
      ...metadata,
      r2_key: modelKey,
      accuracy: metadata.accuracy || metadata.return_rate // 精度が未提供の場合
    });
    
    await env.MODELS.put('latest_model_compressed', JSON.stringify(compressedMeta));
    
    // バージョン履歴を更新（最新10件のみ保持）
    const versionHistory = await env.MODELS.get('model_versions', 'json') || [];
    versionHistory.unshift({
      version: metadata.version,
      return_rate: metadata.return_rate,
      uploaded_at: new Date().toISOString()
    });
    
    await env.MODELS.put('model_versions', JSON.stringify(versionHistory.slice(0, 10)));
    
    // 統計情報を更新
    await updateSyncStats(env, metadata);
    
    // 古い予測キャッシュをクリア（非同期）
    ctx.waitUntil(clearPredictionCache(env));
    
    return new Response(JSON.stringify({
      success: true,
      version: metadata.version,
      message: 'Model synced successfully',
      improvements: {
        return_rate: metadata.return_rate,
        hit_rate: metadata.hit_rate,
        previous_return_rate: currentModel ? currentModel.rr / 1000 : null
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Model sync error:', error);
    return new Response(JSON.stringify({ 
      error: 'Sync failed',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * 同期統計を更新
 */
async function updateSyncStats(env, metadata) {
  const today = new Date().toISOString().slice(0, 10);
  const statsKey = `stats:sync:${today}`;
  
  const stats = await env.MODELS.get(statsKey, 'json') || {
    sync_count: 0,
    best_return_rate: 0,
    versions: []
  };
  
  stats.sync_count++;
  stats.last_sync = new Date().toISOString();
  stats.versions.push(metadata.version);
  
  if (metadata.return_rate > stats.best_return_rate) {
    stats.best_return_rate = metadata.return_rate;
    stats.best_version = metadata.version;
  }
  
  await env.MODELS.put(statsKey, JSON.stringify(stats), {
    expirationTtl: 86400 * 7 // 7日間保持
  });
}

/**
 * 予測キャッシュをクリア
 */
async function clearPredictionCache(env) {
  // 予測キャッシュのプレフィックス
  const prefix = 'pred:';
  
  // KVのlist操作は無料枠では制限があるため、
  // 個別のキーをクリアする代わりに、TTLに任せる
  console.log('Prediction cache will expire naturally via TTL');
}