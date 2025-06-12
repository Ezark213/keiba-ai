import React, { useMemo } from 'react';

export function PerformanceChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        データがありません
      </div>
    );
  }

  // チャートデータの計算
  const chartData = useMemo(() => {
    const maxReturn = Math.max(...data.map(d => d.return_rate));
    const minReturn = Math.min(...data.map(d => d.return_rate));
    const range = maxReturn - minReturn || 1;
    
    return data.map(d => ({
      ...d,
      normalizedReturn: ((d.return_rate - minReturn) / range) * 100,
      normalizedHit: d.hit_rate * 100
    }));
  }, [data]);

  // 最新7日分のみ表示
  const recentData = chartData.slice(-7);

  return (
    <div className="relative h-64">
      {/* Y軸ラベル */}
      <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-500">
        <span>{(Math.max(...data.map(d => d.return_rate)) * 100).toFixed(0)}%</span>
        <span>{(Math.min(...data.map(d => d.return_rate)) * 100).toFixed(0)}%</span>
      </div>

      {/* チャートエリア */}
      <div className="ml-12 h-full relative">
        {/* 目標ライン（80%） */}
        <div 
          className="absolute w-full border-t-2 border-dashed border-green-400"
          style={{ top: '20%' }}
        >
          <span className="absolute -top-3 right-0 text-xs text-green-600 bg-white px-1">
            目標 80%
          </span>
        </div>

        {/* バーチャート */}
        <div className="h-full flex items-end justify-between gap-2 pb-6">
          {recentData.map((day, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              {/* 還元率バー */}
              <div className="w-full relative flex-1 flex items-end">
                <div
                  className="w-full bg-primary-500 rounded-t transition-all duration-300 hover:bg-primary-600 relative group"
                  style={{ height: `${day.normalizedReturn}%` }}
                >
                  {/* ツールチップ */}
                  <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    還元率: {(day.return_rate * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              
              {/* 日付ラベル */}
              <div className="mt-2 text-xs text-gray-500">
                {new Date(day.date).toLocaleDateString('ja-JP', { 
                  month: 'numeric', 
                  day: 'numeric' 
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 凡例 */}
      <div className="mt-4 flex items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary-500 rounded"></div>
          <span className="text-gray-600">還元率</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 border-2 border-dashed border-green-400"></div>
          <span className="text-gray-600">目標</span>
        </div>
      </div>

      {/* サマリー */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="text-center">
          <p className="text-gray-500">平均還元率</p>
          <p className="font-semibold">
            {(data.reduce((sum, d) => sum + d.return_rate, 0) / data.length * 100).toFixed(1)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-gray-500">最高還元率</p>
          <p className="font-semibold text-green-600">
            {(Math.max(...data.map(d => d.return_rate)) * 100).toFixed(1)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-gray-500">目標達成日数</p>
          <p className="font-semibold">
            {data.filter(d => d.return_rate >= 0.8).length}日
          </p>
        </div>
      </div>
    </div>
  );
}