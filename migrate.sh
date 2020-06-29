#!/bin/bash
docker-compose exec backend /bin/bash -c "flask db init; flask db migrate -m 'init db'; flask db upgrade"
docker-compose exec postgres psql -c "INSERT INTO types (name) VALUES ('Villa'),('Land')" -U balihotproperty
