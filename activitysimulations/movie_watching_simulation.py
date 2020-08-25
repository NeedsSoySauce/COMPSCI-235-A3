from datetime import datetime
from typing import List
from random import randint, sample, choice, random

from .abstract_movie_watching_simulation import AbstractMovingWatchingSimulation

from domainmodel.movie import Movie
from domainmodel.user import User
from domainmodel.review import Review


def _rand_string(min_length: int = 8, max_length: int = 32):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return "".join(choice(chars) for _ in range(randint(min_length, max_length)))


class MovieWatchingSimulation(AbstractMovingWatchingSimulation):
    _DEFAULT_USER_COUNT = 10
    _DEFAULT_MIN_MOVIES_PER_USER = 0
    _DEFAULT_MAX_MOVIES_PER_USER = None

    @staticmethod
    def _validate_params(num_users: int, min_num_movies: int, max_num_movies: int):
        if not isinstance(num_users, int):
            raise TypeError(f"'num_users' must be of type 'int' but was '{type(num_users).__name__}'")

        if num_users <= 0:
            raise ValueError("'num_users' must be greater than zero")

        if not isinstance(min_num_movies, int):
            raise TypeError(f"'min_num_movies' must be of type 'int' but was '{type(min_num_movies).__name__}'")

        if min_num_movies < 0:
            raise ValueError("'min_num_movies' must be greater than or equal to zero")

        if not isinstance(max_num_movies, int) and max_num_movies is not None:
            raise TypeError(f"'max_num_movies' must be of type 'int' but was '{type(max_num_movies).__name__}'")

        if max_num_movies is not None:
            if max_num_movies < 0:
                raise ValueError("'max_num_movies' must be greater than or equal to zero")

            if max_num_movies < min_num_movies:
                raise ValueError("'max_num_movies' must be greater than or equal to 'min_num_movies'")

    def simulate(self,
                 num_users: int = _DEFAULT_USER_COUNT,
                 min_num_movies: int = _DEFAULT_MIN_MOVIES_PER_USER,
                 max_num_movies: int = _DEFAULT_MAX_MOVIES_PER_USER
                 ) -> 'State':

        self._validate_params(num_users, min_num_movies, max_num_movies)

        users = []
        reviews = []

        num_movies = len(self._movies)
        upper_bound = min(max_num_movies or num_movies, num_movies)
        population = list(range(0, num_movies))
        now = datetime.utcnow().timestamp()

        for i in range(num_users):
            username = _rand_string(4)
            password = _rand_string()
            user = User(username, password)

            # Pick n distinct movies
            movies = [self._movies[idx] for idx in sample(population, randint(min_num_movies, upper_bound))]

            # Add those movies to the user's watchlist
            for movie in movies:
                user.add_to_watchlist(movie)

            # Watch a random number of movies on the user's watchlist
            for j in range(randint(0, user.watchlist_size())):
                user.watch_movie(movies[j])

            # Review a random number of the movies the user watched
            for j in range(randint(0, len(user.watched_movies))):
                movie = movies[j]
                review_text = _rand_string()
                rating = randint(0, 10)

                release_date = datetime(movie.release_date, 1, 1).timestamp()
                delta = randint(0, int(now - release_date))  # float -> int will be lossy but not a big deal here
                delta += random()  # Add a random number of milliseconds
                timestamp = datetime.fromtimestamp(now - delta)

                review = Review(movie, review_text, rating, timestamp)
                user.add_review(review)
                reviews.append(review)

            users.append(user)

        return self.State(users, reviews)
