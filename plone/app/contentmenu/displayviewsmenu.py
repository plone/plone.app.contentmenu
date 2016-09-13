# -*- coding: utf-8 -*-
from plone.app.contentmenu.interfaces import IDisplayViewsMenu
from zope.browsermenu.menu import BrowserMenu
from zope.component import getAdapters
from zope.interface import implementer


@implementer(IDisplayViewsMenu)
class DisplayViewsMenu(BrowserMenu):

    def getMenuItemByAction(self, context, request, action):
        # Normalize actions; strip view prefix
        if action.startswith('@@'):
            action = action[2:]
        if action.startswith('++view++'):
            action = action[8:]

        for name, item in getAdapters((context, request),
                                      self.getMenuItemType()):
            item_action = item.action
            # Normalize menu item action; never uses ++view++
            if item_action.startswith('@@'):
                item_action = item_action[2:]

            if item_action == action:
                return item
