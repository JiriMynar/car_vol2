#!/bin/bash

# Skript pro obnovení databáze systému rezervace firemních vozidel
# Tento skript obnovuje PostgreSQL databázi ze zálohy

# Konfigurace
DB_NAME="car_reservation"
DB_USER="car_reservation_user"
DB_HOST="localhost"
DB_PORT="5432"

# Kontrola, zda byl poskytnut záložní soubor
if [ $# -eq 0 ]; then
    echo "Použití: $0 <backup_file.sql.gz>"
    echo "Příklad: $0 /var/backups/car-reservation/car_reservation_backup_20231201_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Kontrola existence záložního souboru
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Chyba: Záložní soubor '$BACKUP_FILE' nebyl nalezen!"
    exit 1
fi

# Potvrzení obnovení
echo "VAROVÁNÍ: Toto kompletně nahradí současnou databázi!"
echo "Databáze: $DB_NAME"
echo "Záložní soubor: $BACKUP_FILE"
read -p "Jste si jisti, že chcete pokračovat? (ano/ne): " CONFIRM

if [ "$CONFIRM" != "ano" ]; then
    echo "Obnovení bylo zrušeno."
    exit 0
fi

# Vytvoření dočasného adresáře pro extrakci
TEMP_DIR=$(mktemp -d)
TEMP_SQL="$TEMP_DIR/restore.sql"

# Extrakce záložního souboru
echo "Extrahuji záložní soubor..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"
else
    cp "$BACKUP_FILE" "$TEMP_SQL"
fi

# Kontrola úspěšnosti extrakce
if [ $? -ne 0 ]; then
    echo "Chyba: Extrakce záložního souboru selhala!"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Zastavení aplikace (pokud běží)
echo "Zastavuji aplikační služby..."
# systemctl stop car-reservation  # Odkomentujte při použití systemd

# Obnovení databáze
echo "Spouštím obnovení databáze..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
    --no-password --quiet < "$TEMP_SQL"

# Kontrola úspěšnosti obnovení
if [ $? -eq 0 ]; then
    echo "Obnovení databáze bylo úspěšně dokončeno!"
else
    echo "Chyba: Obnovení databáze selhalo!"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Vyčištění dočasných souborů
rm -rf "$TEMP_DIR"

# Spuštění aplikace (pokud byla zastavena)
echo "Spouštím aplikační služby..."
# systemctl start car-reservation  # Odkomentujte při použití systemd

echo "Proces obnovení byl dokončen."
echo "Prosím ověřte, že aplikace funguje správně."

