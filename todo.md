# TODO - Oprava systému rezervace aut pro render.com

## Fáze 2: Identifikace chyb a problémů

### Identifikované problémy:

1. **Chybějící Procfile pro render.com** - [ ]
   - Render.com potřebuje Procfile pro spuštění aplikace

2. **Problematická konfigurace databáze** - [ ]
   - Render.com používá PostgreSQL s specifickým formátem DATABASE_URL
   - Potřeba upravit parsing DATABASE_URL pro Render

3. **Chybějící runtime.txt** - [ ]
   - Specifikace verze Pythonu pro Render

4. **Problematické cesty k souborům** - [ ]
   - Statická složka může být problematická
   - Cesty k databázi SQLite nebudou fungovat na Render

5. **Chybějící build skripty** - [ ]
   - Render potřebuje build skripty pro frontend

6. **Konfigurace portů** - [ ]
   - Render používá proměnnou PORT

7. **Produkční konfigurace** - [ ]
   - Debug mode musí být vypnutý
   - Bezpečnostní klíče z environment variables

## Fáze 3: Oprava kódu a konfigurace

- [x] Vytvořit Procfile
- [x] Upravit main.py pro Render kompatibilitu
- [x] Vytvořit runtime.txt
- [x] Upravit konfiguraci databáze
- [x] Vytvořit build skripty
- [x] Opravit cesty k souborům
- [x] Nastavit produkční konfigurace
- [x] Přidat gunicorn do requirements.txt
- [x] Vytvořit render.yaml
- [x] Vytvořit .env.example

## Fáze 4: Testování a finalizace

- [x] Otestovat lokálně s SQLite
- [x] Ověřit Flask aplikaci
- [x] Zkontrolovat gunicorn spuštění
- [x] Opravit deprecated @app.before_first_request
- [x] Opravit frontend závislosti (date-fns konflikt)
- [x] Vytvořit návod pro nasazení na Render
- [x] Otestovat build skript

## Fáze 5: Dodání opravené verze

- [ ] Zabalit opravenou verzi
- [ ] Poskytnout instrukce pro nasazení

