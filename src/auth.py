from flask import Blueprint, request 
from flask.json import jsonify
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED , HTTP_200_OK
from src.database import db, User
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
@swag_from("./docs/auth/register.yaml")
def register():
    device_id = request.json['device_id']
    device_os_version = request.json['device_os_version']
    device_model = request.json['device_model']

    if len(device_id) == 0:
        return jsonify({'error':'Device id should not be empty!'}), HTTP_400_BAD_REQUEST

    user = User(device_id = device_id, device_os_version = device_os_version, device_model = device_model)
    db.session.add(user)
    db.session.commit()

    refresh = create_refresh_token(identity=user.id)
    access = create_access_token(identity=user.id)

    return jsonify({
        'message' : "User Created",
        'user': {
            'refresh_token':refresh,
            'access_token': access,
            'device_id' : device_id
        }
    }), HTTP_201_CREATED

@auth.post('/login')
@swag_from("./docs/auth/login.yaml")
def login():
    device_id = request.json.get('device_id', '')
    
    user = User.query.filter_by(device_id=device_id).first()

    if user:
        refresh = create_refresh_token(identity=user.id)
        access = create_access_token(identity=user.id)

        return jsonify({
            'user' : {
                'refresh_token':refresh,
                'access_token': access,
                'device_id': user.device_id
            }
        }), HTTP_200_OK
    else:
        return jsonify({'error':'Wrong Credentials'}), HTTP_401_UNAUTHORIZED

@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    return jsonify({
        "device_id":user.device_id,
        "device_os_version":user.device_os_version
    }), HTTP_200_OK

@auth.get("/token/refresh")
@jwt_required(refresh=True)
@swag_from("./docs/auth/refresh_token.yaml")
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity = identity)

    return jsonify({
        "access_token":access
    }), HTTP_200_OK