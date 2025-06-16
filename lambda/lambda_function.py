"""
AWS Lambda関数エントリーポイント
Strands Agentを使用してAIアシスタント機能を提供
"""
import io
import os
import sys
import json
import logging
from typing import Dict, Any
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request, calculator, current_time
# カスタムツールをインポート
from custom_tools import generate_hash
# from custom_tools import generate_hash, json_formatter, text_analyzer

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# アシスタントのシステムプロンプト
ASSISTANT_SYSTEM_PROMPT = os.environ.get(
    'ASSISTANT_SYSTEM_PROMPT',
    """あなたは様々なツールにアクセスできる有用なAIアシスタントです。
HTTPリクエストの実行、数式の計算、現在の日時情報の取得に加えて、
ハッシュ生成、JSON整形、テキスト分析などの追加機能も利用できます。
常に親切で、利用可能なツールを使って正確な情報を提供してください。"""
)

# Lambda設定定数
DEFAULT_TIMEOUT = int(os.environ.get('DEFAULT_TIMEOUT', '30'))  # デフォルトタイムアウト（秒）
MAX_PROMPT_LENGTH = int(os.environ.get('MAX_PROMPT_LENGTH', '10000'))  # プロンプトの最大文字数
DEFAULT_MODEL_ID = os.environ.get('DEFAULT_MODEL_ID', 'us.amazon.nova-pro-v1:0')  # デフォルトのBedrockモデルID

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Strands Agents SDKを使用してリクエストを処理するAWS Lambdaハンドラー関数
    
    Args:
        event: リクエストデータを含むLambdaイベント
        context: Lambdaコンテキストオブジェクト
        
    Returns:
        statusCodeとbodyを含むレスポンス辞書
    """
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
        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'プロンプトが提供されていません',
                    'message': 'リクエストボディまたはイベントにプロンプトを含めてください'
                }, ensure_ascii=False)
            }
        
        if len(prompt) > MAX_PROMPT_LENGTH:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'プロンプトが長すぎます',
                    'message': f'プロンプトは{MAX_PROMPT_LENGTH}文字以内にしてください'
                }, ensure_ascii=False)
            }
        
        # オプション: イベントからモデル設定を抽出
        model_config = body.get('model_config', {})
        
        # 利用可能なツールを持つエージェントを作成
        # デフォルトモデルIDが環境変数で指定されている場合は使用
        if DEFAULT_MODEL_ID and 'model' not in model_config:
            model_config['model'] = DEFAULT_MODEL_ID
            
        agent = Agent(
            system_prompt=ASSISTANT_SYSTEM_PROMPT,
            tools=[
                http_request,
                calculator,
                current_time,
                generate_hash,
                # json_formatter,
                # text_analyzer
            ],
            **model_config  # カスタムモデル設定を許可
        )
        
        # 使用されるモデル情報をログに出力
        used_model = None
        try:
            # Agentインスタンスから実際のモデル情報を取得
            if hasattr(agent, 'model'):
                model_info = agent.model
                
                # BedrockModelインスタンスの場合
                if isinstance(model_info, BedrockModel):
                    # BedrockModelの初期化時にmodel_idパラメータが使用される
                    # まず直接アクセスを試みる
                    for attr_name in ['model_id', '_model_id', 'id', '_id']:
                        if hasattr(model_info, attr_name):
                            attr_value = getattr(model_info, attr_name)
                            if attr_value:
                                used_model = attr_value
                                break
                    
                    # それでも取得できない場合は__dict__を確認
                    if not used_model and hasattr(model_info, '__dict__'):
                        model_dict = model_info.__dict__
                        logger.info(f"BedrockModelの内部状態: {list(model_dict.keys())}")
                        
                        # よくあるキー名をチェック
                        for key in ['model_id', '_model_id', 'id', '_id', 'model', '_model']:
                            if key in model_dict and model_dict[key]:
                                used_model = model_dict[key]
                                break
                
                # 文字列の場合（モデルIDが直接指定されている）
                elif isinstance(model_info, str):
                    used_model = model_info
                
                # その他のオブジェクトの場合
                else:
                    logger.info(f"未知のモデルタイプ: {type(model_info)}")
                    used_model = str(model_info)
            
            # エージェントのモデル情報が取得できない場合
            if not used_model:
                if 'model' in model_config:
                    used_model = model_config['model']
                else:
                    # Strands Agentsのデフォルト
                    used_model = DEFAULT_MODEL_ID
                    logger.info(f"デフォルトモデル {DEFAULT_MODEL_ID} を使用")
                    
            logger.info(f"使用モデル: {used_model}")
            
        except Exception as e:
            logger.error(f"モデル情報の取得中にエラー: {str(e)}", exc_info=True)
            used_model = DEFAULT_MODEL_ID
        
        # プロンプトを処理
        logger.info(f"プロンプトを処理中: {prompt[:100]}...")  # 最初の100文字をログ出力
        
        # 標準出力をキャプチャして全ての応答を収集
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        complete_response = ""
        
        try:
            # 標準出力をキャプチャ
            sys.stdout = captured_output
            
            # エージェントを実行
            response = agent(prompt)
            
            # 標準出力を元に戻す
            sys.stdout = old_stdout
            
            # キャプチャした出力を取得
            captured_text = captured_output.getvalue()
            
            # 最終的な応答を取得
            final_response = str(response)
            
            # キャプチャした出力がある場合は、それも含める
            if captured_text:
                # 出力をログに記録
                logger.info(f"エージェントの出力:\n{captured_text}")
                # 全体の応答として結合（出力と最終応答を含む）
                complete_response = captured_text.strip()
                # 最終応答が出力に含まれていない場合は追加
                if final_response and final_response not in complete_response:
                    complete_response = complete_response + "\n\n" + final_response if complete_response else final_response
            else:
                complete_response = final_response
                
        except Exception as e:
            # エラーが発生した場合は標準出力を元に戻す
            sys.stdout = old_stdout
            logger.error(f"応答処理中のエラー: {str(e)}")
            raise
        finally:
            # 確実に標準出力を元に戻す
            sys.stdout = old_stdout
            captured_output.close()
        
        logger.info(f"完全な応答: {complete_response}")
        logger.info("プロンプト処理完了")
        
        # レスポンスをフォーマット
        response_body = {
            'response': complete_response,
            'prompt': prompt,
            'success': True
        }
        
        # 使用したモデル情報を含める
        if used_model:
            response_body['model_used'] = used_model
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_body, ensure_ascii=False)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': '無効なJSON',
                'message': f'リクエストボディの解析に失敗しました: {str(e)}'
            }, ensure_ascii=False)
        }
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': '内部サーバーエラー',
                'message': f'エラーが発生しました: {str(e)}',
                'type': type(e).__name__
            }, ensure_ascii=False)
        }

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