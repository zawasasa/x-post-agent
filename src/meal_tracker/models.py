"""食事記録のデータモデル"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Meal:
    """食事記録を表すデータクラス"""

    id: str
    datetime: str  # ISO 8601形式
    meal_type: str  # "breakfast", "lunch", "dinner", "snack"
    menu_items: List[str]  # メニュー項目のリスト
    categories: List[str]  # カテゴリー（和食、洋食、中華など）
    tags: List[str]  # タグ（ヘルシー、高タンパクなど）
    calories: Optional[int] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Meal':
        """辞書から Meal オブジェクトを生成"""
        return cls(**data)

    @classmethod
    def create_new(
        cls,
        meal_type: str,
        menu_items: List[str],
        categories: List[str],
        tags: List[str] = None,
        calories: Optional[int] = None,
        notes: Optional[str] = None
    ) -> 'Meal':
        """新しい食事記録を作成"""
        from uuid import uuid4

        return cls(
            id=str(uuid4()),
            datetime=datetime.now().isoformat(),
            meal_type=meal_type,
            menu_items=menu_items,
            categories=categories,
            tags=tags or [],
            calories=calories,
            notes=notes
        )


@dataclass
class MealRecommendation:
    """メニュー提案を表すデータクラス"""

    recommended_items: List[str]
    categories: List[str]
    reason: str  # 提案理由
    nutritional_balance: Dict[str, str]  # 栄養バランスの説明
    confidence_score: float  # 提案の信頼度（0.0-1.0）

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return asdict(self)
