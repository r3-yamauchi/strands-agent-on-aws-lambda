# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AWS Lambda上でStrands Agentを実行するサーバーレスアプリケーション。AWS CDK v2（Python）でデプロイし、軽量化されたツール実装を使用。

### アーキテクチャ

- **Lambda関数**: Strands Agentを実行（Python 3.11）
- **Lambda Function URLs**: 直接HTTPSエンドポイントを提供
- **Lambda Layer**: 依存関係を管理（strands-agents SDK）
- **IAM Role**: AWS Bedrockへのアクセス権限
- **ツール実装**: strands-agents-toolsパッケージを使用（http_request、calculator、current_time）、カスタムツール（generate_hash）
- **完全な応答キャプチャ**: stdout/stderrをキャプチャしてLLMの思考過程を含む全応答を取得

### 主要な設計決定

1. **strands-agents-tools使用**: 公式ツールパッケージを使用して信頼性と機能性を向上
2. **カスタムツール実装**: generate_hashツールで独自機能を提供（json_formatter、text_analyzerは現在無効化中）
3. **uv対応**: 高速な依存関係管理とビルドのため
4. **環境変数サポート**: 柔軟な設定変更を可能にするため

## 重要なコマンド

### デプロイ

```bash
# ロングオプション
./deploy.sh --profile <AWS_PROFILE> --region <AWS_REGION> [--memory <MB>] [--timeout <分>]

# ショートオプション  
./deploy.sh -p <AWS_PROFILE> -r <AWS_REGION> [-m <MB>] [-t <分>]
```

### Lambda Layer構築

```bash
python build_layer.py
```

### CDK直接操作

```bash
cdk synth --profile <PROFILE>
cdk deploy --profile <PROFILE>
cdk destroy --profile <PROFILE>
```

### ローカルテスト

```bash
python tests/test_strands_tools.py  # strands-agents-toolsツールテスト
python tests/test_custom_tools.py   # カスタムツールテスト
python tests/test_local_with_custom_tools.py  # Lambda関数テスト（要Bedrock権限）
python tests/test_strands_agent.py  # Strands Agent統合テスト
```

### 依存関係管理（uv使用）

```bash
uv sync                    # 依存関係インストール
source .venv/bin/activate  # 仮想環境アクティベート
```

## ディレクトリ構造と重要ファイル

```text
lambda/
├── lambda_function.py     # Lambdaハンドラー（日本語コメント付き）
└── custom_tools.py        # カスタムツール実装

stacks/
└── strands_agent_stack.py # CDKスタック定義（日本語コメント付き）

tests/
├── test_local.py                    # Lambda関数テスト
├── test_local_with_custom_tools.py  # カスタムツール含むLambda関数テスト
├── test_tools_only.py               # ツール単体テスト
├── test_strands_tools.py           # strands-agents-toolsツールテスト
├── test_custom_tools.py            # カスタムツール単体テスト
├── test_strands_agent.py           # Strands Agent統合テスト
└── test_import.py                  # パッケージインポートテスト

build_layer.py            # Lambda Layer構築スクリプト（uv対応）
deploy.sh                 # デプロイスクリプト（uv対応）
pyproject.toml           # Pythonプロジェクト設定（uv用）
```

## Lambda関数の詳細

### Lambda関数のアーキテクチャ

- **Runtime**: Python 3.11
- **Architecture**: ARM64 (AWS Graviton2)
- **メモリ**: 1024MB（デフォルト、カスタマイズ可能）
- **タイムアウト**: 10分（デフォルト、カスタマイズ可能）

### 環境変数

- `ASSISTANT_SYSTEM_PROMPT`: システムプロンプトのカスタマイズ
- `DEFAULT_TIMEOUT`: HTTPリクエストタイムアウト（デフォルト: 30秒）
- `MAX_PROMPT_LENGTH`: プロンプト最大文字数（デフォルト: 10000）
- `DEFAULT_MODEL_ID`: 使用するBedrockモデルID（デフォルト: Nova Pro us.amazon.nova-pro-v1:0）
- `PYTHONPATH`: `/opt/python`（Lambda Layer用）
- `AWS_REGION`: リージョン設定

