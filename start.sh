#!/bin/bash
cd ravager
python config.py
python housekeeping.py
python services/aria/handler.py &
P1=$!
gunicorn -b 0.0.0.0:${PORT} main:app &
P2=$!
celery -A ravager.celery_tasks.tasks purge -f
celery -A ravager.celery_tasks.tasks  worker -B  --loglevel info --concurrency 5 --autoscale=10,5 --logfile ../logs/celery.log --events --pool prefork &
P3=$!
wait $P1 $P2 $P3