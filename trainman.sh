#!/bin/bash
source ~/venv/bin/activate
celery -A trainman worker --loglevel=info --concurrency=1
