build:
	@bash build.sh

deploy:
	@make build
	@bash deploy.sh apply
	@kubectl delete pods --all

delete:
	@bash deploy.sh delete
