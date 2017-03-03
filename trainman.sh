#!/bin/bash
celery -A trainman worker -c 1 -l info
