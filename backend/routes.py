import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys
from . import app

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
with open(json_url) as f:
    songs_list: list = json.load(f)

# MongoDB connection, use your own credentials. host.docker.internal > redirects to the host machine from a Docker container.
mongodb_service = os.environ.get('MONGODB_SERVICE', 'mongodb')
mongodb_username = os.environ.get('MONGODB_USERNAME', 'admin')
mongodb_password = os.environ.get('MONGODB_PASSWORD', 'admin')
mongodb_port = os.environ.get('MONGODB_PORT', '27017')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    URL = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}:{mongodb_port}/api_concerts_songs?authSource=admin"
    print(f"Using MongoDB user: {mongodb_username}")
    print(f"MongoDB URL: {URL}")
else:
    URL = f"mongodb://{mongodb_service}:{mongodb_port}"
    print(f"Using MongoDB user: {mongodb_username}")
    print(f"MongoDB URL: {URL}")

try:
    client = MongoClient(URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    app.logger.info("Connected to MongoDB successfully.")
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")
    sys.exit(1)
except Exception as e:
    app.logger.error(f"MongoDB connection error: {str(e)}")
    sys.exit(1)

try:
    db = client.api_concerts_songs
    db.api_concerts_songs.drop()
    db.api_concerts_songs.insert_many(songs_list)
except Exception as e:
    app.logger.error(f"Error inserting initial data: {str(e)}")
    sys.exit(1)


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint to verify if the service is running."""
    return jsonify(dict(status="OK")), 200


@app.route("/count", methods=["GET"])
def count_song():
    """Endpoint to count the number of songs in the database."""
    count_songs = db.api_concerts_songs.count_documents({})
    return {"songs": count_songs}, 200


@app.route("/songs", methods=["GET"])
def get_songs():
    """Endpoint to retrieve all songs from the database."""
    songs = db.api_concerts_songs.find({})
    return jsonify(parse_json(songs)), 200


@app.route("/song/<int:id>", methods=["GET"])
def get_song(id):
    """Endpoint to retrieve a specific song by its ID."""
    song = db.api_concerts_songs.find({"id": id})
    return jsonify(parse_json(song))


@app.route("/song", methods=["POST"])
def post_song():
    """Endpoint to add a new song to the database."""
    json_request = request.get_json()

    if not json_request:
        return {"message": "Content not found"}, 400

    db_document_song = db.songs.find_one({"id": json_request["id"]})

    if db_document_song == None:
            document_song = {
                "id": json_request['id'],
                "title": json_request['title'],
                "lyrics": json_request['lyrics'],
            }
            db_post = db.api_concerts_songs.insert_one(document_song)
            return {"insert id": str(db_post.inserted_id)}, 201
    return {"message": f"music with id {json_request['id']} already exists!"}, 302


@app.route("/song/<int:id>", methods=["PUT"])
def put_song(id):
    """Endpoint to update an existing song by its ID."""
    json_request = request.get_json()

    if not json_request:
        return {"message": "Content not found"}, 400

    db_document_song = db.api_concerts_songs.find_one({"id": id})

    if db_document_song is not None:
        song_update = db.songs.find_one({"id": id})
        json_song_update = parse_json(song_update)
        keys = ['title', 'lyrics']
        if {k: json_request[k] for k in keys} == {k: json_song_update[k] for k in keys}: 
            return {"message": "song found, but nothing updated"}, 200
        
        document_song = {
                "$set": {
                    "title": json_request['title'],
                    "lyrics": json_request['lyrics'],
                }
            }

        db.api_concerts_songs.update_one({"id": id}, document_song)
        song_updated = db.api_concerts_songs.find_one({"id": id})

        json_song_updated = parse_json(song_updated)
        return jsonify(json_song_updated), 201
    return {"message": f"id {id} not found"}, 400


@app.route("/song/<int:id>", methods=["DELETE"])
def del_song(id):
    """Endpoint to delete a song by its ID."""
    try:
        document_song = db.api_concerts_songs.find_one({"id": id})
        if document_song != None:
            db.api_concerts_songs.delete_one({"id": id})
            return {"message": f"id {id} removed"}, 204
        else:
            return {"message": f"id {id} not found"}, 404
    except Exception:
        return {"message": f"Data base error {document_song}"}, 500
