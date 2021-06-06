from contextlib import contextmanager

from django.http import HttpRequest, HttpResponse
from django.db import connections
from django.test import SimpleTestCase


from .models import Book

# Copied from https://github.com/django/django/blob/ecf8af79355c8daa67722bd0de946b351f7f613d/django/test/testcases.py#L144
class _DatabaseFailure:
    def __init__(self, wrapped, message):
        self.wrapped = wrapped
        self.message = message

    def __call__(self):
        raise AssertionError(self.message)


@contextmanager
def disallow_db_connections():
    for alias in connections:
        connection = connections[alias]
        for name, operation in SimpleTestCase._disallowed_connection_methods:
            message = SimpleTestCase._disallowed_database_msg % {
                "test": "%s.%s"
                % (SimpleTestCase.__module__, SimpleTestCase.__qualname__),
                "alias": alias,
                "operation": operation,
            }
            method = getattr(connection, name)
            setattr(connection, name, _DatabaseFailure(method, message))

    yield

    for alias in connections:
        connection = connections[alias]
        for name, _ in SimpleTestCase._disallowed_connection_methods:
            method = getattr(connection, name)
            setattr(connection, name, method.wrapped)


# /
def index(request: HttpRequest) -> HttpResponse:

    book = Book.objects.select_related("author").last()

    with disallow_db_connections():
        # This will work, because all data is already loaded
        # and we **don't** need to make another DB query to
        # get the author name
        serialized_author = f"Author: {book.author.name}"

    return HttpResponse(serialized_author)


# /error/
def error_example(request: HttpRequest) -> HttpResponse:
    book = Book.objects.last()

    with disallow_db_connections():
        # This will raise an exception because another DB query
        # would have to be made to get the author name
        serialized_author = f"Author: {book.author.name}"

    return HttpResponse(serialized_author)
