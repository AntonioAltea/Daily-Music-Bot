run:
	python3 src/main.py

clean:
	@echo "Cleaning database..."
	@ - rm -f db/*

docker-build:
	docker build --rm -t daily-music-bot .

docker-run:
	docker run --rm daily-music-bot

docker-rm-dangling:
	@docker rmi $(docker images -f "dangling=true" -q)

fly-destroy:
	flyctl apps destroy daily-music-bot

fly-create:
	flyctl apps create daily-music-bot
	flyctl deploy

fly-console:
	flyctl ssh console

fly-stop:
	flyctl scale count 0

fly-resume:
	flyctl scale count 1

fly-proxy:
	fly proxy 10022:22

fly-download-database:
	scp -r -P 10022 root@localhost:/db/ .

fly-upload-database:
	scp -P 10022 db/* root@localhost:/db/

fly-upload-env:
	scp -P 10022 .env root@localhost:.env

fly-ssh-key:
	flyctl ssh issue --agent