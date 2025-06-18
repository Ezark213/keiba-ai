/**
 * データ圧縮ユーティリティ
 * Cloudflare KV無料枠最適化用
 */

export const compressionUtils = {
  /**
   * モデルメタデータを圧縮（約1/3サイズに）
   */
  compressModel(model) {
    return {
      v: model.version.substring(0, 8), // バージョン短縮
      rr: Math.round(model.return_rate * 1000), // 整数化（0.801 -> 801）
      hr: Math.round(model.hit_rate * 1000),
      ac: Math.round(model.accuracy * 1000),
      // 特徴量重要度はTOP5のみ、略称使用
      fi: Object.entries(model.feature_importance || {})
        .slice(0, 5)
        .map(([k, v]) => [
          k.substring(0, 8), // キー名短縮
          Math.round(v * 100)
        ]),
      ts: Date.now(), // タイムスタンプ（Unix時間）
      fc: model.feature_count || 0
    };
  },
  
  /**
   * 圧縮されたモデルを展開
   */
  decompressModel(compressed) {
    return {
      version: compressed.v,
      return_rate: compressed.rr / 1000,
      hit_rate: compressed.hr / 1000,
      accuracy: compressed.ac / 1000,
      feature_importance: Object.fromEntries(
        compressed.fi.map(([k, v]) => [k, v / 100])
      ),
      timestamp: new Date(compressed.ts).toISOString(),
      feature_count: compressed.fc
    };
  },
  
  /**
   * 予測結果を圧縮
   */
  compressPredictions(predictions) {
    return predictions.map(p => ({
      n: p.horse_num,
      nm: p.horse_name.substring(0, 10), // 馬名短縮
      p: Math.round(p.win_prob * 1000),
      o: Math.round(p.odds * 10),
      ev: Math.round(p.expected_value * 100),
      r: p.recommended_bet > 0 ? 1 : 0,
      rb: Math.round(p.recommended_bet * 1000)
    }));
  },
  
  /**
   * 圧縮された予測を展開
   */
  decompressPredictions(compressed) {
    return compressed.map(c => ({
      horse_num: c.n,
      horse_name: c.nm,
      win_prob: c.p / 1000,
      odds: c.o / 10,
      expected_value: c.ev / 100,
      recommended: c.r === 1,
      recommended_bet: c.rb / 1000
    }));
  },
  
  /**
   * バッチデータを圧縮（複数の更新を1つにまとめる）
   */
  compressBatch(updates) {
    return {
      t: Date.now(),
      c: updates.length,
      d: updates.map(u => ({
        k: u.key.substring(0, 10),
        v: this.genericCompress(u.value)
      }))
    };
  },
  
  /**
   * 汎用圧縮（数値の短縮など）
   */
  genericCompress(value) {
    if (typeof value === 'number') {
      return Math.round(value * 1000) / 1000;
    }
    if (typeof value === 'string' && value.length > 20) {
      return value.substring(0, 20) + '...';
    }
    return value;
  }
};