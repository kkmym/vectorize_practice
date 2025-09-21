## vectorize_practice

PoC 用のベクトル化・検索・要約スクリプト群です。

### 構成

- `data/` 求人JSONなどのサンプルデータ
- `src/01_PoC/01_tfidf_python.py` TF-IDF によるベクトル化のPoC
- `src/01_PoC/02_bm25_python.py` BM25 によるスコアリングのPoC
- `src/01_PoC/03_summarize_mixed_data.py` MIXED求人JSONに要約 `content.summary` を追記（約300文字の単一テキスト。`--max-chars`で変更可）

### セットアップ

Python 3.11 での実行を想定。必要なら `requirements.txt` をインストールしてください。

### 使い方（要約追記）

`data/rds_results_MIXED_20250913.json` を読み込み、各求人に約300文字の単一テキスト要約を追加します。
要約には次の要素を圧縮して含めます：業務、必須/歓迎スキル、会社概要。

実行例（上書き保存。自動で `.bak` を作成）:

```
python -m src.01_PoC.03_summarize_mixed_data --input data/rds_results_MIXED_20250913.json --max-chars 300
```

出力:
- 標準出力に処理件数を表示
- 入力JSONを上書き（バックアップ: `data/rds_results_MIXED_20250913.json.bak`）

### 備考

- Dockerfile / devcontainer での実行も可能です。
