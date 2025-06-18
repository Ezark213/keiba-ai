#!/bin/bash

# JRDBスマートダウンロード（簡略版）
export JRDB_USER=25067698
export JRDB_PASSWORD=87086387
export DOWNLOAD_FILE_OUTPUT_DIRECTORY=/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine/data/jrdb_real/

JRDB_BASE_URL=http://www.jrdb.com/member/data/

echo "🚀 JRDBスマートダウンロード開始"
echo "重要ファイルを自動取得します..."

download_file() {
    local filetype=$1
    local date=$2
    
    local filename_upper=$(echo "${filetype}" | tr '[:lower:]' '[:upper:]')
    local filename="${filename_upper}${date}.lzh"
    local url="${JRDB_BASE_URL}${filetype}/${filename}"
    local output_path="${DOWNLOAD_FILE_OUTPUT_DIRECTORY}${filename}"
    
    echo "📥 試行: $filename"
    
    status_code=$(curl -u ${JRDB_USER}:${JRDB_PASSWORD} "$url" -o /dev/null -w '%{http_code}\n' -s)
    
    if [ "$status_code" = "200" ]; then
        curl -u ${JRDB_USER}:${JRDB_PASSWORD} "$url" -L -o "$output_path" -s
        if [ -f "$output_path" ]; then
            echo "✅ 成功: $filename"
            return 0
        fi
    fi
    
    echo "⏭️  スキップ: $filename"
    return 1
}

# 重要な日付（2024年末のG1開催日）
important_dates=(
    "241229"  # 有馬記念
    "241228"  # ホープフルS
    "241222"  # 阪神カップ
    "241221"  # 朝日杯FS
    "241215"  # 中山大障害
    "241208"  # チャンピオンズC
    "241201"  # ジャパンカップ
    "241124"  # ジャパンカップダート
    "241117"  # エリザベス女王杯
    "241110"  # 天皇賞秋
)

successful_downloads=0
total_attempts=0

echo ""
echo "📊 重要データダウンロード中..."

for filetype in "sed" "kyi" "bac"; do
    echo ""
    echo "🎯 ${filetype} ファイルダウンロード..."
    
    type_success=0
    
    for date in "${important_dates[@]}"; do
        total_attempts=$((total_attempts + 1))
        
        if download_file "$filetype" "$date"; then
            type_success=$((type_success + 1))
            successful_downloads=$((successful_downloads + 1))
        fi
        
        # レート制限
        sleep 1
        
        # 各タイプ5個で十分
        if [ "$type_success" -ge 5 ]; then
            echo "  ✅ ${filetype} 完了: ${type_success}個取得"
            break
        fi
    done
done

echo ""
echo "="*50
echo "🎉 ダウンロード完了!"
echo "="*50
echo "📊 結果:"
echo "  成功: $successful_downloads ファイル"
echo "  試行: $total_attempts 回"

# ダウンロードしたファイルを確認
downloaded_files=$(find "${DOWNLOAD_FILE_OUTPUT_DIRECTORY}" -name "*.lzh" | wc -l | tr -d ' ')
echo "  総LZHファイル: ${downloaded_files}個"

if [ "$successful_downloads" -gt 0 ]; then
    echo ""
    echo "🚀 ダウンロードしたファイル:"
    find "${DOWNLOAD_FILE_OUTPUT_DIRECTORY}" -name "*.lzh" -exec basename {} \; | sort | head -10
    
    echo ""
    echo "💡 次のステップ:"
    echo "1. python download_jrdb_data.py  # ファイル展開"
    echo "2. システム性能の大幅向上を期待！"
else
    echo ""
    echo "⚠️ 新しいファイルはダウンロードできませんでした"
    echo "💡 手動ダウンロードを検討してください"
fi