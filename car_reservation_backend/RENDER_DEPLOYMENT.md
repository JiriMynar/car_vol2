# Návod pro nasazení na Render.com

Tento dokument obsahuje podrobné instrukce pro nasazení systému rezervace firemních vozidel na platformu Render.com.

## Příprava před nasazením

### 1. Požadavky
- Účet na [Render.com](https://render.com)
- Git repozitář s kódem aplikace
- PostgreSQL databáze (automaticky poskytována Render.com)

### 2. Struktura projektu
Ujistěte se, že váš projekt obsahuje tyto soubory:
```
car_reservation_backend/
├── Procfile                 # Definuje jak spustit aplikaci
├── runtime.txt             # Specifikuje verzi Pythonu
├── requirements.txt        # Python závislosti
├── build.sh               # Build skript
├── render.yaml            # Konfigurace pro Render
├── .env.example           # Příklad environment variables
└── src/
    ├── main.py            # Hlavní Flask aplikace
    └── ...
```

## Nasazení na Render.com

### Metoda 1: Přes Git repozitář (doporučeno)

1. **Nahrajte kód do Git repozitáře**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/car-reservation-system.git
   git push -u origin main
   ```

2. **Vytvořte novou službu na Render.com**
   - Přihlaste se na [Render.com](https://render.com)
   - Klikněte na "New +" → "Web Service"
   - Připojte váš Git repozitář
   - Vyberte branch (obvykle `main`)

3. **Konfigurace služby**
   - **Name**: `car-reservation-system`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn src.main:app`
   - **Plan**: `Free` (pro testování)

### Metoda 2: Přes render.yaml

1. **Nahrajte render.yaml do root adresáře**
   ```yaml
   services:
     - type: web
       name: car-reservation-backend
       env: python
       buildCommand: "./build.sh"
       startCommand: "gunicorn src.main:app"
       plan: free
       envVars:
         - key: FLASK_ENV
           value: production
         - key: SECRET_KEY
           generateValue: true
         - key: JWT_SECRET_KEY
           generateValue: true
   ```

2. **Nasaďte přes Render Dashboard**
   - Klikněte na "New +" → "Blueprint"
   - Vyberte váš repozitář
   - Render automaticky detekuje render.yaml

## Konfigurace databáze

### 1. Vytvoření PostgreSQL databáze
- V Render Dashboard klikněte na "New +" → "PostgreSQL"
- **Name**: `car-reservation-db`
- **Plan**: `Free`
- Poznamenejte si connection string

### 2. Propojení databáze s aplikací
- V nastavení vaší web služby přidejte environment variable:
  - **Key**: `DATABASE_URL`
  - **Value**: Connection string z PostgreSQL služby

## Environment Variables

Nastavte tyto proměnné prostředí v Render Dashboard:

### Povinné
- `DATABASE_URL`: Automaticky nastaveno při propojení s PostgreSQL
- `SECRET_KEY`: Vygenerováno automaticky nebo nastavte vlastní
- `JWT_SECRET_KEY`: Vygenerováno automaticky nebo nastavte vlastní
- `FLASK_ENV`: `production`

### Volitelné
- `PORT`: Automaticky nastaveno Render.com
- `CORS_ORIGINS`: `*` (nebo specifické domény)

## Řešení problémů

### Časté chyby a řešení

1. **Build selhává**
   ```
   Error: Permission denied
   ```
   **Řešení**: Ujistěte se, že build.sh má spustitelná práva:
   ```bash
   chmod +x build.sh
   ```

2. **Aplikace se nespustí**
   ```
   Error: No module named 'src'
   ```
   **Řešení**: Zkontrolujte, že Procfile obsahuje správnou cestu:
   ```
   web: gunicorn src.main:app
   ```

3. **Databázové chyby**
   ```
   Error: could not connect to server
   ```
   **Řešení**: Ověřte, že DATABASE_URL je správně nastaveno a databáze je spuštěna.

4. **Frontend se nenačítá**
   ```
   404 Not Found
   ```
   **Řešení**: Ujistěte se, že build.sh správně kopíruje frontend soubory do src/static/.

### Logování a debugging

1. **Zobrazení logů**
   - V Render Dashboard → vaše služba → "Logs"
   - Nebo použijte Render CLI: `render logs -s your-service-name`

2. **Debug mode**
   - Pro produkci vždy nastavte `FLASK_ENV=production`
   - Pro debugging dočasně změňte na `development`

## Aktualizace aplikace

### Automatické nasazení
- Render automaticky nasadí novou verzi při push do hlavní branch
- Sledujte progress v "Events" tab

### Manuální nasazení
- V Render Dashboard → vaše služba → "Manual Deploy"
- Vyberte branch a klikněte "Deploy"

## Monitoring a údržba

### 1. Health check
- Render automaticky monitoruje dostupnost aplikace
- Endpoint pro health check: `https://your-app.onrender.com/api/health`

### 2. Metriky
- CPU a paměť usage v Render Dashboard
- Response time a error rate

### 3. Zálohy databáze
- PostgreSQL na Render má automatické zálohy
- Pro manuální zálohu použijte pg_dump

## Bezpečnost

### 1. Environment variables
- Nikdy necommitujte tajné klíče do Git
- Používejte Render's secret management

### 2. HTTPS
- Render automaticky poskytuje SSL certifikát
- Všechny requesty jsou automaticky přesměrovány na HTTPS

### 3. Firewall
- Render automaticky chrání proti DDoS útokům
- Aplikace je dostupná pouze přes HTTPS

## Škálování

### Free tier omezení
- 750 hodin/měsíc
- Aplikace "spí" po 15 minutách nečinnosti
- 512 MB RAM

### Upgrade na placený plán
- Pro produkční použití doporučujeme Starter plán ($7/měsíc)
- Bez omezení času běhu
- Více RAM a CPU

## Kontakt a podpora

- Render dokumentace: https://render.com/docs
- Render komunita: https://community.render.com
- Support: support@render.com

## Checklist před nasazením

- [ ] Kód je v Git repozitáři
- [ ] Všechny soubory (Procfile, runtime.txt, requirements.txt) jsou přítomny
- [ ] Build.sh má spustitelná práva
- [ ] Environment variables jsou nastaveny
- [ ] PostgreSQL databáze je vytvořena a propojena
- [ ] Aplikace byla testována lokálně
- [ ] Frontend je správně buildnutý (pokud existuje)

Po dokončení těchto kroků by vaše aplikace měla být úspěšně nasazena na Render.com!

