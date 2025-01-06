from tmdbv3api import TMDb, Movie, Genre, Discover
import os

class TMDBService:
    def __init__(self):
        self.tmdb = TMDb()
        self.tmdb.api_key = 'e889297f45708465dad1aae3216b1c44'
        self.tmdb.language = 'en'
        self.movie = Movie()
        self.genre = Genre()
        self.discover = Discover()

    def get_popular_movies(self, page=1):
        movies = self.movie.popular(page=page)
        return [self._format_movie(movie) for movie in movies]

    def get_movie_details(self, movie_id):
        movie = self.movie.details(movie_id)
        videos = self.movie.videos(movie_id)
        trailer = next((video for video in videos if video.type == 'Trailer' and video.site == 'YouTube'), None)
        
        return {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster_path': f"https://image.tmdb.org/t/p/w500{movie.poster_path}",
            'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.backdrop_path}",
            'release_date': movie.release_date,
            'vote_average': movie.vote_average,
            'genres': [genre.name for genre in movie.genres],
            'trailer_key': trailer.key if trailer else None
        }

    def search_movies(self, query, page=1):
        movies = self.movie.search(query, page=page)
        return [self._format_movie(movie) for movie in movies]

    def get_movies_by_genre(self, genre_id, page=1):
        movies = self.discover.discover_movies({
            'with_genres': genre_id,
            'page': page
        })
        return [self._format_movie(movie) for movie in movies]

    def get_similar_movies(self, movie_id):
        movies = self.movie.similar(movie_id)
        return [self._format_movie(movie) for movie in movies]

    def get_genres(self):
        return self.genre.movie_list()

    def get_movie_credits(self, movie_id):
        return self.movie.credits(movie_id)

    def _format_movie(self, movie):
        return {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster_path': movie.poster_path,
            'release_date': movie.release_date,
            'vote_average': movie.vote_average
        }
