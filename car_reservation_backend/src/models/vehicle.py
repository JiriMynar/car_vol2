from src.models.database import db, BaseModel

class Vehicle(BaseModel):
    __tablename__ = 'vehicles'
    
    vehicle_id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    color = db.Column(db.String(50), nullable=True)
    fuel_type = db.Column(db.String(50), nullable=False)
    seating_capacity = db.Column(db.Integer, nullable=False)
    transmission_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Active')
    description = db.Column(db.Text, nullable=True)
    odometer_reading = db.Column(db.Integer, nullable=False, default=0)
    last_service_date = db.Column(db.Date, nullable=True)
    next_service_date = db.Column(db.Date, nullable=True)
    technical_inspection_expiry_date = db.Column(db.Date, nullable=True)
    highway_vignette_expiry_date = db.Column(db.Date, nullable=True)
    emission_inspection_expiry_date = db.Column(db.Date, nullable=True)
    entry_permissions_notes = db.Column(db.Text, nullable=True)
    
    # Vztahy
    reservations = db.relationship('Reservation', backref='vehicle', lazy=True)
    service_records = db.relationship('ServiceRecord', backref='vehicle', lazy=True)
    damage_records = db.relationship('DamageRecord', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.make} {self.model} ({self.license_plate})>'
    
    def to_dict(self):
        return {
            'vehicle_id': self.vehicle_id,
            'make': self.make,
            'model': self.model,
            'license_plate': self.license_plate,
            'color': self.color,
            'fuel_type': self.fuel_type,
            'seating_capacity': self.seating_capacity,
            'transmission_type': self.transmission_type,
            'status': self.status,
            'description': self.description,
            'odometer_reading': self.odometer_reading,
            'last_service_date': self.last_service_date.isoformat() if self.last_service_date else None,
            'next_service_date': self.next_service_date.isoformat() if self.next_service_date else None,
            'technical_inspection_expiry_date': self.technical_inspection_expiry_date.isoformat() if self.technical_inspection_expiry_date else None,
            'highway_vignette_expiry_date': self.highway_vignette_expiry_date.isoformat() if self.highway_vignette_expiry_date else None,
            'emission_inspection_expiry_date': self.emission_inspection_expiry_date.isoformat() if self.emission_inspection_expiry_date else None,
            'entry_permissions_notes': self.entry_permissions_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_available(self, start_time, end_time, exclude_reservation_id=None):
        """Kontrola dostupnosti vozidla pro zadané časové období"""
        from src.models.reservation import Reservation
        
        if self.status != 'Active':
            return False
            
        # Kontrola překrývajících se rezervací
        query = Reservation.query.filter(
            Reservation.vehicle_id == self.vehicle_id,
            Reservation.status == 'Confirmed',
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        )
        
        if exclude_reservation_id:
            query = query.filter(Reservation.reservation_id != exclude_reservation_id)
            
        overlapping_reservations = query.all()
        return len(overlapping_reservations) == 0

