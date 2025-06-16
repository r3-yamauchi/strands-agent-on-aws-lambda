#!/usr/bin/env python3
"""
依存関係を含むLambda Layerをビルド
"""
import os
import shutil
import subprocess
import sys


def build_layer():
    """依存関係を含むLambda Layerをビルド"""
    print("Lambda Layerをビルド中...")
    
    # ディレクトリ構造を作成
    layer_dir = "lambda_layer"
    python_dir = os.path.join(layer_dir, "python")
    
    # 既存のレイヤーディレクトリをクリーンアップ
    if os.path.exists(layer_dir):
        shutil.rmtree(layer_dir)
    
    os.makedirs(python_dir)
    
    # uvが利用可能か確認
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        use_uv = True
        print("uvを使用して依存関係をインストール...")
    except (subprocess.CalledProcessError, FileNotFoundError):
        use_uv = False
        print("uvが見つかりません、pipにフォールバックします...")
    
    # レイヤーディレクトリに依存関係をインストール
    print("依存関係をインストール中...")
    if use_uv:
        # pyproject.tomlからrequirementsをエクスポート
        subprocess.check_call([
            "uv", "pip", "compile", "pyproject.toml",
            "-o", "requirements-lambda.txt",
            "--no-emit-package", "strands-agent-lambda"
        ])
        
        # uvを使用してインストール
        subprocess.check_call([
            "uv", "pip", "install",
            "-r", "requirements-lambda.txt",
            "--target", python_dir,
            "--python-platform", "aarch64-unknown-linux-gnu",
            "--python-version", "3.11"
        ])
        
        # 一時ファイルをクリーンアップ
        os.remove("requirements-lambda.txt")
    else:
        # pipにフォールバック
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", "requirements.txt",
            "-t", python_dir,
            "--platform", "manylinux2014_aarch64",
            "--only-binary", ":all:",
            "--upgrade"
        ])
    
    # レイヤーサイズを削減するため不要なファイルを削除
    print("不要なファイルをクリーンアップ中...")
    for root, dirs, files in os.walk(python_dir):
        # __pycache__ディレクトリを削除
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
        
        # .pycファイルを削除
        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo"):
                os.remove(os.path.join(root, file))
        
        # テストディレクトリを削除
        for dir_name in ["tests", "test", "__tests__", "testing"]:
            if dir_name in dirs:
                shutil.rmtree(os.path.join(root, dir_name))
    
    print(f"Lambda Layerが{layer_dir}/に正常にビルドされました")
    
    # レイヤーサイズを確認
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(layer_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    print(f"レイヤーサイズ: {total_size / 1024 / 1024:.2f} MB")
    if total_size > 250 * 1024 * 1024:  # 250 MB制限
        print("警告: レイヤーサイズがLambdaの250MB制限を超えています！")


if __name__ == "__main__":
    build_layer()