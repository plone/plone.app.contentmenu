from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from html import escape
from operator import itemgetter
from plone.app.content.browser.folderfactories import _allowedTypes
from plone.app.contentmenu import PloneMessageFactory as _
from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.interfaces import IDisplayMenu
from plone.app.contentmenu.interfaces import IDisplaySubMenuItem
from plone.app.contentmenu.interfaces import IFactoriesMenu
from plone.app.contentmenu.interfaces import IFactoriesSubMenuItem
from plone.app.contentmenu.interfaces import IPortletManagerMenu
from plone.app.contentmenu.interfaces import IPortletManagerSubMenuItem
from plone.app.contentmenu.interfaces import IWorkflowMenu
from plone.app.contentmenu.interfaces import IWorkflowSubMenuItem
from plone.base import utils
from plone.base.interfaces.constrains import IConstrainTypes
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from plone.base.interfaces.structure import INonStructuralFolder
from plone.memoize.instance import memoize
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager
from plone.protect.utils import addTokenToUrl
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer

import json
import pkg_resources
import plone.locking  # noqa: F401


PMF = _  # used for dynamic messages we don't want to extract

try:
    pkg_resources.get_distribution("Products.CMFPlacefulWorkflow")
    from Products.CMFPlacefulWorkflow.permissions import ManageWorkflowPolicies
except pkg_resources.DistributionNotFound:
    from Products.CMFCore.permissions import ManagePortal as ManageWorkflowPolicies


@implementer(IActionsSubMenuItem)
class ActionsSubMenuItem(BrowserSubMenuItem):
    title = _("label_actions_menu", default="Actions")
    description = _(
        "title_actions_menu", default="Actions for the current content item"
    )
    submenuId = "plone_contentmenu_actions"
    icon = "toolbar-action/actions"
    order = 30
    extra = {
        "id": "plone-contentmenu-actions",
        "li_class": "plonetoolbar-content-action",
    }

    def __init__(self, context, request):
        super().__init__(context, request)
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    @property
    def action(self):
        folder = self.context
        if not self.context_state.is_structural_folder():
            folder = aq_parent(aq_inner(self.context))
        return folder.absolute_url() + "/folder_contents"

    @memoize
    def available(self):
        actions_tool = getToolByName(self.context, "portal_actions")
        editActions = actions_tool.listActionInfos(
            object=self.context, categories=("object_buttons",), max=1
        )
        return len(editActions) > 0

    def selected(self):
        return False


@implementer(IActionsMenu)
class ActionsMenu(BrowserMenu):
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter((context, request), name="plone_context_state")
        editActions = context_state.actions("object_buttons")
        if not editActions:
            return results

        for action in editActions:
            if not action["allowed"]:
                continue
            aid = action["id"]
            cssClass = f"actionicon-object_buttons-{aid}"
            icon = action.get("icon", None)
            modal = action.get("modal", None)
            if modal:
                cssClass += " pat-plone-modal"

            results.append(
                {
                    "title": action["title"],
                    "description": action.get("description", ""),
                    "action": addTokenToUrl(action["url"], request),
                    "selected": False,
                    "icon": icon,
                    "extra": {
                        "id": "plone-contentmenu-actions-" + aid,
                        "separator": None,
                        "class": cssClass,
                        "modal": modal,
                    },
                    "submenu": None,
                }
            )
        return results


