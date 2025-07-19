-- Počáteční data pro systém rezervace firemních vozidel
-- Spustit po schema.sql

-- Vložení výchozích rolí
INSERT INTO roles (role_name, description) VALUES 
('Employee', 'Standardní zaměstnanec se základními oprávněními pro rezervace'),
('Fleet Administrator', 'Administrátor s plným přístupem ke správě vozového parku')
ON CONFLICT (role_name) DO NOTHING;

-- Vložení ukázkových vozidel
INSERT INTO vehicles (
    make, model, license_plate, color, fuel_type, seating_capacity, 
    transmission_type, status, description, odometer_reading,
    technical_inspection_expiry_date, highway_vignette_expiry_date,
    entry_permissions_notes
) VALUES 
(
    'Škoda', 'Octavia', '1A2 3456', 'Stříbrná', 'Benzín', 5,
    'Manuální', 'Active', 'Komfortní sedan s klimatizací a GPS navigací', 45000,
    CURRENT_DATE + INTERVAL '180 days', CURRENT_DATE + INTERVAL '90 days',
    'Pro vjezd do areálu firmy XYZ je nutná čipová karta č. 12345'
),
(
    'Volkswagen', 'Passat', '2B3 4567', 'Černá', 'Nafta', 5,
    'Automatická', 'Active', 'Prostorný sedan s automatickou převodovkou', 32000,
    CURRENT_DATE + INTERVAL '120 days', CURRENT_DATE + INTERVAL '90 days',
    NULL
),
(
    'Ford', 'Transit', '3C4 5678', 'Bílá', 'Nafta', 9,
    'Manuální', 'Active', 'Velkoprostorový vůz pro přepravu více osob', 78000,
    CURRENT_DATE + INTERVAL '60 days', CURRENT_DATE + INTERVAL '90 days',
    NULL
),
(
    'Toyota', 'Corolla', '4D5 6789', 'Modrá', 'Hybrid', 5,
    'Automatická', 'Active', 'Ekonomický hybrid s nízkou spotřebou', 25000,
    CURRENT_DATE + INTERVAL '200 days', CURRENT_DATE + INTERVAL '90 days',
    'Ekologické vozidlo - vhodné pro městské jízdy'
),
(
    'BMW', 'X3', '5E6 7890', 'Šedá', 'Nafta', 5,
    'Automatická', 'Active', 'Luxusní SUV pro reprezentativní účely', 15000,
    CURRENT_DATE + INTERVAL '150 days', CURRENT_DATE + INTERVAL '90 days',
    'Pouze pro vedoucí pracovníky a důležité obchodní jednání'
)
ON CONFLICT (license_plate) DO NOTHING;

-- Vložení ukázkového admin uživatele (bude vytvořen automaticky při prvním přihlášení)
-- Toto je pouze pro referenci - skuteční uživatelé jsou vytvářeni přes SSO přihlášení

-- Vložení ukázkových servisních záznamů
INSERT INTO service_records (
    vehicle_id, service_date, service_type, description, cost, performed_by
) VALUES 
(
    (SELECT vehicle_id FROM vehicles WHERE license_plate = '1A2 3456'),
    CURRENT_DATE - INTERVAL '30 days',
    'Pravidelný servis',
    'Výměna oleje, kontrola brzd, výměna vzduchového filtru',
    2500.00,
    'Autoservis Novák s.r.o.'
),
(
    (SELECT vehicle_id FROM vehicles WHERE license_plate = '2B3 4567'),
    CURRENT_DATE - INTERVAL '45 days',
    'Oprava klimatizace',
    'Doplnění chladiva, výměna kabinového filtru',
    1200.00,
    'Autoservis Novák s.r.o.'
),
(
    (SELECT vehicle_id FROM vehicles WHERE license_plate = '3C4 5678'),
    CURRENT_DATE - INTERVAL '15 days',
    'Výměna pneumatik',
    'Přezutí na zimní pneumatiky, vyvážení kol',
    3200.00,
    'Pneuservis Rychlý s.r.o.'
);

-- Vytvoření pohledu pro kalendář rezervací (volitelné)
CREATE OR REPLACE VIEW reservation_calendar AS
SELECT 
    r.reservation_id,
    r.start_time,
    r.end_time,
    r.purpose,
    r.destination,
    r.status,
    v.make || ' ' || v.model AS vehicle_name,
    v.license_plate,
    u.first_name || ' ' || u.last_name AS user_name,
    u.email AS user_email
FROM reservations r
JOIN vehicles v ON r.vehicle_id = v.vehicle_id
JOIN users u ON r.user_id = u.user_id
WHERE r.status = 'Confirmed'
ORDER BY r.start_time;

-- Vytvoření pohledu pro dostupnost vozidel (volitelné)
CREATE OR REPLACE VIEW vehicle_availability AS
SELECT 
    v.vehicle_id,
    v.make,
    v.model,
    v.license_plate,
    v.status,
    v.seating_capacity,
    v.fuel_type,
    v.transmission_type,
    CASE 
        WHEN v.status != 'Active' THEN 'Nedostupné'
        WHEN EXISTS (
            SELECT 1 FROM reservations r 
            WHERE r.vehicle_id = v.vehicle_id 
            AND r.status = 'Confirmed'
            AND r.start_time <= CURRENT_TIMESTAMP 
            AND r.end_time > CURRENT_TIMESTAMP
        ) THEN 'Obsazeno'
        ELSE 'Dostupné'
    END AS current_availability
FROM vehicles v
ORDER BY v.make, v.model;

