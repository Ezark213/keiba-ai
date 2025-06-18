# 具体的な特徴量エンジニアリング実装
import numpy as np
from typing import Dict, List
from .base import FeatureEngineer


class IDMDistanceFeature(FeatureEngineer):
    """IDMと距離適性の相互作用特徴量"""
    
    @property
    def name(self) -> str:
        return "idm_distance"
    
    @property
    def description(self) -> str:
        return "IDMと距離適性の相互作用特徴量"
    
    def get_feature_names(self) -> List[str]:
        return [
            'idm_distance_interaction',
            'idm_normalized',
            'distance_aptitude_normalized'
        ]
    
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        idm = horse_data.get('idm', 50.0)
        distance_aptitude = horse_data.get('distance_aptitude', 1.0)
        
        # IDMの正規化 (30-80の範囲を0-1に)
        idm_normalized = max(0, min(1, (idm - 30) / 50))
        
        # 距離適性の正規化
        distance_normalized = max(0, min(2, distance_aptitude))
        
        return {
            'idm_distance_interaction': idm_normalized * distance_normalized,
            'idm_normalized': idm_normalized,
            'distance_aptitude_normalized': distance_normalized
        }


class JockeyInteractionFeature(FeatureEngineer):
    """騎手関連の相互作用特徴量"""
    
    @property
    def name(self) -> str:
        return "jockey_interaction"
    
    def get_feature_names(self) -> List[str]:
        return [
            'jockey_horse_synergy',
            'jockey_class_compatibility',
            'jockey_weight_efficiency'
        ]
    
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        jockey_index = horse_data.get('jockey_index', 50.0)
        horse_class = race_data.get('class', 3)  # クラス (1-6)
        weight = horse_data.get('weight', 55.0)
        
        # 騎手と馬のシナジー
        horse_ability = horse_data.get('idm', 50.0)
        synergy = (jockey_index / 100) * (horse_ability / 100)
        
        # 騎手のクラス適性 (高いクラスほど難しい)
        class_compatibility = jockey_index / (horse_class * 10 + 40)
        
        # 重量効率性
        weight_efficiency = jockey_index / max(50, weight)
        
        return {
            'jockey_horse_synergy': synergy,
            'jockey_class_compatibility': class_compatibility,
            'jockey_weight_efficiency': weight_efficiency
        }


class TimeFormFeature(FeatureEngineer):
    """タイム・フォーム関連特徴量"""
    
    @property
    def name(self) -> str:
        return "time_form"
    
    def get_feature_names(self) -> List[str]:
        return [
            'recent_form_trend',
            'time_consistency',
            'pace_adaptability'
        ]
    
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        # 最近のタイム指数（模擬データ）
        recent_times = horse_data.get('recent_time_indices', [50.0, 52.0, 48.0])
        
        # フォームトレンド（最近3走の改善傾向）
        if len(recent_times) >= 2:
            trend = np.mean(np.diff(recent_times))
        else:
            trend = 0.0
        
        # タイムの一貫性（標準偏差の逆数）
        if len(recent_times) > 1:
            consistency = 1.0 / (np.std(recent_times) + 1.0)
        else:
            consistency = 0.5
        
        # ペース適応性（距離とタイムの関係）
        distance = race_data.get('distance', 1600)
        avg_time = np.mean(recent_times) if recent_times else 50.0
        pace_adaptability = avg_time / np.sqrt(distance / 1000)
        
        return {
            'recent_form_trend': trend,
            'time_consistency': consistency,
            'pace_adaptability': pace_adaptability
        }


class WeightAdjustmentFeature(FeatureEngineer):
    """重量調整関連特徴量"""
    
    @property
    def name(self) -> str:
        return "weight_adjustment"
    
    def get_feature_names(self) -> List[str]:
        return [
            'weight_burden_ratio',
            'weight_change_impact',
            'optimal_weight_deviation'
        ]
    
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        current_weight = horse_data.get('weight', 55.0)
        horse_size = horse_data.get('horse_weight', 480.0)  # 馬体重
        previous_weight = horse_data.get('previous_weight', current_weight)
        
        # 重量負担比率
        burden_ratio = current_weight / horse_size * 1000  # パーセンテージ調整
        
        # 重量変化の影響
        weight_change = current_weight - previous_weight
        change_impact = abs(weight_change) * 0.1  # 重量変化1kgあたり0.1ポイント影響
        
        # 最適重量からの偏差（理想重量を馬体重の12%と仮定）
        optimal_weight = horse_size * 0.12
        deviation = abs(current_weight - optimal_weight) / optimal_weight
        
        return {
            'weight_burden_ratio': burden_ratio,
            'weight_change_impact': change_impact,
            'optimal_weight_deviation': deviation
        }


class RaceConditionFeature(FeatureEngineer):
    """レース条件関連特徴量"""
    
    @property
    def name(self) -> str:
        return "race_condition"
    
    def get_feature_names(self) -> List[str]:
        return [
            'track_condition_suitability',
            'distance_experience',
            'field_size_impact',
            'class_step_adjustment'
        ]
    
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        # 馬場状態適性
        track_condition = race_data.get('track_condition', 'good')
        horse_track_preference = horse_data.get('track_preferences', {})
        
        condition_mapping = {'heavy': 0.2, 'muddy': 0.4, 'good': 1.0, 'firm': 0.8}
        base_suitability = condition_mapping.get(track_condition, 0.5)
        
        # 馬の適性を反映
        preference_modifier = horse_track_preference.get(track_condition, 0.0)
        track_suitability = base_suitability * (1 + preference_modifier)
        
        # 距離経験
        race_distance = race_data.get('distance', 1600)
        experienced_distances = horse_data.get('experienced_distances', [])
        
        if experienced_distances:
            closest_distance = min(experienced_distances, 
                                 key=lambda x: abs(x - race_distance))
            distance_diff = abs(race_distance - closest_distance)
            distance_experience = max(0, 1 - distance_diff / 800)  # 800m差で半減
        else:
            distance_experience = 0.3  # 未経験は低い値
        
        # 頭数影響
        field_size = race_data.get('field_size', 16)
        # 大きなフィールドでは混戦度が高い
        field_impact = 1.0 / np.sqrt(field_size / 10)
        
        # クラス適応
        race_class = race_data.get('class', 3)
        horse_best_class = horse_data.get('best_class_performance', 3)
        class_step = race_class - horse_best_class
        class_adjustment = max(0.1, 1.0 - abs(class_step) * 0.2)
        
        return {
            'track_condition_suitability': track_suitability,
            'distance_experience': distance_experience,
            'field_size_impact': field_impact,
            'class_step_adjustment': class_adjustment
        }