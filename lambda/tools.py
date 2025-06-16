import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional, Union
import math
import re
from strands import tool


@tool
def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Union[str, Dict[str, Any]]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    外部APIに対してHTTPリクエストを実行します。
    
    Args:
        url: リクエストを送信するURL
        method: HTTPメソッド (GET, POST, PUT, DELETE など)
        headers: オプションのヘッダー辞書
        body: オプションのリクエストボディ (文字列またはJSON用の辞書)
        timeout: リクエストタイムアウト (秒)
        
    Returns:
        Dict[str, Any]: 以下のキーを含む辞書
            - status_code: HTTPステータスコード
            - headers: レスポンスヘッダー
            - body: レスポンスボディ
            - error: エラーメッセージ（エラー時のみ）
        
    Examples:
        >>> http_request("https://api.example.com/data")
        >>> http_request("https://api.example.com/create", method="POST", body={"key": "value"})
    """
    try:
        # ヘッダーを準備
        if headers is None:
            headers = {}
        
        # ボディのエンコーディングを処理
        data = None
        if body is not None:
            if isinstance(body, dict):
                data = json.dumps(body).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            else:
                data = body.encode('utf-8')
        
        # リクエストを作成
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        # リクエストを実行
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode('utf-8')
            
            # JSONレスポンスのパースを試みる
            try:
                response_data = json.loads(response_body)
            except json.JSONDecodeError:
                response_data = response_body
            
            return {
                'status_code': response.status,
                'headers': dict(response.headers),
                'body': response_data
            }
            
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'headers': dict(e.headers),
            'body': e.read().decode('utf-8'),
            'error': str(e)
        }
    except Exception as e:
        return {
            'error': f'リクエストが失敗しました: {str(e)}',
            'status_code': None
        }


@tool
def calculator(expression: str) -> Union[float, int, str]:
    """
    数式を安全に評価します。
    
    Args:
        expression: 評価する数式
        
    Returns:
        計算結果
        
    Examples:
        >>> calculator("2 + 2")
        4
        >>> calculator("sin(3.14159/2)")
        1.0
        >>> calculator("sqrt(16) + 3**2")
        13.0
    """
    try:
        # 安全な関数を定義
        safe_dict = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e
        }
        
        # 潜在的に危険な文字を削除
        if re.search(r'[^\d\+\-\*\/\(\)\.\s\w,]', expression):
            # 安全な文字と関数名のみを許可
            allowed_pattern = r'^[\d\+\-\*\/\(\)\.\s\w,]+$'
            if not re.match(allowed_pattern, expression):
                return f"エラー: 式に無効な文字が含まれています"
        
        # 式を評価
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # 結果をフォーマット
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result
        
    except ZeroDivisionError:
        return "エラー: ゼロ除算"
    except Exception as e:
        return f"エラー: {str(e)}"


@tool
def datetime_tool(timezone: Optional[str] = None) -> str:
    """
    現在の日時を取得します。
    
    Args:
        timezone: オプションのタイムゾーン名 (例: 'UTC', 'US/Eastern', 'Asia/Tokyo')
                 指定しない場合はUTC時間を返します
        
    Returns:
        ISO 8601形式の現在日時
        
    Examples:
        >>> datetime_tool()
        '2024-01-20T15:30:00+00:00'
        >>> datetime_tool("US/Pacific")
        '2024-01-20T07:30:00-08:00'
    """
    try:
        from zoneinfo import ZoneInfo
        
        # 現在時刻を取得
        if timezone:
            try:
                tz = ZoneInfo(timezone)
                now = datetime.now(tz)
            except Exception:
                # タイムゾーンが無効な場合はUTCにフォールバック
                from datetime import timezone as tz
                now = datetime.now(tz.utc)
                return f"無効なタイムゾーン '{timezone}' です。UTC時間を返します: {now.isoformat()}"
        else:
            from datetime import timezone as tz
            now = datetime.now(tz.utc)
            return now.isoformat()
        
        return now.isoformat()
        
    except ImportError:
        # Python < 3.9 でzoneinfoがない場合のフォールバック
        from datetime import timezone as tz
        now = datetime.now(tz.utc)
        return now.isoformat()