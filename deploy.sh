#!/bin/bash
set -e

echo "Strands Agent AWS Lambda CDK Deploy"
echo "====================================="
echo ""

# バージョン
VERSION="2.0.0"

# 必須引数
AWS_PROFILE=""
AWS_REGION=""
LAMBDA_MEMORY=""
LAMBDA_TIMEOUT=""
FUNCTION_NAME=""
MODEL_ID="us.amazon.nova-pro-v1:0"

# オプション
STACK_TYPE=${CDK_STACK_TYPE:-"standard"}  # standard, migration, secure
ENVIRONMENT=${ENVIRONMENT:-"dev"}
DRY_RUN=false
FORCE_DEPLOY=false

# カラーコード
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルパー関数
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# コマンドライン引数の解析
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
        --model|-M)
            MODEL_ID="$2"
            shift 2
            ;;
        --stack-type|-s)
            STACK_TYPE="$2"
            shift 2
            ;;
        --environment|-e)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE_DEPLOY=true
            shift
            ;;
        --version|-v)
            echo "Strands Agent Lambda Deploy Script v${VERSION}"
            exit 0
            ;;
        --help|-h)
            echo "使用方法: $0 [オプション]"
            echo ""
            echo "必須引数:"
            echo "  -p, --profile <profile>  使用するAWSプロファイル"
            echo "  -r, --region <region>    デプロイ先のAWSリージョン"
            echo ""
            echo "オプション:"
            echo "  -m, --memory <size>      Lambdaメモリサイズ（MB、デフォルト: 1024）"
            echo "  -t, --timeout <minutes>  Lambdaタイムアウト（分、デフォルト: 10）"
            echo "  -n, --name <name>        Lambda関数名（デフォルト: strands-agent-sample1）"
            echo "  -M, --model <model_id>   BedrockモデルID（デフォルト: us.amazon.nova-pro-v1:0）"
            echo "  -s, --stack-type <type>  スタックタイプ (standard/migration/secure, デフォルト: standard)"
            echo "  -e, --environment <env>  環境 (デフォルト: dev)"
            echo "  --dry-run                実際のデプロイを行わずにシンセサイズのみ実行"
            echo "  --force                  確認プロンプトをスキップ"
            echo "  -v, --version            バージョン情報を表示"
            echo "  -h, --help               このヘルプメッセージを表示"
            echo ""
            echo "例:"
            echo "  $0 -p myprofile -r us-east-1"
            echo "  $0 -p myprofile -r us-east-1 -m 2048 -t 15"
            echo "  $0 -p myprofile -r us-east-1 -s migration -e staging"
            exit 0
            ;;
        *)
            print_error "不明なオプション: $1"
            echo "使用方法を確認するには --help または -h を使用してください"
            exit 1
            ;;
    esac
done

# プロファイルとリージョンの必須チェック
if [ -z "$AWS_PROFILE" ]; then
    print_error "AWSプロファイルが指定されていません。--profile <profile> または -p <profile> を使用してください"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    print_error "AWSリージョンが指定されていません。--region <region> または -r <region> を使用してください"
    exit 1
fi

# 設定内容を表示
echo "デプロイ設定:"
echo "-------------------------------------"
echo "プロファイル: $AWS_PROFILE"
echo "リージョン: $AWS_REGION"
echo "スタックタイプ: $STACK_TYPE"
echo "環境: $ENVIRONMENT"
if [ ! -z "$LAMBDA_MEMORY" ]; then
    echo "メモリ: ${LAMBDA_MEMORY}MB"
fi
if [ ! -z "$LAMBDA_TIMEOUT" ]; then
    echo "タイムアウト: ${LAMBDA_TIMEOUT}分"
fi
if [ ! -z "$FUNCTION_NAME" ]; then
    echo "関数名: $FUNCTION_NAME"
fi
if [ ! -z "$MODEL_ID" ]; then
    echo "モデルID: $MODEL_ID"
fi
echo "-------------------------------------"

# AWS認証情報の検証
export AWS_PROFILE=$AWS_PROFILE
export AWS_REGION=$AWS_REGION
export CDK_DEFAULT_REGION=$AWS_REGION

# AWSアカウントIDを取得
print_info "AWS認証情報を検証中..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile $AWS_PROFILE 2>/dev/null)
if [ -z "$AWS_ACCOUNT_ID" ]; then
    print_error "AWSアカウントIDの取得に失敗しました。AWSプロファイルと認証情報を確認してください"
    exit 1
fi
export CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID

print_success "AWS Account ID: $AWS_ACCOUNT_ID"

# Bedrockアクセス確認
print_info "Bedrockアクセスを確認中..."
# set -eを一時的に無効化してBedrockチェックを実行
set +e

