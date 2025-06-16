#!/usr/bin/env python
"""strands-agentsとstrands-agents-toolsの統合テスト"""

import os
# デフォルトモデルを設定（モデルアクセスエラーを回避）
os.environ['DEFAULT_MODEL_ID'] = 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'

try:
    print("1. strands_toolsのツールをインポート...")
    from strands_tools import http_request  # http_requestはモジュール自体がツール
    from strands_tools.calculator import calculator  # calculator関数をインポート
    from strands_tools.current_time import current_time  # current_time関数をインポート
    print("✅ インポート成功")
    
    print("\n2. strands.Agentをインポート...")
    from strands import Agent
    print("✅ インポート成功")
    
    print("\n3. ツールの属性を確認...")
    print(f"calculator TOOL_SPEC: {hasattr(calculator, 'TOOL_SPEC')}")
    print(f"current_time TOOL_SPEC: {hasattr(current_time, 'TOOL_SPEC')}")
    print(f"http_request TOOL_SPEC: {hasattr(http_request, 'TOOL_SPEC')}")
    
    print("\n4. エージェントを作成...")
    # すべてのツールを含めてエージェントを作成
    agent = Agent(
        system_prompt="You are a helpful assistant with access to HTTP request, calculator, and time tools.",
        tools=[http_request, calculator, current_time]
    )
    print("✅ エージェント作成成功（すべてのツールを含む）")
    
    print("\n5. 簡単なテストを実行...")
    try:
        response = agent("What is 2+2?")
        print(f"応答: {response}")
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()