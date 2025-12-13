up:
	@docker compose up -d
	@echo "Text Listenr: http://localhost:3000"
	@echo "Viewer: http://localhost:8080"

down:
	@docker compose down
	@echo "Server stopped"

restart: down up

cp-raycast-script:
	@cp client/raycast.sh /Users/aobaiwaki/Documents/Raycast/scripts