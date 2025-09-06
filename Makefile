PROJECT=projectcontainer

build:
	docker build --force-rm $(options) -t leafroute-web:latest .

build-prod:
	$(MAKE) build --options="--target production"

compose-start:
	docker-compose -p $(PROJECT) up --remove-orphans $(options) -d

compose-stop:
	docker-compose -p $(PROJECT) down --remove-orphans $(options)

compose-manage-py:
	docker-compose -p $(PROJECT) run --rm website python manage.py $(cmd)

# mysql-start:
# 	docker run  --name mysql-container -p 3306:3306 -e MYSQL_ROOT_PASSWORD=szakdoga -d mysql:8.0