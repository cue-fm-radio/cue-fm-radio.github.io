# Cue-FM浜松 & エンカレ！ 公式サイト

公開先: https://cue-fm-radio.github.io/

- index.html: 2サイトを選べるポータル
- cue-fm.html: サークル紹介・活動・見学・連絡先
- enkare.html: 番組紹介（公開時に最新回を挿入）
- episodes.html: 配信一覧（公開時にRSSで置換）
- gallery.html: 活動写真6枚・動画2本
- contact.html: 番組おたより（フォーム改修中）

## RSS自動更新

フィード: https://anchor.fm/s/ec273278/podcast/rss
GitHub Actionsの .github/workflows/rss-pages.yml が毎週木曜12:45日本時間（03:45 UTC）に実行されます。mainへの変更時とActionsのRun workflowからも更新可能です。実行時間には遅延があり、RSS公開が実行後の場合は次回更新になります。

update_rss.py がRSSを取得し、エピソード一覧と最新回を生成してGitHub Pagesへ公開します。タイトル・説明・画像・配信ページリンクを取り込みます。HTMLは文字列として処理し、管理者のメール情報は出力しません。取得に失敗した場合は公開を止め、既存サイトを保持します。

HTMLのソースはテンプレートです。生成済みページをそのままソースへ上書きしないでください。公開リポジトリでは60日間操作がないと定期実行が無効になるため、Actionsの状態を定期的に確認してください。

旧サイトはGit履歴 c923780ccbcccb7f5e4694a89baa06d473b853c8 と公開前ZIPに保存。Wixサイトは変更していません。
