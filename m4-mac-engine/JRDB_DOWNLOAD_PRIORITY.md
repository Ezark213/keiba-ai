# JRDBファイル手動ダウンロード優先順位

## 🎯 最優先ファイル（必須）

### 1. SED - 成績データ
**最重要** - レース結果、着順、オッズなど
```
SED241229.lzh (有馬記念)
SED241228.lzh
SED241222.lzh
SED241221.lzh
SED241215.lzh
SED241208.lzh
SED241201.lzh
SED241124.lzh
SED241117.lzh
SED241110.lzh
```

### 2. KYI - 競走馬データ
**重要** - 馬の基本情報、血統、成績
```
KYI241229.lzh
KYI241228.lzh
KYI241222.lzh
KYI241221.lzh
KYI241215.lzh
KYI241208.lzh
KYI241201.lzh
KYI241124.lzh
KYI241117.lzh
KYI241110.lzh
```

## 🔥 高優先ファイル

### 3. BAC - 番組データ
**重要** - レース条件、賞金、グレード
```
BAC241229.lzh
BAC241228.lzh
BAC241222.lzh
BAC241221.lzh
BAC241215.lzh
```

### 4. CYB - 調教データ
**有用** - 調教タイム、コース、評価
```
CYB241229.lzh
CYB241228.lzh
CYB241222.lzh
CYB241221.lzh
CYB241215.lzh
```

## 📈 追加推奨ファイル

### 5. KAB - 開催データ
**補完** - 天候、馬場状態、時刻
```
KAB241229.lzh
KAB241228.lzh
KAB241222.lzh
```

### 6. UKC - 馬基本データ
**補完** - 馬の詳細情報
```
UKC241229.lzh
UKC241228.lzh
```

## 🎯 ダウンロード戦略

### Phase 1: 最小構成（必須）
1. **SED** × 5-10ファイル（最新から）
2. **KYI** × 5-10ファイル（対応する日付）

**目標**: 3,000-5,000レースデータ確保

### Phase 2: 品質向上
3. **BAC** × 5ファイル
4. **CYB** × 5ファイル

**目標**: 予測精度向上

### Phase 3: 完全体
5. **KAB** × 3ファイル
6. **UKC** × 3ファイル

**目標**: 最高精度システム

## 📅 重要な日付（優先的にダウンロード）

### 2024年末（G1多数）
- **12/29**: 有馬記念（最重要）
- **12/28**: ホープフルS
- **12/22**: 阪神カップ
- **12/21**: 朝日杯FS

### 2024年秋（重賞多数）
- **12/15**: 中山大障害
- **12/08**: チャンピオンズC
- **12/01**: ジャパンカップ
- **11/24**: ジャパンカップダート

## 🔗 ダウンロードURL形式

JRDBメンバーページ:
```
https://www.jrdb.com/member/
```

ファイル直リンク例:
```
https://www.jrdb.com/member/data/sed/SED241229.lzh
https://www.jrdb.com/member/data/kyi/KYI241229.lzh
```

## 📁 保存先

ダウンロードしたファイルは以下に配置:
```
/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine/data/jrdb_real/
```

## ⚡ クイックスタート

**最速で効果を得たい場合:**
1. SED241229.lzh（有馬記念）
2. SED241222.lzh 
3. SED241215.lzh
4. KYI241229.lzh
5. KYI241222.lzh

これだけで大幅な予測精度向上が期待できます。

## 🎉 完了後

ダウンロード完了後：
```bash
python download_jrdb_data.py  # 自動展開・整理
```

システム再起動：
```bash
make start-claude
```

現在の還元率97.7%からさらなる向上が期待できます！