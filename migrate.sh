#!/bin/bash
docker exec -it balihot-property_backend_1 /bin/bash -c "flask db init; flask db migrate -m 'init db'; flask db upgrade"
