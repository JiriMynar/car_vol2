from src.models.database import db, BaseModel

class AppUser(BaseModel):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    intranet_id = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(50), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Vztahy
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<AppUser {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'intranet_id': self.intranet_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role_id': self.role_id,
            'role_name': self.role.role_name if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def has_role(self, role_name):
        """Kontrola, zda má uživatel specifickou roli"""
        return self.role and self.role.role_name == role_name
    
    def is_admin(self):
        """Kontrola, zda je uživatel administrátor vozového parku"""
        return self.has_role('Fleet Administrator')

