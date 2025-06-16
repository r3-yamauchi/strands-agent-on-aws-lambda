"""
ユーティリティ関数とヘルパー
"""
import io
import sys
import logging
import functools
import time
from typing import Any, Callable, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime


logger = logging.getLogger(__name__)


@contextmanager
def capture_stdout():
    """標準出力を安全にキャプチャするコンテキストマネージャー"""
    old_stdout = sys.stdout
    captured_output = io.StringIO()
    
    try:
        sys.stdout = captured_output
        yield captured_output
    finally:
        # 確実に標準出力を元に戻す
        sys.stdout = old_stdout


@contextmanager
def capture_all_output():
    """標準出力と標準エラー出力の両方をキャプチャ"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        yield stdout_capture, stderr_capture
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        try:
            stdout_capture.close()
            stderr_capture.close()
        except Exception:
            pass


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """例外発生時にリトライするデコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay_time = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay_time} seconds..."
                        )
                        time.sleep(delay_time)
                        delay_time *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def sanitize_error_message(error: Exception, include_type: bool = True) -> str:
    """エラーメッセージをサニタイズして安全に返す"""
    error_msg = str(error)
    
    # センシティブな情報をマスク
    sensitive_patterns = [
        r'arn:aws:[^:]+:[^:]+:[^:]+:[^/\s]+',  # AWS ARN
        r'AKIA[0-9A-Z]{16}',  # AWS Access Key
        r'[0-9a-zA-Z/+=]{40}',  # AWS Secret Key
    ]
    
    import re
    for pattern in sensitive_patterns:
        error_msg = re.sub(pattern, '***REDACTED***', error_msg)
    
    if include_type:
        return f"{type(error).__name__}: {error_msg}"
    return error_msg


def validate_prompt(prompt: str, max_length: int) -> Tuple[bool, Optional[str]]:
    """プロンプトのバリデーション"""
    if not prompt:
        return False, "プロンプトが提供されていません"
    
    if not isinstance(prompt, str):
        return False, "プロンプトは文字列である必要があります"
    
    if len(prompt) > max_length:
        return False, f"プロンプトが長すぎます（最大{max_length}文字）"
    
    # 危険な文字のチェック
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # スクリプトタグ
        r'javascript:',  # JavaScriptプロトコル
        r'data:text/html',  # データURI
    ]
    
    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, "プロンプトに許可されていない内容が含まれています"
    
    return True, None


def get_model_info(agent: Any, model_config: dict, default_model: str) -> str:
    """エージェントから使用モデル情報を安全に取得"""
    try:
        # エージェントのモデル属性を確認
        if hasattr(agent, 'model'):
            model = agent.model
            
            # よくある属性名をチェック
            for attr in ['model_id', '_model_id', 'id', '_id']:
                if hasattr(model, attr):
                    value = getattr(model, attr)
                    if value:
                        return str(value)
            
            # 文字列の場合
            if isinstance(model, str):
                return model
        
        # model_configから取得
        if 'model' in model_config:
            return model_config['model']
        
        # デフォルトを返す
        return default_model
        
    except Exception as e:
        logger.warning(f"Failed to get model info: {str(e)}")
        return default_model


def measure_execution_time(func: Callable) -> Callable:
    """関数の実行時間を測定するデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper


def format_response(
    success: bool,
    data: Optional[dict] = None,
    error: Optional[str] = None,
    status_code: int = 200
) -> dict:
    """統一されたレスポンス形式を生成"""
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'X-Response-Time': datetime.now().isoformat(),
        }
    }
    
    body = {'success': success}
    
    if data:
        body.update(data)
    
    if error:
        body['error'] = error
    
    import json
    response['body'] = json.dumps(body, ensure_ascii=False)
    
    return response