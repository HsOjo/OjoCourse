from app.admin.common import admin_required
from app.base import Controller


class AdminBaseController(Controller):
    def add_route(self, rule, view_func, admin_only=True, **kwargs):
        if admin_only:
            view_func = admin_required(view_func)
        super().add_route(rule, view_func, **kwargs)
