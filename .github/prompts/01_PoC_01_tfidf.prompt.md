---
mode: 'agent'
model: 'Claude Sonnet 4'
---

# STEP1
DataFrameにJSONファイルを読み込みたい。
下記のようなJSONの場合、どうしたらいい？
```
{"jobs":[この配列の中身をDataFrameに読み込みたい]}
```

# STEP2
DataFrame `df` には配列でデータが入っている。
配列の各要素は以下のような構造を持っている。
```yaml
id: 12345
category: CTO
content:
    job:
        title: カスタマーエンジニア
        description: "顧客のニーズを理解し、最適なソリューションを提供する役割です。"
        requirements: "顧客とのコミュニケーション能力"
    company:
        company_features: "フレックスタイム制度、リモートワーク可"
```

配列の各要素に `all_text` という項目を追加したい。
`all_text` には、`content` 内の全てのテキストを結合したものを入れたい。

# トークナイザーの動作確認
```shell
python -c "
from fugashi import GenericTagger
def tokenize_ja(text):
    tagger = GenericTagger('-d /var/lib/mecab/dic/ipadic-utf8')
    return [w.surface for w in tagger(text) if len(w.feature) > 0 and w.feature[0] not in ('助詞','助動詞','記号')]

print('Tokenizer test:', tokenize_ja('Fintechサービスの開発をリード。技術戦略策定に関わる仕事。'))
"
```