from flask import Flask, render_template, request, jsonify
from services.tmdb_service import TMDBService

app = Flask(__name__)
tmdb_service = TMDBService()

@app.route('/')
def home():
    popular_movies = tmdb_service.get_popular_movies()
    genres = tmdb_service.get_genres()
    return render_template('home.html', 
                         featured_movies=popular_movies[:8], 
                         genres=genres)

@app.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre')
    search = request.args.get('search')
    
    if search:
        movies = tmdb_service.search_movies(search, page)
    elif genre:
        genre_obj = next((g for g in tmdb_service.get_genres() if g.name.lower() == genre.lower()), None)
        if genre_obj:
            movies = tmdb_service.get_movies_by_genre(genre_obj.id, page)
        else:
            movies = tmdb_service.get_popular_movies(page)
    else:
        movies = tmdb_service.get_popular_movies(page)
    
    return render_template('movies.html',
                         movies=movies,
                         genres=tmdb_service.get_genres(),
                         current_page=page)

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = tmdb_service.get_movie_details(movie_id)
    similar_movies = tmdb_service.get_similar_movies(movie_id)
    credits = tmdb_service.get_movie_credits(movie_id)
    
    return render_template('movie_details.html',
                         movie=movie,
                         similar_movies=similar_movies[:4],
                         credits=credits)

@app.route('/api/genres')
def get_genres():
    genres = tmdb_service.get_genres()
    return jsonify([{'id': genre.id, 'name': genre.name} for genre in genres])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