@implementer(IDisplaySubMenuItem)
class DisplaySubMenuItem(BrowserSubMenuItem):
    title = _("label_choose_template", default="Display")
    submenuId = "plone_contentmenu_display"
    icon = "toolbar-action/display"
    order = 40

    def __init__(self, context, request):
        super().__init__(context, request)
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    @property
    def extra(self):
        return {
            "id": "plone-contentmenu-display",
            "disabled": self.disabled(),
            "li_class": "plonetoolbar-display-view",
        }

    @property
    def description(self):
        if self.disabled():
            return _(
                "title_remove_index_html_for_display_control",
                default="Delete or rename the index_html item to gain "
                "full control over how this folder is "
                "displayed.",
            )
        return _(
            "title_choose_default_view",
            default="Select the view mode for this folder, or set a "
            "content item as its default view.",
        )

    @property
    def action(self):
        if self.disabled():
            return ""
        if self.context_state.is_default_page():
            return self.context_state.parent().absolute_url() + "/select_default_view"
        return self.context.absolute_url() + "/select_default_view"

    @memoize
    def available(self):
        if self.disabled():
            return False

        isDefaultPage = self.context_state.is_default_page()

        folder = None
        context = None

        folderLayouts = []
        folderCanSetLayout = False
        contextLayouts = []

        # If this is a default page, also get menu items relative to the parent
        if isDefaultPage:
            folder = ISelectableBrowserDefault(aq_parent(aq_inner(self.context)), None)

        if folder is not None:
            if folder.canSetDefaultPage():
                # Always Show the menu if we can set a default-page (short cut)
                return True
            folderLayouts = folder.getAvailableLayouts()
            folderCanSetLayout = folder.canSetLayout()

        context = ISelectableBrowserDefault(self.context, None)
        contextLayouts = []
        contextCanSetLayout = False
        contextCanSetDefaultPage = False

        if context is not None:
            contextLayouts = context.getAvailableLayouts()
            contextCanSetLayout = context.canSetLayout()
            contextCanSetDefaultPage = context.canSetDefaultPage()

        # we have more than one layout to choose from?
        return (
            (folderCanSetLayout and len(folderLayouts) > 1)
            or (folder is None and contextCanSetDefaultPage)
            or (contextCanSetLayout and len(contextLayouts) > 1)
        )

    def selected(self):
        return False

    @memoize
    def disabled(self):
        # As we don't have the view we need to parse the url to see
        # if its folder_contents
        context = self.context
        if self.context_state.is_default_page():
            context = aq_parent(aq_inner(context))
        if not getattr(context, "isPrincipiaFolderish", False):
            return False
        elif "index_html" not in context:
            return False
        else:
            return True


