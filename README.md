# Systém rezervace firemních vozidel

Kompletní webová aplikace pro správu a rezervaci firemních vozidel s moderním React frontendem a Flask backend API.

## Přehled funkcí

### Pro zaměstnance
- **Přihlášení pomocí intranet ID** - Simulace SSO integrace
- **Prohlížení dostupných vozidel** - Seznam všech aktivních vozidel s detaily
- **Vytváření rezervací** - Rezervace vozidel pro konkrétní časové období
- **Správa vlastních rezervací** - Zobrazení a úprava vlastních rezervací
- **Kalendářové zobrazení** - Přehled rezervací v kalendáři

### Pro administrátory vozového parku
- **Správa vozidel** - Přidávání, úprava a deaktivace vozidel
- **Správa všech rezervací** - Přehled a správa všech rezervací v systému
- **Správa uživatelů** - Správa uživatelských účtů a rolí
- **Servisní záznamy** - Evidence servisních zásahů a údržby
- **Záznamy o poškození** - Evidence škod a oprav vozidel
- **Reporty a statistiky** - Přehledy využití vozového parku

## Technické specifikace

### Backend (Flask)
- **Framework**: Flask 3.x s SQLAlchemy ORM
- **Databáze**: PostgreSQL (produkce) / SQLite (vývoj)
- **Autentizace**: JWT tokeny s mock SSO
- **API**: RESTful API s JSON odpověďmi
- **Dokumentace**: Automaticky generovaná API dokumentace

### Frontend (React)
- **Framework**: React 18 s Vite
- **Styling**: Tailwind CSS s shadcn/ui komponenty
- **Routing**: React Router pro SPA navigaci
- **State Management**: React hooks a Context API
- **HTTP klient**: Axios pro API komunikaci

### Databázové schéma
- **roles** - Role uživatelů (Employee, Fleet Administrator)
- **users** - Uživatelské účty s vazbou na role
- **vehicles** - Vozidla s technickými údaji a stavem
- **reservations** - Rezervace s časovými údaji a účelem
- **service_records** - Servisní záznamy vozidel
- **damage_records** - Záznamy o poškozeních a opravách

## Struktura projektu

```
car_reservation_system/
├── car_reservation_backend/          # Flask backend aplikace
│   ├── src/
│   │   ├── models/                   # SQLAlchemy modely
│   │   ├── routes/                   # API endpointy
│   │   └── main.py                   # Hlavní Flask aplikace
│   ├── database/                     # Databázové skripty
│   │   ├── schema.sql               # PostgreSQL schéma
│   │   ├── initial_data.sql         # Počáteční data
│   │   ├── backup.sh                # Skript pro zálohování
│   │   └── restore.sh               # Skript pro obnovení
│   ├── config.py                    # Konfigurace prostředí
│   ├── .env.example                 # Příklad proměnných prostředí
│   └── requirements.txt             # Python závislosti
├── car_reservation_frontend/         # React frontend aplikace
│   ├── src/
│   │   ├── components/              # React komponenty
│   │   ├── pages/                   # Stránky aplikace
│   │   ├── hooks/                   # Custom React hooks
│   │   └── lib/                     # Utility funkce
│   ├── public/                      # Statické soubory
│   └── package.json                 # Node.js závislosti
└── deployment/                      # Nasazovací skripty a konfigurace
```

## Instalace a spuštění

### Požadavky
- Python 3.11+
- Node.js 20+
- PostgreSQL 13+ (pro produkci)
- Git

### Vývojové prostředí

#### 1. Backend setup
```bash
cd car_reservation_backend

# Vytvoření virtuálního prostředí
python -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\\Scripts\\activate  # Windows

# Instalace závislostí
pip install -r requirements.txt

# Spuštění aplikace (SQLite databáze se vytvoří automaticky)
python src/main.py
```

Backend bude dostupný na `http://localhost:5000`

#### 2. Frontend setup
```bash
cd car_reservation_frontend

# Instalace závislostí
npm install
# nebo
pnpm install

# Spuštění vývojového serveru
npm run dev
# nebo
pnpm run dev
```

Frontend bude dostupný na `http://localhost:5173`

### Produkční nasazení

#### 1. Příprava PostgreSQL databáze
```bash
# Přihlášení jako postgres uživatel
sudo -u postgres psql

# Vytvoření databáze a uživatele
CREATE DATABASE car_reservation;
CREATE USER car_reservation_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE car_reservation TO car_reservation_user;
\\q

# Spuštění databázových skriptů
cd car_reservation_backend/database
psql -U car_reservation_user -d car_reservation -f schema.sql
psql -U car_reservation_user -d car_reservation -f initial_data.sql
```

#### 2. Konfigurace prostředí
```bash
cd car_reservation_backend

# Zkopírování a úprava konfigurace
cp .env.example .env
# Upravte .env soubor s produkčními hodnotami

# Nastavení proměnných prostředí
export FLASK_ENV=production
export DATABASE_URL=postgresql://car_reservation_user:secure_password_here@localhost:5432/car_reservation
```

