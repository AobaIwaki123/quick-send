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

# --- Cloud Run Deployment ---

PROJECT_ID ?= your-project-id
REGION ?= asia-northeast1
SERVICE_NAME ?= quick-send-api
IMAGE_NAME ?= gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)

gcp-build: ## Dockerイメージをビルド (Google Cloud Build)
	gcloud builds submit --tag $(IMAGE_NAME) .

gcp-deploy: ## Cloud Run へデプロイ
	gcloud run deploy $(SERVICE_NAME) \
		--image $(IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--set-env-vars PROJECT_ID=$(PROJECT_ID)

gcp-config: ## デプロイ設定の確認
	@echo "Project: $(PROJECT_ID)"
	@echo "Region:  $(REGION)"
	@echo "Image:   $(IMAGE_NAME)"

# --- Memos Cloud Run Deployment ---

MEMOS_SERVICE_NAME ?= memos
MEMOS_DB_INSTANCE ?= $(PROJECT_ID):$(REGION):memos-db
MEMOS_DB_PASS ?= your-password

gcp-deploy-memos: ## Memos 本体を Cloud Run へデプロイ
	gcloud run deploy $(MEMOS_SERVICE_NAME) \
		--image neosmemo/memos:stable \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--add-cloudsql-instances $(MEMOS_DB_INSTANCE) \
		--set-env-vars DRIVER=postgres \
		--set-env-vars DSN="postgresql://memos:$(MEMOS_DB_PASS)@localhost/memos?host=/cloudsql/$(MEMOS_DB_INSTANCE)" \
		--port 5230