@implementer(IDisplayMenu)
class DisplayMenu(BrowserMenu):
    def getMenuItems(self, obj, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter((obj, request), name="plone_context_state")
        isDefaultPage = context_state.is_default_page()

        parent = None
        folder = None
        if isDefaultPage:
            # If this is a default page, also get menu items relative to thr
            # parent
            parent = aq_parent(aq_inner(obj))
            folder = ISelectableBrowserDefault(parent, None)

        folderLayouts = []
        folderCanSetLayout = False
        folderCanSetDefaultPage = False
        if folder is not None:
            folderLayouts = folder.getAvailableLayouts()
            folderCanSetLayout = folder.canSetLayout()
            folderCanSetDefaultPage = folder.canSetDefaultPage()

        contextLayouts = []
        contextCanSetLayout = False
        contextCanSetDefaultPage = False

        context = ISelectableBrowserDefault(obj, None)
        if context is not None:
            contextLayouts = context.getAvailableLayouts()
            contextCanSetLayout = context.canSetLayout()
            contextCanSetDefaultPage = context.canSetDefaultPage()

        # Short circuit if neither folder nor object will provide us with
        # items
        if not (
            folderCanSetLayout
            or folderCanSetDefaultPage
            or contextCanSetLayout
            or contextCanSetDefaultPage
        ):
            return []

        # Only show the block 'Folder display' and 'Item display' separators if
        # they are necessars
        useSeparators = False
        if folderCanSetLayout or folderCanSetDefaultPage:
            if (
                contextCanSetLayout and len(contextLayouts) > 1
            ) or contextCanSetDefaultPage:
                useSeparators = True

        folder_index = 0
        # 1. If this is a default-page, first render folder options
        if folder is not None:
            folderUrl = parent.absolute_url()

            if useSeparators:
                results.append(
                    {
                        "title": _(
                            "label_current_folder_views", default="Folder display"
                        ),
                        "description": "",
                        "action": None,
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "folderHeader",
                            "separator": "actionSeparator",
                            "class": "",
                        },
                        "submenu": None,
                    }
                )
                folder_index = len(results)

            # Display the selected item (i.e. the context)
            results.insert(
                folder_index,
                {
                    "title": _(
                        "label_item_selected",
                        default="Item: ${contentitem}",
                        mapping={"contentitem": escape(utils.safe_text(obj.Title()))},
                    ),
                    "description": "",
                    "action": None,
                    "selected": True,
                    "icon": None,
                    "extra": {
                        "id": "folderDefaultPageDisplay",
                        "separator": None,
                        "class": "active",
                    },
                    "submenu": None,
                },
            )

            if folderCanSetLayout:
                for id, title in folderLayouts:
                    results.append(
                        {
                            "title": title,
                            "description": "",
                            "action": addTokenToUrl(
                                "{}/selectViewTemplate?templateId={}".format(
                                    folderUrl,
                                    id,
                                ),
                                request,
                            ),
                            "selected": False,
                            "icon": None,
                            "extra": {
                                "id": "folder-" + id,
                                "separator": None,
                                "class": "",
                            },
                            "submenu": None,
                        }
                    )
            # Let the user change the selection
            if folderCanSetDefaultPage:
                results.append(
                    {
                        "title": _(
                            "label_change_default_item",
                            default="Change content item as default " "view...",
                        ),
                        "description": _(
                            "title_change_default_view_item",
                            default="Change the item used as default"
                            " view in this folder",
                        ),
                        "action": f"{folderUrl}/select_default_page",
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "folderChangeDefaultPage",
                            "separator": None,
                            "class": "pat-plone-modal",
                        },
                        "submenu": None,
                    }
                )

        # 2. Render context options
        item_index = 0
        if context is not None:
            contextUrl = obj.absolute_url()
            selected = context.getLayout()
            defaultPage = context.getDefaultPage()
            layouts = context.getAvailableLayouts()

            if useSeparators:
                results.append(
                    {
                        "title": _("label_current_item_views", default="Item display"),
                        "description": "",
                        "action": None,
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "contextHeader",
                            "separator": "actionSeparator",
                            "class": "",
                        },
                        "submenu": None,
                    }
                )
                item_index = len(results)

            # If context is a default-page in a folder, that folder's views
            # will be shown. Only show context views if there are any to show.

            showLayouts = not isDefaultPage or len(layouts) > 1

            if showLayouts and contextCanSetLayout:
                for id, title in contextLayouts:
                    is_selected = defaultPage is None and id == selected
                    # Selected item on top
                    index = item_index if is_selected else len(results)
                    results.insert(
                        index,
                        {
                            "title": title,
                            "description": "",
                            "action": addTokenToUrl(
                                "{}/selectViewTemplate?templateId={}".format(
                                    contextUrl,
                                    id,
                                ),
                                request,
                            ),
                            "selected": is_selected,
                            "icon": None,
                            "extra": {
                                "id": "plone-contentmenu-display-" + id,
                                "separator": None,
                                "class": is_selected and "active" or "",
                            },
                            "submenu": None,
                        },
                    )

            # Allow setting / changing the default-page, unless this is a
            # default-page in a parent folder.
            if not INonStructuralFolder.providedBy(obj):
                if defaultPage is None:
                    if contextCanSetDefaultPage:
                        results.append(
                            {
                                "title": _(
                                    "label_choose_item",
                                    default="Select a content item\n"
                                    "as default view...",
                                ),
                                "description": _(
                                    "title_select_default_view_item",
                                    default="Select an item to be used as "
                                    "default view in this folder...",
                                ),
                                "action": addTokenToUrl(
                                    f"{contextUrl}/select_default_page",
                                    request,
                                ),
                                "selected": False,
                                "icon": None,
                                "extra": {
                                    "id": "contextSetDefaultPage",
                                    "separator": None,
                                    "class": "pat-plone-modal",
                                    "modal": json.dumps(
                                        {"actionOptions": {"redirectOnResponse": True}}
                                    ),
                                },
                                "submenu": None,
                            }
                        )
                else:
                    defaultPageObj = getattr(obj, defaultPage, None)
                    defaultPageTitle = ""
                    if defaultPageObj is not None:
                        if getattr(aq_base(defaultPageObj), "Title"):
                            defaultPageTitle = defaultPageObj.Title()
                        else:
                            defaultPageTitle = getattr(
                                aq_base(defaultPageObj), "title", ""
                            )

                    # Selected item on top
                    results.insert(
                        item_index,
                        {
                            "title": _(
                                "label_item_selected",
                                default="Item: ${contentitem}",
                                mapping={
                                    "contentitem": escape(
                                        utils.safe_text(defaultPageTitle)
                                    )
                                },
                            ),
                            "description": "",
                            "action": None,
                            "selected": True,
                            "icon": None,
                            "extra": {
                                "id": "contextDefaultPageDisplay",
                                "separator": None,
                                "class": "",
                            },
                            "submenu": None,
                        },
                    )
                    if contextCanSetDefaultPage:
                        results.append(
                            {
                                "title": _(
                                    "label_change_item",
                                    default="Change content item\nas "
                                    "default view...",
                                ),
                                "description": _(
                                    "title_change_default_view_item",
                                    default="Change the item used as default "
                                    "view in this folder",
                                ),
                                "action": f"{contextUrl}/select_default_page",
                                "selected": False,
                                "icon": None,
                                "extra": {
                                    "id": "contextChangeDefaultPage",
                                    "separator": None,
                                    "class": "pat-plone-modal",
                                    "modal": json.dumps(
                                        {"actionOptions": {"redirectOnResponse": True}}
                                    ),
                                },
                                "submenu": None,
                            }
                        )

        return results


