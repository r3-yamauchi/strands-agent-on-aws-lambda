# AWS Strands Agents SDK を使用する Lambda関数

[AWS Strands Agents SDK](https://strandsagents.com/latest/) を使用して AWS Lambda上でAIエージェントを動作させる Lambda関数です。

## 🚀 特徴

- **サーバーレスアーキテクチャ**: AWS LambdaとLambda Function URLsによる完全サーバーレス構成
- **AIアシスタント機能**: Strands Agents SDK を使用したAI対話機能（デフォルトでNova Pro）
- **公式ツール統合**: strands-agents-toolsパッケージによる信頼性の高いツール機能
- **カスタムツール拡張**: ハッシュ生成などの独自ツール実装（JSON整形、テキスト分析は現在無効化中）
- **AWS CDK v2対応**: Python 3.11による簡潔なインフラ定義
- **ARM64アーキテクチャ**: AWS Graviton2によるコスト効率とパフォーマンスの向上（最大20%コスト削減）
- **uv対応**: 高速なPythonパッケージマネージャーによる効率的な依存関係管理
- **完全な応答取得**: LLMの思考過程（thinking）とツール使用を含む全ての応答をキャプチャ
- **詳細なログ出力**: CloudWatch Logsでリクエスト・レスポンス・モデル情報・完全な応答内容を確認可能
- **環境変数による柔軟な設定**: システムプロンプト、タイムアウト、モデルIDなどのカスタマイズが可能

## 📦 含まれるツール

### 公式ツール (strands-agents-tools パッケージ)

1. **http_request**: 外部APIへのHTTPリクエスト実行
   - 包括的な認証サポート（Bearer、Basic、JWT、AWS SigV4など）
   - セッション管理、メトリクス、ストリーミングサポート
   - Cookieハンドリング、リダイレクト制御

2. **calculator**: SymPyを使用した高度な数学演算
   - 式評価、方程式の解、微分・積分、極限、級数展開
   - 行列演算サポート
   - エラーメッセージは日本語

3. **current_time**: タイムゾーン対応の現在時刻取得
   - ISO 8601形式で現在時刻を取得
   - タイムゾーンサポート（UTC、US/Pacific、Asia/Tokyoなど）
   - DEFAULT_TIMEZONE環境変数でデフォルトタイムゾーン設定可能

### カスタムツール (独自実装)

4. **generate_hash**: テキストのハッシュ値生成
   - MD5、SHA1、SHA256、SHA512アルゴリズムサポート
   - 元のテキスト長も返却

5. **json_formatter**: JSON文字列の整形（現在無効化中）
   - インデントレベルのカスタマイズ可能
   - 日本語文字の正しい表示（ensure_ascii=False）
   - キーのソート

6. **text_analyzer**: テキストの統計情報分析（現在無効化中）
   - 総文字数、単語数、行数のカウント
   - 文字種別カウント（大文字、小文字、数字、空白文字）
   - 日本語文字カウント（ひらがな、カタカナ、漢字）
   - 平均単語長の計算

## 🏗️ アーキテクチャ

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ Lambda Function │────▶│    Lambda    │────▶│   Bedrock   │
│      URLs       │     │   Function   │     │     API     │
│  (HTTPS直接)     │     │   (ARM64)    │     └─────────────┘
└─────────────────┘     └──────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │ Lambda Layer │
                        │ (依存関係)    │
                        │   (ARM64)    │
                        └──────────────┘
```

## 📋 前提条件

- **Python 3.11以上** - Lambda関数のランタイム要件
- **AWS CLIが設定済み** - 適切な認証情報とプロファイル設定
- **AWS CDK v2 CLI** - `npm install -g aws-cdk` でインストール
- **（推奨）uv パッケージマネージャー** - 高速な依存関係管理
- **AWS Bedrockへのアクセス権限** - デプロイ先リージョンでBedrockが利用可能であること
- **CDKブートストラップ済み** - 初回デプロイ時は `cdk bootstrap` が必要

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/r3-yamauchi/strands-agent-on-aws-lambda
cd strands-agent-on-aws-lambda
```

### 2. 依存関係のインストール（uvを使用）

```bash
# uvがインストールされていない場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# 仮想環境をアクティベート
source .venv/bin/activate
```

### 3. 依存関係のインストール（pipを使用）

```bash
# 仮想環境を作成
python -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements-dev.txt
```

## 🚀 デプロイ

### クイックデプロイ

```bash
# ロングオプション
./deploy.sh --profile <aws-profile> --region <aws-region>

# ショートオプション
./deploy.sh -p <aws-profile> -r <aws-region>
```

### カスタマイズオプション

```bash
# ロングオプション
./deploy.sh \
  --profile myprofile \
  --region us-east-1 \
  --memory 2048 \
  --timeout 15

# ショートオプション
./deploy.sh \
  -p myprofile \
  -r us-east-1 \
  -m 128 \
  -t 1
```

パラメータ:
- `-p, --profile`: AWSプロファイル名（必須）
- `-r, --region`: AWSリージョン（必須） - Bedrockが利用可能なリージョンを指定
- `-m, --memory`: Lambdaメモリサイズ（MB、デフォルト: 1024、最小: 128、最大: 10240）
- `-t, --timeout`: Lambdaタイムアウト（分、デフォルト: 10、最大: 15）
- `-n, --name`: Lambda関数名（デフォルト: strands-agent-sample1）
- `-h, --help`: ヘルプメッセージを表示

### デプロイプロセス

1. Lambda Layer構築（依存関係のパッケージング）
2. CDKスタックのシンセサイズ
3. CloudFormationスタックのデプロイ
4. Lambda Function URLの表示

## 📡 使用方法

### Lambda Function URLへのリクエスト

デプロイ後に表示されるLambda Function URLを使用：

```bash
curl -X POST https://your-function-url.lambda-url.region.on.aws/ \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "現在の日時を教えてください。また、100の平方根を計算してください。'Hello World'のSHA256ハッシュも生成してください。"
  }'
```

注意: Lambda Function URLsは直接HTTPSエンドポイントを提供するため、追加のパス（例: `/invoke`）は不要です。

### リクエスト形式

```json
{
  "prompt": "AIアシスタントへの質問またはタスク",
  "model_config": {
    // オプション: モデル設定のカスタマイズ
  }
}
```

#### model_config の詳細

`model_config` オブジェクトでは、Strands Agentがサポートする任意のモデル設定パラメータを指定できます：

```json
{
  "prompt": "AIアシスタントへの質問またはタスク",
  "model_config": {
    "model": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

**主な設定可能なパラメータ：**
- `model`: 使用するBedrockモデルID
- `temperature`: 生成のランダム性（0-1、デフォルト: 0.7）
- `max_tokens`: 最大トークン数（デフォルト: 4096）
- その他Strands Agentがサポートするパラメータ

**利用可能なBedrockモデルID例：**
- `us.amazon.nova-pro-v1:0` (Nova Pro - デフォルト)
- `us.amazon.nova-lite-v1:0` (Nova Lite)
- `us.amazon.nova-micro-v1:0` (Nova Micro)
- `us.anthropic.claude-3-5-sonnet-20241022-v2:0` (Claude 3.5 Sonnet)
- `us.anthropic.claude-3-7-sonnet-20250219-v1:0` (Claude 3.7 Sonnet)
- `us.anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku)

