run:
	python3 src/main.py

clean:
	@echo "Cleaning database..."
	@ - rm -f db/*

built-image:
	docker build -t daily-music-bot .

run-image:
	docker run daily-music-bot

stop-fly:
	flyctl scale count 0

start-fly:
	flyctl scale count 1