# まず、bedrockコマンドが利用可能かチェック
aws bedrock help >/dev/null 2>&1
if [ $? -ne 0 ]; then
    print_warning "AWS CLIにbedrockコマンドが見つかりません"
    echo "  → AWS CLIが古い可能性があります。バージョン2.13.0以上が必要です"
    echo "    現在のAWS CLIバージョン: $(aws --version 2>/dev/null || echo "バージョン取得失敗")"
    echo ""
    echo "  AWS CLIを更新するには:"
    echo "    brew upgrade awscli  # macOSの場合"
    echo "    pip install --upgrade awscli  # pipの場合"
    echo ""
    echo "  注意: この警告はデプロイを妨げませんが、Lambda関数の実行時にBedrockアクセスが必要です"
else
    # bedrockコマンドが存在する場合、list-foundation-modelsを実行
    BEDROCK_ERROR=$(aws bedrock list-foundation-models --region $AWS_REGION --profile $AWS_PROFILE 2>&1 | head -10)
    BEDROCK_EXIT_CODE=$?
    
    if [ $BEDROCK_EXIT_CODE -eq 0 ]; then
        print_success "Bedrockへのアクセスを確認"
    else
        print_warning "Bedrockアクセスの確認に失敗しました"
        # エラーの詳細を表示
        if [[ "$BEDROCK_ERROR" == *"UnrecognizedClientException"* ]]; then
            echo "  → Bedrockがこのリージョンで有効化されていない可能性があります"
        elif [[ "$BEDROCK_ERROR" == *"AccessDeniedException"* ]]; then
            echo "  → IAM権限が不足しています。bedrock:ListFoundationModels権限が必要です"
        else
            echo "  → エラー: ${BEDROCK_ERROR}"
        fi
        echo ""
        echo "  注意: この警告はデプロイを妨げませんが、Lambda関数の実行時にBedrockアクセスが必要です"
    fi
fi

set -e

# 依存関係のインストール
echo ""
print_info "CDK依存関係をインストール中..."
uv pip install aws-cdk-lib constructs --quiet

# Lambda Layerの構築
echo ""
print_info "Lambda Layerを構築中..."
if python build_layer.py; then
    print_success "Lambda Layerの構築が完了しました"
else
    print_error "Lambda Layerの構築に失敗しました"
    exit 1
fi

# CDK Bootstrapの確認
echo ""
print_info "CDKブートストラップを確認中..."
if cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION --profile $AWS_PROFILE 2>/dev/null; then
    print_success "CDKブートストラップ完了"
else
    print_info "CDKは既にブートストラップ済みです"
fi

# CDKシンセサイズ
echo ""
print_info "CDKシンセサイズ中..."

# スタックタイプに応じたアプリファイルを選択
if [ "$STACK_TYPE" = "migration" ]; then
    export CDK_STACK_TYPE="migration"
    APP_PY="app_migration.py"
elif [ "$STACK_TYPE" = "secure" ]; then
    export CDK_STACK_TYPE="secure"
    APP_PY="app_migration.py"
else
    APP_PY="app.py"
fi

# CDKコンテキストパラメータの構築
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
if [ ! -z "$MODEL_ID" ]; then
    CDK_CONTEXT="$CDK_CONTEXT -c default_model_id=$MODEL_ID"
fi

# スタック名の設定
STACK_NAME="StrandsAgentStack"
if [ "$ENVIRONMENT" != "dev" ]; then
    STACK_NAME="StrandsAgentStack-${ENVIRONMENT}"
fi

if [ -f "$APP_PY" ]; then
    cdk synth $CDK_CONTEXT --app "python $APP_PY" --profile $AWS_PROFILE
else
    cdk synth $CDK_CONTEXT --profile $AWS_PROFILE
fi

if [ $? -eq 0 ]; then
    print_success "CDKシンセサイズが完了しました"
else
    print_error "CDKシンセサイズに失敗しました"
    exit 1
fi

# ドライランモード
if [ "$DRY_RUN" = true ]; then
    echo ""
    print_warning "ドライランモード: 実際のデプロイは行われません"
    exit 0
fi

# デプロイ確認
if [ "$FORCE_DEPLOY" != true ]; then
    echo ""
    print_warning "デプロイを開始します"
    read -p "続行するにはENTERを押すか、キャンセルするにはCtrl+Cを押してください: "
fi

# デプロイ実行
echo ""
print_info "スタックをデプロイ中..."

if [ -f "$APP_PY" ]; then
    cdk deploy $CDK_CONTEXT --app "python $APP_PY" --profile $AWS_PROFILE --require-approval never
else
    cdk deploy $CDK_CONTEXT --profile $AWS_PROFILE --require-approval never
fi

if [ $? -eq 0 ]; then
    echo ""
    print_success "デプロイが正常に完了しました！"
    echo ""
    echo "Lambda Function URLはCloudFormationの出力を確認するか、"
    echo "AWSコンソールで確認してください。URLを使用して以下のようにテストできます:"
    echo "例:"
    echo '  curl -X POST <FUNCTION_URL> \'
    echo '    -H "Content-Type: application/json" \'
    echo '    -d '\''{"prompt": "現在の日時を教えてください"}'\'''
else
    print_error "デプロイに失敗しました"
    exit 1
fi