### エラーレスポンス

すべてのエラーレスポンスは`ensure_ascii=False`で日本語を正しく表示。

### バリデーション

- プロンプトの存在確認
- プロンプト長の制限（MAX_PROMPT_LENGTH）

### 完全な応答キャプチャ

- **stdout/stderrキャプチャ**: `io.StringIO`と`contextlib.redirect_stdout/stderr`を使用
- **思考過程の保存**: LLMのthinkingプロセスとツール使用詳細をキャプチャ
- **CloudWatch Logs出力**: 完全な応答をログに記録してデバッグに利用可能

## 使用ツール

strands-agents-toolsパッケージから以下のツールを使用：

### http_request

- 包括的な認証サポート（Bearer、Basic、JWT、AWS SigV4など）
- セッション管理、メトリクス、ストリーミングサポート
- Cookieハンドリング、リダイレクト制御

### calculator

- SymPyを使用した高度な数学演算
- 式評価、方程式の解、微分・積分、極限、級数展開
- 行列演算サポート

### current_time

- ISO 8601形式で現在時刻を取得
- タイムゾーンサポート（UTC、US/Pacific、Asia/Tokyoなど）
- DEFAULT_TIMEZONE環境変数でデフォルトタイムゾーン設定可能

## カスタムツール

custom_tools.pyで実装されているカスタムツール：

### generate_hash

- MD5、SHA1、SHA256、SHA512アルゴリズムサポート
- テキストのハッシュ値と元のテキスト長を返却

### json_formatter（現在無効化中）

- JSON文字列の整形
- インデントレベルのカスタマイズ
- 日本語文字の正しい表示

### text_analyzer（現在無効化中）

- テキストの統計情報分析
- 文字数、単語数、行数、文字種別カウント

## CDKスタックの設定

### カスタマイズ可能な項目

- `lambda_memory`: メモリサイズ（MB）
- `lambda_timeout`: タイムアウト（分）
- `reserved_concurrent`: 予約同時実行数

### Lambda Function URLs設定

- **直接HTTPSエンドポイント**: シンプルなアーキテクチャ
- **CORS**: すべてのオリジンを許可（本番環境では変更推奨）
- **認証**: auth_type=NONE（パブリックアクセス）
- **ログレベル**: INFO

## 開発時の注意点

1. **Bedrock権限**: デプロイ先リージョンでBedrockモデルへのアクセス権限が必要
2. **Lambda Layerサイズ**: 250MB制限に注意
3. **日本語処理**: `ensure_ascii=False`を使用してJSONレスポンスで日本語を正しく表示
4. **strands-agents-tools使用**: 公式ツールパッケージを使用して信頼性の高いツール機能を提供
5. **カスタムツール拡張**: generate_hashツールで独自機能を追加
6. **stdoutキャプチャ**: Strands Agentsが出力する内容を全てキャプチャして完全な応答を取得

## よくあるエラーと対処法

### AccessDeniedException (Bedrock)

- リージョンでBedrockが有効か確認
- IAMロールの権限を確認

### Lambda Layerビルドエラー

- ARM64の場合: `aarch64-unknown-linux-gnu`プラットフォーム指定を確認
- x86_64の場合: `x86_64-manylinux2014`プラットフォーム指定を確認
- 依存関係のサイズを確認

### タイムアウトエラー

- Lambda関数のタイムアウトを増やす
- HTTPリクエストのタイムアウトを調整

### Function URLsアクセスエラー

- Lambda Function URLsは直接HTTPSエンドポイントを提供し、追加のパス（例: `/invoke`）は不要
- Function URLが正しくデプロイされているか確認
- CORS設定が適切か確認

## コード品質の維持

- すべてのコメントは日本語で記述
- 型ヒントを積極的に使用
- エラーハンドリングを適切に実装
- 環境変数でカスタマイズ可能にする
