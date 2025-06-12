import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';

export function RecentPredictions({ predictions }) {
  if (!predictions || predictions.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>最近の予測</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {predictions.slice(0, 5).map((pred, index) => (
            <div
              key={`${pred.race_id}-${index}`}
              className="border-l-4 border-primary-200 pl-4 py-2"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    レースID: {pred.race_id}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(pred.timestamp).toLocaleString('ja-JP')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">
                    推奨: {pred.recommended_bets.length}頭
                  </p>
                </div>
              </div>
              
              {/* 推奨馬 */}
              <div className="mt-2 flex flex-wrap gap-2">
                {pred.recommended_bets.map(bet => (
                  <span
                    key={bet.horse_num}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    {bet.horse_num}番 (EV: {bet.expected_value.toFixed(2)})
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        {predictions.length > 5 && (
          <p className="mt-4 text-sm text-gray-500 text-center">
            他 {predictions.length - 5} 件の予測
          </p>
        )}
      </CardContent>
    </Card>
  );
}