@implementer(IFactoriesSubMenuItem)
class FactoriesSubMenuItem(BrowserSubMenuItem):
    title = _("label_add_new_item", default="Add new\u2026")
    submenuId = "plone_contentmenu_factory"
    icon = "toolbar-action/factories"
    order = 10
    description = _(
        "title_add_new_items_inside_item", default="Add new items inside this item"
    )

    def __init__(self, context, request):
        super().__init__(context, request)
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    @property
    def extra(self):
        return {
            "id": "plone-contentmenu-factories",
            "li_class": "plonetoolbar-contenttype",
        }

    @property
    def action(self):
        return addTokenToUrl(
            f"{self._addContext().absolute_url()}/folder_factories",
            self.request,
        )

    def available(self):
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if self._addingToParent() and not self.context_state.is_default_page():
            return False
        return len(itemsToAdd) > 0 or showConstrainOptions

    def selected(self):
        return False

    @memoize
    def _addContext(self):
        if self.context_state.is_structural_folder():
            return self.context
        return self.context_state.folder()

    @memoize
    def _itemsToAdd(self):
        context = self.context_state.folder()
        return [(context, fti) for fti in self._addableTypesInContext(context)]

    def _addableTypesInContext(self, addContext):
        allowed_types = _allowedTypes(self.request, addContext)
        constrain = IConstrainTypes(addContext, None)
        if constrain is None:
            return allowed_types
        locallyAllowed = constrain.getLocallyAllowedTypes()
        return [fti for fti in allowed_types if fti.getId() in locallyAllowed]

    @memoize
    def _addingToParent(self):
        add_context_url = self._addContext().absolute_url()
        return add_context_url != self.context.absolute_url()

    @memoize
    def _showConstrainOptions(self):
        addContext = self._addContext()
        constrain = ISelectableConstrainTypes(addContext, None)
        if constrain is None:
            return False
        elif constrain.canSetConstrainTypes() and constrain.getDefaultAddableTypes():
            return True
        elif len(constrain.getLocallyAllowedTypes()) < len(
            constrain.getImmediatelyAddableTypes()
        ):
            return True


