#!/bin/bash

# JRDBから実データを自動ダウンロード
export JRDB_USER=25067698
export JRDB_PASSWORD=87086387
export DOWNLOAD_FILE_OUTPUT_DIRECTORY=/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine/data/jrdb_real/

JRDB_BASE_URL=http://www.jrdb.com/member/data/
EXTENTION=.lzh

filepath() {
  FILENAME_PREFIX=$(echo $FILETYPE | tr '[a-z]' '[A-Z]')
  echo ${FILETYPE}/${FILENAME_PREFIX}${FILEDATE}${EXTENTION}
}

file_exists() {
  curl -u ${JRDB_USER}:${JRDB_PASSWORD} ${JRDB_BASE_URL}$(filepath) -o /dev/null -w '%{http_code}\n' -s
}

download() {
  echo "📥 ダウンロード中: $(filepath)"
  curl -u ${JRDB_USER}:${JRDB_PASSWORD} ${JRDB_BASE_URL}$(filepath) -L -o ${DOWNLOAD_FILE_OUTPUT_DIRECTORY}$(filepath)
}

extract_lha() {
  echo "📦 展開中: $(filepath)"
  # lhaコマンドがない場合のフォールバック
  if command -v lha >/dev/null 2>&1; then
    lha -xw=${DOWNLOAD_FILE_OUTPUT_DIRECTORY}${FILETYPE} ${DOWNLOAD_FILE_OUTPUT_DIRECTORY}$(filepath) 2>/dev/null || true
  else
    echo "⚠️ lhaコマンドがインストールされていません。.lzhファイルをそのまま保存します。"
  fi
}

pre_process() {
  mkdir -p ${DOWNLOAD_FILE_OUTPUT_DIRECTORY}${FILETYPE}
}

download_file() {
  FILETYPE=$1
  FILEDATE=$2
  
  pre_process
  
  status_code=$(file_exists)
  if [ $status_code != 200 ]; then
    echo "❌ ファイルが見つかりません: ${JRDB_BASE_URL}$(filepath)"
    return 1
  fi
  
  download
  extract_lha
  
  echo "✅ 完了: $FILETYPE $FILEDATE"
  return 0
}

main() {
  echo "🏇 JRDBから実データをダウンロード開始..."
  
  # 最近のファイル日付を生成（過去30日間）
  dates=()
  for i in {0..30}; do
    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS
      date_str=$(date -v-${i}d '+%y%m%d')
    else
      # Linux
      date_str=$(date -d "${i} days ago" '+%y%m%d')
    fi
    dates+=($date_str)
  done
  
  # ダウンロードするファイルタイプ
  file_types=("sed" "kyi" "bac")
  
  downloaded_count=0
  
  for file_type in "${file_types[@]}"; do
    echo "📊 $file_type ファイルをダウンロード中..."
    
    for date in "${dates[@]}"; do
      if download_file $file_type $date; then
        downloaded_count=$((downloaded_count + 1))
        
        # 十分なファイルがダウンロードできたら終了
        if [ $downloaded_count -ge 10 ]; then
          break 2
        fi
      fi
      
      # レート制限
      sleep 1
    done
  done
  
  echo "🎯 ダウンロード完了: ${downloaded_count}ファイル"
  
  # ダウンロードしたファイルを確認
  echo "📁 ダウンロードしたファイル:"
  find ${DOWNLOAD_FILE_OUTPUT_DIRECTORY} -name "*.lzh" -o -name "*.txt" | head -10
  
  return 0
}

main "$@"