from src.models.database import db, BaseModel

class ServiceRecord(BaseModel):
    __tablename__ = 'service_records'
    
    service_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    performed_by = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<ServiceRecord {self.service_id}: {self.service_type} for {self.vehicle.license_plate if self.vehicle else "N/A"}>'
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'vehicle_id': self.vehicle_id,
            'vehicle_info': {
                'make': self.vehicle.make,
                'model': self.vehicle.model,
                'license_plate': self.vehicle.license_plate
            } if self.vehicle else None,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'service_type': self.service_type,
            'description': self.description,
            'cost': float(self.cost) if self.cost else None,
            'performed_by': self.performed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

