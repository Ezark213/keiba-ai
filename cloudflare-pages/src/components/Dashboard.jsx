import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid';
import { Card } from './ui/Card';

export function Dashboard({ status }) {
  if (!status) {
    return (
      <div className="card p-6">
        <p className="text-gray-500">データを読み込み中...</p>
      </div>
    );
  }

  const metrics = [
    {
      name: '現在の還元率',
      value: `${(status.current_return_rate * 100).toFixed(1)}%`,
      target: '80%',
      isAchieved: status.current_return_rate >= 0.80,
      change: status.return_rate_change || 0,
      description: '目標: 80%以上'
    },
    {
      name: '的中率',
      value: `${(status.hit_rate * 100).toFixed(1)}%`,
      target: '15%',
      isAchieved: status.hit_rate >= 0.15,
      change: status.hit_rate_change || 0,
      description: '単勝的中率'
    },
    {
      name: '本日のベット数',
      value: status.daily_bets?.toLocaleString() || '0',
      subValue: `月間: ${status.monthly_bets?.toLocaleString() || '0'}`,
      description: '実行済み予測'
    },
    {
      name: 'モデル精度',
      value: `${((status.model_accuracy || 0) * 100).toFixed(1)}%`,
      subValue: `v${status.model_version || '-'}`,
      description: 'AUCスコア'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          パフォーマンスダッシュボード
        </h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {metrics.map((metric) => (
            <Card key={metric.name} className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600">
                    {metric.name}
                  </p>
                  <div className="mt-2 flex items-baseline">
                    <p className={`text-2xl font-semibold ${
                      metric.isAchieved ? 'text-green-600' : 'text-gray-900'
                    }`}>
                      {metric.value}
                    </p>
                    {metric.change !== undefined && (
                      <span className={`ml-2 flex items-center text-sm ${
                        metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metric.change >= 0 ? (
                          <ArrowUpIcon className="h-4 w-4" />
                        ) : (
                          <ArrowDownIcon className="h-4 w-4" />
                        )}
                        {Math.abs(metric.change * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-gray-500">
                    {metric.description}
                  </p>
                  {metric.subValue && (
                    <p className="mt-1 text-xs text-gray-400">
                      {metric.subValue}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* 重要特徴量 */}
      {status.feature_importance && (
        <Card className="p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4">
            重要特徴量 TOP5
          </h3>
          <div className="space-y-3">
            {Object.entries(status.feature_importance)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 5)
              .map(([feature, importance], index) => (
                <div key={feature} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-600 w-6">
                      {index + 1}.
                    </span>
                    <span className="text-sm text-gray-900">
                      {feature}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${importance * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-500 w-12 text-right">
                      {(importance * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </Card>
      )}

      {/* システムステータス */}
      <Card className="p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">キャッシュヒット率</p>
            <p className="font-medium">
              {((status.cache_hit_rate || 0) * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-gray-500">連勝数</p>
            <p className="font-medium">
              {status.winning_streak || 0}
            </p>
          </div>
          <div>
            <p className="text-gray-500">総ベット数</p>
            <p className="font-medium">
              {status.total_bets?.toLocaleString() || '0'}
            </p>
          </div>
          <div>
            <p className="text-gray-500">最終更新</p>
            <p className="font-medium">
              {status.timestamp 
                ? new Date(status.timestamp).toLocaleTimeString('ja-JP')
                : '-'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}