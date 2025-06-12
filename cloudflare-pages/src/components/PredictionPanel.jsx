import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { raceApi } from '../utils/api';

export function PredictionPanel({ onPredict }) {
  const [races, setRaces] = useState([]);
  const [selectedRace, setSelectedRace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTodayRaces();
  }, []);

  const loadTodayRaces = async () => {
    try {
      setLoading(true);
      const data = await raceApi.getTodayRaces();
      setRaces(data.races || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load races:', err);
      setError('レース情報の取得に失敗しました');
      // デモデータ
      setRaces(generateDemoRaces());
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedRace) return;

    try {
      setPredicting(true);
      setError(null);
      
      // デモ用の馬データ（実際はレース選択時に取得）
      const horses = generateDemoHorses(selectedRace);
      
      const result = await onPredict(selectedRace.race_id, horses);
      setPrediction(result);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError('予測に失敗しました');
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>レース予測</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-4">
              <div className="spinner mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">レース情報を読み込み中...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* レース選択 */}
              <div>
                <label htmlFor="race-select" className="block text-sm font-medium text-gray-700 mb-2">
                  レースを選択
                </label>
                <select
                  id="race-select"
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  value={selectedRace?.race_id || ''}
                  onChange={(e) => {
                    const race = races.find(r => r.race_id === e.target.value);
                    setSelectedRace(race);
                    setPrediction(null);
                  }}
                >
                  <option value="">レースを選択してください</option>
                  {races.map(race => (
                    <option key={race.race_id} value={race.race_id}>
                      {race.place} {race.race_num}R - {race.post_time}
                      {race.has_prediction && ' ✓'}
                    </option>
                  ))}
                </select>
              </div>

              {/* 予測ボタン */}
              {selectedRace && (
                <button
                  onClick={handlePredict}
                  disabled={predicting}
                  className="w-full btn-primary"
                >
                  {predicting ? (
                    <>
                      <div className="spinner mr-2"></div>
                      予測中...
                    </>
                  ) : (
                    '予測を実行'
                  )}
                </button>
              )}

              {/* エラー表示 */}
              {error && (
                <div className="rounded-md bg-red-50 p-4">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 予測結果 */}
      {prediction && (
        <Card className="slide-in">
          <CardHeader>
            <CardTitle>予測結果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 推奨ベット */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  推奨ベット（期待値順）
                </h4>
                <div className="space-y-2">
                  {prediction.recommended_bets.map((bet, index) => (
                    <div
                      key={bet.horse_num}
                      className="flex items-center justify-between p-3 bg-green-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-green-700">
                          {index + 1}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">
                            {bet.horse_num}番 {bet.horse_name}
                          </p>
                          <p className="text-sm text-gray-600">
                            勝率 {(bet.win_prob * 100).toFixed(1)}% / オッズ {bet.odds.toFixed(1)}倍
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-green-700">
                          期待値 {bet.expected_value.toFixed(2)}
                        </p>
                        <p className="text-sm text-gray-600">
                          推奨 {bet.bet_amount.toLocaleString()}円
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 全予測一覧 */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  全出走馬の評価
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          馬番
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          馬名
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          勝率
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          オッズ
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          期待値
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {prediction.predictions.map(p => (
                        <tr key={p.horse_num} className={p.expected_value > 1.2 ? 'bg-green-50' : ''}>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {p.horse_num}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {p.horse_name}
                          </td>
                          <td className="px-3 py-2 text-sm text-right text-gray-900">
                            {(p.win_prob * 100).toFixed(1)}%
                          </td>
                          <td className="px-3 py-2 text-sm text-right text-gray-900">
                            {p.odds.toFixed(1)}
                          </td>
                          <td className="px-3 py-2 text-sm text-right font-medium">
                            <span className={p.expected_value > 1.2 ? 'text-green-600' : 'text-gray-900'}>
                              {p.expected_value.toFixed(2)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* メタ情報 */}
              <div className="text-xs text-gray-500 text-right">
                モデル: {prediction.model_version} | 
                予測時刻: {new Date(prediction.timestamp).toLocaleTimeString('ja-JP')}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// デモデータ生成関数
function generateDemoRaces() {
  const places = ['東京', '中山', '阪神'];
  const now = new Date();
  const races = [];
  
  places.forEach(place => {
    for (let i = 1; i <= 4; i++) {
      races.push({
        race_id: `${now.toISOString().slice(0, 10).replace(/-/g, '')}${place}${String(i).padStart(2, '0')}`,
        place,
        race_num: i,
        post_time: `${10 + i}:${i % 2 === 0 ? '30' : '00'}`,
        has_prediction: false
      });
    }
  });
  
  return races;
}

function generateDemoHorses(race) {
  const horses = [];
  const horseCount = 12 + Math.floor(Math.random() * 6);
  
  for (let i = 1; i <= horseCount; i++) {
    horses.push({
      horse_num: i,
      horse_name: `デモホース${i}`,
      odds: Math.round((2 + Math.random() * 48) * 10) / 10,
      idm: 40 + Math.random() * 40,
      jockey_index: 40 + Math.random() * 40,
      trainer_index: 40 + Math.random() * 40,
      info_index: 40 + Math.random() * 40
    });
  }
  
  return horses;
}