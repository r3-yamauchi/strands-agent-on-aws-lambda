"""
AWS Lambda関数エントリーポイント
Strands Agentを使用してAIアシスタント機能を提供
"""
import json
import logging
from typing import Dict, Any
# 遅延インポートを使用してコールドスタートを最適化
Agent = None
BedrockModel = None
http_request = None
calculator = None
current_time = None
use_aws = None

def _lazy_imports():
    """必要になったときにのみモジュールをインポート"""
    global Agent, BedrockModel, http_request, calculator, current_time, use_aws
    if Agent is None:
        from strands import Agent
        from strands.models import BedrockModel
    if http_request is None or calculator is None or current_time is None or use_aws is None:
        from strands_tools import http_request, calculator, current_time, use_aws

# ローカルインポート
from config import config
from utils import capture_stdout, validate_prompt, get_model_info, sanitize_error_message, format_response
from custom_tools import generate_hash, json_formatter, text_analyzer

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 設定の読み込み
ASSISTANT_SYSTEM_PROMPT = config.ASSISTANT_SYSTEM_PROMPT
DEFAULT_TIMEOUT = config.DEFAULT_TIMEOUT
MAX_PROMPT_LENGTH = config.MAX_PROMPT_LENGTH
DEFAULT_MODEL_ID = config.DEFAULT_MODEL_ID

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Strands Agents SDKを使用してリクエストを処理するAWS Lambdaハンドラー関数
    
    Args:
        event: リクエストデータを含むLambdaイベント
        context: Lambdaコンテキストオブジェクト
        
    Returns:
        statusCodeとbodyを含むレスポンス辞書
    """
    # 遅延インポートを実行
    _lazy_imports()
    
    try:
        # リクエストペイロードをログ出力
        logger.info(f"受信したイベント: {json.dumps(event, ensure_ascii=False)}")
        
        # イベントからプロンプトを抽出
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        logger.info(f"リクエストボディ: {json.dumps(body, ensure_ascii=False)}")
        
        prompt = body.get('prompt', event.get('prompt', ''))
        
        # プロンプトのバリデーション
        is_valid, error_msg = validate_prompt(prompt, MAX_PROMPT_LENGTH)
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                data={'message': 'プロンプトの検証に失敗しました'},
                status_code=400
            )
        
        # オプション: イベントからモデル設定を抽出
        model_config = body.get('model_config', {})
        
        # 利用可能なツールを持つエージェントを作成
        # デフォルトモデルIDが環境変数で指定されている場合は使用
        if DEFAULT_MODEL_ID and 'model' not in model_config:
            model_config['model'] = DEFAULT_MODEL_ID
        
        # ツールリストを動的に構築
        # 基本ツール（strands-agents-tools）
        tools = [
            http_request,
            calculator,
            current_time,
        ]
        
        # カスタムツールを設定に基づいて追加
        if config.ENABLE_CUSTOM_TOOLS:
            custom_tools = []
            
            if config.ENABLE_HASH_GENERATOR:
                custom_tools.append(generate_hash)
            if config.ENABLE_JSON_FORMATTER:
                custom_tools.append(json_formatter)
            if config.ENABLE_TEXT_ANALYZER:
                custom_tools.append(text_analyzer)
            
            tools.extend(custom_tools)
            logger.info(f"有効なカスタムツール: {[t.__name__ for t in custom_tools]}")
        
        # AWSツール（strands-agents-toolsに含まれる）
        if config.ENABLE_AWS_TOOLS:
            tools.append(use_aws)
            logger.info("AWSツール(use_aws)を有効化")
        
        # if config.ENABLE_NOVA_REELS:
        #     from nova_tools import nova_reels
        #     tools.append(nova_reels)
        #     logger.info("Nova Reelsツールを有効化")
        
        # MCP Server統合（将来実装）
        # if config.ENABLE_MCP_SERVER:
        #     from mcp_integration import load_mcp_tools
        #     mcp_tools = load_mcp_tools()
        #     tools.extend(mcp_tools)
        #     logger.info(f"MCPツールを{len(mcp_tools)}個ロード")
            
        agent = Agent(
            system_prompt=ASSISTANT_SYSTEM_PROMPT,
            tools=tools,
            **model_config  # カスタムモデル設定を許可
        )
        
        # 使用されるモデル情報をログに出力
        used_model = get_model_info(agent, model_config, DEFAULT_MODEL_ID)
        logger.info(f"使用モデル: {used_model}")
        
        # プロンプトを処理
        logger.info(f"プロンプトを処理中: {prompt[:100]}...")  # 最初の100文字をログ出力
        
        # 標準出力をキャプチャして全ての応答を収集
        with capture_stdout() as captured:
            response = agent(prompt)
            captured_text = captured.getvalue()
        
        # 最終的な応答の構築
        final_response = str(response)
        complete_response = captured_text.strip()
        
        if complete_response and final_response not in complete_response:
            complete_response = f"{complete_response}\n\n{final_response}" if complete_response else final_response
        elif not complete_response:
            complete_response = final_response
            
        if captured_text:
            logger.info(f"エージェントの出力:\n{captured_text}")
        
        logger.info(f"完全な応答: {complete_response}")
        logger.info("プロンプト処理完了")
        
        # レスポンスをフォーマット
        response_data = {
            'response': complete_response,
            'prompt': prompt
        }
        
        # 使用したモデル情報を含める
        if used_model:
            response_data['model_used'] = used_model
        
        return format_response(
            success=True,
            data=response_data,
            status_code=200
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {str(e)}")
        return format_response(
            success=False,
            error='無効なJSON',
            data={'message': f'リクエストボディの解析に失敗しました: {str(e)}'},
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        error_message = sanitize_error_message(e)
        return format_response(
            success=False,
            error='内部サーバーエラー',
            data={
                'message': error_message,
                'type': type(e).__name__
            },
            status_code=500
        )

# ローカルテスト用
if __name__ == "__main__":
    # テストイベント
    test_event = {
        "body": json.dumps({
            "prompt": "現在の日時を教えてください。また、25 * 4 の計算もお願いします。"
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))