# Návod pro nasazení do produkce

Tento dokument obsahuje detailní instrukce pro nasazení systému rezervace firemních vozidel na Linux server.

## Požadavky na server

### Minimální konfigurace
- **OS**: Ubuntu 20.04 LTS nebo novější / CentOS 8+ / Debian 11+
- **RAM**: 2 GB (doporučeno 4 GB)
- **Disk**: 20 GB volného místa
- **CPU**: 2 jádra (doporučeno)
- **Síť**: Veřejná IP adresa a doménové jméno

### Požadovaný software
- Python 3.11+
- Node.js 20+
- PostgreSQL 13+
- Nginx (doporučeno)
- Certbot (pro SSL)

## Příprava serveru

### 1. Aktualizace systému
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Instalace základních balíčků
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git curl

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm postgresql postgresql-server postgresql-contrib nginx git curl
```

### 3. Konfigurace PostgreSQL
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL (první spuštění)
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Vytvoření databáze a uživatele
sudo -u postgres psql << EOF
CREATE DATABASE car_reservation;
CREATE USER car_reservation_user WITH PASSWORD 'VašeSkutečněBezpečnéHeslo123!';
GRANT ALL PRIVILEGES ON DATABASE car_reservation TO car_reservation_user;
ALTER USER car_reservation_user CREATEDB;
\\q
EOF
```

### 4. Konfigurace firewallu
```bash
# Ubuntu (ufw)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Nasazení aplikace

### 1. Vytvoření uživatele pro aplikaci
```bash
sudo useradd -m -s /bin/bash carreservation
sudo usermod -aG sudo carreservation  # Volitelné pro admin přístup
```

### 2. Stažení a příprava kódu
```bash
# Přepnutí na aplikačního uživatele
sudo su - carreservation

# Stažení kódu (nahraďte URL vaším repozitářem)
git clone https://github.com/your-company/car-reservation-system.git
cd car-reservation-system

# Nebo rozbalení ZIP souboru
# unzip car-reservation-system.zip
# cd car-reservation-system
```

### 3. Konfigurace backendu
```bash
cd car_reservation_backend

# Vytvoření virtuálního prostředí
python3 -m venv venv
source venv/bin/activate

# Instalace závislostí
pip install -r requirements.txt
pip install gunicorn  # WSGI server pro produkci

# Konfigurace prostředí
cp .env.example .env

# Úprava .env souboru
nano .env
```

Upravte `.env` soubor s produkčními hodnotami:
```bash
# Databázová konfigurace
DATABASE_URL=postgresql://car_reservation_user:VašeSkutečněBezpečnéHeslo123!@localhost:5432/car_reservation

# Flask konfigurace
SECRET_KEY=vygenerujte-velmi-bezpečný-klíč-zde
JWT_SECRET_KEY=vygenerujte-jiný-bezpečný-klíč-zde

# Aplikační konfigurace
FLASK_ENV=production
FLASK_DEBUG=False

# CORS konfigurace (nahraďte vaší doménou)
CORS_ORIGINS=https://yourdomain.com

# Logování
LOG_LEVEL=INFO
LOG_FILE=/var/log/car-reservation/app.log

# Zálohování
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
```

### 4. Inicializace databáze
```bash
# Spuštění databázových skriptů
cd database
psql -U car_reservation_user -d car_reservation -h localhost -f schema.sql
psql -U car_reservation_user -d car_reservation -h localhost -f initial_data.sql
cd ..
```

### 5. Build a konfigurace frontendu
```bash
cd ../car_reservation_frontend

# Instalace závislostí
npm install

# Konfigurace API URL pro produkci
echo 'VITE_API_URL=https://yourdomain.com/api' > .env.production

# Build produkční verze
npm run build

