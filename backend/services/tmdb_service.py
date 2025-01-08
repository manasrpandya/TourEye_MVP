from tmdbv3api import TMDb, Movie, Genre, Discover, TV
import requests
import os

class TMDBService:
    def __init__(self):
        self.tmdb = TMDb()
        self.api_key = os.getenv('TMDB_API_KEY', 'e889297f45708465dad1aae3216b1c44')
        self.tmdb.api_key = self.api_key
        self.tmdb.language = 'en'
        self.movie = Movie()
        self.genre = Genre()
        self.discover = Discover()
        self.tv = TV()
        self.DOCUMENTARY_GENRE_ID = 99
        self.base_url = "https://api.themoviedb.org/3"

    def get_movie_details(self, movie_id):
        try:
            movie = self.movie.details(movie_id)
            videos = self.movie.videos(movie_id)
            trailer = None
            if videos:
                for video in videos:
                    if hasattr(video, 'type') and hasattr(video, 'site'):
                        if video.type == 'Trailer' and video.site == 'YouTube':
                            trailer = video
                            break
            
            return {
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None,
                'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.backdrop_path}" if movie.backdrop_path else None,
                'release_date': movie.release_date,
                'vote_average': movie.vote_average,
                'genres': [genre.name for genre in movie.genres] if hasattr(movie, 'genres') else [],
                'trailer_key': trailer.key if trailer else None
            }
        except Exception as e:
            print(f"Error in get_movie_details: {e}")
            raise

    def get_series_details(self, series_id):
        try:
            series = self.tv.details(series_id)
            videos = self.tv.videos(series_id)
            trailer = None
            if videos:
                for video in videos:
                    if hasattr(video, 'type') and hasattr(video, 'site'):
                        if video.type == 'Trailer' and video.site == 'YouTube':
                            trailer = video
                            break
            
            return {
                'id': series.id,
                'name': series.name,
                'overview': series.overview,
                'poster_path': f"https://image.tmdb.org/t/p/w500{series.poster_path}" if series.poster_path else None,
                'backdrop_path': f"https://image.tmdb.org/t/p/original{series.backdrop_path}" if series.backdrop_path else None,
                'first_air_date': series.first_air_date,
                'vote_average': series.vote_average,
                'number_of_seasons': series.number_of_seasons if hasattr(series, 'number_of_seasons') else 0,
                'seasons': series.seasons if hasattr(series, 'seasons') else [],
                'genres': [genre.name for genre in series.genres] if hasattr(series, 'genres') else [],
                'trailer_key': trailer.key if trailer else None
            }
        except Exception as e:
            print(f"Error in get_series_details: {e}")
            raise

    def get_popular_movies(self, page=1):
        movies = self.movie.popular(page=page)
        return [self._format_movie(movie) for movie in movies]

    def get_trending_movies(self):
        movies = self.movie.popular()
        return [self._format_movie(movie) for movie in movies][:8]

    def get_popular_series(self, page=1):
        series = self.tv.popular(page=page)
        return [self._format_series(show) for show in series]

    def get_trending_series(self):
        series = self.tv.popular()
        return [self._format_series(show) for show in series][:8]

    def search_movies(self, query, page=1):
        movies = self.movie.search(query, page=page)
        return [self._format_movie(movie) for movie in movies]

    def search_series(self, query, page=1):
        series = self.tv.search(query, page=page)
        return [self._format_series(show) for show in series]

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

    def get_documentaries(self, page=1):
        try:
            print("DEBUG: Starting get_documentaries")
            discover = Discover()
            print("DEBUG: Created Discover instance")
            
            # Try using discover_movies with minimal parameters first
            movies = discover.discover_movies({
                'with_genres': self.DOCUMENTARY_GENRE_ID,
                'page': page
            })
            print(f"DEBUG: Got movies response: {type(movies)}")
            
            formatted_docs = []
            for movie in movies:
                print(f"DEBUG: Processing movie: {movie.id if hasattr(movie, 'id') else 'No ID'}")
                try:
                    # Get full movie details to ensure we have all required data
                    details = self.movie.details(movie.id)
                    print(f"DEBUG: Got details for movie {movie.id}")
                    
                    formatted_doc = {
                        'id': details.id,
                        'title': details.title,
                        'overview': details.overview,
                        'poster_path': f"https://image.tmdb.org/t/p/w500{details.poster_path}" if details.poster_path else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{details.backdrop_path}" if details.backdrop_path else None,
                        'release_date': getattr(details, 'release_date', 'Unknown'),
                        'vote_average': getattr(details, 'vote_average', 0.0)
                    }
                    formatted_docs.append(formatted_doc)
                    print(f"DEBUG: Successfully formatted movie {movie.id}")
                except Exception as e:
                    print(f"DEBUG: Error processing movie {movie.id if hasattr(movie, 'id') else 'Unknown'}: {str(e)}")
                    continue
            
            print(f"DEBUG: Returning {len(formatted_docs)} documentaries")
            return formatted_docs
        except Exception as e:
            print(f"DEBUG: Top-level error in get_documentaries: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return []

    def get_documentary_details(self, documentary_id):
        return self.get_movie_details(documentary_id)

    def get_trending_documentaries(self):
        try:
            print("DEBUG: Starting get_trending_documentaries")
            discover = Discover()
            print("DEBUG: Created Discover instance")
            
            # Try using discover_movies with minimal parameters first
            movies = discover.discover_movies({
                'with_genres': self.DOCUMENTARY_GENRE_ID,
                'page': 1
            })
            print(f"DEBUG: Got movies response: {type(movies)}")
            
            formatted_docs = []
            for movie in movies[:8]:
                print(f"DEBUG: Processing movie: {movie.id if hasattr(movie, 'id') else 'No ID'}")
                try:
                    # Get full movie details to ensure we have all required data
                    details = self.movie.details(movie.id)
                    print(f"DEBUG: Got details for movie {movie.id}")
                    
                    formatted_doc = {
                        'id': details.id,
                        'title': details.title,
                        'overview': details.overview,
                        'poster_path': f"https://image.tmdb.org/t/p/w500{details.poster_path}" if details.poster_path else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{details.backdrop_path}" if details.backdrop_path else None,
                        'release_date': getattr(details, 'release_date', 'Unknown'),
                        'vote_average': getattr(details, 'vote_average', 0.0)
                    }
                    formatted_docs.append(formatted_doc)
                    print(f"DEBUG: Successfully formatted movie {movie.id}")
                except Exception as e:
                    print(f"DEBUG: Error processing movie {movie.id if hasattr(movie, 'id') else 'Unknown'}: {str(e)}")
                    continue
            
            print(f"DEBUG: Returning {len(formatted_docs)} trending documentaries")
            return formatted_docs
        except Exception as e:
            print(f"DEBUG: Top-level error in get_trending_documentaries: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            return []

    def _format_movie(self, movie):
        try:
            return {
                'id': getattr(movie, 'id', 0),
                'title': getattr(movie, 'title', 'Unknown Title'),
                'overview': getattr(movie, 'overview', 'No overview available'),
                'poster_path': getattr(movie, 'poster_path', None),
                'backdrop_path': getattr(movie, 'backdrop_path', None),
                'release_date': getattr(movie, 'release_date', 'Unknown'),
                'vote_average': getattr(movie, 'vote_average', 0.0)
            }
        except Exception as e:
            print(f"Error formatting movie: {e}")
            return None

    def _format_series(self, series):
        return {
            'id': series.id,
            'name': series.name,
            'overview': series.overview,
            'poster_path': series.poster_path,
            'backdrop_path': series.backdrop_path,
            'first_air_date': getattr(series, 'first_air_date', None),
            'vote_average': series.vote_average
        }
