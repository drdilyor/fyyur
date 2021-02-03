from typing import List

from flask import flash, redirect, render_template, request, url_for, jsonify

from src import app, Artist, db, Show, Venue
from src.forms import *

@app.route('/')
def index():
    # recent venues
    # https://stackoverflow.com/questions/4186062/sqlalchemy-order-by-descending
    rv = [{
        "id": v.id,
        "name": v.name,
        "image_link": v.image_link,
    } for v in Venue.query.order_by(Venue.id.desc()).limit(6).all()]

    # recent artists
    ra = [{
        "id": a.id,
        "name": a.name,
        "image_link": a.image_link,
    } for a in Artist.query.order_by(Artist.id.desc()).limit(6).all()]

    return render_template('pages/home.html', recent_venues=rv, recent_artists=ra)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # Sorry future me, I can't explain how does it work
    venues: List[Venue] = Venue.query.all()
    locations = {}

    for v in venues:
        lc = (v.city, v.state)
        if lc in locations:
            locations[lc].append(v)
        else:
            locations[lc] = [v]

    data = []
    for lc, venues in sorted(locations.items()):
        data.append({
            "city": lc[0],
            "state": lc[1],
            "venues": [{
                "id": v.id,
                "name": v.name,
                # we don't need this, do we?
                # "num_upcoming_shows": Show.query.filter(
                #     Show.venue_id == v.id,
                #     Show.start_time > datetime.now()
                # ).count()
            } for v in venues]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    if request.form.get("search_term"):
        # https://stackoverflow.com/questions/42579400/search-function-query-in-flask-sqlalchemy
        venues: List[Venue] = Venue.query.filter(
            Venue.name.ilike('%' + request.form['search_term'] + '%')
        ).all()
        now = datetime.now()
        response = {
            "count": len(venues),
            "data": [{
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": Show.query.filter(
                    Show.venue_id == v.id,
                    Show.start_time > now,
                    )
            } for v in venues]
        }
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))
    else:
        return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    v = Venue.query.get(venue_id)
    data = {
        "id": v.id,
        "name": v.name,
        "genres": v.genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": bool(v.seeking_description),
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,
    }
    now = datetime.now()

    shows = db.session.query(Show)
    join_venue = shows.join(Venue)
    show_for_venue = join_venue.filter(Show.venue_id == venue_id)
    past = show_for_venue.filter(Show.start_time <= now)
    past_shows = past.all()

    shows = db.session.query(Show)
    join_venue = shows.join(Venue)
    show_for_venue = join_venue.filter(Show.venue_id == venue_id)
    upcoming = show_for_venue.filter(Show.start_time > now)
    upcoming_shows = upcoming.all()

    data['past_shows'] = list(map(show_to_dict, past_shows))
    data['upcoming_shows'] = list(map(show_to_dict, upcoming_shows))
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=data)


def show_to_dict(show: Show) -> dict:
    a: Artist = show.artist
    return {
        "artist_id": show.artist_id,
        "artist_name": a.name,
        "artist_image_link": a.image_link,
        "start_time": str(show.start_time),
    }


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# noinspection PyBroadException
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    form = VenueForm(request.form)
    if not form.validate_on_submit():
        flash('Invalid form!')
        return render_template('forms/new_venue.html', form=form)

    try:
        v = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(v)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))

    except Exception:
        db.session.rollback()
        flash("An error occurred!")
        return redirect(url_for('index'))
    finally:
        db.session.close()
    # DONE: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        v = Venue.query.get(venue_id)
        db.session.delete(v)
        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False})

    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = [{
        "id": a.id,
        "name": a.name
    } for a in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    if request.form.get("search_term"):
        # https://stackoverflow.com/questions/42579400/search-function-query-in-flask-sqlalchemy
        artists: List[Artist] = Artist.query.filter(
            Artist.name.ilike('%' + request.form['search_term'] + '%')
        ).all()
        now = datetime.now()
        response = {
            "count": len(artists),
            "data": [{
                "id": a.id,
                "name": a.name,
                "num_upcoming_shows": Show.query.filter(
                    Show.artist_id == a.id,
                    Show.start_time > now,
                    )
            } for a in artists]
        }
        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''))
    else:
        return redirect(url_for('venues'))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    a: Artist = Artist.query.get(artist_id)
    data = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "facebook_link": a.facebook_link,
        "seeking_venue": bool(a.seeking_description),
        "seeking_description": a.seeking_description,
        "image_link": a.image_link,
    }
    now = datetime.now()

    shows = db.session.query(Show)
    join_artist = shows.join(Artist)
    show_for_artist = join_artist.filter(Show.artist_id == artist_id)
    past = show_for_artist.filter(Show.start_time <= now)
    past_shows = past.all()

    shows = db.session.query(Show)
    join_artist = shows.join(Artist)
    show_for_artist = join_artist.filter(Show.artist_id == artist_id)
    upcoming = show_for_artist.filter(Show.start_time > now)
    upcoming_shows = upcoming.all()

    data['past_shows'] = list(map(show_to_dict, past_shows))
    data['upcoming_shows'] = list(map(show_to_dict, upcoming_shows))
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    # DONE: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    if not form.validate_on_submit():
        flash("Invalid form!")
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    try:
        form.populate_obj(artist)
        db.session.commit()
        flash("Artist is successfully edited")
    except Exception:
        db.session.rollback()
        flash("An error occurred!")
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, obj=venue)
    if not form.validate_on_submit():
        flash("Invalid form!")
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    try:
        form.populate_obj(venue)
        db.session.commit()
        flash("Venue is successfully edited")
    except Exception:
        db.session.rollback()
        flash("An error occurred!")
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    if not form.validate_on_submit():
        flash('Invalid form!')
        return render_template('forms/new_artist.html', form=form)

    try:
        a = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(a)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))

    except Exception:
        db.session.rollback()
        flash("An error occurred!")
        return redirect(url_for('index'))
    finally:
        db.session.close()
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": sh.venue_id,
        "venue_name": sh.venue.name,
        "artist_id": sh.artist_id,
        "artist_name": sh.artist.name,
        "artist_image_link": sh.artist.image_link,
        "start_time": str(sh.start_time),
    } for sh in Show.query.all()]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# noinspection PyBroadException
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    data = request.form
    form = ShowForm(data)

    if not form.validate_on_submit():
        flash('Invalid form!')
        return render_template('forms/new_show.html', form=form)

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data,
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
        return redirect(url_for('index'))

    except Exception:
        db.session.rollback()
        flash("An error occurred!")
        return redirect(url_for('index'))
    finally:
        db.session.close()
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
