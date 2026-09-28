#!/usr/bin/env sh
set -eu

project_dir="${PAC_PROJECT_DIR:-/opt/pac-digital-mprj}"
backup_dir="${PAC_BACKUP_DIR:-$project_dir/backups}"
compose="docker compose -f deploy/docker-compose.production.yml -f deploy/docker-compose.edge.yml --env-file .env"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup="$backup_dir/pac-digital-$timestamp.dump"

cd "$project_dir"
install -d -m 0700 "$backup_dir"
$compose exec -T database pg_dump -U pac_app -d pac_digital -Fc > "$backup"
chmod 0600 "$backup"
sha256sum "$backup" > "$backup.sha256"
printf '%s\n' "$backup"
