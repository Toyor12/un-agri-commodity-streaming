sed -i '' 's/# UN Agricultural Commodity Streaming Pipeline/# UN Agricultural Commodity Streaming Pipeline\n\n![Pipeline CI](https:\/\/github.com\/Toyor12\/un-agri-commodity-streaming\/actions\/workflows\/ci.yml\/badge.svg)/' README.md
git add README.md
git commit -m "docs: add CI badge to README"
git push origin main
