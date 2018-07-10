from flask import redirect, flash, url_for, request, abort, jsonify, send_from_directory
from app.errors import bad_request
from app import app, db
from app.models import Client, Notary, User
import os
from config import Config
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


# w3 = Web3(HTTPProvider('http://localhost:8545'))
# w3.eth.defaultAccount = w3.eth.accounts[0]

#<editor-fold desc="Notary api">
@app.route('/api/v0.1/login', methods=['GET'])
def login():
	email = request.args.get('email')
	password_hash = request.args.get('password')
	user = User.query.filter_by(email = email).first_or_404()
	if (user.check_password(password_hash)):
		return '201'
	else:
		return '401'

#</editor-fold>

#<editor-fold desc="Notary api">
@app.route('/api/v0.1/notaries/<string:notary_address>', methods=['GET'])
def get_notary_by_address(notary_address):
	return jsonify(Notary.query.filter_by(address =notary_address).first_or_404().to_dict())


@app.route('/api/v0.1/notaries/<int:notary_id>', methods=['GET'])
def get_notary(notary_id):
	return jsonify(Notary.query.get_or_404(notary_id).to_dict())

@app.route('/api/v0.1/notaries/', methods=['GET'])
def get_notaries():
	a = []
	for notary in Notary.query.all():
		a.append(notary.to_dict())
	return jsonify(a)
#</editor-fold>

#<editor-fold desc="Client api">
@app.route('/api/v0.1/clients/<string:client_address>', methods=['GET'])
def get_client_by_address(client_address):
	return jsonify(Client.query.filter_by(address =client_address).first_or_404().to_dict())


@app.route('/api/v0.1/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
	return jsonify(Client.query.get_or_404(client_id).to_dict())

@app.route('/api/v0.1/clients', methods=['POST'])
def create_client():
	data = request.get_json() or {}
	if 'address' not in data or 'email' not in data or 'password' not in data:
		return bad_request('must include address, email and password fields')
	if 'name' not in data or 'surname' not in data:
		return bad_request('must include name and surname')
	if Notary.query.filter_by(address=data['address']).first():
		return bad_request('user with this address already exist')
	if Notary.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
	client = Client()
	client.from_dict(data, new_user=True)
	db.session.add(client)
	db.session.commit()
	response = jsonify(client.to_dict())
	response.status_code = 201
	response.headers['Location'] = url_for('get_notary', id=client.id)
	return response

@app.route('/api/v0.1/clients/<int:id>', methods=['PUT'])
def update_client(id):
	client = Client.query.get_or_404(id)
	data = request.get_json() or {}
	if 'address' in data and data['address'] != client.address and \
		Client.query.filter_by(address=data['address']).first():
		return bad_request('please use a different address')
	if 'email' in data and data['email'] != client.email and \
		Client.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
	client.from_dict(data, new_user=False)
	db.session.commit()
	return jsonify(client.to_dict())
#</editor-fold>

#<editor-fold desc="Files api">
@app.route('/api/v0.1/files/<filename>', methods=['POST'])
def load_file(filename):
	if '/' in filename:
		abort(400, 'No subdirectories directories allowed')
	with open(os.path.join(Config.FILES_PATH, filename), 'wb') as fp:
		fp.write(request.data)

	return '', 201


@app.route('/api/v0.1/files/<path:path>', methods=['GET'])
def get_file(path):
	return send_from_directory(Config.FILES_PATH, path, as_attachment=True)
#</editor-fold>