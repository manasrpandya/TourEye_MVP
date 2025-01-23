from flask import Flask, render_template, request, jsonify, session
from services.tmdb_service import TMDBService
from services.news_service import NewsService
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  

# Initialize services
tmdb_service = TMDBService()
news_service = NewsService()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# Language dictionary
LANGUAGES = {
    'en': 'English',
    'sw': 'Swahili'
}

@app.before_request
def before_request():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'English'

@app.template_filter('datetime')
def format_datetime(value):
    """Format datetime string to a more readable format."""
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%B %d, %Y")
    except:
        return value

@app.route('/')
def home():
    try:
        # Get featured movies and trending series
        featured_movies = tmdb_service.get_trending_movies()
        trending_series = tmdb_service.get_trending_series()

        return render_template('home.html', 
                            featured_movies=featured_movies,
                            trending_series=trending_series[:3])
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error="Unable to load content at this time.")

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
    try:
        movie = tmdb_service.get_movie_details(movie_id)
        credits = tmdb_service.movie.credits(movie_id)
        similar_movies = tmdb_service.get_similar_movies(movie_id)
        return render_template('movie_details.html',
                         movie=movie,
                         similar_movies=similar_movies[:4],
                         credits=credits)
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return render_template('error.html', error="Unable to fetch movie details at this time.")

@app.route('/series')
def series():
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search')

        if search:
            series_list = tmdb_service.search_series(search, page)
        else:
            series_list = tmdb_service.get_popular_series(page)
            
        trending_series = tmdb_service.get_trending_series()

        return render_template('series.html', 
                            popular_series=series_list,
                            trending_series=trending_series,
                            current_page=page)
    except Exception as e:
        print(f"Error fetching series: {e}")
        return render_template('error.html', error="Unable to fetch series at this time.")

@app.route('/series/<int:series_id>')
def series_detail(series_id):
    try:
        series = tmdb_service.get_series_details(series_id)
        credits = tmdb_service.tv.credits(series_id)
        
        # Process credits data
        cast = []
        if hasattr(credits, 'cast'):
            cast = credits.cast[:12] if len(credits.cast) > 12 else credits.cast

        return render_template('series_detail.html', 
                            series=series,
                            cast=cast)
    except Exception as e:
        print(f"Error fetching series details: {e}")
        return render_template('error.html', error="Unable to fetch series details at this time.")

@app.route('/documentaries')
def documentaries():
    try:
        page = request.args.get('page', 1, type=int)
        documentaries = tmdb_service.get_documentaries(page=page)
        
        if not documentaries:
            return render_template('documentaries.html', 
                                documentaries=[],
                                current_page=1,
                                total_pages=1,
                                error="No documentaries found at this time. Please try again later.")
                                
        return render_template('documentaries.html', 
                             documentaries=documentaries,
                             current_page=page,
                             total_pages=20)  # TMDB typically has 20 pages
    except Exception as e:
        print(f"Error fetching documentaries: {e}")
        return render_template('error.html', error="Unable to fetch documentaries at this time.")

@app.route('/documentary/<int:documentary_id>')
def documentary_details(documentary_id):
    try:
        documentary = tmdb_service.get_documentary_details(documentary_id)
        credits = tmdb_service.movie.credits(documentary_id)
        
        # Process credits data
        cast = []
        if hasattr(credits, 'cast'):
            cast = credits.cast[:12] if len(credits.cast) > 12 else credits.cast

        return render_template('documentary_detail.html', 
                            documentary=documentary,
                            cast=cast)
    except Exception as e:
        print(f"Error fetching documentary details: {e}")
        return render_template('error.html', error="Unable to fetch documentary details at this time.")

@app.route('/e-magazines')
def magazines():
    try:
        page = int(request.args.get('page', 1))
        search_query = request.args.get('q')
        category = request.args.get('category')
        
        if search_query:
            magazines_data = news_service.search_magazines(search_query, page)
        else:
            categories = [category] if category else None
            magazines_data = news_service.get_top_stories(page, categories)
        
        return render_template(
            'magazines.html',
            magazines=magazines_data,
            categories=news_service.get_categories(),
            error=None
        )
    except Exception as e:
        return render_template(
            'magazines.html',
            magazines={'articles': [], 'meta': {}},
            categories=news_service.get_categories(),
            error="Error loading magazines. Please try again later."
        )

@app.route('/games')
def games():
    try:
        return render_template('games.html')
    except Exception as e:
        print(f"Error loading games page: {e}")
        return render_template('error.html', error="Unable to load games page at this time.")

@app.route('/api/genres')
def get_genres():
    genres = tmdb_service.get_genres()
    return jsonify([{'id': genre.id, 'name': genre.name} for genre in genres])

@app.route('/set-language', methods=['POST'])
def set_language():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        language = data.get('language')
        if language not in ['en', 'sw']:
            return jsonify({'status': 'error', 'message': 'Invalid language'}), 400
        
        # Set the language in session
        session['language'] = LANGUAGES[language]
        session.modified = True
        
        return jsonify({
            'status': 'success',
            'message': f'Language changed to {LANGUAGES[language]}',
            'language': LANGUAGES[language]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
