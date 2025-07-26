from . import app
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

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

#client = MongoClient(
#    f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))


######################################################################
# INSERT CODE HERE
######################################################################
@app.route("/health", methods=["GET"])
def health():
    return jsonify(dict(status="OK")), 200


@app.route("/count", methods=["GET"])
def count_song():
    count_songs = db.songs.count_documents({})
    return {"songs": count_songs}, 200


@app.route("/songs", methods=["GET"])
def get_songs():
    songs = db.songs.find({})
    return jsonify(parse_json(songs)), 200


@app.route("/song/<int:id>", methods=["GET"])
def get_song(id):
    song = db.songs.find({"id": id})
    return jsonify(parse_json(song))


@app.route("/song", methods=["POST"])
def post_song():
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
            
            db_post = db.songs.insert_one(document_song)
            return {"insert id": str(db_post.inserted_id)}, 201
    return {"message": f"music with id {json_request['id']} already exists!"}, 302


@app.route("/song/<int:id>", methods=["PUT"])
def put_song(id):
    json_request = request.get_json()

    if not json_request:
        return {"message": "Content not found"}, 400

    db_document_song = db.songs.find_one({"id": id})

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

        db.songs.update_one({"id": id}, document_song)
        song_updated = db.songs.find_one({"id": id})

        json_song_updated = parse_json(song_updated)
        return jsonify(json_song_updated), 201
    return {"message": f"id {id} not found"}, 400


@app.route("/song/<int:id>", methods=["DELETE"])
def del_song(id):
    try:
        document_song = db.songs.find_one({"id": id})
        if document_song != None:
            db.songs.delete_one({"id": id})
            return {"message": f"id {id} removed"}, 204
        else:
            return {"message": f"id {id} not found"}, 404
    except Exception:
        return {"message": f"Data base error {document_song}"}, 500