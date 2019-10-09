from AccessControl.SecurityManagement import getSecurityManager
from plone.app.contentmenu.interfaces import IDisplayViewsMenu
from zope.browsermenu.menu import BrowserMenu
from zope.component import getAdapters
from zope.component import getUtility
from zope.security.interfaces import IPermission
from zope.interface import implementer


@implementer(IDisplayViewsMenu)
class DisplayViewsMenu(BrowserMenu):
    def getMenuItemByAction(self, context, request, action):
        # Normalize actions; strip view prefix
        if action.startswith("@@"):
            action = action[2:]
        if action.startswith("++view++"):
            action = action[8:]

        sm = getSecurityManager()

        for name, item in getAdapters(
            (context, request), self.getMenuItemType()
        ):
            item_action = item.action
            # Normalize menu item action; never uses ++view++
            if item_action.startswith("@@"):
                item_action = item_action[2:]

            if item_action == action:
                permission = getUtility(IPermission, name=item.permission)
                if sm.checkPermission(permission.title, context):
                    return item