**注意事項：**
- 指定するモデルIDは、デプロイ先リージョンのBedrockモデルアクセスで有効化されている必要があります
- モデルIDのプレフィックス（`us.`など）は、リージョンに応じて適切に設定してください

### レスポンス形式

**成功時（200）:**
```json
{
  "response": "現在の日時は2024年6月16日...",
  "prompt": "元のプロンプト",
  "success": true,
  "model_used": "us.amazon.nova-pro-v1:0"
}
```

**エラー時（400/500）:**
```json
{
  "error": "エラータイプ",
  "message": "詳細なエラーメッセージ",
  "type": "Exception"
}
```

## ⚙️ 環境変数

Lambda関数で使用可能な環境変数：

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `ASSISTANT_SYSTEM_PROMPT` | アシスタントのシステムプロンプト | 内蔵プロンプト |
| `DEFAULT_TIMEOUT` | HTTPリクエストのタイムアウト（秒） | `30` |
| `MAX_PROMPT_LENGTH` | プロンプトの最大文字数 | `10000` |
| `DEFAULT_MODEL_ID` | 使用するBedrockモデルID | `us.amazon.nova-pro-v1:0` |
| `PYTHONPATH` | Lambda Layer用パス（自動設定） | `/opt/python` |
| `AWS_REGION` | AWSリージョン（自動設定） | デプロイ先リージョン |

