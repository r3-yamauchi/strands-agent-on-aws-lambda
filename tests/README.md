# テストスイート

このディレクトリには、Lambda関数とツールの統合テストスイートが含まれています。

## 📁 ファイル構成

- `test_tools.py` - strands-agents-toolsの全機能テスト（外部依存なし）
- `test_lambda.py` - Lambda関数の統合テスト（モック/実機両対応）
- `test_custom_tools_pytest.py` - カスタムツールのpytestテスト（カスタムツール使用時のみ）
- `conftest.py` - pytestの設定とフィクスチャ定義

## 🧪 実行方法

### ツールテスト（外部依存なし）

```bash
# 基本的なツールテスト
python tests/test_tools.py

# pytestを使用
pytest tests/test_tools.py -v
```

### Lambda関数テスト

```bash
# モックを使用したテスト（Bedrock不要）
pytest tests/test_lambda.py -v

# 実際のBedrockを使用したテスト
python tests/test_lambda.py --real
```

⚠️ **注意**: `--real`オプションにはAWS Bedrockへのアクセス権限が必要です。

### 全テストの実行

```bash
# pytestで全テストを実行
pytest tests/ -v

# カバレッジレポート付き
pytest tests/ --cov=lambda --cov-report=html
```

## 📝 テスト内容

### test_tools.py

1. **ツールインポートテスト**
   - strands-agents-toolsの正常インポート確認
   - TOOL_SPEC属性の検証

2. **calculator** - 数式計算機能
   - 基本的な算術演算（+、-、*、/）
   - 数学関数（sqrt、sin、cos、exp、log）
   - べき乗計算

3. **current_time** - 日時取得機能
   - デフォルトタイムゾーン
   - 各種タイムゾーン（UTC、Asia/Tokyo、US/Pacific等）
   - ISO 8601形式の検証

4. **http_request** - HTTPリクエスト機能
   - GETリクエストの実行
   - レスポンス構造の検証

### test_lambda.py

**モックテスト（pytest）：**
- 基本的な計算処理
- 現在時刻取得
- エラーハンドリング（プロンプトなし、長すぎるプロンプト）
- モデル設定のカスタマイズ

**実機テスト（--realオプション）：**
- 日付と計算の組み合わせ
- 複雑な数式処理
- ハッシュ生成機能

## 🔧 トラブルシューティング

### ModuleNotFoundError

```bash
# 仮想環境を確認
source .venv/bin/activate

# 依存関係を再インストール
uv sync
```

### AccessDeniedException (Bedrock)

```bash
# AWS認証情報を確認
aws configure list

# Bedrockアクセスを確認
aws bedrock list-foundation-models --region <your-region>
```

### pytest not found

```bash
# pytestをインストール
pip install pytest pytest-cov pytest-mock
```

## 🚀 CI/CD統合

GitHub Actionsでの自動テスト：

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest tests/ -v --cov=lambda
```

## 📊 テストカバレッジ

現在のカバレッジ目標：
- Lambda関数コード: 80%以上
- ツール統合: 90%以上
- エラーハンドリング: 100%