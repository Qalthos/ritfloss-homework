# -*- coding: utf-8 -*-

# turbogears imports
from tg import expose, flash, redirect, request, url

# project specific imports
from tg2app.lib.base import BaseController
from tg2app.model import DBSession, metadata
from tg2app import model as m

import sqlalchemy

from tw2.jit import SQLARadialGraph
from tw2.core import JSSymbol

class JitController(BaseController):
    """ Handles all URLs under the `/jit/` path. """

    @expose('json')
    def data(self, *args, **kw):
        class Tg2AppSQLARadialGraph(SQLARadialGraph):
            id = 'sqlaRadialGraph'
            base_url = '/jit/data/'
            entities = [m.FBUser]

            show_attributes = False
            show_empty_relations = False

            alphabetize_relations = 24
            alphabetize_minimal = True
            excluded_columns = ['friends_2']

        jitwidget = Tg2AppSQLARadialGraph
        resp = jitwidget.request(request)
        return resp.body

    @expose('tg2app.templates.widget')
    def _default(self, *args, **kw):
        """ Serves up the RadialGraph widget """

        assert(len(args) == 1) # how else could it be?
        name = args[0]

        base = DBSession.query(m.FBUser).filter_by(name=name)

        if base.count() == 0 :
            raise LookupError("No such user '%s'" % name)

        if base.count() > 1:
            raise LookupError, "More than one user matches '%s'" % name

        user = base.one()

        # Some color constants for the radial graph
        bg = '#F8F7ED'
        green = '#84CA24'
        blue = '#006295'

        class Tg2AppSQLARadialGraph(SQLARadialGraph):
            id = 'sqlaRadialGraph'
            base_url = '/jit/data/'
            entities = [m.FBUser]
            rootObject = user
            depth = 1

            # Have it occupy the full page
            width = '980'
            height = '980'

            # Have it conform with the site style
            backgroundcolor = bg
            background = { 'CanvasStyles': { 'strokeStyle' : bg } }
            Node = { 'color' : green }
            Edge = { 'color' : blue, 'lineWidth':1.5, }

            # Space things out a little
            levelDistance = 150

            # Override the label style
            onPlaceLabel = JSSymbol(src="""
                (function(domElement, node){
                    domElement.style.display = "none";
                    domElement.innerHTML = node.name;
                    domElement.style.display = "";
                    var left = parseInt(domElement.style.left);
                    domElement.style.width = '120px';
                    domElement.style.height = '';
                    var w = domElement.offsetWidth;
                    domElement.style.left = (left - w /2) + 'px';

                    // This should all be moved to a css file
                    domElement.style.cursor = 'pointer';
                    if ( node._depth <= 1 )
                        domElement.style.color = 'black';
                    else
                        domElement.style.color = 'grey';
                })""")

        return {'widget': Tg2AppSQLARadialGraph}
