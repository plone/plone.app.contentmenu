from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility
from zope.interface import implements
from zope.contentprovider.provider import ContentProviderBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.contentmenu.interfaces import IContentMenuView


class ContentMenuProvider(ContentProviderBase):
    """Content menu provider for the "view" tab: displays the menu
    """

    implements(IContentMenuView)

    index = ViewPageTemplateFile('contentmenu.pt')

    def render(self):
        return self.index()

    # From IContentMenuView

    def available(self):
        return True

    def menu(self):
        menu = getUtility(IBrowserMenu, name='plone_contentmenu')
        items = menu.getMenuItems(self.context, self.request)
        level1_items = []
        level0_items = []
        for item in items:
            if 'extra' in item and 'level' in item['extra'] and item['extra']['level']:
                level1_items.append(item)
            else:
                level0_items.append(item)
        level0_items.reverse()
        level1_items.reverse()
        return {'level0': level0_items, 'level1': level1_items}
