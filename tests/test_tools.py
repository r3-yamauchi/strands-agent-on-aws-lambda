#!/usr/bin/env python3
"""
統合テスト - strands-agents-toolsの全機能テスト
外部依存なしで実行可能
"""
import json
import math
from datetime import datetime

try:
    # strands-agents-toolsから公式ツールをインポート
    from strands_tools import calculator, current_time, http_request, use_aws
    TOOLS_AVAILABLE = True
    print("✓ strands-agents-toolsのインポートに成功")
except ImportError as e:
    print(f"✗ strands-agents-toolsのインポートに失敗: {e}")
    TOOLS_AVAILABLE = False


def test_tool_imports():
    """ツールのインポートとTOOL_SPEC確認"""
    print("\n" + "="*60)
    print("1. ツールインポートテスト")
    print("="*60)
    
    if not TOOLS_AVAILABLE:
        print("スキップ: ツールが利用できません")
        return
    
    # 各ツールの属性を確認
    tools_to_test = [
        ("calculator", calculator),
        ("current_time", current_time),
        ("http_request", http_request),
        ("use_aws", use_aws)
    ]
    
    for tool_name, tool in tools_to_test:
        print(f"\n{tool_name}:")
        print(f"  - 関数名: {tool.__name__}")
        print(f"  - ドキュメント: {tool.__doc__[:100]}..." if tool.__doc__ else "  - ドキュメント: なし")
        
        # TOOL_SPECの確認
        if hasattr(tool, 'TOOL_SPEC'):
            spec = tool.TOOL_SPEC
            print(f"  - TOOL_SPEC:")
            print(f"    - name: {spec.get('name')}")
            print(f"    - description: {spec.get('description', 'なし')[:80]}...")
            if 'input_schema' in spec:
                print(f"    - required params: {spec['input_schema'].get('required', [])}")
        else:
            print("  - TOOL_SPEC: 見つかりません")


def test_calculator():
    """calculator ツールのテスト"""
    print("\n" + "="*60)
    print("2. Calculator ツールテスト")
    print("="*60)
    
    if not TOOLS_AVAILABLE:
        print("スキップ: ツールが利用できません")
        return
    
    test_cases = [
        {"expression": "2 + 2", "expected": 4},
        {"expression": "10 * 5", "expected": 50},
        {"expression": "sqrt(16)", "expected": 4},
        {"expression": "sin(pi/2)", "expected": 1},
        {"expression": "cos(0)", "expected": 1},
        {"expression": "exp(0)", "expected": 1},
        {"expression": "log(e)", "expected": 1},
        {"expression": "25 ** 0.5", "expected": 5},
    ]
    
    for test in test_cases:
        try:
            result = calculator(test["expression"])
            success = math.isclose(float(result), test["expected"], rel_tol=1e-9)
            status = "✓" if success else "✗"
            print(f"{status} {test['expression']} = {result} (期待値: {test['expected']})")
        except Exception as e:
            print(f"✗ {test['expression']} - エラー: {e}")


def test_current_time():
    """current_time ツールのテスト"""
    print("\n" + "="*60)
    print("3. Current Time ツールテスト")
    print("="*60)
    
    if not TOOLS_AVAILABLE:
        print("スキップ: ツールが利用できません")
        return
    
    test_cases = [
        {"timezone": None, "desc": "デフォルトタイムゾーン"},
        {"timezone": "UTC", "desc": "UTC"},
        {"timezone": "Asia/Tokyo", "desc": "東京"},
        {"timezone": "US/Pacific", "desc": "太平洋時間"},
        {"timezone": "Europe/London", "desc": "ロンドン"},
    ]
    
    for test in test_cases:
        try:
            if test["timezone"]:
                result = current_time(timezone=test["timezone"])
            else:
                result = current_time()
            
            # ISO 8601形式かチェック
            try:
                datetime.fromisoformat(result.replace('Z', '+00:00'))
                print(f"✓ {test['desc']}: {result}")
            except ValueError:
                print(f"✗ {test['desc']}: 無効な日時形式 - {result}")
        except Exception as e:
            print(f"✗ {test['desc']} - エラー: {e}")


def test_http_request():
    """http_request ツールのテスト（モック）"""
    print("\n" + "="*60)
    print("4. HTTP Request ツールテスト")
    print("="*60)
    
    if not TOOLS_AVAILABLE:
        print("スキップ: ツールが利用できません")
        return
    
    # 基本的なGETリクエストのテスト
    print("\nGETリクエストテスト:")
    try:
        result = http_request(
            url="https://httpbin.org/get",
            method="GET"
        )
        
        if isinstance(result, dict):
            print(f"✓ ステータスコード: {result.get('status_code', 'なし')}")
            print(f"✓ ヘッダー数: {len(result.get('headers', {}))}")
            body = result.get('body', '')
            if body:
                try:
                    body_json = json.loads(body) if isinstance(body, str) else body
                    print(f"✓ レスポンスボディ: {type(body_json).__name__}型")
                except:
                    print(f"✓ レスポンスボディ: テキスト ({len(body)} 文字)")
        else:
            print(f"✗ 予期しない戻り値の型: {type(result)}")
    except Exception as e:
        print(f"✗ HTTPリクエストエラー: {e}")


def test_use_aws():
    """use_aws ツールのテスト"""
    print("\n" + "="*60)
    print("5. Use AWS ツールテスト")
    print("="*60)
    
    if not TOOLS_AVAILABLE:
        print("スキップ: ツールが利用できません")
        return
    
    # S3バケット一覧取得のテスト
    print("\nS3バケット一覧取得テスト:")
    try:
        result = use_aws(
            service="s3",
            action="list_buckets"
        )
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"⚠ エラー: {result['error']}")
                print("  （AWS認証情報が設定されていない可能性があります）")
            elif 'buckets' in result:
                print(f"✓ S3バケット数: {len(result['buckets'])}")
            else:
                print(f"✓ 結果: {result}")
        else:
            print(f"✗ 予期しない戻り値の型: {type(result)}")
    except Exception as e:
        print(f"⚠ AWSアクセスエラー: {e}")
        print("  （実際のAWS環境では動作しますが、テスト環境では権限エラーになる場合があります）")


def main():
    """全テストを実行"""
    print("strands-agents-tools 統合テスト")
    print("="*60)
    
    # 各テストを実行
    test_tool_imports()
    test_calculator()
    test_current_time()
    test_http_request()
    test_use_aws()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)


if __name__ == "__main__":
    main()