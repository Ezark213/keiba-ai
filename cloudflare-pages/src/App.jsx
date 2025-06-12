import React, { useState, useEffect } from 'react';
import { Dashboard } from './components/Dashboard';
import { PredictionPanel } from './components/PredictionPanel';
import { PerformanceChart } from './components/PerformanceChart';
import { RecentPredictions } from './components/RecentPredictions';
import { usePolling } from './hooks/usePolling';
import { api } from './utils/api';

const API_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [modelStatus, setModelStatus] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ポーリングでステータス更新（WebSocketの代替）
  const { data: statusData } = usePolling('/api/status', 30000); // 30秒ごと

  useEffect(() => {
    // 初期データ取得
    fetchInitialData();
  }, []);

  useEffect(() => {
    // ポーリングデータの反映
    if (statusData) {
      setModelStatus(statusData);
    }
  }, [statusData]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [statusRes, perfRes] = await Promise.all([
        api.get('/api/status'),
        api.get('/api/performance/history?days=30')
      ]);
      
      setModelStatus(statusRes);
      setPerformance(perfRes);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch initial data:', err);
      setError('データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const predictRace = async (raceId, horses) => {
    try {
      const prediction = await api.post('/api/predict', { race_id: raceId, horses });
      setPredictions(prev => [prediction, ...prev].slice(0, 50));
      return prediction;
    } catch (err) {
      console.error('Prediction failed:', err);
      throw err;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" style={{ width: '40px', height: '40px' }}></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error && !modelStatus) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={fetchInitialData} className="btn-primary">
            再読み込み
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🏇 競馬予測システム v3.0
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                AI駆動の高精度予測で還元率80%以上を実現
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className={`status-badge ${
                modelStatus?.status === 'operational' ? 'status-badge-success' : 'status-badge-warning'
              }`}>
                {modelStatus?.status === 'operational' ? '● 正常稼働中' : '○ 準備中'}
              </span>
              {modelStatus && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium">モデル:</span> {modelStatus.model_version}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ダッシュボード（左側2列） */}
          <div className="lg:col-span-2 space-y-6">
            <Dashboard status={modelStatus} />
            
            {performance && (
              <div className="card p-6">
                <h2 className="text-lg font-semibold mb-4">パフォーマンス推移</h2>
                <PerformanceChart data={performance.history} />
              </div>
            )}
            
            <RecentPredictions predictions={predictions} />
          </div>
          
          {/* 予測パネル（右側1列） */}
          <div>
            <PredictionPanel onPredict={predictRace} />
          </div>
        </div>
      </main>

      {/* フッター */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>Powered by Cloudflare Workers & M4 Mac & Claude API</p>
            <p className="mt-1">
              最終更新: {modelStatus?.last_model_update 
                ? new Date(modelStatus.last_model_update).toLocaleString('ja-JP')
                : '-'}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}