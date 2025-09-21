import unicodedata
from typing import List
from sudachipy import dictionary, tokenizer as T

# Sudachiのトークナイザを作成
_tokenizer = dictionary.Dictionary().create()

# 残す品詞の先頭カテゴリ（pos[0]）
_KEEP_POS0 = {"名詞", "動詞", "形容詞"}

def normalize_text(s: str) -> str:
    # 全角/半角や互換文字の正規化＆小文字化（表記ゆれ対策）
    # return unicodedata.normalize("NFKC", s).lower()
    return unicodedata.normalize("NFKC", s) # dictionary_form() を通すと大文字になるワードがあり、ここでやっても意味がない

def tokenize_ja(text: str, mode: T.Tokenizer.SplitMode = T.Tokenizer.SplitMode.C) -> List[str]:
    """
    - Cモードでできるだけ長めに分割
    - 原形（dictionary_form）へ正規化
    - 名詞・動詞・形容詞のみ残す
    """
    text = normalize_text(text)
    morphemes = _tokenizer.tokenize(text, mode=mode)

    tokens: List[str] = []
    for m in morphemes:
        pos0 = m.part_of_speech()[0]  # 例: ('名詞','普通名詞','一般',... ) の先頭
        if pos0 in _KEEP_POS0:
            lemma = m.dictionary_form().lower()  # 原形化 ＋ 小文字に統一
            if lemma and lemma != "":    # 空は弾く
                tokens.append(lemma)
    return tokens

if __name__ == "__main__":
    # txt = "ディープラーニングによるレコメンド開発を行いました。PythonとNLPの知見歓迎。"
    # txt = "業務:スカウトのAIアシスト搭載「engage」をはじめとする、HR Techプロダクトのデータ分析の為の仕組みづくり、データの分析 必須:SQLでのデータ分析実務経験、Pythonでのデータ分析、アルゴリズム開発実務経験"
    txt = "宇宙飛行士の若田光一さんが国際宇宙ステーションの第３９代船長に就任した"
    # print(tokenize_ja(txt))  # 動作確認
    tokenize_ja(txt)
