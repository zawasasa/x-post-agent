#!/usr/bin/env python3
"""食事メニュー分析・提案アプリのエントリーポイント"""

import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from meal_tracker.cli import main

if __name__ == "__main__":
    main()
