# テストスクリプト

このディレクトリには、Lambda関数とツールのテストスクリプトが含まれています。

## 📁 ファイル構成

- `test_tools_only.py` - 個別ツールの動作確認
- `test_local.py` - Lambda関数の統合テスト（要Bedrock権限）

## 🧪 実行方法

### ツールのみのテスト

```bash
# testsディレクトリから実行
cd tests
python test_tools_only.py

# またはプロジェクトルートから
python tests/test_tools_only.py
```

このテストは外部依存なしで実行可能です。

### Lambda関数のテスト

```bash
# testsディレクトリから実行
cd tests
python test_local.py

# またはプロジェクトルートから
python tests/test_local.py
```

⚠️ **注意**: このテストにはAWS Bedrockへのアクセス権限が必要です。

## 📝 テスト内容

### test_tools_only.py

1. **calculator** - 数式計算機能
   - 基本的な算術演算
   - 数学関数（sqrt、sin等）

2. **datetime_tool** - 日時取得機能
   - UTC時間の取得
   - タイムゾーン処理

3. **http_request** - HTTPリクエスト機能
   - GETリクエストの実行
   - レスポンスの検証

### test_local.py

Lambda関数の統合テストケース：

1. **日付と計算のテスト** - 複数ツールの組み合わせ
2. **複雑な計算テスト** - 高度な数式処理
3. **HTTPリクエストテスト** - 外部API呼び出し
4. **エラーハンドリング** - プロンプトなしのケース

## 🔧 トラブルシューティング

### ModuleNotFoundError

```bash
# プロジェクトルートから実行することを推奨
python tests/test_tools_only.py
```

### AccessDeniedException

AWS認証情報とBedrockへのアクセス権限を確認してください：

```bash
aws configure list
aws bedrock list-foundation-models --region <your-region>
```

## 🚀 今後の改善予定

- モックを使用した単体テストの追加
- pytest フレームワークの導入
- CI/CD対応のテストスイート構築