## 🤖 使用されるLLMモデル

デフォルトでは、Amazon BedrockのNova Pro（`us.amazon.nova-pro-v1:0`）が使用されます。

モデルの変更方法：
1. 環境変数 `DEFAULT_MODEL_ID` で設定
2. リクエストごとに `model_config.model` で指定

使用されたモデルは：
- CloudWatch Logsに記録されます
- APIレスポンスの `model_used` フィールドに含まれます

## 📝 完全な応答キャプチャ

このLambda関数は、LLMの思考過程（thinking）やツール使用を含む完全な応答をキャプチャします：

- **stdout/stderrキャプチャ**: Strands Agentsがstdoutに出力する内容を全てキャプチャ
- **構造化された応答**: JSONレスポンスの `full_response` フィールドに完全な内容を含む
- **CloudWatch Logs**: 完全な応答はCloudWatch Logsにも記録され、デバッグに利用可能

## 📊 モニタリングとログ

### CloudWatch Logs

Lambda関数は以下の情報をCloudWatch Logsに記録します：

- **ロググループ**: `/aws/lambda/<関数名>` (デフォルト: `/aws/lambda/strands-agent-sample1`)
- **保持期間**: 1週間（変更可能）
- **ログレベル**: INFO
- **記録される情報**:
  - リクエスト・レスポンスの内容
  - 使用されたBedrockモデルID
  - LLMの思考過程（thinking）とツール使用の詳細
  - エラー情報とスタックトレース

ログの確認方法：
```bash
# CloudWatch Logsでログを確認
aws logs tail /aws/lambda/strands-agent-sample1 --follow --profile <your-profile>
```

### メトリクス

自動的に収集されるメトリクス：
- Lambda実行時間
- エラー率
- 同時実行数
- Function URLリクエスト数
- メモリ使用量
- コールドスタート発生率

## 🧪 ローカルテスト

### ツールのテスト

公式ツール（strands-agents-tools）のテスト：

```bash
python tests/test_strands_tools.py
```

カスタムツールの単体テスト：

```bash
python tests/test_custom_tools.py
```

テスト内容：
- **公式ツール**: calculator、current_time、http_request
- **カスタムツール**: generate_hash、json_formatter、text_analyzer

### Lambda関数のテスト（要Bedrock権限）

カスタムツールを含む完全なLambda関数テスト：

```bash
python tests/test_local_with_custom_tools.py
```

Strands Agent統合テスト：

```bash
python tests/test_strands_agent.py
```

注意: AWS認証情報とBedrockへのアクセス権限が必要です。

## 📁 プロジェクト構成

```
.
├── lambda/                    # Lambda関数コード
│   ├── lambda_function.py     # メインハンドラー
│   └── custom_tools.py       # カスタムツール実装
├── stacks/                   # CDKスタック定義
│   └── strands_agent_stack.py
├── tests/                    # テストスクリプト
│   ├── test_local.py         # Lambda関数テスト
│   ├── test_local_with_custom_tools.py # カスタムツール含むLambda関数テスト
│   ├── test_tools_only.py    # ツール単体テスト
│   ├── test_strands_tools.py # strands-agents-toolsツールテスト
│   ├── test_custom_tools.py  # カスタムツール単体テスト
│   ├── test_strands_agent.py # Strands Agent統合テスト
│   └── test_import.py        # パッケージインポートテスト
├── app.py                    # CDKアプリケーション
├── deploy.sh                 # デプロイスクリプト
├── build_layer.py            # Lambda Layer構築
├── pyproject.toml            # Pythonプロジェクト設定
└── cdk.json                  # CDK設定
```

## 🏗️ CDKスタック構成

CDKスタックは以下のAWSリソースをプロビジョニングします：

### 主要コンポーネント

1. **Lambda関数**
   - Runtime: Python 3.11
   - アーキテクチャ: ARM64 (AWS Graviton2)
   - メモリ: 1024MB（カスタマイズ可能、128MB〜10240MB）
   - タイムアウト: 10分（カスタマイズ可能、最大15分）
   - 環境変数によるカスタマイズサポート
   - 予約同時実行数の設定可能

2. **Lambda Layer**
   - strands-agents SDK v0.1.7、strands-agents-tools v0.1.5、および依存関係を含む
   - ARM64アーキテクチャ用にビルド（aarch64-unknown-linux-gnu）
   - Lambda関数のサイズを削減し、デプロイを高速化
   - サイズ制限: 250MB以内

