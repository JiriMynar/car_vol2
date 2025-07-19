#!/bin/bash

# Skript pro zálohování databáze systému rezervace firemních vozidel
# Tento skript vytváří zálohu PostgreSQL databáze

# Konfigurace
DB_NAME="car_reservation"
DB_USER="car_reservation_user"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="/var/backups/car-reservation"
RETENTION_DAYS=30

# Vytvoření adresáře pro zálohy, pokud neexistuje
mkdir -p "$BACKUP_DIR"

# Generování názvu záložního souboru s časovým razítkem
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/car_reservation_backup_$TIMESTAMP.sql"

# Vytvoření zálohy
echo "Spouštím zálohování databáze..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-password --verbose --clean --if-exists --create \
    > "$BACKUP_FILE"

# Kontrola úspěšnosti zálohy
if [ $? -eq 0 ]; then
    echo "Záloha byla úspěšně dokončena: $BACKUP_FILE"
    
    # Komprese zálohy
    gzip "$BACKUP_FILE"
    echo "Záloha byla zkomprimována: $BACKUP_FILE.gz"
    
    # Odstranění starých záloh (starších než RETENTION_DAYS)
    find "$BACKUP_DIR" -name "car_reservation_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Staré zálohy byly vyčištěny (starší než $RETENTION_DAYS dní)"
    
else
    echo "Zálohování selhalo!"
    exit 1
fi

# Volitelné: Nahrání do cloudového úložiště nebo vzdáleného serveru
# Příklad pro rsync na vzdálený server:
# rsync -av "$BACKUP_FILE.gz" user@backup-server:/path/to/backups/

echo "Proces zálohování byl dokončen."