@implementer(IFactoriesMenu)
class FactoriesMenu(BrowserMenu):
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        factories_view = getMultiAdapter((context, request), name="folder_factories")

        haveMore = False
        include = None

        addContext = factories_view.add_context()
        allowedTypes = _allowedTypes(request, addContext)

        constraints = IConstrainTypes(addContext, None)
        if constraints is not None:
            include = constraints.getImmediatelyAddableTypes()
            if len(include) < len(allowedTypes):
                haveMore = True

        results = factories_view.addable_types(include=include)

        if haveMore:
            url = f"{addContext.absolute_url()}/folder_factories"
            results.append(
                {
                    "title": _("folder_add_more", default="More\u2026"),
                    "description": _("Show all available content types"),
                    "action": url,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "plone-contentmenu-more",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        constraints = ISelectableConstrainTypes(addContext, None)
        if constraints is not None:
            if (
                constraints.canSetConstrainTypes()
                and constraints.getDefaultAddableTypes()
            ):
                url = "{}/folder_constraintypes_form".format(
                    addContext.absolute_url(),
                )
                results.append(
                    {
                        "title": _("folder_add_settings", default="Restrictions\u2026"),
                        "description": _(
                            "title_configure_addable_content_types",
                            default="Configure which content types can be "
                            "added here",
                        ),
                        "action": url,
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "plone-contentmenu-settings",
                            "separator": None,
                            "class": "",
                        },
                        "submenu": None,
                    }
                )

        # Also add a menu item to add items to the default page
        context_state = getMultiAdapter((context, request), name="plone_context_state")
        if (
            context_state.is_structural_folder()
            and context_state.is_default_page()
            and self._contentCanBeAdded(context, request)
        ):
            results.append(
                {
                    "title": _(
                        "default_page_folder", default="Add item to default page"
                    ),
                    "description": _(
                        "desc_default_page_folder",
                        default="If the default page is also a folder, "
                        "add items to it from here.",
                    ),
                    "action": context.absolute_url() + "/@@folder_factories",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "plone-contentmenu-add-to-default-page",
                        "separator": None,
                        "class": "pat-plone-modal",
                    },
                    "submenu": None,
                }
            )

        return results

    def _contentCanBeAdded(self, addContext, request):
        """Find out if content can be added either by local constraints on the
        context or by allowed_content_types on the FTI.
        """
        constrain = IConstrainTypes(addContext, None)
        if constrain is None:
            return _allowedTypes(request, addContext)
        return constrain.getLocallyAllowedTypes()


@implementer(IWorkflowSubMenuItem)
class WorkflowSubMenuItem(BrowserSubMenuItem):
    MANAGE_SETTINGS_PERMISSION = "Manage portal"

    title = _("label_state", default="State:")
    short_title = _("State")
    icon = "toolbar-action/workflow"
    submenuId = "plone_contentmenu_workflow"
    order = 20

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.tools = getMultiAdapter((context, request), name="plone_tools")
        self.context = context
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    @property
    def extra(self):
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()
        return {
            "id": "plone-contentmenu-workflow",
            "class": f"state-{state}",
            "state": state,
            "stateTitle": stateTitle,
            "shortTitle": self.short_title,
            "li_class": "plonetoolbar-workfow-transition",
        }

    @property
    def description(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return _(
                "title_change_state_of_item", default="Change the state of this item"
            )
        return ""

    @property
    def action(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return self.context.absolute_url() + "/content_status_history"
        return ""

    @memoize
    def available(self):
        return self.context_state.workflow_state() is not None

    def selected(self):
        return False

    @memoize
    def _manageSettings(self):
        return self.tools.membership().checkPermission(
            WorkflowSubMenuItem.MANAGE_SETTINGS_PERMISSION, self.context
        )

    @memoize
    def _transitions(self):
        wf_tool = getToolByName(self.context, "portal_workflow")
        return wf_tool.listActionInfos(object=self.context, max=1)

    @memoize
    def _currentStateTitle(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state


@implementer(IWorkflowMenu)
class WorkflowMenu(BrowserMenu):
    # BBB: These actions (url's) existed in old workflow definitions
    # but were never used. The scripts they reference don't exist in
    # a standard installation. We allow the menu to fail gracefully
    # if these are encountered.

    BOGUS_WORKFLOW_ACTIONS = (
        "content_hide_form",
        "content_publish_form",
        "content_reject_form",
        "content_retract_form",
        "content_show_form",
        "content_submit_form",
    )

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        locking_info = queryMultiAdapter((context, request), name="plone_lock_info")
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        wf_tool = getToolByName(context, "portal_workflow")
        workflowActions = wf_tool.listActionInfos(object=context)

        for action in workflowActions:
            if action["category"] != "workflow":
                continue

            cssClass = ""
            actionUrl = action["url"]
            if actionUrl == "":
                actionUrl = "{0}/content_status_modify?workflow_action={1}"
                actionUrl = actionUrl.format(
                    context.absolute_url(),
                    action["id"],
                )
                cssClass = ""

            description = ""

            transition = action.get("transition", None)
            if transition is not None:
                description = transition.description

            baseUrl = "{0}/content_status_modify?workflow_action={1}"
            for bogus in self.BOGUS_WORKFLOW_ACTIONS:
                if actionUrl.endswith(bogus):
                    if getattr(context, bogus, None) is None:
                        actionUrl = baseUrl.format(
                            context.absolute_url(),
                            action["id"],
                        )
                        cssClass = ""
                    break

            if action["allowed"]:
                results.append(
                    {
                        "title": action["title"],
                        "description": description,
                        "action": addTokenToUrl(actionUrl, request),
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "workflow-transition-{}".format(action["id"]),
                            "separator": None,
                            "class": cssClass,
                        },
                        "submenu": None,
                    }
                )

        url = context.absolute_url()

        if len(results) > 0:
            results.append(
                {
                    "title": _("label_advanced", default="Advanced..."),
                    "description": "",
                    "action": url + "/content_status_history",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "workflow-transition-advanced",
                        "separator": "actionSeparator",
                        "class": "pat-plone-modal",
                    },
                    "submenu": None,
                }
            )

        pw = getToolByName(context, "portal_placeful_workflow", None)
        if pw is not None:
            if _checkPermission(ManageWorkflowPolicies, context):
                results.append(
                    {
                        "title": _("workflow_policy", default="Policy..."),
                        "description": "",
                        "action": url + "/@@placeful-workflow-configuration",
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "workflow-transition-policy",
                            "separator": None,
                            "class": "",
                        },
                        "submenu": None,
                    }
                )

        return results


