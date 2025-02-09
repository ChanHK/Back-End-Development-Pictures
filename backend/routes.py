from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    if data:
        return jsonify(data), 200

    return {"message": "Internal server error"}, 500

######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    if data:
        picture = next((p for p in data if p["id"] == id), None)

        if picture:
            return jsonify(picture), 200

    return jsonify({"message": "Picture not found"}), 404


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    picture = request.get_json()

    if not picture or "id" not in picture:
        return jsonify({"message": "Invalid request, 'id' is required"}), 400

    # Check for duplicate ID
    if any(p["id"] == picture["id"] for p in data):
        return jsonify({"Message": f"picture with id {picture['id']} already present"}), 302

    data.append(picture)

    # Save to file
    with open(json_url, "w") as file:
        json.dump(data, file, indent=4)

    return jsonify(picture), 201

######################################################################
# UPDATE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    picture_data = request.get_json()

    if not picture_data:
        return jsonify({"message": "Invalid request, data is required"}), 400  # Bad Request

    # Find the picture by ID
    for index, picture in enumerate(data):
        if picture["id"] == id:
            # Update the existing dictionary with new data
            data[index].update(picture_data)

            # Save changes to the file
            with open(json_url, "w") as file:
                json.dump(data, file, indent=4)

            return jsonify({"message": "Picture updated successfully", "picture": data[index]}), 200  # OK

    return jsonify({"message": "Picture not found"}), 404  # Not Found


######################################################################
# DELETE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    global data

    # Find the picture by ID
    picture = next((p for p in data if p["id"] == id), None)

    if not picture:
        return jsonify({"message": "Picture not found"}), 404  # Return 404 if not found

    # Remove the picture from the list
    data = [p for p in data if p["id"] != id]

    # Save updated list to file
    with open(json_url, "w") as file:
        json.dump(data, file, indent=4)

    return "", 204 
