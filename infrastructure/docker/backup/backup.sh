#!/bin/bash

set -e

CLIENT_NAME="${CLIENT_NAME}"
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_PASSWORD="${DB_PASSWORD}"
DB_HOST="${DB_HOST:-db}"
S3_BUCKET="${S3_BUCKET}"
S3_PREFIX="${S3_PREFIX}"
RETENTION_DAILY="${RETENTION_DAILY:-7}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-4}"
RETENTION_MONTHLY="${RETENTION_MONTHLY:-3}"
ENCRYPTION_KEY="${ENCRYPTION_KEY}"
GPG_RECIPIENT="${GPG_RECIPIENT}"

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)
DAY_OF_MONTH=$(date +%d)

mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly" "${BACKUP_DIR}/monthly"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2
}

wait_for_db() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" > /dev/null 2>&1; then
            log "Database is ready"
            return 0
        fi
        log "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "Database did not become ready in time"
    return 1
}

create_backup() {
    local backup_type="$1"
    local backup_file="${BACKUP_DIR}/${backup_type}/${CLIENT_NAME}_${backup_type}_${DATE}.sql.gz.enc"
    local temp_file="${BACKUP_DIR}/${backup_type}/${CLIENT_NAME}_${backup_type}_${DATE}.sql.gz"
    
    log "Starting ${backup_type} backup for ${CLIENT_NAME}"
    
    if pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -Fc -f "${temp_file}" 2>/dev/null; then
        log "Database dump created successfully"
    else
        error "Database dump failed"
        return 1
    fi
    
    if [ -n "${ENCRYPTION_KEY}" ] && command -v gpg > /dev/null 2>&1; then
        log "Encrypting backup with GPG"
        echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 -c -o "${backup_file}" "${temp_file}"
        rm -f "${temp_file}"
        backup_file="${temp_file}.enc"
    else
        mv "${temp_file}" "${backup_file}"
    fi
    
    local backup_size=$(du -h "${backup_file}" | cut -f1)
    log "Backup created: ${backup_file} (${backup_size})"
    
    upload_to_s3 "${backup_file}" "${backup_type}"
    
    rm -f "${backup_file}"
}

upload_to_s3() {
    local file="$1"
    local backup_type="$2"
    
    log "Uploading to S3: ${S3_BUCKET}/${S3_PREFIX}${CLIENT_NAME}/${backup_type}/"
    
    if command -v aws > /dev/null 2>&1; then
        aws s3 cp "${file}" "s3://${S3_BUCKET}/${S3_PREFIX}${CLIENT_NAME}/${backup_type}/" \
            --storage-class STANDARD \
            --metadata "client=${CLIENT_NAME},type=${backup_type},date=${DATE}"
    elif command -v mc > /dev/null 2>&1; then
        mc cp "${file}" "s3/${S3_BUCKET}/${S3_PREFIX}${CLIENT_NAME}/${backup_type}/"
    else
        error "Neither AWS CLI nor MinIO Client found"
        return 1
    fi
    
    log "Upload complete"
}

cleanup_old_backups() {
    local backup_type="$1"
    local retention="$2"
    
    log "Cleaning up ${backup_type} backups (retention: ${retention})"
    
    local cutoff_date
    case "$backup_type" in
        daily)
            cutoff_date=$(date -d "-${retention} days" +%Y%m%d)
            ;;
        weekly)
            cutoff_date=$(date -$((retention * 7)) +%Y%m%d)
            ;;
        monthly)
            cutoff_date=$(date -$((retention * 30)) +%Y%m%d)
            ;;
    esac
    
    for file in "${BACKUP_DIR}/${backup_type}"/*.sql.gz.enc; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            local file_date=$(echo "$filename" | grep -oP '\d{8}_\d{6}')
            if [ -n "$file_date" ] && [ "${file_date:0:8}" -lt "$cutoff_date" ]; then
                log "Removing old backup: $file"
                rm -f "$file"
                
                log "Removing from S3: ${S3_PREFIX}${CLIENT_NAME}/${backup_type}/$filename"
                if command -v aws > /dev/null 2>&1; then
                    aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}${CLIENT_NAME}/${backup_type}/$filename"
                fi
            fi
        fi
    done
}

main() {
    log "=== Backup process started for ${CLIENT_NAME} ==="
    
    wait_for_db
    
    create_backup "_old_backups "daily"
    cleanupdaily" "${RETENTION_DAILY}"
    
    if [ "$DAY_OF_WEEK" = "1" ]; then
        create_backup "weekly"
        cleanup_old_backups "weekly" "${RETENTION_WEEKLY}"
    fi
    
    if [ "$DAY_OF_MONTH" = "01" ]; then
        create_backup "monthly"
        cleanup_old_backups "monthly" "${RETENTION_MONTHLY}"
    fi
    
    log "=== Backup process completed ==="
}

if [ "${BACKUP_MODE:-auto}" = "auto" ]; then
    main "$@"
elif [ "${BACKUP_MODE:-auto}" = "restore" ]; then
    echo "Restore mode - waiting for restore command"
    tail -f /dev/null
fi
