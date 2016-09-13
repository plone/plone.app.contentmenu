Introduction
============

plone.app.contentmenu contains the logic that powers Plone's content menu which is part of the toolbar.

It provides the menus items (and its submenues) for

- factories menu (order=10)
- workflows menu (order=20)
- actions menu (order=30)
- display menu (order=40)
- manage portlets menu (order=50)

Note that menu items are ordered by an 'ordered' property.
To allow third party products to slot their own sub-menus in between the default menu items, these are registered with gaps.

Custom menus
============

Custom menus are registered in ``configure.zcml`` like so::

    <browser:menu
        id="my_content_menu"
        title="The 'My' menu - allows to do new exciting stuff"
        class=".menu.MyMenu"
    />

im ``menu.py`` the class looks like so::

    # -*- coding: utf-8 -*-
    from plone.memoize.instance import memoize
    from zope.browsermenu.interfaces import IBrowserMenu
    from zope.browsermenu.menu import BrowserMenu
    from zope.browsermenu.menu import BrowserSubMenuItem
    from zope.component import getMultiAdapter
    from zope.i18nmessageid import MessageFactory
    from zope.interface import implementer

    _ = MessageFactory('my.fancy')


    class IMyMainMenuItem(IBrowserMenu):
        """The main my menu item.

        You may want to place this in interfaces.py
        """


    class IMyMenu(IBrowserMenu):
        """The my menu.

        You may want to place this in interfaces.py
        """


    @implementer(IMyMainMenuItem)
    class MyMainMenuItem(BrowserSubMenuItem):
        # This is in fact a submenu item of the parent menu, thus the name
        # of the inherited class tells it, don't be confused.

        title = _(u'label_my_menu', default=u'My')
        description = _(u'title_my_menu',
                        default=u'My for the current content item')
        submenuId = 'my_fance_menu'

        order = 35
        extra = {
            'id': 'my-fance-menu',
            'li_class': 'plonetoolbar-content-my-fancy'
        }

        def __init__(self, context, request):
            super(BrowserSubMenuItem, self).__init__(context, request)
            self.context_state = getMultiAdapter(
                (context, request),
                name='plone_context_state'
            )

        @property
        def action(self):
            # return the url to be loaded if clicked on the link.
            # even if a submenu exists it will be active if javascript is disbaled
            return self.context.absolute_url()

        @memoize
        def available(self):
            # check if the menu is available and shown or not
            return True

        def selected(self):
            # check if the menu should be shown as selected
            return False


    @implementer(IMyMenu)
    class ActionsMenu(BrowserMenu):

        def getMenuItems(self, context, request):
            """Return menu item entries in a TAL-friendly form."""
            results = []

            # here a single item is added. do what needed to add several entrys
            results.append({
                'title': 'My item 1',
                'description': 'An my item',
                'action': '/url/to/action',
                'selected': False,
                'icon': 'some_icon_class',
                'extra': {
                    'id': 'plone-contentmenu-my-fancy-one',
                    'separator': None,
                    'class': 'my-class pat-plone-modal',
                    'modal': 'width: 400'
                },
                'submenu': None,
            })

            return results


Source Code
===========

Contributors please read the document `Process for Plone core's development <http://docs.plone.org/develop/plone-coredev/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.app.contentmenu>`_.
