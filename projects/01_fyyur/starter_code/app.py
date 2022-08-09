#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
from unicodedata import name
import dateutil.parser
import babel
from flask import abort, render_template, request, flash, redirect, url_for, jsonify
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
import collections.abc
from models import *
collections.Callable = collections.abc.Callable

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  areagroups = Venue.query.distinct(Venue.city,Venue.state).order_by(Venue.city).all()
  all_venue=[]
  for areadata in areagroups:
    areavenues = Venue.query.filter(Venue.state==areadata.state, Venue.city==areadata.city)
    venues=[]
    for venuedata in areavenues:
        num_up =Show.query.filter(Show.venue_id==venuedata.id).filter(Show.start_time>datetime.now()).count()
        venues.append(
          {
        "id": venuedata.id,
        "name": venuedata.name,
        "num_upcoming_shows": num_up
        }
        )
    all_venue.append(
      {
        "city": areadata.city,
        "state": areadata.state,
        "venues":venues
      }
    )
  return render_template('pages/venues.html', areas=all_venue)
 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response=[]
  search_key=request.form.get('search_term')
  result = Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.name.ilike('%'+search_key+'%')).all()  
  result_data = []
  for r in result: 
    upcome_num=Show.query.filter(Show.venue_id==r.id).filter(Show.start_time>datetime.now()).count() 
    result_data.append(
      {
        "id":r.id,
        "name":r.name,
        "num_upcoming shows":upcome_num
      }
    )
  response={
    "count": len(result),
    "data": result_data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_venue={}
  Venue_data = Venue.query.get(venue_id)
  #flash(Venue_data)
  past_show_data=[]
  upcoming_show_data=[]
  #upcome_num=Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).count()
  #past_num=Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time<=datetime.now()).count()
  show_join_artist = Show.query.join('artist').filter(Show.venue_id==venue_id)
  
  past_data = show_join_artist.filter(Show.start_time<=datetime.now())
  for showdata in past_data:
    past_show_data.append(
    {
    "artist_id": showdata.artist_id,
    "artist_name": showdata.artist.name,
    "artist_image_link":showdata.artist.image_link,
    "start_time":showdata.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    )

  upcoming_data = show_join_artist.filter(Show.start_time>datetime.now())
  for showdata in upcoming_data:
        upcoming_show_data.append(
          {
        "artist_id": showdata.artist_id,
        "artist_name": showdata.artist.name,
        "artist_image_link":showdata.artist.image_link,
        "start_time":showdata.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        )

  current_venue={
    "id": Venue_data.id,
    "name": Venue_data.name,
    "genres":Venue_data.genres,
    "address":Venue_data.address,
    "city": Venue_data.city,
    "state": Venue_data.state,
    "phone":Venue_data.phone,
    "website":Venue_data.website_link,
    "facebook_link":Venue_data.facebook_link,
    "seeking_talent":Venue_data.seeking_talent,
    "seeking_description":Venue_data.seeking_description,
    "image_link":Venue_data.image_link,
    "past_shows":past_show_data,
    "upcoming_shows":upcoming_show_data,
    "past_shows_count": len(past_show_data),
    "upcoming_shows_count": len(upcoming_show_data)
    }
  return render_template('pages/show_venue.html', venue=current_venue)
  
  
  
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
  error=False
  #get data from form request
  try:
    form = VenueForm()
    new_venue = Venue(name = form.name.data, 
    city = form.city.data, 
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data)
    
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
      db.session.close()
  if error:
      abort (400)
  else:
      return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue removed successfully')
  except:
      db.session.rollback()
      flash('Venue could not be removed at the moment')
  finally:
      db.session.close()
  #return None
  return jsonify({'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artistlist = db.session.query(Artist.id,Artist.name)
  all_artist=[]
  for artistdetail in artistlist:
    all_artist.append(
      {
    "id": artistdetail.id,
    "name": artistdetail.name,
    }
    )
  return render_template('pages/artists.html', artists=all_artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response=[]
  search_key=request.form.get('search_term')
  result = Artist.query.with_entities(Artist.id,Artist.name).filter(Artist.name.ilike('%'+search_key+'%')).all()
  result_data = []
  for r in result: 
    upcome_num=Show.query.filter(Show.artist_id==r.id).filter(Show.start_time>datetime.now()).count() 
    result_data.append(
      {
        "id":r.id,
        "name":r.name,
        "num_upcoming shows":upcome_num
      }
    )
  response={
    "count": len(result),
    "data": result_data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  current_artist={}
  artist_data = Artist.query.get(artist_id)
  #flash(artist_data)
  past_show_data=[]
  upcoming_show_data=[]
  show_join_venue = Show.query.join('venue').filter(Show.artist_id==artist_id)
  
  past_data = show_join_venue.filter(Show.start_time<=datetime.now())
  for showdata in past_data:
    past_show_data.append(
    {
    "venue_id": showdata.venue_id,
    "venue_name": showdata.venue.name,
    "venue_image_link":showdata.venue.image_link,
    "start_time":showdata.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    )

  upcoming_data = show_join_venue.filter(Show.start_time>datetime.now())
  for showdata in upcoming_data:
    upcoming_show_data.append(
    {
    "venue_id": showdata.venue_id,
    "venue_name": showdata.venue.name,
    "venue_image_link":showdata.venue.image_link,
    "start_time":showdata.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    )

  current_artist={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres":artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone":artist_data.phone,
    "website":artist_data.website_link,
    "facebook_link":artist_data.facebook_link,
    "seeking_venue":artist_data.seeking_venue,
    "seeking_description":artist_data.seeking_description,
    "image_link":artist_data.image_link,
    "past_shows":past_show_data,
    "upcoming_shows":upcoming_show_data,
    "past_shows_count": len(past_show_data),
    "upcoming_shows_count": len(upcoming_show_data)
    }
  return render_template('pages/show_artist.html', artist=current_artist)
  
 
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  error=False
  #get data from form request
  try:
    artist_to_edit = Artist.query.get(artist_id)
    form.populate_obj(artist_to_edit)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully edited!')
  except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
  finally:
      db.session.close()
  if error:
      abort (400)
  else:
      return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error=False
  #get data from form request
  try:
    venue_to_edit = Venue.query.get(venue_id)
    form.populate_obj(venue_to_edit)
    #db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully edited!')
  except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
  finally:
      db.session.close()
  if error:
      abort (400)
  else:
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
  error=False
  #get data from form request
  try:
    form = ArtistForm()
    new_artist = Artist(name = form.name.data, 
    city = form.city.data, 
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data)
    
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except Exception as e:
      print(e)
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
      db.session.close()
  if error:
      abort (400)
  else:
      return render_template('pages/home.html')


  # # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real shows data.
  showlist=[]
  shows_list = Show.query.join('venue').join('artist').all()
  for showdetail in shows_list:
      showlist.append({
    "venue_id": showdetail.venue.id,
    "venue_name": showdetail.venue.name,
    "artist_id": showdetail.artist.id,
    "artist_name": showdetail.artist.name,
    "artist_image_link": showdetail.artist.image_link,
    "start_time": showdetail.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=showlist)

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
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')
  
  error=False
  #get data from form request
  try:
    form = ShowForm()
    new_show = Show(artist_id = form.artist_id.data, 
    venue_id = form.venue_id.data, 
    start_time = form.start_time.data)
    
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')

  except Exception as e:
      print(e)
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
  if error:
      abort (400)
  else:
      return render_template('pages/home.html')

#BONUS: Implemented a primitive search shows by venue id functionality
@app.route('/shows/search', methods=['POST'])
def search_shows():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response=[]
  search_key=request.form.get('search_term')
  result = Show.query.join('venue').join('artist').filter(Show.venue_id == search_key).all()  
  
  showlist=[]
  for showdetail in result:
      showlist.append({
    "venue_id": showdetail.venue.id,
    "venue_name": showdetail.venue.name,
    "artist_id": showdetail.artist.id,
    "artist_name": showdetail.artist.name,
    "artist_image_link": showdetail.artist.image_link,
    "start_time": showdetail.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/show.html', shows=showlist)
  

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
