/**
 * 競馬予測API - Cloudflare Workers
 * 無料枠最適化版
 */

import { handlePredict } from './handlers/predict.js';
import { handleStatus } from './handlers/status.js';
import { handleModelSync } from './handlers/modelSync.js';
import { handleRaces } from './handlers/races.js';
import { handlePerformance } from './handlers/performance.js';
import { corsMiddleware } from './middleware/cors.js';
import { authMiddleware } from './middleware/auth.js';
import { compressionUtils } from './utils/compression.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS処理
    const corsResponse = corsMiddleware(request);
    if (corsResponse) return corsResponse;
    
    // ルーティング定義
    const routes = {
      // 予測API（キャッシュ活用）
      '/api/predict': async () => handlePredict(request, env, ctx),
      
      // ステータスAPI（ポーリング用）
      '/api/status': async () => handleStatus(request, env),
      '/api/status/poll': async () => handleStatus(request, env),
      
      // レース情報API
      '/api/races/today': async () => handleRaces(request, env, 'today'),
      '/api/races/upcoming': async () => handleRaces(request, env, 'upcoming'),
      
      // パフォーマンス履歴
      '/api/performance/history': async () => handlePerformance(request, env),
      
      // モデル同期（M4 Macから）
      '/api/model/sync': async () => {
        const authResult = await authMiddleware(request, env);
        if (authResult.error) return authResult.response;
        return handleModelSync(request, env, ctx);
      },
      
      // 最新モデル情報取得
      '/api/model/latest': async () => {
        const modelMeta = await env.MODELS.get('latest_model_compressed', 'json');
        if (!modelMeta) {
          return new Response(JSON.stringify({ error: 'No model available' }), {
            status: 404,
            headers: { 'Content-Type': 'application/json' }
          });
        }
        
        // 圧縮解除
        const decompressed = compressionUtils.decompressModel(modelMeta);
        return new Response(JSON.stringify(decompressed), {
          headers: { 'Content-Type': 'application/json' }
        });
      },
      
      // ヘルスチェック
      '/health': async () => new Response('OK', { status: 200 })
    };
    
    // ルート処理
    const handler = routes[url.pathname];
    if (!handler) {
      return new Response('Not Found', { status: 404 });
    }
    
    try {
      const response = await handler();
      
      // レスポンスヘッダー追加
      const headers = new Headers(response.headers);
      headers.set('X-Powered-By', 'Keiba-Prediction-v3');
      
      // キャッシュヘッダー設定（無料枠最適化）
      if (url.pathname.startsWith('/api/races') || url.pathname === '/api/status') {
        headers.set('Cache-Control', 'public, max-age=60'); // 1分キャッシュ
      }
      
      return new Response(response.body, {
        status: response.status,
        headers
      });
      
    } catch (error) {
      console.error('Error:', error);
      return new Response(JSON.stringify({ 
        error: 'Internal Server Error',
        message: error.message 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  },
  
  // スケジュールトリガー（無料枠では使用不可だが、将来の拡張用）
  async scheduled(event, env, ctx) {
    console.log('Scheduled event triggered');
    // バッチ処理などをここで実行
  }
};