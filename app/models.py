from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime, timedelta
import os

class User(UserMixin, db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	address = db.Column(db.String(120), nullable=False, unique=True)
	name = db.Column(db.String(30), nullable=False)
	second_name = db.Column(db.String(30))
	surname = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	type = db.Column(db.String(20))
	token = db.Column(db.String(32), index=True, unique=True)
	token_expiration = db.Column(db.DateTime)

	__mapper_args__ = {
		'polymorphic_on': type,
		'polymorphic_identity': 'user'
	}

	def set_password(self, password):
		self.password_hash = password

	def check_password(self, password):
		return self.password_hash == password

	def to_dict(self, include_email=False):
		data = {
			'id': self.id,
			'address': self.address,
			'name' : self.name,
			'second_name': self.second_name,
			'surname': self.second_name,
			'token': self.token
		}
		if include_email:
			data['email'] = self.email
		return data

	def from_dict(self, data, new_user=False):
		for field in ['address', 'name', 'email', 'second_name', 'surname', 'type']:
			if field in data:
				setattr(self, field, data[field])
		if new_user and 'password' in data:
			self.set_password(data['password'])


	def get_token(self, expires_in=604800):
		now = datetime.utcnow()
		if self.token and self.token_expiration > now + timedelta(seconds=60):
			return self.token
		self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
		self.token_expiration = now + timedelta(seconds=expires_in)
		db.session.add(self)
		return self.token

	def revoke_token(self):
		self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

	@staticmethod
	def check_token(token):
		user = User.query.filter_by(token=token).first()
		if user is None or user.token_expiration < datetime.utcnow():
			return None
		return user


class Client(User, db.Model):
	agreements = db.relationship('Agreement', backref='owner')

	__mapper_args__ = {
		'polymorphic_identity': 'client',
	}

	def to_dict(self, include_email=False):
		data = super().to_dict()
		data['agreements'] = 'some data'
		return data

	def from_dict(self, data, new_user=False):
		super().from_dict(data, new_user)
		self.type = 'client'


class Notary(User, db.Model):
	license = db.Column(db.String(50))

	__mapper_args__ = {
		'polymorphic_identity': 'notary',
	}

	def to_dict(self, include_email=False):
		data = super().to_dict()
		data['licence'] = self.license
		return data

	def from_dict(self, data, new_user=False):
		super().from_dict(data, new_user)
		if 'license' in data:
			setattr(self, 'licence', data['license'])


class Agreement(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	address = db.Column(db.String(120), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def to_dict(self):
		data = {
			'id': self.id,
			'address': self.address,
			'user_id': self.user_id
		}
		return data
