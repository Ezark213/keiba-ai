#!/bin/bash

# JRDB一括ダウンロードスクリプト
# 大量のJRDBデータを自動で取得

set -e

export JRDB_USER=25067698
export JRDB_PASSWORD=87086387
export DOWNLOAD_FILE_OUTPUT_DIRECTORY=/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine/data/jrdb_real/

JRDB_BASE_URL=http://www.jrdb.com/member/data/

echo "🏇 JRDB一括ダウンロード開始"
echo "="*50

# ダウンロード関数
download_file() {
    local filetype=$1
    local date=$2
    
    local filename="${filetype^^}${date}.lzh"
    local url="${JRDB_BASE_URL}${filetype}/${filename}"
    local output_path="${DOWNLOAD_FILE_OUTPUT_DIRECTORY}${filename}"
    
    echo "📥 ダウンロード試行: $filename"
    
    # ファイル存在チェック
    status_code=$(curl -u ${JRDB_USER}:${JRDB_PASSWORD} "$url" -o /dev/null -w '%{http_code}\n' -s)
    
    if [ "$status_code" = "200" ]; then
        # ダウンロード実行
        curl -u ${JRDB_USER}:${JRDB_PASSWORD} "$url" -L -o "$output_path" -s
        
        if [ -f "$output_path" ]; then
            file_size=$(du -h "$output_path" | cut -f1)
            echo "✅ 成功: $filename ($file_size)"
            return 0
        else
            echo "❌ 失敗: $filename (ダウンロードエラー)"
            return 1
        fi
    else
        echo "⏭️  スキップ: $filename (ファイルなし)"
        return 1
    fi
}

# 日付生成関数（過去N日分）
generate_dates() {
    local days_back=$1
    local dates=()
    
    for i in $(seq 0 $days_back); do
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            date_str=$(date -v-${i}d '+%y%m%d')
        else
            # Linux
            date_str=$(date -d "${i} days ago" '+%y%m%d')
        fi
        dates+=($date_str)
    done
    
    echo "${dates[@]}"
}

# メイン一括ダウンロード
bulk_download() {
    echo "🎯 一括ダウンロード戦略:"
    echo "  - 対象期間: 過去90日間"
    echo "  - ファイルタイプ: SED, KYI, BAC, CYB, KAB"
    echo "  - 推定ファイル数: 最大450個"
    echo ""
    
    read -p "続行しますか？ (y/n): " confirm
    if [[ $confirm != "y" ]]; then
        echo "キャンセルしました"
        exit 0
    fi
    
    # ダウンロード統計
    total_attempts=0
    successful_downloads=0
    
    # ファイルタイプと優先度
    declare -A file_types=(
        ["sed"]="最重要"
        ["kyi"]="重要"
        ["bac"]="推奨"
        ["cyb"]="有用"
        ["kab"]="補完"
    )
    
    # 日付リスト生成（過去90日）
    dates=($(generate_dates 90))
    
    echo "📅 対象日付数: ${#dates[@]}日"
    echo ""
    
    # ファイルタイプごとにダウンロード
    for filetype in "${!file_types[@]}"; do
        echo "📊 ${filetype^^}ファイル（${file_types[$filetype]}）をダウンロード中..."
        
        type_success=0
        type_attempts=0
        
        for date in "${dates[@]}"; do
            if download_file "$filetype" "$date"; then
                type_success=$((type_success + 1))
                successful_downloads=$((successful_downloads + 1))
            fi
            
            type_attempts=$((type_attempts + 1))
            total_attempts=$((total_attempts + 1))
            
            # レート制限（サーバー負荷軽減）
            sleep 0.5
            
            # 進捗表示
            if [ $((type_attempts % 10)) -eq 0 ]; then
                echo "  📈 進捗: ${type_attempts}/${#dates[@]} (${type_success}個成功)"
            fi
            
            # 十分なファイルが取得できたら次のタイプへ
            if [ "$type_success" -ge 30 ]; then
                echo "  🎯 十分なデータを取得しました ($type_success個)"
                break
            fi
        done
        
        echo "  ✅ ${filetype^^}完了: ${type_success}個取得"
        echo ""
    done
    
    # 結果サマリー
    echo "="*50
    echo "🎉 一括ダウンロード完了"
    echo "="*50
    echo "📊 結果:"
    echo "  試行回数: $total_attempts"
    echo "  成功数: $successful_downloads"
    echo "  成功率: $(( successful_downloads * 100 / total_attempts ))%"
    
    # ダウンロードしたファイルを確認
    echo ""
    echo "📁 ダウンロードしたファイル:"
    find "${DOWNLOAD_FILE_OUTPUT_DIRECTORY}" -name "*.lzh" -exec basename {} \; | sort | head -20
    
    downloaded_count=$(find "${DOWNLOAD_FILE_OUTPUT_DIRECTORY}" -name "*.lzh" | wc -l)
    echo "  総ファイル数: ${downloaded_count}個"
    
    # 容量確認
    total_size=$(du -sh "${DOWNLOAD_FILE_OUTPUT_DIRECTORY}" | cut -f1)
    echo "  総容量: $total_size"
    
    if [ "$successful_downloads" -gt 20 ]; then
        echo ""
        echo "🚀 十分なデータが取得できました！"
        echo "💡 次のステップ:"
        echo "  1. python download_jrdb_data.py  # ファイル展開"
        echo "  2. make start-claude             # システム再起動"
        echo "  3. 大幅な性能向上を期待！"
    else
        echo ""
        echo "⚠️ データが不足しています。"
        echo "💡 手動ダウンロードも検討してください。"
    fi
}

# スマートダウンロード（重要ファイルのみ）
smart_download() {
    echo "🧠 スマートダウンロード（重要ファイルのみ）"
    echo "  - 対象: 過去30日の重要ファイル"
    echo "  - タイプ: SED, KYI, BAC"
    echo ""
    
    dates=($(generate_dates 30))
    successful_downloads=0
    
    for filetype in "sed" "kyi" "bac"; do
        echo "📊 ${filetype^^}ファイルダウンロード中..."
        
        for date in "${dates[@]}"; do
            if download_file "$filetype" "$date"; then
                successful_downloads=$((successful_downloads + 1))
            fi
            sleep 0.3
            
            # 各タイプ10個で十分
            if [ "$successful_downloads" -ge 10 ]; then
                break
            fi
        done
    done
    
    echo "✅ スマートダウンロード完了: ${successful_downloads}個"
}

# メニュー表示
echo "🎯 JRDBダウンロードオプション:"
echo "1. 一括ダウンロード（過去90日、全タイプ）"
echo "2. スマートダウンロード（過去30日、重要タイプのみ）"
echo "3. キャンセル"
echo ""

read -p "選択してください (1-3): " choice

case $choice in
    1)
        bulk_download
        ;;
    2)
        smart_download
        ;;
    3)
        echo "キャンセルしました"
        exit 0
        ;;
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac