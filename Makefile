up:
	@docker compose up -d
	@echo "Server running on http://localhost:3000"

down:
	@docker compose down
	@echo "Server stopped"

cp-raycast-script:
	@cp client/raycast.sh /Users/aobaiwaki/Documents/Raycast/scripts