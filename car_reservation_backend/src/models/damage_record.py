from src.models.database import db, BaseModel
import json

class DamageRecord(BaseModel):
    __tablename__ = 'damage_records'
    
    damage_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    date_of_damage = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    estimated_cost = db.Column(db.Numeric(10, 2), nullable=True)
    actual_cost = db.Column(db.Numeric(10, 2), nullable=True)
    repair_status = db.Column(db.String(50), nullable=False, default='Pending')
    photos = db.Column(db.Text, nullable=True)  # JSON string of photo paths
    
    def __repr__(self):
        return f'<DamageRecord {self.damage_id}: {self.description[:50]}... for {self.vehicle.license_plate if self.vehicle else "N/A"}>'
    
    def to_dict(self):
        photos_list = []
        if self.photos:
            try:
                photos_list = json.loads(self.photos)
            except json.JSONDecodeError:
                photos_list = []
        
        return {
            'damage_id': self.damage_id,
            'vehicle_id': self.vehicle_id,
            'vehicle_info': {
                'make': self.vehicle.make,
                'model': self.vehicle.model,
                'license_plate': self.vehicle.license_plate
            } if self.vehicle else None,
            'date_of_damage': self.date_of_damage.isoformat() if self.date_of_damage else None,
            'description': self.description,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'repair_status': self.repair_status,
            'photos': photos_list,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def add_photo(self, photo_path):
        """Přidání cesty k fotografii do seznamu fotografií"""
        photos_list = []
        if self.photos:
            try:
                photos_list = json.loads(self.photos)
            except json.JSONDecodeError:
                photos_list = []
        
        photos_list.append(photo_path)
        self.photos = json.dumps(photos_list)
    
    def remove_photo(self, photo_path):
        """Odstranění cesty k fotografii ze seznamu fotografií"""
        photos_list = []
        if self.photos:
            try:
                photos_list = json.loads(self.photos)
            except json.JSONDecodeError:
                photos_list = []
        
        if photo_path in photos_list:
            photos_list.remove(photo_path)
            self.photos = json.dumps(photos_list)

