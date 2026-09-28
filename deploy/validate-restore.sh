#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ] || [ ! -f "$1" ]; then
  printf 'Uso: %s /caminho/backup.dump\n' "$0" >&2
  exit 2
fi

project_dir="${PAC_PROJECT_DIR:-/opt/pac-digital-mprj}"
restore_db="pac_restore_validation"
compose="docker compose -f deploy/docker-compose.production.yml -f deploy/docker-compose.edge.yml --env-file .env"
backup="$1"

cd "$project_dir"
cleanup() { $compose exec -T database dropdb -U pac_app --if-exists "$restore_db" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM
cleanup
$compose exec -T database createdb -U pac_app "$restore_db"
$compose exec -T database pg_restore -U pac_app -d "$restore_db" --exit-on-error < "$backup"
$compose exec -T database psql -U pac_app -d "$restore_db" -v ON_ERROR_STOP=1 -Atc "select 'demands=' || count(*) from demands; select 'migrations=' || count(*) from alembic_version;"
printf 'restore_validation=success\n'
