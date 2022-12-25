from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(600), nullable=False)
    device_os_version = db.Column(db.String(600), nullable=False)
    device_model = db.Column(db.String(600), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"User(device_id = {self.device_id}, device_os_version = {self.device_os_version}, device_model = {self.device_model})"

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    link = db.Column(db.String(600), unique=True, nullable=False)
    category = db.Column(db.String(600), nullable=False)
    views_count = db.Column(db.Integer, nullable=False, default=0)
    report_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Group(title = {self.title}, description = {self.description}, link = {self.link}, category = {self.category}, views_count = {self.view_count}, report_count = {self.report_count})"