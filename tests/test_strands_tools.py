#!/usr/bin/env python
"""strands-agents-toolsのインポートテスト"""

try:
    # strands_toolsからツールをインポート
    from strands_tools import http_request  # http_requestはモジュール自体がツール
    from strands_tools.calculator import calculator  # calculator関数をインポート
    from strands_tools.current_time import current_time  # current_time関数をインポート
    print("✅ strands_tools から正常にインポートできました")
    print(f"- http_request モジュール: {http_request}")
    print(f"  利用可能な属性: {[attr for attr in dir(http_request) if not attr.startswith('_')]}")
    print(f"\n- calculator 関数: {calculator}")
    print(f"  利用可能な属性: {[attr for attr in dir(calculator) if not attr.startswith('_')]}")
    print(f"\n- current_time 関数: {current_time}")
    print(f"  利用可能な属性: {[attr for attr in dir(current_time) if not attr.startswith('_')]}")
    
    # TOOL_SPEC属性を確認
    print("\n\n各ツールのTOOL_SPEC属性:")
    
    if hasattr(http_request, 'TOOL_SPEC'):
        print("✅ http_request モジュールにTOOL_SPECが存在")
    
    if hasattr(calculator, 'TOOL_SPEC'):
        print("✅ calculator 関数にTOOL_SPECが存在")
        
    if hasattr(current_time, 'TOOL_SPEC'):
        print("✅ current_time 関数にTOOL_SPECが存在")
        
except ImportError as e:
    print(f"❌ インポートエラー: {e}")