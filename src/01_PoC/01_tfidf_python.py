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
    # return [w.surface for w in tagger(text) if len(w.feature) > 0 and w.feature[0] not in ("助詞","助動詞","記号")]
    return [w.surface for w in tagger(text) if len(w.feature) > 0 and w.feature[0] in ("名詞","動詞","形容詞")]

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

def print_top10_words(X, vectorizer):
    # 各文書で重要な単語上位10語を表示する
    feature_names = np.array(vectorizer.get_feature_names_out())
    for row in X:  # row は 1×V の疎行列
        arr = row.toarray()                       # シンプルに密へ（小規模ならOK）
        idx = np.argsort(arr, axis=1)[:, ::-1]    # 降順インデックス
        print(feature_names[idx][:, :10])         # 上位10語

def main():
    # JSONファイルを読み込み
    with open('../../data/rds_results_MIXED_20250913.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # "jobs"配列をDataFrameに変換
    df = pd.DataFrame(data['jobs'])
    print("DataFrame作成")
    print(f"行数: {len(df)}")
    
    # all_text項目を追加
    # df['all_text'] = df['content'].apply(extract_all_text)
    # print("\nSTEP2完了: all_text項目を追加")

    # 新列 summary を作成（欠損は空文字）
    df['summary'] = df['content'].apply(lambda c: (c or {}).get('summary', ''))

    # TF-IDFベクトル化
    # vectorizer = TfidfVectorizer(tokenizer=tokenize_ja, token_pattern=None, min_df=1, ngram_range=(1,2))
    vectorizer = TfidfVectorizer(tokenizer=tokenize_ja, token_pattern=None, min_df=1)
    X = vectorizer.fit_transform(df["summary"])

    # TF-IDFに対してクエリ実行
    # print(search(X, vectorizer, df, "機械学習 Python 可視化 因果"))
    # print(search(X, vectorizer, df, "可視化 因果 分析 評価"))
    # print(search(X, vectorizer, df, "アーキテクチャ 技術 戦略 選定"))

    print_top10_words(X, vectorizer)

if __name__ == "__main__":
    main()
