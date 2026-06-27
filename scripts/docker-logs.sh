#!/bin/bash
# Просмотр логов всех сервисов

docker-compose logs -f "$@"