go:
	docker compose up --build -d
logs:
	docker logs mailbot-dokumentacja -f
kill:
	@docker kill $$(docker ps -q --filter "name=mailbot-dokumentacja*")
remove:
	docker rmi -f $$(docker images -q --filter=reference='mailbot-dokumentacja*')

