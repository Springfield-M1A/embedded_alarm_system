from app import db
from datetime import datetime

class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    label = db.Column(db.String(100))
    days = db.Column(db.String(20))  # Day info (e.g., "0,1,2,3,4")
    specific_date = db.Column(db.Date)  # For specific dates
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time,
            'label': self.label,
            'days': self.days,
            'specific_date': self.specific_date.strftime('%Y-%m-%d') if self.specific_date else None,
            'is_active': self.is_active
        }

class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }