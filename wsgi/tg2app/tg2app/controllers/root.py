# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates

from tg2app.lib.base import BaseController
from tg2app.model import DBSession, metadata
from tg2app import model
from tg2app.controllers.error import ErrorController

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the tg2app application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    error = ErrorController()

    @expose('tg2app.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('json')
    def get_users(self):
        users = DBSession.query(model.User).all()
        return {
                'users': [user.to_json() for user in users]
                }

    @expose()
    def add_user(self, username):
        if len(username) != 7:
            flash('Username must be 7 characters!')
            redirect('/')

        my_user = model.User(
                user_name=username,
                email_address=username + '@linkybook.com',
                display_name='No Display Name',
            )
        DBSession.add(my_user)

        redirect('/get_users')

    @expose('tg2app.templates.homework')
    def homework(self):
        """Handle the 'about' page."""
        return dict()

    @expose('tg2app.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('tg2app.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)
