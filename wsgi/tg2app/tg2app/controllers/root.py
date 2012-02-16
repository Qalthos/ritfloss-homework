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
from tg2app.controllers.jit import JitController

from sqlalchemy import desc
from datetime import datetime, timedelta
import random

__all__ = ['RootController']


# Add this function OUTSIDE of the RootController
def log_message(msg):
    model.DBSession.add(model.Message(msg=msg))


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

    # nasty
    jit = JitController()

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

    @expose()
    def do_logout(self, name):
        query = model.Login.query.filter_by(name=name)
        
        if query.count() == 0:
            # wtf...  when would this happen?
            log_message("'%s' (who DNE) tried to logout." % name)
            redirect('http://ritfloss.rtfd.org/')

        user = query.first()
        log_message("'%s' logged out." % user.name)
        model.DBSession.delete(user)
        redirect('http://ritfloss.rtfd.org/')

    @expose('json')
    def do_save_fb_user(self, referring_id, id, name, access_token):

        print "top of save user with:", referring_id, "and", id, referring_id == id

        if id == referring_id:
            return "WAT?"

        query = model.FBUser.query.filter_by(id=id)

        if query.count() == 0:
            user = model.FBUser(
                id=id,
                name=name,
            )
            model.DBSession.add(user)

            log_message('Spidered %s.  Totally awesome.' % unicode(user))

        if referring_id and referring_id != "0" and referring_id != "me":
            user = query.one()
            friend = model.FBUser.query.filter_by(id=referring_id).one()

            if friend not in user.friends:
                user.friends.append(friend)
                friend.friends.append(user)
                log_message('%s is friends with %s.' % (
                    unicode(user),
                    unicode(friend),
                ))

        return {'id': id}


    @expose()
    def do_login(self, name, access_token):

        query = model.Login.query.filter_by(name=name)

        if query.count() == 0:
            user = model.Login(name=name)
            model.DBSession.add(user)
        elif query.count() > 1:
            # wtf...  when would this happen?
            user = query.first()
        else:
            user = query.one()

        user.access_token = access_token
        user.last_seen = datetime.now()

        log_message("%s logged in" % user.name)

        redirect(url('/waiting/{name}#access_token={token}'.format(
            name=user.name, token=user.access_token)))

    @expose('json')
    @expose('tg2app.templates.waiting', content_type='text/html')
    def waiting(self, name):
        users = model.Login.query.all()
        def prune_idle(user):
            if datetime.now() - user.last_seen > timedelta(minutes=20):
                log_message("%s went idle.  Logging out." % user.name)
                model.DBSession.delete(user)
                return False
            return True

        users = filter(prune_idle, users)

        if name not in [user.name for user in users]:
            log_message("'%s' tried unauthorized access." % name)
            redirect('/')

        messages = model.Message.query\
                .order_by(desc(model.Message.created_on))\
                .limit(40).all()

        return {
            'users':[user.__json__() for user in users],
            'messages':[msg.__json__() for msg in messages],
        }

    @expose('tg2app.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('tg2app.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)
