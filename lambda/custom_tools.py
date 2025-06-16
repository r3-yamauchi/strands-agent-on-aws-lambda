"""
カスタムツールの実装例
strands-agents-toolsに含まれない独自機能の実装方法
"""
import json
import hashlib
from typing import Dict, Any, Union
from strands import tool


@tool
def generate_hash(text: str, algorithm: str = "sha256") -> Dict[str, Union[str, int]]:
    """
    テキストのハッシュ値を生成します。
    
    Args:
        text: ハッシュ化するテキスト
        algorithm: 使用するアルゴリズム（md5, sha1, sha256, sha512）
        
    Returns:
        ハッシュ値とアルゴリズムを含む辞書
    """
    try:
        if algorithm not in ["md5", "sha1", "sha256", "sha512"]:
            return {"error": f"サポートされていないアルゴリズム: {algorithm}"}
        
        hash_func = getattr(hashlib, algorithm)
        hash_value = hash_func(text.encode()).hexdigest()
        
        return {
            "algorithm": algorithm,
            "hash": hash_value,
            "original_length": len(text)
        }
    except Exception as e:
        return {"error": f"ハッシュ生成エラー: {str(e)}"}


@tool
def json_formatter(json_string: str, indent: int = 2) -> str:
    """
    JSON文字列を整形します。
    
    Args:
        json_string: 整形するJSON文字列
        indent: インデントのスペース数
        
    Returns:
        整形されたJSON文字列
    """
    try:
        data = json.loads(json_string)
        return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True)
    except json.JSONDecodeError as e:
        return f"JSON解析エラー: {str(e)}"
    except Exception as e:
        return f"エラー: {str(e)}"


@tool
def text_analyzer(text: str) -> Dict[str, Any]:
    """
    テキストの基本的な統計情報を分析します。
    
    Args:
        text: 分析するテキスト
        
    Returns:
        文字数、単語数、行数などの統計情報
    """
    try:
        # 基本統計
        char_count = len(text)
        line_count = text.count('\n') + 1 if text else 0
        word_count = len(text.split())
        
        # 文字種別カウント
        uppercase_count = sum(1 for c in text if c.isupper())
        lowercase_count = sum(1 for c in text if c.islower())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        
        # 日本語文字カウント
        hiragana_count = sum(1 for c in text if '\u3040' <= c <= '\u309f')
        katakana_count = sum(1 for c in text if '\u30a0' <= c <= '\u30ff')
        kanji_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        
        return {
            "総文字数": char_count,
            "単語数": word_count,
            "行数": line_count,
            "文字種別": {
                "大文字": uppercase_count,
                "小文字": lowercase_count,
                "数字": digit_count,
                "空白文字": space_count,
                "ひらがな": hiragana_count,
                "カタカナ": katakana_count,
                "漢字": kanji_count
            },
            "平均単語長": round(char_count / word_count, 2) if word_count > 0 else 0
        }
    except Exception as e:
        return {"error": f"テキスト分析エラー: {str(e)}"}




# カスタムツールをエクスポート
__all__ = [
    'generate_hash',
    'json_formatter', 
    'text_analyzer'
]