@implementer(IPortletManagerSubMenuItem)
class PortletManagerSubMenuItem(BrowserSubMenuItem):
    MANAGE_SETTINGS_PERMISSION = "Portlets: Manage portlets"

    title = _("manage_portlets_link", default="Manage portlets")
    submenuId = "plone_contentmenu_portletmanager"
    icon = "toolbar-action/portlets"
    order = 50

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context = context
        self.context_state = getMultiAdapter(
            (context, request), name="plone_context_state"
        )

    @property
    def extra(self):
        return {
            "id": "plone-contentmenu-portletmanager",
            "li_class": "plonetoolbar-portlet-manager",
        }

    @property
    def description(self):
        if self._manageSettings():
            return _(
                "title_change_portlets", default="Change the portlets of this item"
            )
        else:
            return ""

    @property
    def action(self):
        return self.context.absolute_url() + "/manage-portlets"

    @memoize
    def available(self):
        secman = getSecurityManager()
        has_manage_portlets_permission = secman.checkPermission(
            "Portlets: Manage portlets", self.context
        )
        if not has_manage_portlets_permission:
            return False
        else:
            return ILocalPortletAssignable.providedBy(self.context)

    def selected(self):
        return False

    @memoize
    def _manageSettings(self):
        secman = getSecurityManager()
        has_manage_portlets_permission = secman.checkPermission(
            self.MANAGE_SETTINGS_PERMISSION, self.context
        )
        return has_manage_portlets_permission


@implementer(IPortletManagerMenu)
class PortletManagerMenu(BrowserMenu):
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        items = []
        sm = getSecurityManager()
        # Bail out if the user can't manage portlets
        if not sm.checkPermission(
            PortletManagerSubMenuItem.MANAGE_SETTINGS_PERMISSION, context
        ):
            return items
        blacklist = getUtility(IRegistry).get(
            "plone.app.portlets.PortletManagerBlacklist", []
        )
        managers = getUtilitiesFor(IPortletManager)
        current_url = context.absolute_url()

        items.append(
            {
                "title": _("manage_all_portlets", default="All…"),
                "description": "Manage all portlets",
                "action": addTokenToUrl(f"{current_url}/manage-portlets", request),
                "selected": False,
                "icon": None,
                "extra": {"id": "portlet-manager-all", "separator": None},
                "submenu": None,
            }
        )

        for manager in managers:
            manager_name = manager[0]
            # Don't show items like 'plone.dashboard1' by default
            if manager_name in blacklist:
                continue
            item = {
                "title": PMF(
                    manager_name, default=" ".join(manager_name.split(".")).title()
                ),
                "description": manager_name,
                "action": addTokenToUrl(
                    f"{current_url}/@@topbar-manage-portlets/{manager_name}",
                    request,
                ),
                "selected": False,
                "icon": None,
                "extra": {
                    "id": f"portlet-manager-{manager_name}",
                    "separator": None,
                },
                "submenu": None,
            }

            items.append(item)
        return sorted(items, key=itemgetter("title"))
