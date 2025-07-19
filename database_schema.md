
# Databázové schéma pro aplikaci rezervace firemních aut

Následující databázové schéma je navrženo pro PostgreSQL a reflektuje funkční požadavky a entity popsané v zadání. Vztahy mezi tabulkami jsou definovány pomocí primárních a cizích klíčů pro zajištění datové integrity.

## 1. Tabulka: `users` (Uživatelé)

Ukládá informace o uživatelích systému. Předpokládá se, že `intranet_id` je unikátní identifikátor z firemního intranetu.

| Název sloupce      | Datový typ         | Omezení                               | Popis                                    |
| :----------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `user_id`          | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID uživatele                    |
| `intranet_id`      | `VARCHAR(255)`     | `UNIQUE`, `NOT NULL`                  | ID uživatele z intranetu                 |
| `first_name`       | `VARCHAR(255)`     | `NOT NULL`                            | Křestní jméno uživatele                  |
| `last_name`        | `VARCHAR(255)`     | `NOT NULL`                            | Příjmení uživatele                       |
| `email`            | `VARCHAR(255)`     | `UNIQUE`, `NOT NULL`                  | E-mailová adresa uživatele               |
| `phone_number`     | `VARCHAR(50)`      | `NULLABLE`                            | Telefonní číslo uživatele                |
| `role_id`          | `INTEGER`          | `NOT NULL`, `FOREIGN KEY` references `roles(role_id)` | ID role uživatele                        |
| `is_active`        | `BOOLEAN`          | `NOT NULL`, `DEFAULT TRUE`            | Zda je uživatel aktivní                  |
| `created_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## 2. Tabulka: `roles` (Role)

Definuje různé role uživatelů v systému.

| Název sloupce      | Datový typ         | Omezení                               | Popis                                    |
| :----------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `role_id`          | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID role                         |
| `role_name`        | `VARCHAR(50)`      | `UNIQUE`, `NOT NULL`                  | Název role (např. 'Employee', 'Fleet Administrator') |
| `description`      | `TEXT`             | `NULLABLE`                            | Popis role                               |
| `created_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## 3. Tabulka: `vehicles` (Vozidla)

Ukládá detailní informace o firemních vozidlech.

| Název sloupce                       | Datový typ         | Omezení                               | Popis                                    |
| :---------------------------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `vehicle_id`                        | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID vozidla                      |
| `make`                              | `VARCHAR(100)`     | `NOT NULL`                            | Značka vozidla                           |
| `model`                             | `VARCHAR(100)`     | `NOT NULL`                            | Model vozidla                            |
| `license_plate`                     | `VARCHAR(20)`      | `UNIQUE`, `NOT NULL`                  | Registrační značka (SPZ)                 |
| `color`                             | `VARCHAR(50)`      | `NULLABLE`                            | Barva vozidla                            |
| `fuel_type`                         | `VARCHAR(50)`      | `NOT NULL`                            | Typ paliva (např. 'Petrol', 'Diesel', 'Electric', 'Hybrid') |
| `seating_capacity`                  | `INTEGER`          | `NOT NULL`                            | Počet míst ve vozidle                    |
| `transmission_type`                 | `VARCHAR(50)`      | `NOT NULL`                            | Typ převodovky (např. 'Manual', 'Automatic') |
| `status`                            | `VARCHAR(50)`      | `NOT NULL`, `DEFAULT 'Active'`        | Stav vozidla (např. 'Active', 'In Service', 'Deactivated', 'Archived') |
| `description`                       | `TEXT`             | `NULLABLE`                            | Obecné informace a výbava                |
| `odometer_reading`                  | `INTEGER`          | `NOT NULL`                            | Aktuální stav tachometru                 |
| `last_service_date`                 | `DATE`             | `NULLABLE`                            | Datum poslední servisní prohlídky        |
| `next_service_date`                 | `DATE`             | `NULLABLE`                            | Datum další plánované servisní prohlídky |
| `technical_inspection_expiry_date`  | `DATE`             | `NULLABLE`                            | Datum platnosti STK                      |
| `highway_vignette_expiry_date`      | `DATE`             | `NULLABLE`                            | Datum platnosti dálniční známky         |
| `emission_inspection_expiry_date`   | `DATE`             | `NULLABLE`                            | Datum platnosti emisní kontroly          |
| `entry_permissions_notes`           | `TEXT`             | `NULLABLE`                            | Poznámky k vjezdům do firem              |
| `created_at`                        | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`                        | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## 4. Tabulka: `reservations` (Rezervace)

Ukládá informace o rezervacích vozidel.

| Název sloupce         | Datový typ         | Omezení                               | Popis                                    |
| :-------------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `reservation_id`      | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID rezervace                    |
| `vehicle_id`          | `INTEGER`          | `NOT NULL`, `FOREIGN KEY` references `vehicles(vehicle_id)` | ID rezervovaného vozidla                 |
| `user_id`             | `INTEGER`          | `NOT NULL`, `FOREIGN KEY` references `users(user_id)` | ID uživatele, který rezervaci vytvořil   |
| `start_time`          | `TIMESTAMP`        | `NOT NULL`                            | Datum a čas začátku rezervace            |
| `end_time`            | `TIMESTAMP`        | `NOT NULL`                            | Datum a čas konce rezervace              |
| `purpose`             | `VARCHAR(255)`     | `NOT NULL`                            | Účel cesty                               |
| `destination`         | `VARCHAR(255)`     | `NOT NULL`                            | Cíl cesty                                |
| `number_of_passengers`| `INTEGER`          | `NULLABLE`                            | Počet osob ve vozidle                    |
| `status`              | `VARCHAR(50)`      | `NOT NULL`, `DEFAULT 'Confirmed'`     | Stav rezervace (např. 'Confirmed', 'Cancelled', 'Completed') |
| `user_notes`          | `TEXT`             | `NULLABLE`                            | Poznámky uživatele k rezervaci           |
| `admin_notes`         | `TEXT`             | `NULLABLE`                            | Poznámky administrátora k rezervaci      |
| `created_at`          | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`          | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## 5. Tabulka: `service_records` (Servisní záznamy)

