from zope.component import getAdapters
from zope.interface import implements

# BBB Zope 2.12
try:
    from zope.browsermenu.menu import BrowserMenu
except ImportError:
    from zope.app.publisher.browser.menu import BrowserMenu

from plone.app.contentmenu.interfaces import IDisplayViewsMenu


class DisplayViewsMenu(BrowserMenu):

    implements(IDisplayViewsMenu)

    def getMenuItemByAction(self, object, request, action):
        # Normalize actions; strip view prefix
        if action.startswith('@@'):
            action = action[2:]
        if action.startswith('++view++'):
            action = action[8:]

        for name, item in getAdapters((object, request),
                                      self.getMenuItemType()):
            item_action = item.action
            # Normalize menu item action; never uses ++view++
            if item_action.startswith('@@'):
                item_action = item_action[2:]

            if item_action == action:
                return item
