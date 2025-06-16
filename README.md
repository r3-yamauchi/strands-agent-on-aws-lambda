# AWS Strands Agents SDK Lambda Sample

このプロジェクトは、AWS Lambda関数内でAWS Strands Agents SDKを使用するサンプル実装です。

## 概要

AWS Strands Agents SDKがLambda Layerとしてデプロイ済みの環境で、そのSDKを利用するLambda関数の実装例を提供します。

## ファイル構成

- `lambda_function.py` - Lambda関数のメインハンドラー
- `requirements.txt` - 依存関係（Lambda Layerで提供されるため参照用）
- `sample_event.json` - テスト用のLambdaイベント
- `deploy_config.json` - Lambda関数のデプロイ設定
- `README.md` - このファイル

## 機能

このサンプルLambda関数は以下の機能を提供します：

1. **HTTPリクエスト** - `http_request`ツールを使用した外部APIへのアクセス
2. **計算機能** - `calculator`ツールを使用した数式計算
3. **日時情報** - `datetime_tool`を使用した現在の日時取得

## 使用方法

### 1. 前提条件

- AWS Strands Agents SDKがLambda Layerとしてデプロイ済み
- 適切なIAMロールの設定（Bedrock APIへのアクセス権限）

### 2. デプロイ設定の更新

`deploy_config.json`内の以下の値を実際の値に置き換えてください：

```json
{
  "layers": [
    "arn:aws:lambda:REGION:ACCOUNT_ID:layer:strands-agents-sdk:VERSION"
  ],
  "role": "arn:aws:iam::ACCOUNT_ID:role/strands-agent-lambda-role"
}
```

### 3. Lambda関数の呼び出し

#### API Gateway経由（HTTP POST）
```bash
curl -X POST https://your-api-gateway-url/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "現在の日時を教えてください。また、100の20%はいくつですか？"}'
```

#### AWS CLI経由
```bash
aws lambda invoke \
  --function-name strands-agent-sample \
  --payload file://sample_event.json \
  response.json
```

## リクエスト形式

```json
{
  "prompt": "エージェントへの質問やリクエスト",
  "model_config": {
    // オプション: モデル設定のカスタマイズ
  }
}
```

## レスポンス形式

### 成功時（200）
```json
{
  "response": "エージェントからの応答",
  "prompt": "元のプロンプト",
  "success": true
}
```

### エラー時（400/500）
```json
{
  "error": "エラータイプ",
  "message": "エラーの詳細メッセージ"
}
```

## IAMポリシー

Lambda関数には以下の権限が必要です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

## カスタマイズ

### システムプロンプトの変更

`lambda_function.py`内の`ASSISTANT_SYSTEM_PROMPT`を編集して、エージェントの振る舞いをカスタマイズできます。

### ツールの追加

`strands_tools`から追加のツールをインポートして、`tools`リストに追加できます：

```python
from strands_tools import another_tool

agent = Agent(
    system_prompt=ASSISTANT_SYSTEM_PROMPT,
    tools=[http_request, calculator, datetime_tool, another_tool]
)
```

## トラブルシューティング

### タイムアウトエラー
- Lambda関数のタイムアウト設定を増やしてください（最大15分）
- `deploy_config.json`の`timeout`値を調整

### 権限エラー
- IAMロールにBedrock APIへのアクセス権限があることを確認
- Lambda LayerのARNが正しいことを確認

## 参考リンク

- [AWS Strands Agents SDK ドキュメント](https://docs.aws.amazon.com/strands-agents/)
- [AWS Lambda ドキュメント](https://docs.aws.amazon.com/lambda/)