3. **Lambda Function URLs**
   - 直接HTTPSエンドポイント（API Gateway不要）
   - CORS対応（POSTリクエスト、全オリジン許可）
   - 認証なし（パブリックアクセス、auth_type=NONE）
   - CloudWatchログ統合（ログレベル: INFO）
   - 追加パス不要（例: `/invoke`は不要）

4. **IAM Role**
   - Lambda基本実行権限
   - AWS Bedrock InvokeModel権限
   - CloudWatch Logs書き込み権限
   - X-Ray トレーシング権限（オプション）

### スタック構造

```python
StrandsAgentStack
├── Lambda実行ロール（IAMロール）
│   ├── 基本的なLambda実行権限
│   └── Bedrockアクセス権限
├── Lambda Layer（依存関係）
└── Lambda関数
    ├── ハンドラー: lambda_function.lambda_handler
    ├── ランタイム: Python 3.11
    ├── 環境変数設定
    └── Function URL
        ├── 直接HTTPSエンドポイント
        ├── CORS設定
        └── 認証: NONE（パブリック）
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. CDKブートストラップエラー

```bash
# エラー: "This stack uses assets, so the toolkit stack must be deployed"
# 解決方法:
cdk bootstrap aws://ACCOUNT_ID/REGION --profile YOUR_PROFILE
```

#### 2. Lambda Layerサイズエラー

```bash
# エラー: "Layer size exceeds Lambda limit"
# 解決方法:
# requirements.txtから不要な依存関係を削除
# または、複数のLayerに分割
# 250MBの制限内に収める
```

#### 3. デプロイ権限エラー

```bash
# エラー: "User is not authorized to perform: iam:CreateRole"
# 解決方法:
# IAMポリシーに必要な権限を追加
```

#### 4. Bedrock権限エラー（AccessDeniedException）

```bash
# エラー: "AccessDeniedException when calling Bedrock"
# 解決方法:
# 1. リージョンでBedrockが利用可能か確認
# 2. IAMロールにBedrock権限を追加
```

#### 5. Lambda Function URLsのアクセスエラー

```bash
# エラー: "403 Forbidden" または "404 Not Found"
# 解決方法:
# 1. Function URLが正しくデプロイされているか確認
# 2. Lambda Function URLsは直接HTTPSエンドポイントを提供し、追加のパス（例: `/invoke`）は不要
# 3. CORS設定が適切か確認
```

#### 6. Lambda関数タイムアウト

- `--timeout`パラメータで増やす（最大15分）
- 処理内容を見直して最適化

#### 7. メモリ不足エラー

- `--memory`パラメータで増やす（最大10240MB）
- CloudWatch Logsでメモリ使用量を確認

## 🎨 カスタマイズ

### Lambda関数の設定

`stacks/strands_agent_stack.py`で変更可能：

```python
# メモリサイズの変更（MB）
memory_size = self.node.try_get_context("lambda_memory") or 1024

# タイムアウトの変更（分）
timeout_minutes = self.node.try_get_context("lambda_timeout") or 10

# 予約同時実行数の設定
reserved_concurrent = self.node.try_get_context("reserved_concurrent") or None

