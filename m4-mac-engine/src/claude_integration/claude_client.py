"""
Claude統合クライアント - API不使用版
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from loguru import logger

from config import config

class ClaudeClient:
    """Claude統合クライアント（API不使用・直接実行版）"""
    
    def __init__(self):
        self.use_direct_mode = config.use_live_claude
        logger.info("Claude直接実行モードで初期化")
        
    async def analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンス分析と改善提案（直接実行版）"""
        try:
            if self.use_direct_mode:
                # Claude Code環境での直接分析
                suggestions = self._direct_analysis(performance_data)
                logger.info(f"Claude直接分析完了: {len(suggestions.get('recommendations', []))}件の提案")
                return suggestions
            else:
                # フォールバック（API使用しない）
                return self._fallback_suggestions(performance_data)
            
        except Exception as e:
            logger.error(f"Claude分析エラー: {e}")
            return self._fallback_suggestions(performance_data)
    
    def _direct_analysis(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Claude Code環境での直接分析"""
        current_rate = performance_data.get('return_rate', 0)
        target_rate = config.target_return_rate
        gap = target_rate - current_rate
        
        # 直接的な分析ロジック
        analysis = {
            "analysis": {
                "current_status": f"現在還元率{current_rate:.1%}、目標{target_rate:.0%}との差{gap:.1%}",
                "strengths": ["継続的な学習サイクル", "データ取得の自動化"],
                "weaknesses": []
            },
            "recommendations": [],
            "new_features": [],
            "model_params": {}
        }
        
        # ギャップに応じた推奨事項
        if gap > 0.1:  # 10%以上のギャップ
            analysis["analysis"]["weaknesses"].extend([
                "予測精度の不足", "特徴量の活用不足", "モデルの単純さ"
            ])
            analysis["recommendations"].extend([
                {
                    "category": "特徴量エンジニアリング",
                    "title": "高度な相互作用特徴量の追加",
                    "description": "IDM×騎手、調教師×距離など複合指標を生成",
                    "priority": "high",
                    "implementation": "feature_engineering"
                },
                {
                    "category": "モデル改善",
                    "title": "アンサンブル学習の導入",
                    "description": "複数モデルの組み合わせで予測精度向上",
                    "priority": "high",
                    "implementation": "model_enhancement"
                }
            ])
            analysis["new_features"].extend([
                "idm_jockey_synergy", "trainer_distance_expertise", "pace_scenario_fit"
            ])
            analysis["model_params"]["num_leaves"] = 47
            analysis["model_params"]["learning_rate"] = 0.06
            
        elif gap > 0.05:  # 5-10%のギャップ
            analysis["analysis"]["weaknesses"].extend([
                "パラメータ調整の余地", "ベッティング戦略の改善点"
            ])
            analysis["recommendations"].extend([
                {
                    "category": "ハイパーパラメータ最適化",
                    "title": "学習率とモデル複雑度の調整",
                    "description": "より積極的な学習とモデル表現力向上",
                    "priority": "medium",
                    "implementation": "parameter_tuning"
                },
                {
                    "category": "ベッティング戦略",
                    "title": "ケリー基準の最適化",
                    "description": "より積極的なベッティング戦略",
                    "priority": "medium",
                    "implementation": "betting_optimization"
                }
            ])
            analysis["model_params"]["learning_rate"] = min(
                config.model_params["learning_rate"] * 1.2, 0.08
            )
            
        else:  # 5%未満の微調整
            analysis["recommendations"].append({
                "category": "微調整",
                "title": "閾値とリスク管理の最適化",
                "description": "細かな調整で安定性向上",
                "priority": "low",
                "implementation": "fine_tuning"
            })
        
        return analysis
    
    def _create_analysis_prompt(self, performance_data: Dict[str, Any]) -> str:
        """分析プロンプト作成"""
        return f"""
        競馬予測システムの現在のパフォーマンスを分析し、改善案を提案してください。

        ## 現在の指標
        - 還元率: {performance_data.get('return_rate', 0):.1%}
        - サイクル数: {performance_data.get('cycle_count', 0)}
        - 目標還元率: 80%

        ## 直近のパフォーマンス履歴
        {json.dumps(performance_data.get('history', []), ensure_ascii=False, indent=2)}

        ## 現在使用中の特徴量
        {performance_data.get('current_features', [])}

        ## 分析要求
        以下の観点から具体的な改善案を提案してください：

        1. **特徴量エンジニアリング**
           - 新しい特徴量の提案
           - 既存特徴量の組み合わせ
           - 外部要因の活用

        2. **モデル最適化**
           - ハイパーパラメータ調整
           - アンサンブル手法
           - 正則化戦略

        3. **ベッティング戦略**
           - ケリー基準の調整
           - リスク管理の改善
           - 期待値閾値の最適化

        4. **データ活用**
           - 追加データソースの提案
           - データ前処理の改善

        ## 回答形式
        JSON形式で以下の構造で回答してください：
        ```json
        {{
            "analysis": {{
                "current_status": "現状分析",
                "strengths": ["強み1", "強み2"],
                "weaknesses": ["弱み1", "弱み2"]
            }},
            "recommendations": [
                {{
                    "category": "特徴量エンジニアリング",
                    "title": "提案タイトル",
                    "description": "詳細説明",
                    "priority": "high|medium|low",
                    "implementation": "実装方法"
                }}
            ],
            "new_features": [
                "新特徴量名1",
                "新特徴量名2"
            ],
            "model_params": {{
                "learning_rate": 0.05,
                "num_leaves": 31
            }}
        }}
        ```
        """
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Claude応答の解析"""
        try:
            # JSONブロックを抽出
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                # JSONブロックがない場合、全体をJSONとして解析を試行
                return json.loads(response_text)
                
        except json.JSONDecodeError:
            logger.warning("Claude応答のJSON解析に失敗、テキスト解析に切り替え")
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """テキスト応答の簡易解析"""
        suggestions = {
            "analysis": {
                "current_status": "Claude応答の自動解析",
                "strengths": ["既存システムの安定性"],
                "weaknesses": ["応答形式の解析困難"]
            },
            "recommendations": [],
            "new_features": [],
            "model_params": {}
        }
        
        # キーワードベースの簡易解析
        lines = response_text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            
            # 特徴量の抽出
            if '特徴量' in line and any(keyword in line for keyword in ['新しい', '追加', '提案']):
                # 簡易的な特徴量名抽出
                if 'interaction' in line.lower():
                    suggestions["new_features"].append("interaction_feature")
                if '時系列' in line:
                    suggestions["new_features"].append("time_series_feature")
            
            # 推奨事項の抽出
            if any(keyword in line for keyword in ['推奨', '提案', '改善']):
                suggestions["recommendations"].append({
                    "category": "general",
                    "title": "Claude提案",
                    "description": line,
                    "priority": "medium",
                    "implementation": "手動実装が必要"
                })
        
        return suggestions
    
    def _fallback_suggestions(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """フォールバック提案（Claude API失敗時）"""
        current_return_rate = performance_data.get('return_rate', 0)
        
        suggestions = {
            "analysis": {
                "current_status": "システム自動分析",
                "strengths": ["継続的な学習サイクル", "データ取得の自動化"],
                "weaknesses": []
            },
            "recommendations": [],
            "new_features": [],
            "model_params": {}
        }
        
        # 還元率に基づく改善提案
        if current_return_rate < 0.75:
            suggestions["recommendations"].append({
                "category": "モデル改善",
                "title": "特徴量の追加",
                "description": "相互作用特徴量とトレンド特徴量を追加",
                "priority": "high",
                "implementation": "feature_engineering"
            })
            suggestions["new_features"].extend([
                "idm_jockey_interaction",
                "recent_form_trend"
            ])
        
        elif current_return_rate < 0.80:
            suggestions["recommendations"].append({
                "category": "ベッティング最適化",
                "title": "ケリー係数の調整",
                "description": "よりアグレッシブなベッティング戦略",
                "priority": "medium",
                "implementation": "betting_optimization"
            })
            suggestions["model_params"]["kelly_fraction"] = 0.3
        
        else:
            suggestions["recommendations"].append({
                "category": "維持",
                "title": "現状維持",
                "description": "良好なパフォーマンスを維持",
                "priority": "low",
                "implementation": "monitor"
            })
        
        return suggestions
    
    async def generate_feature_ideas(self, sample_data: Dict[str, Any]) -> List[str]:
        """新しい特徴量のアイデア生成"""
        try:
            prompt = f"""
            競馬予測のための新しい特徴量を提案してください。

            現在のデータサンプル:
            {json.dumps(sample_data, ensure_ascii=False, indent=2)[:1000]}...

            以下の観点から実装可能な特徴量を5-10個提案してください：
            1. 相互作用特徴量（既存特徴量の組み合わせ）
            2. 時系列特徴量（トレンド、移動平均など）
            3. 統計特徴量（順位、偏差値など）
            4. 外部要因（天候、馬場状態との組み合わせ）

            各特徴量について、名前と簡単な計算方法を提示してください。
            """
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-haiku-20240307",  # 軽量モデルを使用
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            # 特徴量名を抽出
            feature_names = self._extract_feature_names(response.content[0].text)
            
            logger.info(f"Claude特徴量提案: {len(feature_names)}件")
            return feature_names
            
        except Exception as e:
            logger.error(f"特徴量生成エラー: {e}")
            return self._default_feature_ideas()
    
    def _extract_feature_names(self, response_text: str) -> List[str]:
        """応答から特徴量名を抽出"""
        feature_names = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # 特徴量名らしい行を抽出
            if any(keyword in line.lower() for keyword in ['feature', '特徴量', '_index', '_ratio', '_score']):
                # 英数字とアンダースコアのみの名前を抽出
                import re
                matches = re.findall(r'[a-zA-Z][a-zA-Z0-9_]*', line)
                for match in matches:
                    if len(match) > 3 and '_' in match:
                        feature_names.append(match.lower())
        
        return list(set(feature_names))[:10]  # 重複除去、最大10個
    
    def _default_feature_ideas(self) -> List[str]:
        """デフォルト特徴量アイデア"""
        return [
            "idm_distance_interaction",
            "jockey_trainer_synergy",
            "recent_performance_trend",
            "track_condition_aptitude",
            "pace_scenario_fit",
            "weight_change_impact",
            "class_rise_adaptation",
            "seasonal_performance_index"
        ]