from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify

db = SQLAlchemy()

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    movies = db.relationship('Movie', secondary='movie_genres', back_populates='genres')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    duration = db.Column(db.Integer)  # in minutes
    rating = db.Column(db.Float, default=0.0)
    cover_image = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    genres = db.relationship('Genre', secondary='movie_genres', back_populates='movies')
    reviews = db.relationship('Review', back_populates='movie', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Movie, self).__init__(*args, **kwargs)
        if self.title:
            self.slug = slugify(self.title)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    movie = db.relationship('Movie', back_populates='reviews')

# Association table for movie-genre relationship
movie_genres = db.Table('movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)
