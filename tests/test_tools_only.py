#!/usr/bin/env python3
"""
strands-agents-toolsのツールを直接テスト
各ツールの動作を個別に確認
"""
import sys
import os

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

# strands-agents-toolsからツールをインポート
from strands_tools import http_request  # http_requestはモジュール自体がツール
from strands_tools.calculator import calculator  # calculator関数をインポート
from strands_tools.current_time import current_time  # current_time関数をインポート


def test_tools():
    print("strands-agents-toolsをテスト中...")
    
    # calculatorをテスト
    print("\n1. calculatorのテスト:")
    try:
        result1 = calculator(expression="2 + 2")
        print(f"   2 + 2 = {result1['content'][0]['text']}")
        
        result2 = calculator(expression="sqrt(16)")
        print(f"   sqrt(16) = {result2['content'][0]['text']}")
        
        result3 = calculator(expression="sin(pi/2)")
        print(f"   sin(pi/2) = {result3['content'][0]['text']}")
    except Exception as e:
        print(f"   エラー: {e}")
    
    # current_timeをテスト
    print("\n2. current_timeのテスト:")
    try:
        # UTC時間
        utc_time = current_time()
        print(f"   UTC時間: {utc_time}")
        
        # 日本時間
        jst_time = current_time(timezone="Asia/Tokyo")
        print(f"   日本時間: {jst_time}")
        
        # 無効なタイムゾーン
        try:
            invalid_tz = current_time(timezone="Invalid/Zone")
            print(f"   無効なタイムゾーン: {invalid_tz}")
        except ValueError as ve:
            print(f"   無効なタイムゾーンエラー（期待通り）: {ve}")
    except Exception as e:
        print(f"   エラー: {e}")
    
    # http_requestをテスト（特殊なシグネチャのため簡易テスト）
    print("\n3. http_requestのテスト:")
    print("   注意: http_requestはToolUseオブジェクトが必要なため、シグネチャの確認のみ")
    print(f"   関数シグネチャ: {http_request.__name__}")
    print(f"   TOOL_SPEC存在: {hasattr(http_request, 'TOOL_SPEC')}")
    
    print("\n✅ strands-agents-toolsのテストが完了しました！")


if __name__ == "__main__":
    test_tools()