# Zkopírování do backend static složky
mkdir -p ../car_reservation_backend/src/static
cp -r dist/* ../car_reservation_backend/src/static/

cd ../car_reservation_backend
```

### 6. Test aplikace
```bash
# Aktivace virtuálního prostředí
source venv/bin/activate

# Test spuštění
python src/main.py

# Aplikace by měla být dostupná na http://server-ip:5000
# Ukončete testování pomocí Ctrl+C
```

## Konfigurace systémových služeb

### 1. Vytvoření systemd služby
```bash
sudo nano /etc/systemd/system/car-reservation.service
```

Obsah souboru:
```ini
[Unit]
Description=Car Reservation System
After=network.target postgresql.service

[Service]
Type=exec
User=carreservation
Group=carreservation
WorkingDirectory=/home/carreservation/car-reservation-system/car_reservation_backend
Environment=PATH=/home/carreservation/car-reservation-system/car_reservation_backend/venv/bin
ExecStart=/home/carreservation/car-reservation-system/car_reservation_backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Spuštění a povolení služby
```bash
sudo systemctl daemon-reload
sudo systemctl start car-reservation
sudo systemctl enable car-reservation
sudo systemctl status car-reservation
```

### 3. Konfigurace logování
```bash
# Vytvoření adresáře pro logy
sudo mkdir -p /var/log/car-reservation
sudo chown carreservation:carreservation /var/log/car-reservation

# Konfigurace logrotate
sudo nano /etc/logrotate.d/car-reservation
```

Obsah logrotate konfigurace:
```
/var/log/car-reservation/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 carreservation carreservation
    postrotate
        systemctl reload car-reservation
    endscript
}
```

## Konfigurace Nginx

### 1. Vytvoření konfigurace
```bash
sudo nano /etc/nginx/sites-available/car-reservation
```

Obsah konfigurace:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Přesměrování na HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL konfigurace (bude nastavena certbotem)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Bezpečnostní hlavičky
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip komprese
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;

    # Statické soubory
    location /static/ {
        alias /home/carreservation/car-reservation-system/car_reservation_backend/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API endpointy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend aplikace
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Velikost uploadu
    client_max_body_size 16M;
}
```

### 2. Povolení konfigurace
```bash
sudo ln -s /etc/nginx/sites-available/car-reservation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## SSL certifikát

### 1. Instalace Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 2. Získání SSL certifikátu
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Automatické obnovení
```bash
# Test automatického obnovení
sudo certbot renew --dry-run

# Cron job je obvykle nastaven automaticky, ale můžete zkontrolovat:
sudo crontab -l
```

## Konfigurace zálohování

### 1. Nastavení automatického zálohování
```bash
# Vytvoření adresáře pro zálohy
sudo mkdir -p /var/backups/car-reservation
sudo chown carreservation:carreservation /var/backups/car-reservation

# Nastavení cron jobu pro uživatele carreservation
sudo su - carreservation
crontab -e
```

Přidejte řádek pro denní zálohu:
```bash
0 2 * * * /home/carreservation/car-reservation-system/car_reservation_backend/database/backup.sh
```

### 2. Test zálohování
```bash
cd /home/carreservation/car-reservation-system/car_reservation_backend/database
./backup.sh
```

## Monitoring a údržba

### 1. Kontrola stavu služeb
```bash
# Stav aplikace
sudo systemctl status car-reservation

# Stav databáze
sudo systemctl status postgresql

# Stav webového serveru
sudo systemctl status nginx

# Logy aplikace
sudo journalctl -u car-reservation -f

# Logy Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Aktualizace aplikace
```bash
# Přepnutí na aplikačního uživatele
sudo su - carreservation
cd car-reservation-system

# Stažení aktualizací
git pull origin main

# Aktualizace backendu
cd car_reservation_backend
source venv/bin/activate
pip install -r requirements.txt

# Aktualizace frontendu
cd ../car_reservation_frontend
npm install
npm run build
cp -r dist/* ../car_reservation_backend/src/static/

# Restart služby
sudo systemctl restart car-reservation
```

### 3. Monitoring výkonu
```bash
# Instalace htop pro monitoring
sudo apt install htop

# Monitoring procesů
htop

# Monitoring diskového prostoru
df -h

# Monitoring paměti
free -h

# Monitoring síťového provozu
sudo netstat -tulpn | grep :443
```

## Řešení problémů

### Časté problémy a řešení

1. **Aplikace se nespustí**
   ```bash
   # Kontrola logů
   sudo journalctl -u car-reservation -n 50
   
   # Kontrola konfigurace
   sudo systemctl status car-reservation
   ```

2. **Databázové připojení selhává**
   ```bash
   # Test připojení
   psql -U car_reservation_user -d car_reservation -h localhost
   
   # Kontrola PostgreSQL
   sudo systemctl status postgresql
   ```

3. **Nginx chyby**
   ```bash
   # Test konfigurace
   sudo nginx -t
   
   # Kontrola logů
   sudo tail -f /var/log/nginx/error.log
   ```

4. **SSL problémy**
   ```bash
   # Obnovení certifikátu
   sudo certbot renew
   
   # Kontrola platnosti
   sudo certbot certificates
   ```

### Kontakty pro podporu

V případě problémů kontaktujte:
- Systémového administrátora
- Vývojový tým
- IT helpdesk

## Bezpečnostní doporučení

1. **Pravidelné aktualizace**
   - Aktualizujte operační systém měsíčně
   - Aktualizujte aplikační závislosti při každé nové verzi

2. **Monitoring bezpečnosti**
   - Nastavte fail2ban pro ochranu před útoky
   - Monitorujte přístupové logy
   - Používejte silná hesla a klíče

3. **Zálohy**
   - Testujte obnovení ze záloh měsíčně
   - Uchovávejte zálohy na vzdáleném místě
   - Šifrujte citlivé zálohy

4. **Síťová bezpečnost**
   - Používejte firewall
   - Omezujte SSH přístup
   - Monitorujte síťový provoz