Ukládá historii servisních záznamů pro každé vozidlo.

| Název sloupce      | Datový typ         | Omezení                               | Popis                                    |
| :----------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `service_id`       | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID servisního záznamu           |
| `vehicle_id`       | `INTEGER`          | `NOT NULL`, `FOREIGN KEY` references `vehicles(vehicle_id)` | ID vozidla, ke kterému se záznam vztahuje |
| `service_date`     | `DATE`             | `NOT NULL`                            | Datum provedení servisu                  |
| `service_type`     | `VARCHAR(100)`     | `NOT NULL`                            | Typ servisu (např. 'Oil Change', 'Tire Rotation') |
| `description`      | `TEXT`             | `NOT NULL`                            | Detailní popis provedeného servisu       |
| `cost`             | `DECIMAL(10, 2)`   | `NULLABLE`                            | Náklady na servis                        |
| `performed_by`     | `VARCHAR(255)`     | `NULLABLE`                            | Kdo servis provedl                       |
| `created_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## 6. Tabulka: `damage_records` (Záznamy o poškození)

Ukládá informace o poškozeních nebo nehodách vozidel.

| Název sloupce      | Datový typ         | Omezení                               | Popis                                    |
| :----------------- | :----------------- | :------------------------------------ | :--------------------------------------- |
| `damage_id`        | `SERIAL`           | `PRIMARY KEY`                         | Unikátní ID záznamu o poškození          |
| `vehicle_id`       | `INTEGER`          | `NOT NULL`, `FOREIGN KEY` references `vehicles(vehicle_id)` | ID vozidla, ke kterému se záznam vztahuje |
| `date_of_damage`   | `DATE`             | `NOT NULL`                            | Datum poškození                          |
| `description`      | `TEXT`             | `NOT NULL`                            | Popis poškození                          |
| `estimated_cost`   | `DECIMAL(10, 2)`   | `NULLABLE`                            | Odhadované náklady na opravu             |
| `actual_cost`      | `DECIMAL(10, 2)`   | `NULLABLE`                            | Skutečné náklady na opravu               |
| `repair_status`    | `VARCHAR(50)`      | `NOT NULL`, `DEFAULT 'Pending'`       | Stav opravy (např. 'Pending', 'Repaired', 'Irreparable') |
| `photos`           | `TEXT`             | `NULLABLE`                            | Cesty k fotografiím poškození (JSON string pole) |
| `created_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas vytvoření záznamu                    |
| `updated_at`       | `TIMESTAMP`        | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | Čas poslední aktualizace záznamu         |

## Vztahy mezi tabulkami:

*   `users` 1:N `reservations` (jeden uživatel může mít mnoho rezervací)
*   `roles` 1:N `users` (jedna role může být přiřazena mnoha uživatelům)
*   `vehicles` 1:N `reservations` (jedno vozidlo může mít mnoho rezervací)
*   `vehicles` 1:N `service_records` (jedno vozidlo může mít mnoho servisních záznamů)
*   `vehicles` 1:N `damage_records` (jedno vozidlo může mít mnoho záznamů o poškození)

## Indexy:

Pro optimalizaci výkonu dotazů budou vytvořeny indexy na často používaných sloupcích a cizích klíčích:

*   `users`: `intranet_id`, `email`, `role_id`
*   `vehicles`: `license_plate`, `status`
*   `reservations`: `vehicle_id`, `user_id`, `start_time`, `end_time`, `status`
*   `service_records`: `vehicle_id`, `service_date`
*   `damage_records`: `vehicle_id`, `date_of_damage`

Toto schéma poskytuje robustní základ pro implementaci všech požadovaných funkcionalit aplikace.

