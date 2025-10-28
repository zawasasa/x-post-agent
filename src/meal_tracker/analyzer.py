"""食事記録の傾向分析"""

from typing import List, Dict, Tuple
from collections import Counter
from datetime import datetime, timedelta

from .models import Meal


class MealAnalyzer:
    """食事記録を分析するクラス"""

    def __init__(self, meals: List[Meal]):
        self.meals = meals

    def get_favorite_items(self, limit: int = 10) -> List[Tuple[str, int]]:
        """よく食べるメニュー項目を取得"""
        all_items = []
        for meal in self.meals:
            all_items.extend(meal.menu_items)

        item_counter = Counter(all_items)
        return item_counter.most_common(limit)

    def get_category_distribution(self) -> Dict[str, int]:
        """カテゴリー別の食事回数を取得"""
        all_categories = []
        for meal in self.meals:
            all_categories.extend(meal.categories)

        return dict(Counter(all_categories))

    def get_meal_type_distribution(self) -> Dict[str, int]:
        """食事タイプ別の回数を取得"""
        meal_types = [meal.meal_type for meal in self.meals]
        return dict(Counter(meal_types))

    def get_tag_frequency(self) -> Dict[str, int]:
        """タグの頻度を取得"""
        all_tags = []
        for meal in self.meals:
            all_tags.extend(meal.tags)

        return dict(Counter(all_tags))

    def get_recent_trends(self, days: int = 7) -> Dict[str, any]:
        """最近N日間の傾向を分析"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_meals = [
            meal for meal in self.meals
            if datetime.fromisoformat(meal.datetime) >= cutoff_date
        ]

        if not recent_meals:
            return {
                "total_meals": 0,
                "message": f"最近{days}日間の記録がありません"
            }

        analyzer = MealAnalyzer(recent_meals)

        return {
            "total_meals": len(recent_meals),
            "favorite_items": analyzer.get_favorite_items(5),
            "categories": analyzer.get_category_distribution(),
            "meal_types": analyzer.get_meal_type_distribution(),
            "tags": analyzer.get_tag_frequency()
        }

    def get_variety_score(self) -> float:
        """食事の多様性スコアを計算（0.0-1.0）"""
        if not self.meals:
            return 0.0

        all_items = []
        for meal in self.meals:
            all_items.extend(meal.menu_items)

        unique_items = len(set(all_items))
        total_items = len(all_items)

        if total_items == 0:
            return 0.0

        # 多様性スコア = ユニークアイテム数 / 総アイテム数
        return unique_items / total_items

    def get_missing_categories(self, recent_days: int = 7) -> List[str]:
        """最近不足しているカテゴリーを特定"""
        # 過去の全カテゴリーを取得
        all_categories = set()
        for meal in self.meals:
            all_categories.update(meal.categories)

        # 最近のカテゴリーを取得
        cutoff_date = datetime.now() - timedelta(days=recent_days)
        recent_categories = set()
        for meal in self.meals:
            if datetime.fromisoformat(meal.datetime) >= cutoff_date:
                recent_categories.update(meal.categories)

        # 不足しているカテゴリー
        missing = all_categories - recent_categories
        return list(missing)

    def get_nutrition_balance_status(self) -> Dict[str, str]:
        """栄養バランスの状態を推定（タグベース）"""
        recent_meals = self.meals[-14:] if len(self.meals) >= 14 else self.meals
        tag_freq = {}

        for meal in recent_meals:
            for tag in meal.tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1

        total_meals = len(recent_meals)
        balance_status = {}

        # タグの頻度から栄養バランスを推定
        nutrition_tags = {
            'ヘルシー': 0.3,
            '高タンパク': 0.25,
            '野菜多め': 0.4,
            '低カロリー': 0.2
        }

        for tag, ideal_ratio in nutrition_tags.items():
            if tag in tag_freq:
                actual_ratio = tag_freq[tag] / total_meals
                if actual_ratio >= ideal_ratio:
                    balance_status[tag] = "十分"
                elif actual_ratio >= ideal_ratio * 0.5:
                    balance_status[tag] = "やや不足"
                else:
                    balance_status[tag] = "不足"
            else:
                balance_status[tag] = "不足"

        return balance_status

    def get_summary_statistics(self) -> Dict[str, any]:
        """総合統計を取得"""
        if not self.meals:
            return {"message": "記録がありません"}

        return {
            "total_records": len(self.meals),
            "variety_score": round(self.get_variety_score(), 2),
            "favorite_items": self.get_favorite_items(5),
            "category_distribution": self.get_category_distribution(),
            "meal_type_distribution": self.get_meal_type_distribution(),
            "missing_categories": self.get_missing_categories(),
            "nutrition_balance": self.get_nutrition_balance_status()
        }
