from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_DIR = os.path.join(BASE_DIR, "../data/movies")  # Movies directory
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.route('/')
def home():
    """
    Display the homepage with categories and scrolling features.
    """
    return render_template("home.html")

@app.route('/movies')
def movies():
    """
    Display the movies page with tiles of available movies.
    """
    movies = []
    for folder in os.listdir(MOVIES_DIR):
        folder_path = os.path.join(MOVIES_DIR, folder)
        if os.path.isdir(folder_path):
            details_file = os.path.join(folder_path, "details.txt")
            cover_file = os.path.join(folder_path, "cover.jpg")
            if os.path.exists(details_file):
                with open(details_file, 'r') as file:
                    lines = file.readlines()
                    if len(lines) >= 4:
                        movie = {
                            'name': lines[0].strip(),
                            'rating': lines[1].strip(),
                            'year': lines[2].strip(),
                            'description': lines[3].strip(),
                            'cover': f'/data/movies/{folder}/cover.jpg' if os.path.exists(cover_file) else '/static/images/placeholder.jpg',
                            'folder': folder
                        }
                        movies.append(movie)
    return render_template("movies.html", movies=movies)

@app.route('/movie/<movie_folder>')
def movie_details(movie_folder):
    """
    Display details and video for a selected movie.
    """
    folder_path = os.path.join(MOVIES_DIR, movie_folder)
    details_file = os.path.join(folder_path, "details.txt")
    video_file = None

    # Look for the video file
    for file in os.listdir(folder_path):
        if file.endswith(('.mp4', '.mkv', '.avi')):
            video_file = file
            break

    if not os.path.exists(details_file) or not video_file:
        abort(404)

    with open(details_file, 'r') as file:
        lines = file.readlines()
        if len(lines) < 4:
            abort(404)
        movie = {
            'name': lines[0].strip(),
            'rating': lines[1].strip(),
            'year': lines[2].strip(),
            'description': lines[3].strip(),
            'video': f'/data/movies/{movie_folder}/{video_file}'
        }
    return render_template("movie_details.html", movie=movie)

@app.route('/data/movies/<path:filename>')
def serve_movie_files(filename):
    """
    Serve movie-related files (e.g., videos, covers) from the movies directory.
    """
    return send_from_directory(MOVIES_DIR, filename)

@app.route('/static/<path:filename>')
def serve_static_files(filename):
    """
    Serve static assets such as CSS and images.
    """
    return send_from_directory(STATIC_DIR, filename)

@app.errorhandler(404)
def not_found(e):
    """
    Render a 404 error page when a resource is not found.
    """
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
