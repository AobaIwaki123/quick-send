up:
	@docker compose up -d
	@echo "Memos: http://localhost:5230"

down:
	@docker compose down
	@echo "Server stopped"

restart: down up

cp-raycast-script:
	@if [ ! -f .env ]; then echo "❌ .env file not found"; exit 1; fi
	@. ./.env && sed "s/PLACE_HOLDER/$$MEMOS_ACCESS_TOKEN/g" client/raycast.sh > /Users/aobaiwaki/Documents/Raycast/scripts/raycast.sh
	@echo "✅ Copied raycast.sh with ACCESS_TOKEN from .env"