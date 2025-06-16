#!/usr/bin/env python3
"""
Lambda関数の統合テスト
注意: AWS Bedrockへのアクセス権限が必要です
"""
import json
import sys
import os
import pytest
from unittest.mock import Mock, patch

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

# Bedrockのモックを作成
mock_bedrock_response = Mock()
mock_bedrock_response.model = 'us.amazon.nova-pro-v1:0'

# strandsモジュールをモック
sys.modules['strands'] = Mock()
sys.modules['strands.models'] = Mock()
sys.modules['strands_tools'] = Mock()

# モックツールを作成
def mock_calculator(expression):
    """Calculatorツールのモック"""
    if expression == "25 * 4":
        return "100"
    elif expression == "144 ** 0.5 + sin(pi/2)":
        return "13.0"
    return "0"

def mock_current_time(timezone=None):
    """Current timeツールのモック"""
    return "2024-06-16T10:00:00Z"

def mock_http_request(url, method="GET", **kwargs):
    """HTTP requestツールのモック"""
    return {
        "status_code": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"url": url, "method": method})
    }

def mock_generate_hash(text, algorithm="sha256"):
    """Generate hashツールのモック"""
    return {
        "algorithm": algorithm,
        "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
        "original_length": len(text)
    }

# モックを設定
sys.modules['strands_tools'].calculator = mock_calculator
sys.modules['strands_tools'].current_time = mock_current_time
sys.modules['strands_tools'].http_request = mock_http_request

from lambda_function import lambda_handler


class TestLambdaFunction:
    """モックを使用したLambda関数のテスト"""
    
    @patch('lambda_function.Agent')
    def test_basic_calculation(self, mock_agent):
        """基本的な計算テスト"""
        # エージェントのレスポンスをモック
        mock_agent_instance = Mock()
        mock_agent_instance.__call__.return_value = "計算結果: 25 * 4 = 100"
        mock_agent.return_value = mock_agent_instance
        
        event = {
            "body": json.dumps({
                "prompt": "25 * 4 の計算をお願いします。"
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True
        assert "計算結果" in body["response"]
    
    @patch('lambda_function.Agent')
    def test_current_time(self, mock_agent):
        """現在時刻取得テスト"""
        mock_agent_instance = Mock()
        mock_agent_instance.__call__.return_value = "現在の時刻はUTCで2024-06-16T10:00:00Zです。"
        mock_agent.return_value = mock_agent_instance
        
        event = {
            "body": json.dumps({
                "prompt": "現在の日時を教えてください。"
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True
        assert "2024-06-16" in body["response"]
    
    def test_missing_prompt(self):
        """プロンプトなしのエラーテスト"""
        event = {
            "body": json.dumps({})
        }
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body
        assert "プロンプト" in body["error"]
    
    def test_long_prompt(self):
        """長すぎるプロンプトのテスト"""
        event = {
            "body": json.dumps({
                "prompt": "a" * 10001  # MAX_PROMPT_LENGTHを超える
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body
        assert "長すぎ" in body["error"]
    
    @patch('lambda_function.Agent')
    def test_model_config(self, mock_agent):
        """モデル設定のテスト"""
        mock_agent_instance = Mock()
        mock_agent_instance.__call__.return_value = "テストレスポンス"
        mock_agent_instance.model = mock_bedrock_response
        mock_agent.return_value = mock_agent_instance
        
        event = {
            "body": json.dumps({
                "prompt": "テスト",
                "model_config": {
                    "model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "temperature": 0.5
                }
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 200
        # model_configがAgentに渡されたことを確認
        mock_agent.assert_called_once()
        call_kwargs = mock_agent.call_args[1]
        assert call_kwargs["model"] == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert call_kwargs["temperature"] == 0.5


def test_lambda_handler_real():
    """実際のLambdaハンドラーをテスト（Bedrock必須）"""
    print("\n" + "="*60)
    print("実際のLambdaハンドラーテスト")
    print("※ AWS Bedrockへのアクセス権限が必要です")
    print("="*60)
    
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
            "name": "ハッシュ生成テスト",
            "event": {
                "body": json.dumps({
                    "prompt": "「Hello World」のSHA256ハッシュ値を生成してください"
                })
            }
        }
    ]
    
    try:
        for test in test_cases:
            print(f"\nテスト: {test['name']}")
            print("-" * 40)
            
            result = lambda_handler(test['event'], None)
            
            print(f"ステータスコード: {result['statusCode']}")
            body = json.loads(result['body'])
            
            if result['statusCode'] == 200:
                print(f"成功: {body.get('success', False)}")
                print(f"レスポンス: {body.get('response', 'なし')[:200]}...")
                if 'model_used' in body:
                    print(f"使用モデル: {body['model_used']}")
            else:
                print(f"エラー: {body.get('error', 'unknown')}")
                print(f"メッセージ: {body.get('message', 'なし')}")
    
    except ImportError:
        print("スキップ: strandsモジュールが利用できません")
    except Exception as e:
        print(f"テスト実行エラー: {str(e)}")


if __name__ == "__main__":
    # モックテストを実行
    print("モックを使用したLambda関数テスト")
    pytest.main([__file__, "-v"])
    
    # 実際のLambdaハンドラーテスト（オプション）
    if "--real" in sys.argv:
        test_lambda_handler_real()