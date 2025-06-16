#!/usr/bin/env python3
"""
Lambda関数のローカルテスト
注意: AWS Bedrockへのアクセス権限が必要です
"""
import json
import sys
import os

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from lambda_function import lambda_handler


def test_lambda_handler():
    """様々なプロンプトでLambdaハンドラーをテスト"""
    
    # テストケース
    test_cases = [
        {
            "name": "日付と計算のテスト",
            "event": {
                "body": json.dumps({
                    "prompt": "現在の日時を教えてください。また、25 * 4 の計算もお願いします。"
                })
            }
        },
        {
            "name": "複雑な計算テスト",
            "event": {
                "body": json.dumps({
                    "prompt": "144の平方根にsin(pi/2)を加えた値を計算してください"
                })
            }
        },
        {
            "name": "HTTPリクエストテスト（モック）",
            "event": {
                "body": json.dumps({
                    "prompt": "https://httpbin.org/getにGETリクエストを送信してください"
                })
            }
        },
        {
            "name": "プロンプトなしテスト",
            "event": {
                "body": json.dumps({})
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"テスト: {test['name']}")
        print(f"{'='*60}")
        
        result = lambda_handler(test['event'], None)
        
        print(f"ステータスコード: {result['statusCode']}")
        print(f"レスポンス: {json.dumps(json.loads(result['body']), indent=2)}")


if __name__ == "__main__":
    print("Lambda関数をローカルでテスト中...")
    test_lambda_handler()