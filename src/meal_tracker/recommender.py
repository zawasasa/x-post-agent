"""食事メニューの提案エンジン"""

import random
from typing import List, Dict
from datetime import datetime, timedelta

from .models import Meal, MealRecommendation
from .analyzer import MealAnalyzer


class MealRecommender:
    """食事メニューを提案するクラス"""

    # メニューのマスターデータ（実際のアプリでは外部ファイルやDBから読み込む）
    MENU_DATABASE = {
        "和食": [
            "焼き魚", "味噌汁", "納豆", "ご飯", "煮物", "刺身",
            "天ぷら", "すき焼き", "お茶漬け", "おにぎり", "そば", "うどん"
        ],
        "洋食": [
            "パスタ", "ピザ", "ハンバーグ", "ステーキ", "サラダ", "パン",
            "オムライス", "グラタン", "シチュー", "ローストチキン"
        ],
        "中華": [
            "チャーハン", "麻婆豆腐", "餃子", "ラーメン", "酢豚", "エビチリ",
            "青椒肉絲", "春巻き", "小籠包", "炒飯"
        ],
        "イタリアン": [
            "カルボナーラ", "ペペロンチーノ", "リゾット", "カプレーゼ",
            "ミネストローネ", "ラザニア"
        ],
        "エスニック": [
            "カレー", "タイカレー", "フォー", "ガパオライス", "トムヤムクン",
            "パッタイ", "ナシゴレン"
        ]
    }

    def __init__(self, meals: List[Meal]):
        self.meals = meals
        self.analyzer = MealAnalyzer(meals)

    def recommend_next_meal(self, meal_type: str = "lunch") -> MealRecommendation:
        """次の食事メニューを提案"""
        if not self.meals:
            return self._generate_default_recommendation(meal_type)

        # 傾向分析
        favorite_items = dict(self.analyzer.get_favorite_items())
        category_dist = self.analyzer.get_category_distribution()
        missing_categories = self.analyzer.get_missing_categories(recent_days=7)
        nutrition_balance = self.analyzer.get_nutrition_balance_status()

        # 提案戦略を決定
        recommended_category = self._select_recommended_category(
            category_dist, missing_categories
        )

        # メニューアイテムを選択
        recommended_items = self._select_menu_items(
            recommended_category, favorite_items
        )

        # 提案理由を生成
        reason = self._generate_reason(
            recommended_category, missing_categories, nutrition_balance
        )

        # 栄養バランスの説明
        nutritional_balance = self._generate_nutritional_advice(nutrition_balance)

        # 信頼度スコア
        confidence = self._calculate_confidence_score()

        return MealRecommendation(
            recommended_items=recommended_items,
            categories=[recommended_category],
            reason=reason,
            nutritional_balance=nutritional_balance,
            confidence_score=confidence
        )

    def _select_recommended_category(
        self, category_dist: Dict[str, int], missing_categories: List[str]
    ) -> str:
        """推奨カテゴリーを選択"""
        # 不足しているカテゴリーを優先
        if missing_categories:
            # ランダムに不足カテゴリーから選択
            return random.choice(missing_categories)

        # 最も少ないカテゴリーを選択（バランスを取る）
        if category_dist:
            sorted_categories = sorted(category_dist.items(), key=lambda x: x[1])
            return sorted_categories[0][0]

        # デフォルト
        return random.choice(list(self.MENU_DATABASE.keys()))

    def _select_menu_items(
        self, category: str, favorite_items: Dict[str, int]
    ) -> List[str]:
        """メニューアイテムを選択"""
        available_items = self.MENU_DATABASE.get(category, [])

        if not available_items:
            # カテゴリーがマスターにない場合、過去のアイテムから提案
            if favorite_items:
                return list(favorite_items.keys())[:3]
            return ["おすすめメニュー"]

        # 最近食べていないアイテムを優先
        recent_items = set()
        for meal in self.meals[-10:]:  # 最近10件
            recent_items.update(meal.menu_items)

        # まだ食べていないアイテムを探す
        unused_items = [item for item in available_items if item not in recent_items]

        if unused_items:
            # ランダムに2-3個選択
            count = min(3, len(unused_items))
            return random.sample(unused_items, count)
        else:
            # 全て食べている場合はランダム選択
            count = min(3, len(available_items))
            return random.sample(available_items, count)

    def _generate_reason(
        self,
        category: str,
        missing_categories: List[str],
        nutrition_balance: Dict[str, str]
    ) -> str:
        """提案理由を生成"""
        reasons = []

        if category in missing_categories:
            reasons.append(f"最近{category}を食べていないため、バランスを考慮しました。")

        # 栄養バランスの改善提案
        lacking_nutrition = [k for k, v in nutrition_balance.items() if v == "不足"]
        if lacking_nutrition:
            reasons.append(
                f"{', '.join(lacking_nutrition)}が不足気味です。"
            )

        if not reasons:
            reasons.append("食事の多様性を保つため、このカテゴリーをおすすめします。")

        return " ".join(reasons)

    def _generate_nutritional_advice(
        self, nutrition_balance: Dict[str, str]
    ) -> Dict[str, str]:
        """栄養バランスのアドバイスを生成"""
        advice = {}

        for nutrient, status in nutrition_balance.items():
            if status == "不足":
                advice[nutrient] = f"{nutrient}のメニューを増やしましょう"
            elif status == "やや不足":
                advice[nutrient] = f"{nutrient}も意識してみてください"
            else:
                advice[nutrient] = f"{nutrient}は十分摂取できています"

        return advice

    def _calculate_confidence_score(self) -> float:
        """提案の信頼度スコアを計算"""
        # データ量が多いほど信頼度が高い
        meal_count = len(self.meals)

        if meal_count == 0:
            return 0.3
        elif meal_count < 5:
            return 0.5
        elif meal_count < 10:
            return 0.7
        elif meal_count < 20:
            return 0.85
        else:
            return 0.95

    def _generate_default_recommendation(self, meal_type: str) -> MealRecommendation:
        """デフォルトの提案（データがない場合）"""
        category = random.choice(list(self.MENU_DATABASE.keys()))
        items = random.sample(self.MENU_DATABASE[category], 2)

        return MealRecommendation(
            recommended_items=items,
            categories=[category],
            reason="まだ記録がないため、バランスの良い食事から始めましょう。",
            nutritional_balance={
                "ヘルシー": "野菜を多めに摂りましょう",
                "高タンパク": "タンパク質も意識してください"
            },
            confidence_score=0.3
        )

    def get_weekly_meal_plan(self) -> Dict[str, List[str]]:
        """1週間分の食事プランを提案"""
        meal_types = ["breakfast", "lunch", "dinner"]
        weekly_plan = {}

        for day in range(1, 8):
            day_plan = []
            for meal_type in meal_types:
                recommendation = self.recommend_next_meal(meal_type)
                day_plan.append({
                    "meal_type": meal_type,
                    "items": recommendation.recommended_items,
                    "category": recommendation.categories[0]
                })
            weekly_plan[f"Day {day}"] = day_plan

        return weekly_plan
