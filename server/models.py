from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="activity", cascade="all, delete-orphan")
    campers = db.relationship("Camper", secondary="signups", back_populates="activities", overlaps='signups')

    # Add serialization rules
    def to_dict(self, include_signups=False):
        data = {
            'id': self.id,
            'name': self.name,
            'difficulty': self.difficulty
        }
        if include_signups:
            data['signups'] = [signup.to_dict(include_activity=False) for signup in self.signups]
        return data

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="camper", cascade="all, delete-orphan", overlaps='campers')
    activities = db.relationship("Activity", secondary="signups", back_populates="campers", overlaps='signups')

    # Add serialization rules
    def to_dict(self, include_signups=False):
        data = {
            'id': self.id,
            'name': self.name,
            'age': self.age
        }
        if include_signups:
            data['signups'] = [signup.to_dict(include_camper=False) for signup in self.signups]
        return data
    
    # Add validation
    @validates("name")
    def validates_name(self, key, name):
        if not name:
            raise ValueError('Camper must have a name.')
        return name
    
    @validates("age")
    def validates_age(self, key, age):
        if not (8 <= age <= 18):
            raise ValueError('Age cannot be younger than 8 or older than 18.')
        return age
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    # Add relationships
    camper = db.relationship("Camper", back_populates="signups", overlaps='activities,campers')
    activity = db.relationship("Activity", back_populates="signups", overlaps='activities,campers')

    # Add serialization rules
    def to_dict(self, include_camper=True, include_activity=True):
        data = {
            'id': self.id,
            'time': self.time,
            'camper_id': self.camper_id,
            'activity_id': self.activity_id
        }
        if include_camper:
            data['camper'] = self.camper.to_dict()
        if include_activity:
            data['activity'] = self.activity.to_dict()
        return data
    
    # Add validation
    @validates("time")
    def validates_time(self, key, time):
        if not (0 <= time <= 23):
            raise ValueError('Time must be between 0 and 23.')
        return time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
