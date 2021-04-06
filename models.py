from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    facebook_link = db.Column(db.String(120))
    #!!* missing fields *!!
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    website_link = db.Column(db.String(500))
    artists = db.relationship('Show', back_populates='Venue')
    shows = db.relationship('Show', backref=db.backref('venue'), lazy="joined")
    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #!!* missing fields *!!
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    website_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    venues = db.relationship('Show', back_populates='Artist')
    shows = db.relationship('Show', backref=db.backref('artist'), lazy="joined")
    # DONE: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'
    atrist_id = db.Column(db.Integer(), db.ForeignKey(
        "Artist.id"), primary_key=True)
    venue_id = db.Column(db.Integer(), db.ForeignKey(
        "Venue.id"), primary_key=True)
    start_time = db.Column(db.DateTime(), primary_key=True)
    Artist = db.relationship("Artist", back_populates="venues", viewonly=True)
    Venue = db.relationship("Venue", back_populates="artists", viewonly=True)
    # DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
