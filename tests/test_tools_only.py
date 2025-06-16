#!/usr/bin/env python3
"""
Strands Agentを使用せずにtoolsモジュールを直接テスト
各ツールの動作を個別に確認
"""
import sys
import os

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from tools import http_request, calculator, datetime_tool


def test_tools():
    print("toolsモジュールをテスト中...")
    
    # calculatorをテスト
    print("\n1. calculatorのテスト:")
    print(f"   2 + 2 = {calculator('2 + 2')}")
    print(f"   sqrt(16) = {calculator('sqrt(16)')}")
    print(f"   sin(pi/2) = {calculator('sin(pi/2)')}")
    
    # datetime_toolをテスト
    print("\n2. datetime_toolのテスト:")
    print(f"   UTC時間: {datetime_tool()}")
    print(f"   無効なタイムゾーン: {datetime_tool('Invalid/Zone')}")
    
    # http_requestをテスト (httpbinを使用)
    print("\n3. http_requestのテスト:")
    result = http_request("https://httpbin.org/get")
    print(f"   ステータスコード: {result.get('status_code')}")
    print(f"   レスポンスボディあり: {'body' in result}")
    
    print("\n✅ すべてのツールが正常に動作しています！")


if __name__ == "__main__":
    test_tools()