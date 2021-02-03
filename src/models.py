from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from src import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)  # noqa
    name = db.Column(db.String)  # noqa
    city = db.Column(db.String(120))  # noqa
    state = db.Column(db.String(120))  # noqa
    address = db.Column(db.String(120))  # noqa
    phone = db.Column(db.String(120))  # noqa
    image_link = db.Column(db.String(500))  # noqa
    facebook_link = db.Column(db.String(120))  # noqa

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))  # noqa
    shows = db.relationship('Show', backref='venue',
                            lazy=True, cascade='all, delete-orphan')  # noqa
    seeking_description = db.Column(db.String(120), nullable=True)  # noqa
    website = db.Column(db.String(120))  # noqa

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)  # noqa
    name = db.Column(db.String)  # noqa
    city = db.Column(db.String(120))  # noqa
    state = db.Column(db.String(120))  # noqa
    phone = db.Column(db.String(120))  # noqa
    image_link = db.Column(db.String(500))  # noqa
    facebook_link = db.Column(db.String(120))  # noqa

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))  # noqa
    shows = db.relationship('Show', backref='artist',
                            lazy=True, cascade='all, delete-orphan')  # noqa
    seeking_description = db.Column(db.String(120), nullable=True)  # noqa
    website = db.Column(db.String(120))  # noqa

    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"


# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)  # noqa
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)  # noqa
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)  # noqa
    start_time = db.Column(db.DateTime, nullable=False)  # noqa

    def __repr__(self):
        return f"<Show {self.id} {self.artist_id} <-> {self.venue_id}"
