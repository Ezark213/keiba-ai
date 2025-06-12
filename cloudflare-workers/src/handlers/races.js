/**
 * レース情報APIハンドラー
 */

export async function handleRaces(request, env, type) {
  try {
    const today = new Date().toISOString().slice(0, 10);
    let raceData;
    
    switch (type) {
      case 'today':
        raceData = await getTodayRaces(env, today);
        break;
      case 'upcoming':
        raceData = await getUpcomingRaces(env);
        break;
      default:
        return new Response(JSON.stringify({ 
          error: 'Invalid race type' 
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
    }
    
    return new Response(JSON.stringify(raceData), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300' // 5分キャッシュ
      }
    });
    
  } catch (error) {
    console.error('Races API error:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch races',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * 本日のレース情報を取得
 */
async function getTodayRaces(env, date) {
  // KVから本日のレース情報を取得
  const racesKey = `races:${date}`;
  const cachedRaces = await env.MODELS.get(racesKey, 'json');
  
  if (!cachedRaces) {
    // デモデータを返す（実際はM4 Macから同期される）
    return generateDemoRaces(date);
  }
  
  // レースごとの予測状態を追加
  const racesWithStatus = await Promise.all(
    cachedRaces.map(async (race) => {
      const predictionKey = `pred:${race.race_id}`;
      const hasPrediction = await env.PREDICTIONS.get(predictionKey) !== null;
      
      return {
        ...race,
        has_prediction: hasPrediction,
        status: getRaceStatus(race)
      };
    })
  );
  
  return {
    date,
    races: racesWithStatus,
    total_races: racesWithStatus.length,
    predicted_count: racesWithStatus.filter(r => r.has_prediction).length
  };
}

/**
 * 今後のレース情報を取得
 */
async function getUpcomingRaces(env) {
  const races = [];
  const today = new Date();
  
  // 今後3日分のレース情報を取得
  for (let i = 0; i < 3; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() + i);
    const dateStr = date.toISOString().slice(0, 10);
    
    const dayRaces = await env.MODELS.get(`races:${dateStr}`, 'json');
    if (dayRaces) {
      races.push({
        date: dateStr,
        races: dayRaces.map(r => ({
          race_id: r.race_id,
          place: r.place,
          race_num: r.race_num,
          race_name: r.race_name,
          post_time: r.post_time,
          horse_count: r.horses?.length || 0
        }))
      });
    }
  }
  
  return {
    upcoming_days: races,
    total_races: races.reduce((sum, day) => sum + day.races.length, 0)
  };
}

/**
 * レースステータスを判定
 */
function getRaceStatus(race) {
  const now = new Date();
  const postTime = new Date(`${race.date} ${race.post_time}`);
  
  if (now < postTime) {
    const timeDiff = postTime - now;
    const minutesUntil = Math.floor(timeDiff / 60000);
    
    if (minutesUntil < 30) {
      return 'soon'; // まもなく発走
    }
    return 'upcoming'; // 予定
  } else {
    const timeSince = now - postTime;
    const minutesSince = Math.floor(timeSince / 60000);
    
    if (minutesSince < 30) {
      return 'running'; // レース中/結果待ち
    }
    return 'finished'; // 終了
  }
}

/**
 * デモレースデータ生成
 */
function generateDemoRaces(date) {
  const places = ['東京', '中山', '阪神', '京都'];
  const races = [];
  
  places.forEach(place => {
    for (let i = 1; i <= 12; i++) {
      races.push({
        race_id: `${date.replace(/-/g, '')}${place.substring(0, 2)}${String(i).padStart(2, '0')}`,
        date,
        place,
        race_num: i,
        race_name: `第${i}レース`,
        post_time: `${10 + Math.floor(i / 2)}:${(i % 2) * 30}0`,
        distance: 1600 + (i % 3) * 200,
        track: i % 2 === 0 ? 'ダート' : '芝',
        horses: []
      });
    }
  });
  
  return {
    date,
    races,
    total_races: races.length,
    predicted_count: 0
  };
}