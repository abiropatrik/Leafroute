build:
	docker build --force-rm $(options) -t leafroute-web:latest .

build-prod:
	$(MAKE) build --options="--target production"

compose-start:
	docker-compose up --remove-orphans $(options)

compose-stop:
	docker-compose down --remove-orphans $(options)

compose-manage-py:
	docker-compose run --rm web python manage.py $(options) website python manage.py $(cmd)