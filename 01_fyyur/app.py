#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
from datetime import datetime, date 
import string 

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer, default=0)
    upcoming_shows_count = db.Column(db.Integer, default=0)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer,  default=0)
    upcoming_shows_count = db.Column(db.Integer,  default=0) 

class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime())

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  alldata = Venue.query.all()
  data = []
  city_data = []
  state_data = []
  for element in alldata:
      if element.city not in city_data and element.state not in state_data:
          dictionary = {}
          dictionary['city']=element.city
          dictionary['state']=element.state
          venue_dict={}
          venue_dict['id']=element.id
          venue_dict['name']=element.name
          venue_dict['upcoming_shows_count']=element.upcoming_shows_count
          dictionary['venues']=[venue_dict]
          data.append(dictionary)
          city_data.append(element.city)
          state_data.append(element.state)   
      else:
          for char in data:
              if element.city == char['city']:
                  venue_dict={}
                  venue_dict['id']=element.id
                  venue_dict['name']=element.name
                  venue_dict['upcoming_shows_count']=element.upcoming_shows_count
                  char['venues'].append(venue_dict)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  alldata = Venue.query.all()
  search_term = str.lower(request.form.get('search_term'))
  try: 
    response = {'count': 0, }
    dictionary = []
    for venue in alldata:
        name = str.lower(venue.name)
        if search_term in name:
            response['count'] +=1
            data_dict = {}
            data_dict['id']=venue.id
            data_dict['name']=venue.name
            dictionary.append(data_dict)
    response['data']=dictionary   
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venuedata = Venue.query.filter_by(id=venue_id).first()
  allshows=Shows.query.filter_by(venue_id=venue_id).all() 
  past_shows=[]
  upcoming_shows=[]
  for element in allshows:
    dictionary = {}
    dictionary['artist_id']= element.artist_id
    artist = Artist.query.filter_by(id=element.artist_id).first()
    dictionary['artist_name']= artist.name 
    dictionary['artist_image_link'] = artist.image_link
    dictionary['start_time'] = format_datetime(str(element.start_time))
    if element.start_time > datetime.now():
      upcoming_shows.append(dictionary)
    else:
      past_shows.append(dictionary)
  data = {
    'id' : venuedata.id,
    'name' : venuedata.name,
    'genres' : venuedata.genres,
    'address' : venuedata.address,
    'city' : venuedata.city,
    'state' : venuedata.state,
    'phone' : venuedata.phone,
    'website' : venuedata.website,
    'facebook_link' : venuedata.facebook_link,
    'seeking_talent' : venuedata.seeking_talent,
    'seeking_description' : venuedata.seeking_description,
    'image_link' : venuedata.image_link,
    'past_shows' : past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)}
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link, website="", seeking_talent=False, image_link="", past_shows_count=0, upcoming_shows_count=0)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e: 
    error = True
    flash (e)
    db.session.rollback()
    flash ('An error occured. Venue' + venue.name +  'could not be listed')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  Venue.query.filter_by(id=venue_id).delete()
  db.session.commit()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  alldata = Artist.query.all()
  data = []
  for element in alldata:
    dictionary= {}
    dictionary['id']=element.id
    dictionary['name']=element.name
    data.append(dictionary)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  alldata = Artist.query.all()
  search_term = str.lower(request.form.get('search_term'))
  try: 
    response = {'count': 0, }
    dictionary = []
    for artist in alldata:
        name = str.lower(artist.name)
        if search_term in name:
            response['count'] +=1
            data_dict = {}
            data_dict['id']=artist.id
            data_dict['name']=artist.name
            dictionary.append(data_dict)
    response['data']=dictionary   
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artistdata = Artist.query.filter_by(id=artist_id).first()
  allshows=Shows.query.filter_by(artist_id=artist_id).all() 
  past_shows=[]
  upcoming_shows=[]
  for element in allshows:
    dictionary = {}
    dictionary['venue_id']= element.venue_id
    venue = Venue.query.filter_by(id=element.venue_id).first()
    dictionary['venue_name']= venue.name 
    dictionary['venue_image_link'] = venue.image_link
    dictionary['start_time'] = format_datetime(str(element.start_time))
    if element.start_time > datetime.now():
      upcoming_shows.append(dictionary)
    else:
      past_shows.append(dictionary)
  data = {
    'id' : artistdata.id,
    'name' : artistdata.name,
    'genres' : artistdata.genres,
    'city' : artistdata.city,
    'state' : artistdata.state,
    'phone' : artistdata.phone,
    'website' : artistdata.website,
    'facebook_link' : artistdata.facebook_link,
    'seeking_venue' : artistdata.seeking_venue,
    'seeking_description' : artistdata.seeking_description,
    'image_link' : artistdata.image_link,
    'past_shows' : past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)}
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
   # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  alldata = Artist.query.all()
  artist = {}
  for element in alldata:
    if element.id == artist_id:
      artist['id'] = element.id
      artist['name'] = element.name
      artist['city'] = element.city
      artist['state'] = element.state
      artist['phone'] = element.phone
      artist['genres'] = element.genres
      artist['facebook_link'] = element.facebook_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.facebook_link = request.form.get('facebook_link')
    artist.genres = request.form.getlist('genres')
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as e: 
    error = True
    flash (e)
    db.session.rollback()
    flash ('An error occured. Artist' + artist.name +  'could not be updated')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  alldata = Venue.query.all()
  venue = {}
  for element in alldata:
    if element.id == venue_id:
      venue['id'] = element.id
      venue['name'] = element.name
      venue['city'] = element.city
      venue['state'] = element.state
      venue['address'] = element.address
      venue['phone'] = element.phone
      venue['genres'] = element.genres
      venue['facebook_link'] = element.facebook_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.facebook_link = request.form.get('facebook_link')
    venue.genres = request.form.getlist('genres')
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as e: 
    error = True
    flash (e)
    db.session.rollback()
    flash ('An error occured. Venue' + artist.name +  'could not be updated')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, facebook_link=facebook_link, image_link='')
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e: 
    error = True
    flash (e)
    db.session.rollback()
    flash ('An error occured. Artist' + artist.name +  'could not be listed')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  alldata = Shows.query.order_by(Shows.venue_id).all() 
  venuedata = Venue.query.all()
  artistdata = Artist.query.all()
  data = []
  for element in alldata:
    dictionary= {}
    dictionary['venue_id']=element.venue_id
    dictionary['artist_id']=element.artist_id
    dictionary['start_time']=str(element.start_time)
    for char in venuedata:
      if char.id == element.venue_id:
        dictionary['venue_name']=char.name
    for char in artistdata:
      if char.id == element.artist_id:
        dictionary['artist_name']=char.name
        dictionary['artist_image_link']=char.image_link
    data.append(dictionary)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e: 
    error = True
    flash (e)
    db.session.rollback()
    flash ('An error occured. Show could not be listed')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
