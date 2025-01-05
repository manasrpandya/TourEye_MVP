# Tour Eye - MVP Initial Draft

Hello guys! This is an initial draft of the Tour Eye software, for which we are trying to create a Minimum Viable Product (MVP). Our goal is to refine the UI/UX elements and enhance the interactivity of the software for demonstration to investors.
For the exact tasks ahead have a look at the [project here](https://github.com/users/manasrpandya/projects/1/views/3)
## Steps to Install and Run on Your Local Machine
**In short simply run app.py**. For more details go through the file structures and descriptions below 
### Folder Structure

```
backend
  app.py
  static
    css
      style.css
    images
      logo.jpg
      placeholder.jpg
  templates
    error.html
    movies.html
    movie_details.html
    pnr.html (placeholder not really used right now)
data
  American Hustle
    American Hustle.mkv
    American.Hustle.2013.BDRip.X264-SPARKS.srt
    cover.jpg
    details.txt
  Dune The Prophecy
    cover.jpg
    details.txt
    DunePropechy.mp4
  (so on for the rest of the movies)
```

### File Descriptions

- **backend/**
  - `app.py`: Main application file for running the backend.
  - **static/**: Contains static resources.
    - **css/**: Holds the stylesheets.
      - `style.css`: Stylesheet for the application.
    - **images/**: Stores image assets.
      - `logo.jpg`: Logo for the application.
      - `placeholder.jpg`: Placeholder image used in the UI.
  - **templates/**: Contains HTML templates for the frontend.
    - `error.html`: Error page template.
    - `movies.html`: Main movies list page template.
    - `movie_details.html`: Template for individual movie details.
    - `pnr.html`: Template for PNR-related functionalities.

- **data/**
  - **Movie Folders**: Each movie has its own folder containing its files.
    - `American Hustle/`
      - `American Hustle.mkv`: Movie file.
      - `American.Hustle.2013.BDRip.X264-SPARKS.srt`: Subtitle file.
      - `cover.jpg`: Cover image for the movie.
      - `details.txt`: Metadata about the movie.
    - `Dune The Prophecy/`
      - `cover.jpg`: Cover image for the movie.
      - `details.txt`: Metadata about the movie.
      - `DunePropechy.mp4`: Movie file.
    - (Other movies follow the same structure.)

### `details.txt` Structure
Each `details.txt` file contains the following information:
```
<Title of the Movie>  
<Rating>  
<Year>  
<Description of the movie>
```
**Example:**
```
American Hustle  
7.2  
2013  
A description of the movie.
