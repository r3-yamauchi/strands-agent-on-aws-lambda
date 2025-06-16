#!/bin/bash
set -e

echo "Strands Agent AWS Lambda CDK デプロイ"
echo "====================================="

# デフォルト値
AWS_PROFILE=""
AWS_REGION=""
FUNCTION_NAME=""

# コマンドライン引数を解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile|-p)
            AWS_PROFILE="$2"
            shift 2
            ;;
        --region|-r)
            AWS_REGION="$2"
            shift 2
            ;;
        --memory|-m)
            LAMBDA_MEMORY="$2"
            shift 2
            ;;
        --timeout|-t)
            LAMBDA_TIMEOUT="$2"
            shift 2
            ;;
        --name|-n)
            FUNCTION_NAME="$2"
            shift 2
            ;;
        --help|-h)
            echo "使用方法: $0 [オプション]"
            echo "オプション:"
            echo "  -p, --profile <profile>  使用するAWSプロファイル"
            echo "  -r, --region <region>    デプロイ先のAWSリージョン"
            echo "  -m, --memory <size>      Lambdaメモリサイズ（MB、デフォルト: 1024）"
            echo "  -t, --timeout <minutes>  Lambdaタイムアウト（分、デフォルト: 10）"
            echo "  -n, --name <name>        Lambda関数名（デフォルト: strands-agent-sample1）"
            echo "  -h, --help               このヘルプメッセージを表示"
            exit 0
            ;;
        *)
            echo "不明なオプション: $1"
            echo "使用方法を確認するには --help または -h を使用してください"
            exit 1
            ;;
    esac
done

# プロファイルとリージョンが指定されているか確認
if [ -z "$AWS_PROFILE" ]; then
    echo "エラー: AWSプロファイルが必要です。--profile <profile> または -p <profile> を使用してください"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    echo "エラー: AWSリージョンが必要です。--region <region> または -r <region> を使用してください"
    exit 1
fi

echo "使用するAWSプロファイル: $AWS_PROFILE"
echo "デプロイ先リージョン: $AWS_REGION"

# AWS環境変数をエクスポート
export AWS_PROFILE=$AWS_PROFILE
export AWS_REGION=$AWS_REGION
export CDK_DEFAULT_REGION=$AWS_REGION

# AWSアカウントIDを取得
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE)
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "エラー: AWSアカウントIDの取得に失敗しました。AWS認証情報を確認してください。"
    exit 1
fi
export CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID

echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Install CDK dependencies
echo ""
echo "Installing CDK dependencies..."
if command -v uv >/dev/null 2>&1; then
    echo "Using uv for dependency installation..."
    uv pip install aws-cdk-lib constructs
else
    echo "uv not found, using pip..."
    pip install -r requirements-dev.txt
fi

# Build Lambda layer
echo ""
echo "Building Lambda layer..."
python build_layer.py

# Bootstrap CDK (if needed)
echo ""
echo "Bootstrapping CDK environment..."
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION --profile $AWS_PROFILE || true

# Synthesize CDK app
echo ""
echo "Synthesizing CDK app..."
CDK_CONTEXT=""
if [ ! -z "$LAMBDA_MEMORY" ]; then
    CDK_CONTEXT="$CDK_CONTEXT -c lambda_memory=$LAMBDA_MEMORY"
fi
if [ ! -z "$LAMBDA_TIMEOUT" ]; then
    CDK_CONTEXT="$CDK_CONTEXT -c lambda_timeout=$LAMBDA_TIMEOUT"
fi
if [ ! -z "$FUNCTION_NAME" ]; then
    CDK_CONTEXT="$CDK_CONTEXT -c lambda_function_name=$FUNCTION_NAME"
fi

cdk synth $CDK_CONTEXT --profile $AWS_PROFILE

# デプロイ
echo ""
echo "スタックをデプロイ中..."
cdk deploy $CDK_CONTEXT --profile $AWS_PROFILE --require-approval never

echo ""
echo "デプロイが正常に完了しました！"
echo ""
echo "Lambda Function URLをテストするには、上記に表示されたURLを使用してください。"
echo "例:"
echo "  curl -X POST <FUNCTION_URL> \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"prompt\": \"現在の日時を教えてください。\"}'"