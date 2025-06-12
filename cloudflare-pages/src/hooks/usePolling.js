import { useState, useEffect, useRef } from 'react';
import { api } from '../utils/api';

/**
 * 効率的なポーリングフック（無料枠最適化）
 */
export function usePolling(endpoint, interval = 60000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastFetch, setLastFetch] = useState(0);
  const intervalRef = useRef(null);
  const isActiveRef = useRef(true);

  useEffect(() => {
    const fetchData = async () => {
      // レート制限対策
      const now = Date.now();
      if (now - lastFetch < 5000) return; // 5秒以内は無視

      // タブが非アクティブな場合はスキップ
      if (document.hidden || !isActiveRef.current) return;

      try {
        const result = await api.get(endpoint);
        setData(result);
        setError(null);
        setLastFetch(now);

        // ローカルストレージにキャッシュ
        localStorage.setItem(`cache_${endpoint}`, JSON.stringify({
          data: result,
          timestamp: now
        }));
      } catch (err) {
        console.error(`Polling error for ${endpoint}:`, err);
        setError(err);

        // エラー時はキャッシュから復元
        const cached = localStorage.getItem(`cache_${endpoint}`);
        if (cached) {
          const { data: cachedData } = JSON.parse(cached);
          setData(cachedData);
        }
      }
    };

    // 初回取得
    fetchData();

    // ポーリング開始
    const startPolling = () => {
      intervalRef.current = setInterval(fetchData, interval);
    };

    // タブの表示状態に応じてポーリングを制御
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // タブが非表示になったらポーリング停止
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } else {
        // タブが表示されたら即座に取得してポーリング再開
        fetchData();
        startPolling();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // 初回ポーリング開始
    if (!document.hidden) {
      startPolling();
    }

    // クリーンアップ
    return () => {
      isActiveRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [endpoint, interval, lastFetch]);

  return { data, error, refetch: () => setLastFetch(0) };
}