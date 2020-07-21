#!/bit/bash
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app --master --processes 5 --threads 3
