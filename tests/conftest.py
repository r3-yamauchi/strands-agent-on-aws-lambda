"""
pytest設定とフィクスチャ
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
import json

# Lambda関数のパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))


@pytest.fixture
def mock_agent():
    """Strands Agentのモック"""
    mock = Mock()
    mock.return_value = "Mocked response"
    mock.model = Mock(model_id="test-model-id")
    return mock


@pytest.fixture
def lambda_event():
    """Lambda関数のテストイベント"""
    return {
        "body": json.dumps({
            "prompt": "Test prompt",
            "model_config": {
                "temperature": 0.7
            }
        })
    }


@pytest.fixture
def lambda_context():
    """Lambda実行コンテキストのモック"""
    context = Mock()
    context.function_name = "test-function"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789:function:test"
    context.memory_limit_in_mb = "1024"
    context.aws_request_id = "test-request-id"
    context.log_group_name = "/aws/lambda/test-function"
    context.log_stream_name = "test-stream"
    context.get_remaining_time_in_millis = Mock(return_value=300000)
    return context


@pytest.fixture
def mock_bedrock_response():
    """Bedrockレスポンスのモック"""
    return {
        "response": "これはモックされたBedrockの応答です。",
        "model": "us.amazon.nova-pro-v1:0",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20
        }
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """テスト環境のセットアップ"""
    # 環境変数の設定
    test_env = {
        "DEFAULT_MODEL_ID": "test-model",
        "MAX_PROMPT_LENGTH": "1000",
        "DEFAULT_TIMEOUT": "30",
        "PYTHONPATH": "/opt/python",
        "AWS_REGION": "us-east-1",
        "LOG_LEVEL": "DEBUG"
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def captured_logs(caplog):
    """ログキャプチャヘルパー"""
    import logging
    caplog.set_level(logging.INFO)
    return caplog


# マーカーの定義
def pytest_configure(config):
    config.addinivalue_line(
        "markers", 
        "integration: mark test as integration test (requires AWS credentials)"
    )
    config.addinivalue_line(
        "markers", 
        "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", 
        "slow: mark test as slow running"
    )


# テストセッションのセットアップ
def pytest_sessionstart(session):
    """テストセッション開始時の処理"""
    print("\n🧪 Strands Agent Lambda テストスイート開始\n")


def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時の処理"""
    print("\n✅ テストスイート完了\n")