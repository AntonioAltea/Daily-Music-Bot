run:
	python3 src/main.py

clean:
	@echo "Cleaning database..."
	@ - rm -f db/*

docker-buit:
	docker build -t daily-music-bot .

docker-run:
	docker run daily-music-bot

fly-destroy:
	flyctl apps destroy daily-music-bot

fly-create:
	flyctl apps create daily-music-bot
	flyctl deploy