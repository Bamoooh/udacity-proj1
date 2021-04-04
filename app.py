#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Artist, Show, Venue 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# DONE: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # i genuinly hope nobody has to read this pasta, this was really difficult to figure.
    query = db.session.query(Venue).order_by(Venue.city).all()
    print(query)
    if len(query) <= 0:
        return abort(400)

    stateCity = query[0].state + query[0].city
    data = [{
        'city': query[0].city,
        'state': query[0].state,
        'venues': []
    }]
    currentIndex = 0
    for v in query:
        if (stateCity == v.state + v.city):
            vShows = Show.query.filter(Show.venue_id == v.id).all()
            upcomingCount = 0
            for s in vShows:
                if (s.start_time > datetime.now()):
                    upcomingCount += 1
            print(upcomingCount)
            data[currentIndex]['venues'].append({
                'id': v.id,
                'name': v.name,
                'num_upcoming_shows': upcomingCount
            })
        else:
            stateCity = v.state + v.city
            currentIndex += 1
            data.append({
                'city': v.city,
                'state': v.state,
                'venues': []
            })
            for s in vShows:
                if (s.start_time > datetime.now()):
                    upcomingCount += 1
            print(upcomingCount)
            data[currentIndex]['venues'].append({
                'id': v.id,
                'name': v.name,
                'num_upcoming_shows': upcomingCount
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    response = {}
    term = request.form.get('search_term', '')
    search = "%{}%".format(term)
    searchResult = Venue.query.filter(Venue.name.ilike(search)).all()
    response['data'] = searchResult
    response['count'] = len(searchResult)
    return render_template('pages/search_venues.html', results=response, search_term=term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        data = Venue.query.filter_by(id=venue_id).all()[0].__dict__
        past_shows = []
        upcoming_shows = []
        for show in data.shows:
            if (show.start_time > datetime.now()):
                upcoming_shows.append(show)
            else:
                past_shows.append(show)

        data['past_shows'] = past_shows
        data['upcoming_shows'] = upcoming_shows
        data['past_shows_count'] = len(past_shows)
        data['upcoming_shows_count'] = len(upcoming_shows)
        return render_template('pages/show_venue.html', venue=data)
    except:
        return abort(400)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    isError = False
    d = VenueForm(request.form)
    if d.validate():
        try:
            print(d.__dict__)
            venue = Venue()
            d.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()

        except:
            isError = True
            db.session.rollback()
            print(sys.exc_info())

        finally:
            if not isError:
                db.session.close()
                return render_template('pages/home.html')
            else:
                flash('Venue ' + request.form['name'] + ' Failed to submit!')
                return abort(400)
    else: 
        return abort(400)


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    try:
        print('trying to delete', venue_id)
        print(Venue(id=venue_id))
        db.session.delete(Venue.query.filter_by(id=venue_id).first())
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('show_venue', venue_id=venue_id))

    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id = venue_id).all()[0]
    if venue is None:
        abort(404)
    form = VenueForm(obj = venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    if venue is None:
        return abort(404)
    
    form = VenueForm(request.form)    
    if form.validate():
        try:
            form.populate_obj(venue)
            # venue.seeking_talent = True if form.data['seeking_talent'] == 'y' else False
            db.session.commit()
            db.session.close()
            return redirect(url_for('show_venue', venue_id=venue_id))
        except:
            db.session.rollback()
            return abort(400)
    else:
        return abort(400)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    response = {}
    term = request.form.get('search_term', '')
    search = "%{}%".format(term)
    searchResult = Artist.query.filter(Artist.name.ilike(search)).all()
    response['data'] = searchResult
    response['count'] = len(searchResult)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id = artist_id).all()[0]
    data = artist.__dict__
    past_shows = []
    upcoming_shows = []
    for v in artist.shows:
        show = {
            'venue_id': v.Venue.id,
            'vanue_name': v.Venue.name,
            'venue_image_link': v.Venue.image_link,
            'start_time': v.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        if v.start_time >= datetime.now():
            upcoming_shows.append(show)
        else:
            past_shows.append(show)

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        abort(404)
    
    form = ArtistForm(obj = artist)
    # artist = Artist.query.filter_by(id = artist_id).all()[0]
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist.query.filter_by(id=artist_id).first()
            form.populate_obj(artist)
            # artist.seeking_venue = True if form.data['seeking_venue'] == 'y' else False
            db.session.commit()
            db.session.close()
        except:
            return abort(400)

    return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    isError = False
    d = ArtistForm(request.form)
    if d.validate():
        try:
            artist = Artist()
            d.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()

        except:
            isError = True
            db.session.rollback()
            print(sys.exc_info())

        finally:
            if not isError:
                db.session.close()
                return render_template('pages/home.html')
            else:
                flash('Artist ' + request.form['name'] + ' Failed to submit!')
                return abort(400)
    else:
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for s in shows:
        data.append({
            "venue_id": s.venue_id,
            "venue_name": s.Venue.name,
            "artist_id": s.atrist_id,
            "artist_name": s.Artist.name,
            "artist_image_link": s.Artist.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    isError = False
    try:
        d = request.form
        show = Show()
        d.populate_obj(show)
        db.session.add(show)
        db.session.commit()

    except:
        isError = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not isError:
            db.session.close()
            return render_template('pages/home.html')
        else:
            flash('Show ' + request.form['venue_id'] + ' Failed to submit!')
            return abort(400)
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
