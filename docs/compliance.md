# 要件適合マトリクス

この表は正本仕様と実装・機械検証の対応を示します。命令そのものは `templates/`、引き継ぎ型は `schema/handoff.schema.json` を優先します。

| 要件群 | 実装箇所 | 検証 | 状態 |
|---|---|---|---|
| タイトル一行、最初の次、1ターン1Phase、停止文、完了文 | 通常正本「会話状態と進行」 | validator必須文検査 | implemented and verified |
| Phase1〜14と独立したPhase15 | 通常正本・更新正本 | Phase見出しの順序・重複検査 | implemented and verified |
| 新規投資家としての独立性と迎合・逆張り防止 | 通常正本「全体原則」 | 文書レビュー | implemented and verified |
| 事実、会社主張、コンセンサス、仮定、推論、未確認の分類 | 両正本「全体原則／共通規律」 | 必須要素検査 | implemented and verified |
| データ信頼度、シナリオ確率、判断頑健性 | 通常正本、schema | enum・型・合計100検査 | implemented and verified |
| Phase1固定スナップショット、証拠台帳、目標株価非表示 | 通常正本 Phase1 | validator必須文検査 | implemented and verified |
| 希薄化ブリッジと共通の1株価値分母 | 通常正本「株式数の共通定義」・Phase1/3/10/11 | validator必須文検査 | implemented and verified |
| Phase2事業構造、依存関係、3〜6 KPIと価値への因果鎖 | 通常正本 Phase2 | 責務表とのレビュー | implemented and verified |
| Phase3会計品質、資本構造、資金繰り、株主価値検証 | 通常正本 Phase3 | 責務表とのレビュー | implemented and verified |
| Phase4物語の該当性、価値経路、現実との乖離 | 通常正本 Phase4 | 責務表とのレビュー | implemented and verified |
| Phase5強気仮説の変数→KPI→財務→価値経路 | 通常正本 Phase5 | 責務表とのレビュー | implemented and verified |
| Phase6独立した弱気仮説と失敗連鎖 | 通常正本 Phase6 | 責務表とのレビュー | implemented and verified |
| Phase7ファンダメンタルズ、比較調整、異常反応 | 通常正本 Phase7 | 責務表とのレビュー | implemented and verified |
| Phase8観測可能なクラックス、因果階層、二重計上防止 | 通常正本 Phase8 | 文書・サンプルレビュー | implemented and verified |
| Phase9独立判断、相互排他的共同シナリオ、合計100% | 通常正本 Phase9、schema | validator確率・名称検査 | implemented and verified |
| Phase10再現可能な評価式、希薄化、現在価値、目標株価参照順 | 通常正本 Phase10 | validator必須文検査 | implemented and verified |
| Phase11の0〜1、1〜3、3〜12、12〜36カ月 | 通常正本 Phase11 | 責務表とのレビュー | implemented and verified |
| Phase12投資適格性と売買執行の分離、価格条件3分類 | 通常正本 Phase12 | 禁止表現検査・文書レビュー | implemented and verified |
| Phase13原因別モニタリングと根拠ある更新幅 | 通常正本 Phase13 | 責務表とのレビュー | implemented and verified |
| Phase14新規分析なし、カード、FACTS/JUDGMENTS | 通常正本 Phase14、schema | schemaキー・サンプル検査 | implemented and verified |
| Phase15で事実差分を判断変更より先に処理 | 更新正本 Phase15 | 手順順序・更新サンプルレビュー | implemented and verified |
| リベース時の評価再計算 | 両正本 | validator必須語・更新手順レビュー | implemented and verified |
| 厳格な引き継ぎデータ契約 | schema | schema自己整合・instance検査 | implemented and verified |
| UTF-8、LF、Markdown構造 | 全Markdown | validator構造検査 | implemented and verified |
| 外部API、実データ取得、注文実行基盤 | 実装対象外 | リポジトリ構成レビュー | not applicable |
| 利用者認証や外部権限が必要な作業 | なし | ローカル検証 | blockedなし |

## 最終照合の判断

Phase1〜3は投資判断禁止を明記し、Phase4は物語の該当性だけを限定評価します。投資適格性はPhase12まで出しません。固定基準、経済的完全希薄化株式数、因果モデル、共同シナリオ、再現可能な評価、4期間、モニタリング、事実先行の更新はそれぞれ固有のPhaseへ配置しました。競合比較は対象企業評価の材料に限定し、注文執行と投資候補選択は実装していません。
