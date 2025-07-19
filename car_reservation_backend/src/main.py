import os
import sys
# NEMĚŇTE TOTO !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import logging

# Import databáze
from src.models.database import db

# Import všech modelů pro zajištění jejich registrace
from src.models.role import Role
from src.models.app_user import AppUser
from src.models.vehicle import Vehicle
from src.models.reservation import Reservation
from src.models.service_record import ServiceRecord
from src.models.damage_record import DamageRecord

# Import blueprintů
from src.routes.auth import auth_bp
from src.routes.vehicles import vehicles_bp
from src.routes.reservations import reservations_bp
from src.routes.users import users_bp
from src.routes.service_records import service_records_bp
from src.routes.damage_records import damage_records_bp

def create_app():
    """Factory function pro vytvoření Flask aplikace"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Konfigurace z environment variables nebo výchozí hodnoty
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'car-reservation-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

    # Konfigurace databáze
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render.com používá postgres:// ale SQLAlchemy potřebuje postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Vývojové SQLite - pouze pro lokální vývoj
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Produkční nastavení
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        # Nastavení logování pro produkci
        logging.basicConfig(level=logging.INFO)
    else:
        app.config['DEBUG'] = True

    # Inicializace rozšíření
    CORS(app, origins="*")  # Povolit všechny původy
    jwt = JWTManager(app)
    db.init_app(app)

    # Registrace blueprintů
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicles_bp, url_prefix='/api')
    app.register_blueprint(reservations_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(service_records_bp, url_prefix='/api')
    app.register_blueprint(damage_records_bp, url_prefix='/api')

       # JWT error handlery
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token vypršel'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Neplatný token', 'detail': error}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Autorizační token je vyžadován'}), 401

    # Routy pro servírování frontendu
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return jsonify({
                'message': 'API pro rezervaci firemních vozidel',
                'version': '1.0.0',
                'status': 'running',
                'endpoints': {
                    'auth': '/api/auth/login',
                    'vehicles': '/api/vehicles',
                    'reservations': '/api/reservations',
                    'users': '/api/users',
                    'service_records': '/api/service-records',
                    'damage_records': '/api/damage-records'
                }
            }), 200

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'message': 'API pro rezervaci firemních vozidel',
                    'version': '1.0.0',
                    'status': 'running',
                    'endpoints': {
                        'auth': '/api/auth/login',
                        'vehicles': '/api/vehicles',
                        'reservations': '/api/reservations',
                        'users': '/api/users',
                        'service_records': '/api/service-records',
                        'damage_records': '/api/damage-records'
                    }
                }), 200

    return app

# Inicializace databáze a vytvoření výchozích dat
def init_database(app):
    """Inicializace databáze s výchozími rolemi a ukázkovými daty"""
    with app.app_context():
        try:
            db.create_all()
            
            # Vytvoření výchozích rolí, pokud neexistují
            if not Role.query.filter_by(role_name='Employee').first():
                employee_role = Role(
                    role_name='Employee',
                    description='Standardní zaměstnanec se základními oprávněními pro rezervace'
                )
                db.session.add(employee_role)
            
            if not Role.query.filter_by(role_name='Fleet Administrator').first():
                admin_role = Role(
                    role_name='Fleet Administrator',
                    description='Administrátor s plným přístupem ke správě vozového parku'
                )
                db.session.add(admin_role)
            
            # Vytvoření ukázkových vozidel, pokud žádná neexistují
            if not Vehicle.query.first():
                from datetime import date, timedelta
                
                sample_vehicles = [
                    {
                        'make': 'Škoda',
                        'model': 'Octavia',
                        'license_plate': '1A2 3456',
                        'color': 'Stříbrná',
                        'fuel_type': 'Benzín',
                        'seating_capacity': 5,
                        'transmission_type': 'Manuální',
                        'status': 'Active',
                        'description': 'Komfortní sedan s klimatizací a GPS navigací',
                        'odometer_reading': 45000,
                        'technical_inspection_expiry_date': date.today() + timedelta(days=180),
                        'highway_vignette_expiry_date': date.today() + timedelta(days=90),
                        'entry_permissions_notes': 'Pro vjezd do areálu firmy XYZ je nutná čipová karta č. 12345'
                    },
                    {
                        'make': 'Volkswagen',
                        'model': 'Passat',
                        'license_plate': '2B3 4567',
                        'color': 'Černá',
                        'fuel_type': 'Nafta',
                        'seating_capacity': 5,
                        'transmission_type': 'Automatická',
                        'status': 'Active',
                        'description': 'Prostorný sedan s automatickou převodovkou',
                        'odometer_reading': 32000,
                        'technical_inspection_expiry_date': date.today() + timedelta(days=120),
                        'highway_vignette_expiry_date': date.today() + timedelta(days=90)
                    },
                    {
                        'make': 'Ford',
                        'model': 'Transit',
                        'license_plate': '3C4 5678',
                        'color': 'Bílá',
                        'fuel_type': 'Nafta',
                        'seating_capacity': 9,
                        'transmission_type': 'Manuální',
                        'status': 'Active',
                        'description': 'Velkoprostorový vůz pro přepravu více osob',
                        'odometer_reading': 78000,
                        'technical_inspection_expiry_date': date.today() + timedelta(days=60),
                        'highway_vignette_expiry_date': date.today() + timedelta(days=90)
                    }
                ]
                
                for vehicle_data in sample_vehicles:
                    vehicle = Vehicle(**vehicle_data)
                    db.session.add(vehicle)
            
            db.session.commit()
            print("Databáze byla úspěšně inicializována")
            
        except Exception as e:
            print(f"Chyba při inicializaci databáze: {e}")
            db.session.rollback()

# Vytvoření aplikace
app = create_app()

# Inicializace databáze při startu aplikace
with app.app_context():
    init_database(app)

if __name__ == '__main__':
    # Lokální spuštění pro vývoj
    port = int(os.environ.get('PORT', 5000))
    init_database(app)
    app.run(host='0.0.0.0', port=port, debug=True)

