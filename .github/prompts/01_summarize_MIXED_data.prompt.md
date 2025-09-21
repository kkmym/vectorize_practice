JSONに記載されている内容をサマリしたうえで、JSONファイルに追記してほしい。

対象となるJSONファイルは `data/rds_results_MIXED_20250913.json`

`jobs` 配列に複数の求人情報が含まれていて、各求人は以下の項目を持っている。
- content.job.title
- content.job.description
- content.job.requirements
- content.company.company_features

以下の内容を含むよう、全部で300文字程度にサマリしてほしい。
- 必要とされるスキル・経験
- その仕事で取り組める業務内容

サマリした結果は各求人に `content.summary` として追記して。
