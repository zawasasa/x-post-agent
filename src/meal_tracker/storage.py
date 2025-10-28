"""食事記録のストレージ管理"""

import json
import os
from typing import List, Optional
from pathlib import Path

from .models import Meal


class MealStorage:
    """食事記録をJSONファイルで管理するクラス"""

    def __init__(self, data_file: str = "data/meals.json"):
        self.data_file = Path(data_file)
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """データディレクトリが存在することを確認"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("[]")

    def save_meal(self, meal: Meal) -> bool:
        """食事記録を保存"""
        try:
            meals = self.load_all_meals()
            meals.append(meal)
            self._write_meals(meals)
            return True
        except Exception as e:
            print(f"Error saving meal: {e}")
            return False

    def load_all_meals(self) -> List[Meal]:
        """全ての食事記録を読み込み"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Meal.from_dict(meal_data) for meal_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_meal_by_id(self, meal_id: str) -> Optional[Meal]:
        """IDで食事記録を検索"""
        meals = self.load_all_meals()
        for meal in meals:
            if meal.id == meal_id:
                return meal
        return None

    def get_recent_meals(self, limit: int = 10) -> List[Meal]:
        """最近の食事記録を取得"""
        meals = self.load_all_meals()
        # datetimeでソート（新しい順）
        sorted_meals = sorted(meals, key=lambda m: m.datetime, reverse=True)
        return sorted_meals[:limit]

    def get_meals_by_type(self, meal_type: str) -> List[Meal]:
        """食事タイプで絞り込み"""
        meals = self.load_all_meals()
        return [meal for meal in meals if meal.meal_type == meal_type]

    def update_meal(self, meal: Meal) -> bool:
        """食事記録を更新"""
        try:
            meals = self.load_all_meals()
            updated_meals = [meal if m.id == meal.id else m for m in meals]
            self._write_meals(updated_meals)
            return True
        except Exception as e:
            print(f"Error updating meal: {e}")
            return False

    def delete_meal(self, meal_id: str) -> bool:
        """食事記録を削除"""
        try:
            meals = self.load_all_meals()
            filtered_meals = [m for m in meals if m.id != meal_id]
            self._write_meals(filtered_meals)
            return True
        except Exception as e:
            print(f"Error deleting meal: {e}")
            return False

    def _write_meals(self, meals: List[Meal]):
        """食事記録をファイルに書き込み"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            data = [meal.to_dict() for meal in meals]
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_total_count(self) -> int:
        """記録された食事の総数を取得"""
        return len(self.load_all_meals())
