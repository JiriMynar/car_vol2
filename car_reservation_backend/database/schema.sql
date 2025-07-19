-- Databázové schéma systému rezervace firemních vozidel
-- PostgreSQL verze

-- Vytvoření databáze (spustit samostatně jako superuser)
-- CREATE DATABASE car_reservation;
-- CREATE USER car_reservation_user WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE car_reservation TO car_reservation_user;

-- Připojit se k databázi car_reservation před spuštěním zbytku

-- Povolit UUID rozšíření (volitelné, pro budoucí použití)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Vytvoření tabulky rolí
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření tabulky uživatelů
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    intranet_id VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření tabulky vozidel
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    color VARCHAR(50),
    fuel_type VARCHAR(50) NOT NULL,
    seating_capacity INTEGER NOT NULL,
    transmission_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    description TEXT,
    odometer_reading INTEGER NOT NULL DEFAULT 0,
    last_service_date DATE,
    next_service_date DATE,
    technical_inspection_expiry_date DATE,
    highway_vignette_expiry_date DATE,
    emission_inspection_expiry_date DATE,
    entry_permissions_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření tabulky rezervací
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    number_of_passengers INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'Confirmed',
    user_notes TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření tabulky servisních záznamů
CREATE TABLE IF NOT EXISTS service_records (
    service_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    service_date DATE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    cost DECIMAL(10, 2),
    performed_by VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření tabulky záznamů o poškození
CREATE TABLE IF NOT EXISTS damage_records (
    damage_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    date_of_damage DATE NOT NULL,
    description TEXT NOT NULL,
    estimated_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    repair_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    photos TEXT, -- JSON řetězec cest k fotografiím
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vytvoření indexů pro lepší výkon
CREATE INDEX IF NOT EXISTS idx_users_intranet_id ON users(intranet_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);

CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);

CREATE INDEX IF NOT EXISTS idx_reservations_vehicle_id ON reservations(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_start_time ON reservations(start_time);
CREATE INDEX IF NOT EXISTS idx_reservations_end_time ON reservations(end_time);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);

CREATE INDEX IF NOT EXISTS idx_service_records_vehicle_id ON service_records(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_service_records_service_date ON service_records(service_date);

CREATE INDEX IF NOT EXISTS idx_damage_records_vehicle_id ON damage_records(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_damage_records_date_of_damage ON damage_records(date_of_damage);

-- Vytvoření funkce pro automatickou aktualizaci sloupce updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Vytvoření triggerů pro sloupce updated_at
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservations_updated_at BEFORE UPDATE ON reservations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_records_updated_at BEFORE UPDATE ON service_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_damage_records_updated_at BEFORE UPDATE ON damage_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Udělení oprávnění aplikačnímu uživateli
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO car_reservation_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO car_reservation_user;

