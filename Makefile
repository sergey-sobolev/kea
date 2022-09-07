pipenv:
	pipenv install -r requirements.txt --python 3.8

prepare: pipenv

image:
	docker build . -t kea

run-analyzer-container:
	docker run -v ${PWD}/expected.txt:/kea/expected.txt -v ${PWD}/states.def:/kea/states.def --network secure-update_default kea

run-analyzer:	
	pipenv run python kea/analyzer.py ./config.ini --states_def ./states.def --expect ./expected.txt --checker ./sq_checker

run: run-analyzer-container