import flask
import werkzeug.exceptions as error


__all__ = ['BaseHandler', 'add_handler']


POSSIBLE_METHODS = "GET", "POST", "PUT", "DELETE", "HEAD"  


def _jinja_renderer(path):
    def render_from_dict(context_dict):
        return flask.render_template(path)#, **context_dict)
    return render_from_dict


class BaseHandler(object):
    """An inheritable handler inspired by ``the webapp framework``_

    Here's a simple example:

    .. sourcecode:: pycon

       >>> from flaskext.handler import BaseHandler
       >>> class Hello(BaseHandler):
       ...     ROUTE = '/'
       ...
       ...     def get(self):
       ...         return 'hello world'

    A more complicated example:

    .. sourcecode:: pycon

       >>> # some imports
       >>> from flask import Flask
       >>> from flaskext.handler import BaseHandler, add_handler
       >>> from werkzeug.exceptions import NotFound
       >>> # handler definition
       >>> class AuthenticatedUser(BaseHandler):
       ...     ROUTE = '/me'
       ...     TEMPLATE_NAME = 'profile'
       ...
       ...     def validate_get_request(self, req): # called first
       ...         token = req.args.get('access_token')
       ...         user = user_from_access_token(token)
       ...         if user is None:
       ...              raise NotFound('...')
       ...         return user
       ...
       ...     def get(self, user): # called after validation
       ...         return dict(id=user.id, name=user.name, email=user.email)
       >>>
       >>> app = Flask("__name__")
       >>> add_handler(app, AuthenticatedUser)

    This configuration guarantees that ``AuthenticatedUser.get`` will always
    receive a user object. When you request `/me` with `format=json`, it will
    render the dict in json.
    
    What's really nice about this configuration is that you can easily
    inherit validations:

    .. sourcecode:: pycon

       >>> class SignedUserFriends(SignedUser):
       ...     ROUTE = '/me/friends'
       ...
       ...     def get(self, user):
       ...         return dict(user=user, friends=user.friends)

    Take a look at :meth:`BaseHandler.__call__` to learn how it actually works.

    .. seealso:: :meth:`BaseHandler.__call__`

    """
    #: The route this handler should bind to.
    ROUTE = None

    #: The name of the template
    TEMPLATE_NAME = None

    #: Supported formats
    DEFAULT_FORMAT = "html"

    #: The name of the form parameter used to indicate the overridden
    #: method of the request. Set it to None if you want to disable method hack.
    METHOD_HACK = "__method__"

    # customized renderers
    CUSTOM_RENDERER = {"json": flask.jsonify}

    def __init__(self):
        if self.ROUTE is None:
            raise NotImplementedError("A BaseHandler implementation must "
                                      "include self.ROUTE")
        # do this inside a metaclass?
        self.METHODS = [meth for meth in POSSIBLE_METHODS if
                        hasattr(self, meth.lower())]

    def __call__(self, **kwargs):
        """Flask will execute this method directly.

        When Flask receives a request, it invokes ``__call__`` method of the
        registered handler with the appropriate arguments. ``BaseHandler.__call__``
        processes requests in the following order:

          1. finds the appropriate view form 
          2. resolves the REST verb.
          3. validates request using the method associated with the REST verb.
          4. calls the appropriate method with the validated parameters.
          5. renders the output using the template format specified.

        This method runs inside `with`, which means that you can override
        `__enter__` and `__exit__` of your handler and get events to happen
        at setup and teardown.

        """
        with self:
            renderer = self._find_renderer()
            verb = self._resolve_rest_verb().lower()
            validator = getattr(self, "validate_%s_request" % verb, None)
            method = getattr(self, verb)

            if validator:
                params = validator(flask.request, **kwargs)
            else:
                params = kwargs

            if isinstance(params, (list, tuple)):
                context = method(*params)
            elif isinstance(params, dict):
                context = method(**params)
            else:
                context = method(params)

            if renderer:
                return renderer(context)
            return context

    def __enter__(self):
        """Override this method to run code at setup."""
        pass

    def __exit__(self, type, value, traceback):
        """Override this method to run code at teardown."""
        pass

    def _find_renderer(self):
        format = flask.request.values.get("format")
        if format is None:
            format = self.DEFAULT_FORMAT
        if format in self.CUSTOM_RENDERER:
            return self.CUSTOM_RENDERER[format]
        if self.TEMPLATE_NAME:
            return _jinja_renderer('%s.%s' % (self.TEMPLATE_NAME, format))
        return None

    def _resolve_rest_verb(self):
        method = flask.request.method
        if method == "POST" and self.METHOD_HACK:
            fake_meth = flask.request.form.get(self.METHOD_HACK)
            if fake_meth:
                method = fake_meth
        if method.upper() not in self.METHODS:
            raise error.MethodNotAllowed("% is an invalid method" % meth)
        return method


def add_handler(app, *handlers):
    for handler_cls in handlers:
        handler = handler_cls()
        app.add_url_rule(handler.ROUTE,
                         handler.__class__.__name__,
                         handler,
                         methods=handler.METHODS)

