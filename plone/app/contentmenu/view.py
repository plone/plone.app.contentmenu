# -*- coding: utf-8 -*-
from plone.app.contentmenu.interfaces import IContentMenuView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility
from zope.contentprovider.provider import ContentProviderBase
from zope.interface import implementer


@implementer(IContentMenuView)
class ContentMenuProvider(ContentProviderBase):
    """Content menu provider for the "view" tab: displays the menu
    """

    index = ViewPageTemplateFile('contentmenu.pt')

    def render(self):
        return self.index()

    # From IContentMenuView

    def available(self):
        return True

    def menu(self):
        menu = getUtility(IBrowserMenu, name='plone_contentmenu')
        items = menu.getMenuItems(self.context, self.request)
        return items
