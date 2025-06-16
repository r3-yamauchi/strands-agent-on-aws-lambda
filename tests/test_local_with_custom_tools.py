#!/usr/bin/env python3
"""
カスタムツールを含むLambda関数のローカルテスト
注意: AWS Bedrockへのアクセス権限が必要です
"""
import json
import sys
import os

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from lambda_function import lambda_handler


def test_lambda_handler_with_custom_tools():
    """カスタムツールを使用したプロンプトでLambdaハンドラーをテスト"""
    
    # テストケース
    test_cases = [
        {
            "name": "ハッシュ生成テスト",
            "event": {
                "body": json.dumps({
                    "prompt": "「Hello World」のSHA256ハッシュ値を生成してください"
                })
            }
        },
        {
            "name": "JSON整形テスト",
            "event": {
                "body": json.dumps({
                    "prompt": '次のJSONを整形してください: {"name":"テスト","items":[1,2,3],"active":true}'
                })
            }
        },
        {
            "name": "テキスト分析テスト",
            "event": {
                "body": json.dumps({
                    "prompt": "「こんにちは世界！Hello World! 123」というテキストを分析してください"
                })
            }
        },
        {
            "name": "複合的なテスト",
            "event": {
                "body": json.dumps({
                    "prompt": "現在の時刻を取得し、その時刻文字列のMD5ハッシュを生成してください"
                })
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"テスト: {test['name']}")
        print(f"{'='*60}")
        
        try:
            result = lambda_handler(test['event'], None)
            
            print(f"ステータスコード: {result['statusCode']}")
            
            # レスポンスボディをパース
            body = json.loads(result['body'])
            
            if result['statusCode'] == 200:
                print(f"成功: {body.get('success', False)}")
                print(f"レスポンス: {body.get('response', 'なし')}")
                if 'model_used' in body:
                    print(f"使用モデル: {body['model_used']}")
            else:
                print(f"エラー: {body.get('error', 'unknown')}")
                print(f"メッセージ: {body.get('message', 'なし')}")
                
        except Exception as e:
            print(f"テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    print("カスタムツールを含むLambda関数をローカルでテスト中...")
    
    # Nova Proモデルを使用
    os.environ['DEFAULT_MODEL_ID'] = 'us.amazon.nova-pro-v1:0'
    
    test_lambda_handler_with_custom_tools()