#!/bin/bash
docker-compose exec backend /bin/bash -c "flask db init; flask db migrate -m 'init db'; flask db upgrade"
