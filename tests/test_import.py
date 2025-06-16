#!/usr/bin/env python
"""strands-agents-toolsのインポートテスト"""

try:
    print("1. strands_toolsからツールを直接インポート...")
    from strands_tools import http_request, calculator, current_time
    print("✅ 成功しました!")
    print(f"  - http_request: {http_request}")
    print(f"  - calculator: {calculator}")
    print(f"  - current_time: {current_time}")
    
    print("\n2. 各ツールの属性を確認...")
    print(f"  - http_request has __strands_tool__: {hasattr(http_request, '__strands_tool__')}")
    print(f"  - calculator has __strands_tool__: {hasattr(calculator, '__strands_tool__')}")
    print(f"  - current_time has __strands_tool__: {hasattr(current_time, '__strands_tool__')}")
    
    print("\n3. エージェントでツールを使用...")
    from strands import Agent
    agent = Agent(tools=[http_request, calculator, current_time])
    print("✅ エージェントの作成に成功しました!")
    
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
except Exception as e:
    print(f"❌ エラー: {e}")