#### 3. Build a nasazení frontendu
```bash
cd car_reservation_frontend

# Build produkční verze
npm run build
# nebo
pnpm run build

# Zkopírování build souborů do backend static složky
cp -r dist/* ../car_reservation_backend/src/static/
```

#### 4. Spuštění produkční aplikace
```bash
cd car_reservation_backend
source venv/bin/activate

# Spuštění s produkčním WSGI serverem
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## Demo účty

Pro testování aplikace jsou k dispozici následující demo účty:

- **admin** - Administrátor vozového parku s plnými oprávněními
- **employee** - Běžný zaměstnanec s oprávněními pro rezervace

Stačí zadat jedno z těchto intranet ID na přihlašovací stránce.

## API dokumentace

### Autentizace
- `POST /api/auth/login` - Přihlášení pomocí intranet_id
- `GET /api/auth/me` - Získání informací o aktuálním uživateli
- `POST /api/auth/logout` - Odhlášení

### Vozidla
- `GET /api/vehicles` - Seznam všech vozidel
- `GET /api/vehicles/{id}` - Detail vozidla
- `POST /api/vehicles` - Vytvoření nového vozidla (admin)
- `PUT /api/vehicles/{id}` - Úprava vozidla (admin)
- `DELETE /api/vehicles/{id}` - Smazání vozidla (admin)

### Rezervace
- `GET /api/reservations` - Seznam rezervací
- `GET /api/reservations/{id}` - Detail rezervace
- `POST /api/reservations` - Vytvoření nové rezervace
- `PUT /api/reservations/{id}` - Úprava rezervace
- `DELETE /api/reservations/{id}` - Zrušení rezervace

### Uživatelé (admin)
- `GET /api/users` - Seznam všech uživatelů
- `GET /api/users/{id}` - Detail uživatele
- `PUT /api/users/{id}` - Úprava uživatele
- `DELETE /api/users/{id}` - Deaktivace uživatele

### Servisní záznamy (admin)
- `GET /api/service-records` - Seznam servisních záznamů
- `POST /api/service-records` - Vytvoření nového záznamu
- `PUT /api/service-records/{id}` - Úprava záznamu
- `DELETE /api/service-records/{id}` - Smazání záznamu

### Záznamy o poškození (admin)
- `GET /api/damage-records` - Seznam záznamů o poškození
- `POST /api/damage-records` - Vytvoření nového záznamu
- `PUT /api/damage-records/{id}` - Úprava záznamu
- `DELETE /api/damage-records/{id}` - Smazání záznamu

## Zálohování a obnovení

### Automatické zálohování
```bash
# Nastavení cron jobu pro denní zálohy
crontab -e

# Přidání řádku pro denní zálohu ve 2:00
0 2 * * * /path/to/car_reservation_backend/database/backup.sh
```

### Manuální zálohování
```bash
cd car_reservation_backend/database
./backup.sh
```

### Obnovení ze zálohy
```bash
cd car_reservation_backend/database
./restore.sh /path/to/backup/car_reservation_backup_YYYYMMDD_HHMMSS.sql.gz
```

## Bezpečnost

### Produkční konfigurace
- Změňte všechny výchozí tajné klíče v `.env` souboru
- Používejte HTTPS v produkci
- Nastavte firewall pro omezení přístupu k databázi
- Pravidelně aktualizujte závislosti
- Implementujte monitoring a logování

### CORS konfigurace
Pro produkci upravte CORS nastavení v `src/main.py`:
```python
CORS(app, origins=["https://yourdomain.com"])
```

## Řešení problémů

### Časté problémy

1. **Databázové připojení selhává**
   - Zkontrolujte DATABASE_URL v .env souboru
   - Ověřte, že PostgreSQL běží a je dostupný
   - Zkontrolujte oprávnění databázového uživatele

2. **Frontend se nenačítá**
   - Zkontrolujte, že build soubory jsou ve správné složce
   - Ověřte, že backend běží na správném portu
   - Zkontrolujte CORS nastavení

3. **JWT token problémy**
   - Zkontrolujte JWT_SECRET_KEY v konfiguraci
   - Ověřte, že token není vypršelý
   - Zkontrolujte formát Authorization hlavičky

### Logování
Logy aplikace najdete v:
- Vývojové prostředí: Konzole
- Produkční prostředí: `/var/log/car-reservation/app.log`

## Podpora a vývoj

### Rozšíření funkcí
Aplikace je navržena pro snadné rozšíření:
- Přidání nových API endpointů v `src/routes/`
- Vytvoření nových React komponent v `src/components/`
- Rozšíření databázového schématu v `database/schema.sql`

### Testování
```bash
# Backend testy
cd car_reservation_backend
python -m pytest tests/

# Frontend testy
cd car_reservation_frontend
npm run test
```

### Přispívání
1. Forkněte repozitář
2. Vytvořte feature branch
3. Commitněte změny
4. Vytvořte Pull Request

## Licence

Tento projekt je licencován pod MIT licencí. Viz LICENSE soubor pro detaily.

