"""コマンドラインインターフェース"""

import sys
from typing import List

from .storage import MealStorage
from .models import Meal
from .analyzer import MealAnalyzer
from .recommender import MealRecommender


class MealTrackerCLI:
    """食事記録アプリのCLI"""

    def __init__(self):
        self.storage = MealStorage()

    def add_meal(self):
        """食事記録を追加"""
        print("\n=== 食事記録の追加 ===")

        # 食事タイプ
        print("\n食事タイプを選択してください:")
        print("1. 朝食 (breakfast)")
        print("2. 昼食 (lunch)")
        print("3. 夕食 (dinner)")
        print("4. 間食 (snack)")

        meal_type_map = {
            "1": "breakfast",
            "2": "lunch",
            "3": "dinner",
            "4": "snack"
        }

        choice = input("選択 (1-4): ").strip()
        meal_type = meal_type_map.get(choice, "lunch")

        # メニュー項目
        print("\nメニュー項目を入力してください（カンマ区切り）:")
        print("例: ご飯, 味噌汁, 焼き魚")
        menu_items_input = input("メニュー: ").strip()
        menu_items = [item.strip() for item in menu_items_input.split(",")]

        # カテゴリー
        print("\nカテゴリーを入力してください（カンマ区切り）:")
        print("例: 和食, ヘルシー")
        categories_input = input("カテゴリー: ").strip()
        categories = [cat.strip() for cat in categories_input.split(",")]

        # タグ（オプション）
        print("\nタグを入力してください（オプション、カンマ区切り）:")
        print("例: ヘルシー, 高タンパク, 野菜多め")
        tags_input = input("タグ (Enterでスキップ): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

        # カロリー（オプション）
        calories_input = input("\nカロリー (Enterでスキップ): ").strip()
        calories = int(calories_input) if calories_input.isdigit() else None

        # メモ（オプション）
        notes = input("\nメモ (Enterでスキップ): ").strip() or None

        # 食事記録を作成
        meal = Meal.create_new(
            meal_type=meal_type,
            menu_items=menu_items,
            categories=categories,
            tags=tags,
            calories=calories,
            notes=notes
        )

        # 保存
        if self.storage.save_meal(meal):
            print("\n✓ 食事記録を保存しました！")
            print(f"  ID: {meal.id}")
            print(f"  メニュー: {', '.join(meal.menu_items)}")
        else:
            print("\n✗ 保存に失敗しました。")

    def view_recent_meals(self):
        """最近の食事記録を表示"""
        print("\n=== 最近の食事記録 ===")

        meals = self.storage.get_recent_meals(limit=10)

        if not meals:
            print("まだ記録がありません。")
            return

        for i, meal in enumerate(meals, 1):
            print(f"\n{i}. [{meal.meal_type}] {meal.datetime[:10]}")
            print(f"   メニュー: {', '.join(meal.menu_items)}")
            print(f"   カテゴリー: {', '.join(meal.categories)}")
            if meal.tags:
                print(f"   タグ: {', '.join(meal.tags)}")
            if meal.calories:
                print(f"   カロリー: {meal.calories}kcal")

    def analyze_trends(self):
        """傾向を分析"""
        print("\n=== 食事傾向の分析 ===")

        meals = self.storage.load_all_meals()

        if not meals:
            print("まだ記録がありません。")
            return

        analyzer = MealAnalyzer(meals)
        stats = analyzer.get_summary_statistics()

        print(f"\n総記録数: {stats['total_records']}件")
        print(f"多様性スコア: {stats['variety_score']} (0.0-1.0)")

        print("\n【よく食べるメニュー TOP5】")
        for item, count in stats['favorite_items']:
            print(f"  - {item}: {count}回")

        print("\n【カテゴリー別分布】")
        for category, count in stats['category_distribution'].items():
            print(f"  - {category}: {count}回")

        print("\n【食事タイプ別】")
        for meal_type, count in stats['meal_type_distribution'].items():
            print(f"  - {meal_type}: {count}回")

        if stats['missing_categories']:
            print("\n【最近不足しているカテゴリー】")
            for category in stats['missing_categories']:
                print(f"  - {category}")

        print("\n【栄養バランス状態】")
        for nutrient, status in stats['nutrition_balance'].items():
            print(f"  - {nutrient}: {status}")

    def recommend_meal(self):
        """メニューを提案"""
        print("\n=== 次の食事メニュー提案 ===")

        meals = self.storage.load_all_meals()
        recommender = MealRecommender(meals)

        print("\n食事タイプを選択してください:")
        print("1. 朝食 (breakfast)")
        print("2. 昼食 (lunch)")
        print("3. 夕食 (dinner)")

        meal_type_map = {
            "1": "breakfast",
            "2": "lunch",
            "3": "dinner"
        }

        choice = input("選択 (1-3): ").strip()
        meal_type = meal_type_map.get(choice, "lunch")

        recommendation = recommender.recommend_next_meal(meal_type)

        print(f"\n【おすすめメニュー】")
        print(f"カテゴリー: {', '.join(recommendation.categories)}")
        print(f"\nメニュー:")
        for item in recommendation.recommended_items:
            print(f"  - {item}")

        print(f"\n【提案理由】")
        print(f"  {recommendation.reason}")

        print(f"\n【栄養バランスアドバイス】")
        for nutrient, advice in recommendation.nutritional_balance.items():
            print(f"  - {advice}")

        print(f"\n信頼度スコア: {recommendation.confidence_score:.2f}")

    def show_menu(self):
        """メニューを表示"""
        print("\n" + "=" * 50)
        print("  食事メニュー分析・提案アプリ")
        print("=" * 50)
        print("\n1. 食事記録を追加")
        print("2. 最近の食事記録を表示")
        print("3. 傾向を分析")
        print("4. メニューを提案")
        print("5. 終了")
        print()

    def run(self):
        """アプリを実行"""
        print("食事メニュー分析・提案アプリへようこそ！")

        while True:
            self.show_menu()

            choice = input("選択してください (1-5): ").strip()

            if choice == "1":
                self.add_meal()
            elif choice == "2":
                self.view_recent_meals()
            elif choice == "3":
                self.analyze_trends()
            elif choice == "4":
                self.recommend_meal()
            elif choice == "5":
                print("\nありがとうございました！")
                sys.exit(0)
            else:
                print("\n無効な選択です。1-5を入力してください。")

            input("\nEnterキーを押して続ける...")


def main():
    """エントリーポイント"""
    cli = MealTrackerCLI()
    cli.run()


if __name__ == "__main__":
    main()
