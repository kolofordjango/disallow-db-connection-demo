# Explicitly disallow DB queries in Django

Goal: Give Django users the ability to explicitly disallow DB queries using a `with` context manager.

This repo shows a proof of concept implementation using the same approach that is used within `SimpleTestCase` to prevent DB access

All the interesting code is in [core/views.py](core/views.py)

## Examples
Based on the views defined in [core/views.py](core/views.py):

```py
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
```

`curl localhost:8000` works as normal with no error


`curl localhost:8000/error/` results in the following error:

```py
Internal Server Error: /error/
Traceback (most recent call last):
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/fields/related_descriptors.py", line 173, in __get__
    rel_obj = self.field.get_cached_value(instance)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/fields/mixins.py", line 15, in get_cached_value
    return instance._state.fields_cache[cache_name]
KeyError: 'author'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/core/handlers/exception.py", line 47, in inner
    response = get_response(request)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/core/handlers/base.py", line 181, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/core/views.py", line 59, in error_example
    serialized_author = f"Author: {book.author.name}"
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/fields/related_descriptors.py", line 187, in __get__
    rel_obj = self.get_object(instance)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/fields/related_descriptors.py", line 154, in get_object
    return qs.get(self.field.get_reverse_related_filter(instance))
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/query.py", line 431, in get
    num = len(clone)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/query.py", line 262, in __len__
    self._fetch_all()
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/query.py", line 1324, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/query.py", line 51, in __iter__
    results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/.venv/lib/python3.8/site-packages/django/db/models/sql/compiler.py", line 1173, in execute_sql
    cursor = self.connection.cursor()
  File "/Users/wilhelmklopp/workspace/kolofordjango/disallow-db-connection-demo/core/views.py", line 17, in __call__
    raise AssertionError(self.message)
AssertionError: Database queries to 'default' are not allowed in SimpleTestCase subclasses. Either subclass TestCase or TransactionTestCase to ensure proper test isolation or add 'default' to django.test.testcases.SimpleTestCase.databases to silence this failure.
[06/Jun/2021 09:31:11] "GET /error/ HTTP/1.1" 500 105616
```



