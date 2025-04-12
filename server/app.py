#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def get_campers():

    campers = [camper.to_dict() for camper in Camper.query.all()]

    if request.method == 'GET':
        return make_response(campers, 200)
    
    elif request.method == 'POST':
         
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')

        if not name or not age:
            return {'errors': 'Name and age are required'}, 400
        
        if age < 8 or age > 18:
             return {'errors': 'Age cannot be younger than 8 or older than 18.'}, 400
        
        new_camper = Camper(name = name, age = age)

        db.session.add(new_camper)
        db.session.commit()

        response = make_response(
            new_camper.to_dict(),
            201
        )

        return response
         

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter_by(id=id).first()

    if request.method == 'GET':
        if camper:
            response = make_response(
                camper.to_dict(include_signups=True),
                200
            )
            return response 
        else:
            return {'error': 'Camper not found'}, 404
        
    elif request.method == 'PATCH':
        if not camper:
            return {"error": "Camper not found"}, 404
        
        data = request.get_json()

        if not data:
            return {"errors": ["No input data provided"]}, 400

        name = data.get('name')
        age = data.get('age')

        validation_errors = []

        if name == '': 
            validation_errors.append('Name cannot be empty')
        if name:
            camper.name = name
        
        if age:
            try:
                if age < 8 or age > 18:
                    validation_errors.append('Age must be between 8 and 18')
                camper.age = age
            except ValueError as e:
                validation_errors.append(str(e))

        if validation_errors:
            return {'errors': ['validation errors']}, 400
            
        db.session.commit()

        return make_response(camper.to_dict(), 202)

@app.route('/activities')
def get_activities():
    activities = [activity.to_dict() for activity in Activity.query.all()]

    return make_response(activities, 200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activities(id):
    activity = Activity.query.filter_by(id=id).first()

    if not activity:
        return {'error': 'Activity not found'}, 404

    db.session.delete(activity)
    db.session.commit()

    return make_response({}, 204)

@app.route('/signups', methods=['POST'])
def signups():
    data = request.get_json()

    required_fields = ['time', 'camper_id', 'activity_id']
    if not all(field in data for field in required_fields):
        return {'errors': ["validation errors"]}, 400

    try:
        new_signup = Signup(
            time=data['time'],
            camper_id=data['camper_id'],
            activity_id=data['activity_id']
        )

        db.session.add(new_signup)
        db.session.commit()

        return make_response(new_signup.to_dict(), 201)

    except Exception:
        return {'errors': ["validation errors"]}, 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
