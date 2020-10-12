from flask import Blueprint, render_template, request, session, url_for, current_app
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from movie.adapters.repository import instance as repo
from .services import search_movies, create_search_form
from ..auth import services as auth

search_blueprint = Blueprint(
    'search_bp', __name__)


@search_blueprint.route('/search', methods=['GET'])
def search():
    form = create_search_form(repo, request.args)
    user = None

    try:
        user = auth.get_user(repo, session['username'])
    except auth.UnknownUserException:
        # invalid session
        session.clear()
        return redirect(url_for('auth_bp.login'))
    except KeyError:
        # User isn't logged in
        pass

    # Page numbers are displayed as starting from 1 so subtract 1
    try:
        page = int(request.args.get('page') or 1) - 1
        page_size = int(request.args.get('size') or 25)
    except ValueError:
        abort(404)

    query = form.query.data
    genres = form.genres.data
    directors = form.directors.data
    actors = form.actors.data

    if page < 0:
        abort(404)

    results = search_movies(repo, page, page_size=page_size, query=query, genres=genres, directors=directors,
                            actors=actors)

    if page >= results.pages and page != 0:
        abort(404)

    return render_template(
        'search/search.html',
        movies=results.movies,
        hits=results.hits,
        page=results.page,
        pages=results.pages,
        page_size=page_size,
        args={key: request.args[key] for key in request.args if key != 'page'},
        pagination_endpoint='search_bp.search',
        user=user,
        form=form
    )
