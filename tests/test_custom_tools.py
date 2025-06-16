#!/usr/bin/env python3
"""
カスタムツールのテスト
"""
import sys
import os

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from custom_tools import generate_hash, json_formatter, text_analyzer


def test_custom_tools():
    print("カスタムツールをテスト中...")
    
    # generate_hashのテスト
    print("\n1. generate_hashのテスト:")
    text = "Hello, World!"
    for algo in ["sha256", "md5"]:
        result = generate_hash(text, algo)
        print(f"   {algo}: {result}")
    
    # json_formatterのテスト
    print("\n2. json_formatterのテスト:")
    json_str = '{"name":"テスト","value":123,"items":["a","b","c"]}'
    formatted = json_formatter(json_str)
    print("   整形前:", json_str)
    print("   整形後:")
    print("   " + formatted.replace("\n", "\n   "))
    
    # text_analyzerのテスト
    print("\n3. text_analyzerのテスト:")
    sample_text = """Hello World!
これはテストテキストです。
漢字、ひらがな、カタカナ、ABC123が含まれています。"""
    analysis = text_analyzer(sample_text)
    print(f"   分析結果: {analysis}")
    
    print("\n✅ カスタムツールのテストが完了しました！")


if __name__ == "__main__":
    test_custom_tools()