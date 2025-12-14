.PHONY: help up down logs collect learn clean cp-raycast-scripts

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Memos + API Server を起動
	docker compose up -d
	@echo "Memos: http://localhost:5230"
	@echo "API:   http://localhost:8080"

down: ## 停止
	docker compose down

restart: down up

logs: ## ログを表示
	docker compose logs

health: ## 健康チェック
	@curl -s http://localhost:8080/health | python3 -m json.tool

collect: ## データを収集 (API経由)
	@curl -s -X POST http://localhost:8080/collect | python3 -m json.tool

learn: ## パターン学習 (API経由)
	@curl -s -X POST http://localhost:8080/learn | python3 -m json.tool

patterns: ## 学習済みパターンを表示 (API経由)
	@curl -s http://localhost:8080/patterns | python3 -m json.tool

clean: ## 生成ファイルを削除
	rm -rf memos_data/*.json memos_data/*.jsonl
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

cp-raycast-scripts: ## Raycastスクリプトをコピー
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found"; \
		exit 1; \
	fi
	@. ./.env && \
	sed "s/PLACE_HOLDER/$$MEMOS_ACCESS_TOKEN/" client/raycast.rb > /Users/aobaiwaki/Documents/Raycast/scripts/raycast.rb && \
	cp client/learn-patterns.rb /Users/aobaiwaki/Documents/Raycast/scripts/learn-patterns.rb && \
	echo "✅ Raycast scripts copied to /Users/aobaiwaki/Documents/Raycast/scripts/"