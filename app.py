from flask import Flask, request, jsonify

from service import check_health, add_user, add_tags, get_users_by_tags, cleanup_expired_tags
import json
import os
import threading

from flask_cors import CORS

from connection import init_pool

from utils.logger_config import setup_logger

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db, User, UserTags
from config_loader import CONFIG


logger = setup_logger('app')

app = Flask(__name__)

CORS(app)

db_url = (
    f"postgresql://{CONFIG['username']}:{CONFIG['password']}"
    f"@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['dbname']}"
)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)



@app.route("/api/health", methods=["GET"])
def health():
    health_status = check_health() 
    return jsonify({"status": health_status})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    required_fields = ["firstName", "lastName", "password", "phone"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    user_id = add_user(data["firstName"], data["lastName"], data["password"], data["phone"])

    return jsonify({"id": user_id}), 201  


@app.route('/api/users/<int:user_id>/tags', methods=['POST'])
def add_tags_route(user_id):
    print(user_id, request.get_json())
    tags_data = request.get_json()  
    tags = tags_data.get('tags', [])
    expiry = tags_data.get('expiry', 0)

    if add_tags(user_id, tags, expiry):  
        return jsonify({"message": "Tags added successfully"}), 200
    else:
        return jsonify({"message": "Error adding tags"}), 400



@app.route('/api/users', methods=['GET'])
def get_users():
    tags_param = request.args.get("tags")
    if not tags_param:
        return jsonify({"error": "Tags parameter is required"}), 400

    tags = tags_param.split(",")  

    users = get_users_by_tags(tags)

    if not users:
        return jsonify({"users": []}), 200

    return jsonify({"users": users}), 200


def run_cleanup_thread():
    cleanup_thread = threading.Thread(target=cleanup_expired_tags)
    cleanup_thread.daemon = True 
    cleanup_thread.start()

if __name__ == '__main__':
    project_directory = os.path.abspath(os.path.dirname(__file__))

    

    conninfo = (
        f"host={CONFIG['host']} "
        f"port={CONFIG['port']} "
        f"user={CONFIG['username']} "
        f"password={CONFIG['password']} "
        f"dbname={CONFIG['dbname']}"
    )
    init_pool(conninfo)
    run_cleanup_thread()
    
    app.run(debug=True, host='0.0.0.0', port=5001)


