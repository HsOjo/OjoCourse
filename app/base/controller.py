from flask import Blueprint, Flask


class Controller:
    name = None
    import_name = None
    url_prefix = None

    def __init__(self, app: Flask):
        if self.name is None:
            self.name = self.__class__.__name__.lower().replace('controller', '')

        self._blueprint = Blueprint(self.name, self.import_name)

        self.callback_add_routes()

        if self.url_prefix is None:
            self.url_prefix = '/%s' % self.name
        app.register_blueprint(self._blueprint, url_prefix=self.url_prefix)

    def callback_add_routes(self):
        pass

    def add_route(self, rule, view_func, **kwargs):
        func = lambda *args, **kwargs: self._response_func(view_func, *args, **kwargs)
        func.__name__ = view_func.__name__
        self._blueprint.add_url_rule(
            rule, view_func=func,
            **kwargs)

    def _response_func(self, view_func, *args, **kwargs):
        return view_func(*args, **kwargs)
