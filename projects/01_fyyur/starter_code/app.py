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
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#  ---------------------------------------------------------------------------#

#List all the venues, grouping the venues by city,state
#helper
def venues_helper():
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
  return all_venue

#route handler
@app.route('/venues')
def venues():
  all_venue=[]
  all_venue = venues_helper()
  return render_template('pages/venues.html', areas=all_venue)

 
# Case insensitive partial string search on venues
def search_venues_helper(skey):
  result = Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.name.ilike('%'+skey+'%')).all()  
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
  responsedata={
    "count": len(result),
    "data": result_data
  }
  return responsedata

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_key=request.form.get('search_term')
  response = search_venues_helper(search_key)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# shows the venue details page for the given venue_id
#helper method
def show_venue_helper(venue_id):
  current_venue={}
  Venue_data = Venue.query.get(venue_id)
  past_show_data=[]
  upcoming_show_data=[]
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
  return current_venue

#route handler
@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  current_venue=show_venue_helper(venue_id)
  return render_template('pages/show_venue.html', venue=current_venue)
  
  
#  ---------------------------------------------------------------- 
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
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
      Venue.create(new_venue)
      flash('Venue ' + form.name.data + ' was successfully listed!','info')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.','error')
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
      flash('Please verify form. Venue ' + form.name.data + ' could not be listed.','warning')
      return render_template('forms/new_venue.html', form=form)


#  ----------------------------------------------------------------
#  Update Venue based on Venue ID
#  ----------------------------------------------------------------

# Request to edit Venue. Renders the edit_venue page for given Venue ID
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#Populate exiting values for venue and update changes as per user input

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue_to_edit = Venue.query.get(venue_id)
      form.populate_obj(venue_to_edit)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully edited!','info')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be edited.','error')
    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('Invalid Update data. Venue ' + form.name.data + ' could not be edited.','warning')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  ---------------------------------------------------------------- 
#  Delete Venue
#  ----------------------------------------------------------------

# delete a venue based on venue_id if it has no other related object else say cannot be deleted
@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      Venue.delete(venue_id)
      flash('Venue removed successfully','info')
  except:
      db.session.rollback()
      flash('Venue could not be removed at the moment','error')
  finally:
      db.session.close()
  return jsonify({'success': True })


#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
#listing all the artists
#helper
def getArtistList():
  artistlist = db.session.query(Artist.id,Artist.name)
  all_artist=[]
  for artistdetail in artistlist:
    all_artist.append(
      {
    "id": artistdetail.id,
    "name": artistdetail.name,
    }
    )
  return artistlist

#route handler
@app.route('/artists')
def artists():
  allartistlist = getArtistList()
  return render_template('pages/artists.html', artists=allartistlist)

#Case insensitive partial string search on artists for search_term.
#helper
def artist_search_helper(skey):
  result = Artist.query.with_entities(Artist.id,Artist.name).filter(Artist.name.ilike('%'+skey+'%')).all()
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
  response_data={
    "count": len(result),
    "data": result_data
  }
  return response_data

#route handler
@app.route('/artists/search', methods=['POST'])
def search_artists():
  response={}
  search_key=request.form.get('search_term')
  response=artist_search_helper(search_key)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# shows the artist page with the given artist_id
#Helper to display artist
def show_artist_helper(artist_id):
  current_artist_data={}
  artist_data = Artist.query.get(artist_id)
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
  current_artist_data={
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
  
  return current_artist_data

#route handler
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  current_artist={}
  current_artist= show_artist_helper(artist_id)
  
  return render_template('pages/show_artist.html', artist=current_artist)
  

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
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
      Artist.create(new_artist)
      flash('Artist ' + form.name.data + ' was successfully listed!','info')
    except Exception as e:
      print(e)
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.','error')
    finally:
      db.session.close()
      return render_template('pages/home.html')
  else:
    flash('Please verify form. Artist ' + form.name.data + ' could not be listed.','warning')
    return render_template('forms/new_artist.html', form=form)

#  ----------------------------------------------------------------
#  Update Artist based on Artist ID
#  ----------------------------------------------------------------

# Request to edit artist. Renders the edit_artist page for given artist ID
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

# Populate exiting values for artist and update changes as per user input
#helper
def edit_artist_helper(form,artist_id):
  if form.validate():
    try:
      artist_to_edit = Artist.query.get(artist_id)
      form.populate_obj(artist_to_edit)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully edited!','info')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + form.name.data + ' could not be edited.','error')
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('Invalid Update data. Artist ' + form.name.data + ' could not be edited.','warning')
    return redirect(url_for('show_artist', artist_id=artist_id))

#route handler
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf': False})
  return edit_artist_helper(form, artist_id)

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

# displays list of shows at /shows
# helper method to do queries
def shows_helper():
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
  return showlist

#route handler
@app.route('/shows')
def shows():
  showlist=shows_helper()
  return render_template('pages/shows.html', shows=showlist)

#renders form to create show. do not touch.
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# To create new shows in the db, upon submitting new show listing form
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    try:  
      new_show = Show(artist_id = form.artist_id.data, 
      venue_id = form.venue_id.data, 
      start_time = form.start_time.data)
      Show.create(new_show)
      flash('Show was successfully listed!','info')

    except Exception as e:
        print(e)
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.','error')
    finally:
        db.session.close()
        return render_template('pages/home.html')
  else:
    flash('Please verify form. Show could not be listed.','warning')
    return render_template('forms/new_show.html', form=form)
      

#BONUS: Implemented a primitive search shows by venue id functionality
#helper method to perform queries.
def search_shows_helper(skey):
  result = Show.query.join('venue').join('artist').filter(Show.venue_id == skey).all()  
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
  return showlist

#route handler
@app.route('/shows/search', methods=['POST'])
def search_shows():
  search_key=request.form.get('search_term')
  showlist=search_shows_helper(search_key)
  return render_template('pages/show.html', shows=showlist)

#----------------------------------------------------------------------------------

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
