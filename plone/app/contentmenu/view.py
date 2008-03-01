from zope.interface import Interface
from zope.interface import implements

from zope.component import getUtility
from zope.component import adapts

from zope.app.publisher.interfaces.browser import IBrowserMenu

from interfaces import IContentMenuView

from Acquisition import Explicit
from Products.CMFPlone import utils
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class ContentMenuProvider(Explicit):
    """Content menu provider for the "view" tab: displays the menu
    """

    implements(IContentMenuView)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider

    def update(self):
        pass

    render = ZopeTwoPageTemplateFile('contentmenu.pt')

    # From IContentMenuView

    def available(self):
        return True

    def menu(self):
        menu = getUtility(IBrowserMenu, name='plone_contentmenu')
        items = menu.getMenuItems(self.context, self.request)
        items.reverse()
        return items
