.PHONY: help up down collect train eval clean

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Memosを起動
	docker compose up -d
	@echo "Memos: http://localhost:5230"

down: ## Memosを停止
	docker compose down

collect: ## Memosからデータを収集
	python scripts/collect_from_memos.py

learn-patterns: ## 収集データからパターンを学習
	python scripts/learn_patterns.py

train: ## 学習データを準備 (Vertex AI用、オプション)
	python scripts/train_model.py

clean: ## 生成ファイルを削除
	rm -rf data/*.json data/*.jsonl
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install: ## 依存パッケージをインストール
	pip install -r requirements.txt

cp-raycast-script: ## Raycastスクリプトをコピー (要ACCESS_TOKEN設定)
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please create it from .env.example"; \
		exit 1; \
	fi
	@. ./.env && \
	sed "s/PLACE_HOLDER/$$ACCESS_TOKEN/" raycast/quick-send.rb > ~/raycast-scripts/quick-send.rb && \
	chmod +x ~/raycast-scripts/quick-send.rb && \
	echo "✅ Raycast script copied to ~/raycast-scripts/"

format: ## コードフォーマット
	black scripts/ src/
	
lint: ## コードチェック
	flake8 scripts/ src/
	mypy scripts/ src/

test: ## テスト実行
	pytest tests/