# Lambda関数名の変更
function_name = self.node.try_get_context("lambda_function_name") or "strands-agent-sample1"
```

### システムプロンプトのカスタマイズ

環境変数 `ASSISTANT_SYSTEM_PROMPT` を設定することで、AIアシスタントの動作をカスタマイズ：

```python
# CDKスタックで設定
environment = {
    "ASSISTANT_SYSTEM_PROMPT": "あなたは日本語で応答する親切なアシスタントです。"
}
```

### Lambda Function URLsの設定

```python
# Function URLの設定
function_url = lambda_function.add_function_url(
    auth_type=lambda_.FunctionUrlAuthType.NONE,  # パブリックアクセス
    cors={
        "allowed_origins": ["*"],  # 全オリジン許可
        "allowed_methods": [lambda_.HttpMethod.POST],
        "allowed_headers": ["Content-Type"]
    }
)
```

## 📈 パフォーマンスチューニング

### Lambda関数の最適化

1. **メモリサイズの調整**
   - CloudWatch Logsでメモリ使用量を確認
   - 一般的な推奨値: 1024MB〜2048MB
   - メモリ増加によりCPU性能も向上

2. **予約同時実行の設定**
   - 安定したパフォーマンスが必要な場合に設定
   - コールドスタートを削減
   - コスト増加に注意（未使用時も課金）

3. **Lambda SnapStart**（将来的な対応）
   - Python 3.12以降で利用可能予定
   - 起動時間を最大10倍高速化

4. **コールドスタート対策**
   - Lambda Layerによる依存関係の事前ロード
   - 定期的なウォームアップ（CloudWatch Events）
   - 予約同時実行の活用

### ARM64アーキテクチャの利点

このプロジェクトはARM64（AWS Graviton2）を使用しています：

- **コスト削減**: x86_64と比較して最大20%のコスト削減
- **パフォーマンス向上**: より高速な実行
- **エネルギー効率**: 環境に優しい選択
- **メモリ帯域幅の向上**: 大量のデータ処理に適している

x86_64に変更する必要がある場合は、以下を修正してください：

- `build_layer.py`: `aarch64-unknown-linux-gnu` → `x86_64-manylinux2014`
- `stacks/strands_agent_stack.py`: `Architecture.ARM_64` → `Architecture.X86_64`

## 🔐 セキュリティベストプラクティス

### 1. 最小権限の原則
   - 必要最小限のIAM権限のみを付与
   - Bedrock InvokeModel権限のみに制限
   - リソースベースのポリシーを使用

### 2. 認証/認可
   - 現在の設定: パブリックアクセス（auth_type=NONE）
   - **本番環境での推奨設定**:
     ```python
     auth_type=lambda_.FunctionUrlAuthType.AWS_IAM
     ```
   - カスタム認証の実装（APIキー、JWT等）
   - レート制限の実装

### 3. ネットワークセキュリティ
   - VPC内でLambdaを実行（機密データ処理時）
   - セキュリティグループの適切な設定
   - プライベートサブネットでの実行

### 4. データ保護
   - 環境変数の暗号化（AWS Systems Manager Parameter Store）
   - CloudWatch Logsの暗号化
   - 機密情報のログ出力を避ける

### 5. 監査とコンプライアンス
   - AWS CloudTrailによるAPI呼び出しの記録
   - X-Rayによるトレーシング
   - 定期的なセキュリティ監査

## 🧹 リソースのクリーンアップ

### スタック全体を削除

```bash
cdk destroy --profile <aws-profile>
```

削除されるリソース:
- Lambda関数
- Lambda Layer
- IAMロール
- CloudWatch Logsロググループ
- Lambda Function URL

### 個別リソースの削除

CloudFormationコンソールから手動で削除することも可能です。

### 注意事項

- CloudWatch Logsは保持期間（1週間）後に自動削除
- Lambda Layerの古いバージョンは手動削除が必要な場合あり

## 📚 参考リンク

### AWS関連
- [AWS CDK v2 Documentation](https://docs.aws.amazon.com/cdk/v2/guide/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Lambda Function URLs Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)

### プロジェクト関連
- [AWS Strands Agents SDK](https://github.com/strands-agents)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Python 3.11 Release Notes](https://docs.python.org/3/whatsnew/3.11.html)

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを作成して変更内容を議論してください。

### 貢献ガイドライン

1. **コードスタイル**: PEP 8準拠
2. **コメント**: 日本語で記述
3. **テスト**: 新機能には対応するテストを追加
4. **ドキュメント**: README.mdとCLAUDE.mdを更新

## 📞 サポート

技術的な質問や問題がある場合：

1. **GitHubのIssueを作成** - バグ報告や機能要望
2. **トラブルシューティングセクション**を確認 - よくある問題の解決方法
3. **AWS公式ドキュメント**を参照 - AWS固有の問題
4. **CLAUDE.md**を確認 - プロジェクト固有の設定や注意事項

### よくある質問（FAQ）

**Q: Lambda Layerのサイズが大きすぎるエラーが出る**
A: 依存関係を見直し、不要なパッケージを削除してください。250MB制限があります。

**Q: Bedrockのモデルにアクセスできない**
A: リージョンでBedrockが有効か、IAMロールに適切な権限があるか確認してください。

**Q: Function URLにアクセスできない**
A: Lambda Function URLsは直接HTTPSエンドポイントです。追加のパス（例: `/invoke`）は不要です。
