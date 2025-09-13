import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from fugashi import GenericTagger
import numpy as np

def search(X, vectorizer, df, query, topk=3):
    qv = vectorizer.transform([query])
    scores = (X @ qv.T).toarray().ravel()  # コサイン風（正規化しない簡易版）
    idx = np.argsort(-scores)[:topk]
    return df.iloc[idx][["id"]], scores[idx]

def tokenize_ja(text):
    tagger = GenericTagger('-d /var/lib/mecab/dic/ipadic-utf8')
    return [w.surface for w in tagger(text) if len(w.feature) > 0 and w.feature[0] not in ("助詞","助動詞","記号")]

def extract_all_text(content):
    """contentの中の全てのテキストを再帰的に抽出して結合する"""
    def extract_text_recursive(obj, texts):
        if isinstance(obj, dict):
            for value in obj.values():
                extract_text_recursive(value, texts)
        elif isinstance(obj, list):
            for item in obj:
                extract_text_recursive(item, texts)
        elif isinstance(obj, str):
            texts.append(obj)
    
    texts = []
    extract_text_recursive(content, texts)
    return ' '.join(texts)

def main():
    # JSONファイルを読み込み
    with open('../../data/rds_results_CTO_20250911113820.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # "jobs"配列をDataFrameに変換
    df = pd.DataFrame(data['jobs'])
    print("DataFrame作成")
    print(f"行数: {len(df)}")
    
    # all_text項目を追加
    df['all_text'] = df['content'].apply(extract_all_text)
    print("\nSTEP2完了: all_text項目を追加")

    # TF-IDFベクトル化
    vectorizer = TfidfVectorizer(tokenizer=tokenize_ja, token_pattern=None, min_df=1, ngram_range=(1,2))
    X = vectorizer.fit_transform(df["all_text"])

    # TF-IDFに対してクエリ実行
    print(search(X, vectorizer, df, "Fintechサービスの開発をリード。技術戦略策定に関わる仕事。"))

if __name__ == "__main__":
    main()
