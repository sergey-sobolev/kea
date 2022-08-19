pipenv:
	pipenv install -r requirements.txt --python 3.8

prepare: pipenv

image:
	docker build . -t kea

run-analyzer-container:
	docker run --network secure-update_default kea

run-analyzer:	
	pipenv run python kea/analyzer.py ./config.ini

run: run-analyzer-container