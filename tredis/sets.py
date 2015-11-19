"""Redis Set Commands Mixin"""
from tornado import concurrent

# Python 2 support for ascii()
if 'ascii' not in dir(__builtins__):  # pragma: nocover
    from tredis.compat import ascii


class SetsMixin(object):
    """Redis Set Commands Mixin"""

    def sadd(self, key, *members):
        """Add the specified members to the set stored at key. Specified
        members that are already a member of this set are ignored. If key does
        not exist, a new set is created before adding the specified members.

        An error is returned when the value stored at key is not a set.

        Returns :py:data:`True` if all requested members are added. If more
        than one member is passed in and not all members are added, the
        number of added members is returned.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the number of members
           to be added.

        :param key: The key of the set
        :type key: str, bytes
        :param members: One or more positional arguments to add to the set
        :type key: str, bytes
        :returns: Number of items added to the set
        :rtype: bool, int

        """
        def _eval_response(value):
            """Evaluate the response from redis

            :param int value: The number of values added
            :rtype: int, bool

            """
            if value == len(members):
                return True
            else:
                return value

        command = [b'SADD', key] + list(members)

        if self._pipeline:
            return self._pipeline_add(command, _eval_response)

        future = concurrent.TracebackFuture()

        def on_response(response):
            """Process the redis response

            :param response: The future with the response
            :type response: tornado.concurrent.Future

            """
            exc = response.exception()
            if exc:
                future.set_exception(exc)
            else:
                future.set_result(_eval_response(response.result()))

        self._execute(command, on_response)
        return future

    def scard(self, key):
        """Returns the set cardinality (number of elements) of the set stored
        at key.

        .. note::

           **Time complexity**: ``O(1)``

        :param key: The key of the set
        :type key: str, bytes
        :rtype: int
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SCARD', key]
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sdiff(self, *keys):
        """Returns the members of the set resulting from the difference between
        the first set and all the successive sets.

        For example:

        .. code::

            key1 = {a,b,c,d}
            key2 = {c}
            key3 = {a,c,e}
            SDIFF key1 key2 key3 = {b,d}

        Keys that do not exist are considered to be empty sets.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the total number of
           elements in all given sets.

        :param keys: Two or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SDIFF'] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sdiffstore(self, destination, *keys):
        """This command is equal to
        :py:class:`sdiff <tredis.RedisClient.sdiff>`, but instead of
        returning the resulting set, it is stored in destination.

        If destination already exists, it is overwritten.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the total number of
           elements in all given sets.

        :param destination: The set to store the diff into
        :type destination: str, bytes
        :param keys: One or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: int
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SDIFFSTORE', destination] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sinter(self, *keys):
        """Returns the members of the set resulting from the intersection of
        all the given sets.

        For example:

        .. code::

            key1 = {a,b,c,d}
            key2 = {c}
            key3 = {a,c,e}
            SINTER key1 key2 key3 = {c}

        Keys that do not exist are considered to be empty sets. With one of
        the keys being an empty set, the resulting set is also empty (since
        set intersection with an empty set always results in an empty set).

        .. note::

           **Time complexity**: ``O(N*M)`` worst case where ``N`` is the
           cardinality of the smallest set and ``M`` is the number of sets.

        :param keys: Two or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SINTER'] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sinterstore(self, destination, *keys):
        """This command is equal to
        :py:class:`sinter <tredis.RedisClient.sinter>`, but instead of
        returning the resulting set, it is stored in destination.

        If destination already exists, it is overwritten.

        .. note::

           **Time complexity**: ``O(N*M)`` worst case where ``N`` is the
           cardinality of the smallest set and ``M`` is the number of sets.

        :param destination: The set to store the intersection into
        :type destination: str, bytes
        :param keys: One or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: int
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SINTERSTORE', destination] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sismember(self, key, member):
        """Returns :py:data:`True` if ``member`` is a member of the set stored
        at key.

        .. note::

           **Time complexity**: ``O(1)``

        :param key: The key of the set to check for membership in
        :type key: str, bytes
        :param member: The value to check for set membership with
        :type member: str, bytes
        :rtype: bool
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SISMEMBER', key, member]
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def smembers(self, key):
        """Returns all the members of the set value stored at key.

        This has the same effect as running
        :py:class:`sinter <tredis.RedisClient.sinter>` with one argument key.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the set cardinality.

        :param key: The key of the set to return the members from
        :type key: str, bytes
        :rtype: list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SMEMBERS', key]
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def smove(self, source, destination, member):
        """Move member from the set at source to the set at destination. This
        operation is atomic. In every given moment the element will appear to
        be a member of source or destination for other clients.

        If the source set does not exist or does not contain the specified
        element, no operation is performed and :py:data:`False` is returned.
        Otherwise, the element is removed from the source set and added to the
        destination set. When the specified element already exists in the
        destination set, it is only removed from the source set.

        An error is returned if source or destination does not hold a set
        value.

        .. note::

           **Time complexity**: ``O(1)``

        :param source: The source set key
        :type source: str, bytes
        :param destination: The destination set key
        :type destination: str, bytes
        :param member: The member value to move
        :type member: str, bytes
        :rtype: bool
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        return self._execute_and_eval_int_resp([
            b'SMOVE', source, destination, member
        ])

    def spop(self, key, count=None):
        """Removes and returns one or more random elements from the set value
        store at key.

        This operation is similar to
        :py:class:`srandmember <tredis.RedisClient.srandmember>`, that returns
        one or more random elements from a set but does not remove it.

        The count argument will be available in a later version and is not
        available in 2.6, 2.8, 3.0

        Redis 3.2 will be the first version where an optional count argument
        can be passed to :py:class:`spop <tredis.RedisClient.spop>` in order
        to retrieve multiple elements in a single call. The implementation is
        already available in the unstable branch.

        .. note::

           **Time complexity**: Without the count argument ``O(1)``, otherwise
           ``O(N)`` where ``N`` is the absolute value of the passed count.

        :param key: The key to get one or more random members from
        :type key: str, bytes
        :param int count: The number of members to return
        :rtype: bytes, list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SPOP', key]
        if count:  # pragma: nocover
            command.append(ascii(count).encode('ascii'))
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def srandmember(self, key, count=None):
        """When called with just the key argument, return a random element from
        the set value stored at key.

        Starting from Redis version 2.6, when called with the additional count
        argument, return an array of count distinct elements if count is
        positive. If called with a negative count the behavior changes and the
        command is allowed to return the same element multiple times. In this
        case the number of returned elements is the absolute value of the
        specified count.

        When called with just the key argument, the operation is similar to
        :py:class:`spop <tredis.RedisClient.spop>`, however while
        :py:class:`spop <tredis.RedisClient.spop>` also removes the randomly
        selected element from the set,
        :py:class:`srandmember <tredis.RedisClient.srandmember>` will just
        return a random element without altering the original set in any way.

        .. note::

           **Time complexity**: Without the count argument ``O(1)``, otherwise
           ``O(N)`` where ``N`` is the absolute value of the passed count.

        :param key: The key to get one or more random members from
        :type key: str, bytes
        :param int count: The number of members to return
        :rtype: bytes, list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SRANDMEMBER', key]
        if count:
            command.append(ascii(count).encode('ascii'))
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def srem(self, key, *members):
        """Remove the specified members from the set stored at key. Specified
        members that are not a member of this set are ignored. If key does not
        exist, it is treated as an empty set and this command returns ``0``.

        An error is returned when the value stored at key is not a set.

        Returns :py:data:`True` if all requested members are removed. If more
        than one member is passed in and not all members are removed, the
        number of removed members is returned.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the number of members
           to be removed.

        :param key: The key to remove the member from
        :type key: str, bytes
        :param mixed members: One or more member values to remove
        :rtype: bool, int
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        future = concurrent.TracebackFuture()

        def _eval_response(value):
            """Evaluate the response from redis

            :param int value: The number of values removed
            :rtype: int, bool

            """
            if value == len(members):
                return True
            else:
                return value

        def on_response(response):
            """Process the redis response

            :param response: The future with the response
            :type response: tornado.concurrent.Future

            """
            exc = response.exception()
            if exc:
                future.set_exception(exc)
            else:
                future.set_result(_eval_response(response.result()))

        command = [b'SREM', key] + list(members)
        if self._pipeline:
            return self._pipeline_add(command, _eval_response)
        self._execute(command, on_response)
        return future

    def sscan(self, key, cursor=0, pattern=None, count=None):
        """The :py:class:`sscan <tredis.RedisClient.sscan>` command and the
        closely related commands :py:class:`scan <tredis.RedisClient.scan>`,
        :py:class:`hscan <tredis.RedisClient.hscan>` and
        :py:class:`zscan <tredis.RedisClient.zscan>` are used in order to
        incrementally iterate over a collection of elements.

        - :py:class:`scan <tredis.RedisClient.scan>` iterates the set of keys
          in the currently selected Redis database.
        - :py:class:`sscan <tredis.RedisClient.sscan>` iterates elements of
          Sets types.
        - :py:class:`hscan <tredis.RedisClient.hscan>` iterates fields of Hash
          types and their associated values.
        - :py:class:`zscan <tredis.RedisClient.zscan>` iterates elements of
          Sorted Set types and their associated scores.

        **Basic usage**

        :py:class:`sscan <tredis.RedisClient.sscan>` is a cursor based
        iterator. This means that at every call of the command, the server
        returns an updated cursor that the user needs to use as the cursor
        argument in the next call.

        An iteration starts when the cursor is set to ``0``, and terminates
        when the cursor returned by the server is ``0``.

        For more information on :py:class:`scan <tredis.RedisClient.scan>`,
        visit the `Redis docs on scan <http://redis.io/commands/scan>`_.

        .. note::

           **Time complexity**: ``O(1)`` for every call. ``O(N)`` for a
           complete iteration, including enough command calls for the cursor to
           return back to ``0``. ``N`` is the number of elements inside the
           collection.

        :param key: The key to scan
        :type key: str, bytes
        :param int cursor: The server specified cursor value or ``0``
        :param pattern: An optional pattern to apply for key matching
        :type pattern: str, bytes
        :param int count: An optional amount of work to perform in the scan
        :rtype: int, list
        :returns: A tuple containing the cursor and the list of set items
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        future = concurrent.TracebackFuture()

        def _format_response(value):
            """Format the response from redis

            :param tuple value: The return response from redis
            :rtype: tuple(int, list)

            """
            return int(value[0]), value[1]

        def on_response(response):
            """Process the redis response

            :param response: The future with the response
            :type response: tornado.concurrent.Future

            """
            exc = response.exception()
            if exc:
                future.set_exception(exc)
            else:
                future.set_result(_format_response(response.result()))

        command = [b'SSCAN', key, ascii(cursor).encode('ascii')]
        if pattern:
            command += [b'MATCH', pattern]
        if count:
            command += [b'COUNT', ascii(count).encode('ascii')]

        if self._pipeline:
            return self._pipeline_add(command, _format_response)

        self._execute(command, on_response)
        return future

    def sunion(self, *keys):
        """Returns the members of the set resulting from the union of all the
        given sets.

        For example:

        .. code::

            key1 = {a,b,c,d}
            key2 = {c}
            key3 = {a,c,e}
            SUNION key1 key2 key3 = {a,b,c,d,e}

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the total number of
           elements in all given sets.

        Keys that do not exist are considered to be empty sets.

        :param keys: Two or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: list
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SUNION'] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)

    def sunionstore(self, destination, *keys):
        """This command is equal to
        :py:meth:`sunion <tredis.RedisClient.sunion>`, but instead of returning
        the resulting set, it is stored in destination.

        If destination already exists, it is overwritten.

        .. note::

           **Time complexity**: ``O(N)`` where ``N`` is the total number of
           elements in all given sets.

        :param destination: The set to store the union into
        :type destination: str, bytes
        :param keys: One or more set keys as positional arguments
        :type keys: str, bytes
        :rtype: int
        :raises: :py:exc:`RedisError <tredis.exceptions.RedisError>`

        """
        command = [b'SUNIONSTORE', destination] + list(keys)
        if self._pipeline:
            return self._pipeline_add(command)
        return self._execute(command)
