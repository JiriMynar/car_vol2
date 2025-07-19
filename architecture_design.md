
# Architektura webové aplikace pro rezervaci firemních aut

Na základě detailních specifikací bude aplikace postavena na modulární a škálovatelné architektuře, která umožní snadnou údržbu a budoucí rozšíření. Zvolené technologie jsou Python (Flask) pro backend, React pro frontend a PostgreSQL pro databázi.

## 1. Backend (API Server)

*   **Technologie**: Python 3.x s frameworkem Flask.
*   **Účel**: Poskytování RESTful API pro komunikaci s frontendem a správu dat.
*   **Klíčové komponenty**:
    *   **Autentizace a Autorizace**: Integrace s firemním intranetem pro Single Sign-On (SSO). Pro autorizaci API požadavků bude použito JWT (JSON Web Tokens). Flask-JWT-Extended bude vhodná knihovna.
    *   **Databázová interakce**: SQLAlchemy jako ORM (Object-Relational Mapper) pro interakci s PostgreSQL databází. To zajistí abstrakci databáze a usnadní manipulaci s daty.
    *   **Business Logika**: Moduly pro správu vozidel, rezervací, uživatelů, servisních záznamů, záznamů o poškození a notifikací.
    *   **API Endpoints**: Definice RESTful endpointů pro všechny operace (GET, POST, PUT, DELETE) pro jednotlivé zdroje (vozidla, rezervace, uživatelé atd.).
    *   **Validace dat**: Zajištění validace vstupních dat na straně serveru pro bezpečnost a integritu dat.
    *   **Logování**: Implementace logování pro auditní účely a ladění.

## 2. Frontend (Uživatelské rozhraní)

*   **Technologie**: React.js s Create React App (nebo Vite) pro rychlý start a efektivní vývoj.
*   **Účel**: Poskytování intuitivního a responzivního uživatelského rozhraní pro interakci s backend API.
*   **Klíčové komponenty**:
    *   **Responzivní Design**: Použití moderních CSS frameworků (např. Tailwind CSS nebo Material-UI) a flexibilních layoutů pro zajištění plné podpory pro desktop, tablet a mobilní zařízení.
    *   **Správa stavu**: Context API nebo Redux pro správu globálního stavu aplikace (např. uživatelská data, stav načítání).
    *   **Routing**: React Router pro navigaci mezi různými pohledy aplikace.
    *   **Komponenty UI**: Vytvoření znovupoužitelných komponent pro formuláře, tabulky, kalendáře, notifikace atd.
    *   **API Komunikace**: Použití `fetch` API nebo knihovny jako Axios pro asynchronní komunikaci s backend API.
    *   **Autentizace**: Zpracování JWT tokenů a správa uživatelských relací na straně klienta.

## 3. Databáze

*   **Technologie**: PostgreSQL (relační databáze).
*   **Účel**: Ukládání všech aplikačních dat.
*   **Klíčové aspekty**:
    *   **Schéma**: Detailní schéma databáze bude definováno v samostatné sekci, včetně tabulek, sloupců, datových typů, primárních a cizích klíčů a indexů.
    *   **Integrita dat**: Využití databázových omezení (např. `NOT NULL`, `UNIQUE`, `FOREIGN KEY`) pro zajištění integrity dat.
    *   **Transakce**: Zajištění atomických operací pro komplexní databázové transakce (např. vytvoření rezervace).

## 4. Integrace a Bezpečnost

*   **SSO s Intranetem**: Mock-up pro SSO integraci, protože přímá integrace s reálným LDAP/Active Directory je mimo rozsah sandboxu. V reálném nasazení by se použil vhodný protokol (např. OAuth2/OpenID Connect).
*   **HTTPS**: Veškerá komunikace bude předpokládat HTTPS. To bude zajištěno konfigurací webového serveru (např. Nginx) v produkčním prostředí.
*   **Validace vstupů**: Důkladná validace na frontend i backend straně.
*   **Ochrana proti útokům**: Základní ochrana proti XSS (sanitizace vstupů na frontend, `httpOnly` flag pro JWT tokeny) a CSRF (použití CSRF tokenů, pokud je to relevantní pro Flask).

## 5. Nasazení (Deployment)

*   **Prostředí**: Linux server (Ubuntu 22.04 LTS).
*   **Backend**: Gunicorn jako WSGI server pro Flask aplikaci, Nginx jako reverzní proxy.
*   **Frontend**: Nginx pro servírování statických souborů React aplikace.
*   **Databáze**: Samostatná instance PostgreSQL serveru.
*   **Instrukce**: Detailní instrukce pro instalaci závislostí, konfiguraci a spuštění aplikace.

