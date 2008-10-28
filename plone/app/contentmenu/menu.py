from urllib import quote_plus
from cgi import escape

from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.app.component.hooks import getSite

from zope.i18n import translate
from zope.i18nmessageid.message import Message

from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem

from plone.memoize.instance import memoize

from Acquisition import aq_inner, aq_base

from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from interfaces import IActionsSubMenuItem
from interfaces import IDisplaySubMenuItem
from interfaces import IFactoriesSubMenuItem
from interfaces import IWorkflowSubMenuItem

from interfaces import IActionsMenu
from interfaces import IDisplayMenu
from interfaces import IFactoriesMenu
from interfaces import IWorkflowMenu

from Products.CMFPlone import utils
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.content.browser.folderfactories import _allowedTypes

def _safe_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8', 'ignore')
    return text


class ActionsSubMenuItem(BrowserSubMenuItem):
    implements(IActionsSubMenuItem)

    title = _(u'label_actions_menu', default=u'Actions')
    description = _(u'title_actions_menu', default=u'Actions for the current content item')
    submenuId = 'plone_contentmenu_actions'

    order = 10
    extra = {'id': 'plone-contentmenu-actions'}

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')

    def getToolByName(self, tool):
        return getToolByName(getSite(), tool)

    @property
    def action(self):
        folder = self.context
        if not self.context_state.is_structural_folder():
            folder = utils.parent(self.context)
        return folder.absolute_url() + '/folder_contents'

    @memoize
    def available(self):
        actions_tool = self.getToolByName('portal_actions')
        editActions = actions_tool.listActionInfos(object=aq_inner(self.context), categories=('object_buttons',), max=1)
        return len(editActions) > 0

    def selected(self):
        return False


class ActionsMenu(BrowserMenu):
    implements(IActionsMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        portal_state = getMultiAdapter((context, request), name='plone_portal_state')

        actions_tool = getToolByName(aq_inner(context), 'portal_actions')
        editActions = actions_tool.listActionInfos(object=aq_inner(context), categories=('object_buttons',))

        if not editActions:
            return []

        plone_utils = getToolByName(context, 'plone_utils')
        portal_url = portal_state.portal_url()

        for action in editActions:
            if action['allowed']:
                cssClass = 'actionicon-object_buttons-%s' % action['id']
                icon = plone_utils.getIconFor('object_buttons', action['id'], None)
                if icon:
                    icon = '%s/%s' % (portal_url, icon)

                results.append({ 'title'       : action['title'],
                                 'description' : '',
                                 'action'      : action['url'],
                                 'selected'    : False,
                                 'icon'        : icon,
                                 'extra'       : {'id': action['id'], 'separator': None, 'class': cssClass},
                                 'submenu'     : None,
                                 })

        return results


class DisplaySubMenuItem(BrowserSubMenuItem):
    implements(IDisplaySubMenuItem)

    title = _(u'label_choose_template', default=u'Display')
    submenuId = 'plone_contentmenu_display'

    order = 20

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')

    @property
    def extra(self):
        return {'id': 'plone-contentmenu-display', 'disabled': self.disabled()}

    @property
    def description(self):
        if self.disabled():
            return _(u'title_remove_index_html_for_display_control', default=u'Delete or rename the index_html item to gain full control over how this folder is displayed.')
        else:
            return _(u'title_choose_default_view', default=u'Select the view mode for this folder, or set a content item as its default view.')

    @property
    def action(self):
        if self.disabled():
            return ''
        else:
            if self.context_state.is_default_page():
                return self.context_state.parent().absolute_url() + '/select_default_view'
            else:
                return self.context.absolute_url() + '/select_default_view'

    @memoize
    def available(self):
        if self.disabled():
            return False

        isDefaultPage = self.context_state.is_default_page()

        folder = None
        context = None

        folderLayouts = []
        contextLayouts = []

        # If this is a default page, also get menu items relative to the parent
        if isDefaultPage:
            folder = ISelectableBrowserDefault(utils.parent(self.context), None)

        context = ISelectableBrowserDefault(self.context, None)

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

        if context is not None:
            contextLayouts = context.getAvailableLayouts()
            contextCanSetLayout = context.canSetLayout()
            contextCanSetDefaultPage = context.canSetDefaultPage()

        # Show the menu if we either can set a default-page, or we have more
        # than one layout to choose from.
        if (folderCanSetDefaultPage) or \
           (folderCanSetLayout and len(folderLayouts) > 1) or \
           (folder is None and contextCanSetDefaultPage) or \
           (contextCanSetLayout and len(contextLayouts) > 1):
            return True
        else:
            return False

    def selected(self):
        return False

    @memoize
    def disabled(self):
        context = self.context
        if self.context_state.is_default_page():
            context = utils.parent(context)
        if not getattr(context, 'isPrincipiaFolderish', False):
            return False
        elif 'index_html' not in context.objectIds():
            return False
        else:
            return True


class DisplayMenu(BrowserMenu):
    implements(IDisplayMenu)

    def getMenuItems(self, obj, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter((obj, request), name='plone_context_state')
        isDefaultPage = context_state.is_default_page()

        parent = None

        folder = None
        context = None

        folderLayouts = []
        contextLayouts = []

        # If this is a default page, also get menu items relative to the parent
        if isDefaultPage:
            parent = utils.parent(obj)
            folder = ISelectableBrowserDefault(parent, None)

        context = ISelectableBrowserDefault(obj, None)

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

        if context is not None:
            contextLayouts = context.getAvailableLayouts()
            contextCanSetLayout = context.canSetLayout()
            contextCanSetDefaultPage = context.canSetDefaultPage()

        # Short circuit if neither folder nor object will provide us with
        # items
        if not (folderCanSetLayout or folderCanSetDefaultPage or \
                contextCanSetLayout or contextCanSetDefaultPage):
            return []

        # Only show the block "Folder display" and "Item display" separators if
        # they are necessars
        useSeparators = False
        if folderCanSetLayout or folderCanSetDefaultPage:
            if (contextCanSetLayout and len(contextLayouts) > 1) or \
                contextCanSetDefaultPage:
                useSeparators = True

        # 1. If this is a default-page, first render folder options
        if folder is not None:
            folderUrl = parent.absolute_url()

            if useSeparators:
                results.append({ 'title'       : _(u'label_current_folder_views', default=u'Folder display'),
                                 'description' : '',
                                 'action'      : None,
                                 'selected'    : False,
                                 'icon'        : None,
                                 'extra'       : {'id': 'folderHeader', 'separator': 'actionSeparator', 'class': ''},
                                 'submenu'     : None,
                                 })

            if folderCanSetLayout:
                for id, title in folderLayouts:
                    results.append({ 'title'       : title,
                                     'description' : '',
                                     'action'      : '%s/selectViewTemplate?templateId=%s' % (folderUrl, id,),
                                     'selected'    : False,
                                     'icon'        : None,
                                     'extra'       : {'id': 'folder-' + id, 'separator': None, 'class': ''},
                                     'submenu'     : None,
                                     })
            # Display the selected item (i.e. the context)
            results.append({ 'title'       : _(u'label_item_selected', default=u'Item: ${contentitem}', mapping={'contentitem' : escape(_safe_unicode(obj.Title()))}),
                             'description' : '',
                             'action'      : None,
                             'selected'    : True,
                             'icon'        : None,
                             'extra'       : {'id': 'folderDefaultPageDisplay', 'separator': 'actionSeparator', 'class': 'actionMenuSelected'},
                             'submenu'     : None,
                             })
            # Let the user change the selection
            if folderCanSetDefaultPage:
                results.append({ 'title'       : _(u'label_change_default_item', default=u'Change content item as default view...'),
                                 'description' : _(u'title_change_default_view_item', default=u'Change the item used as default view in this folder'),
                                 'action'      : '%s/select_default_page' % (folderUrl,),
                                 'selected'    : False,
                                 'icon'        : None,
                                 'extra'       : {'id': 'folderChangeDefaultPage', 'separator': 'actionSeparator', 'class': ''},
                                 'submenu'     : None,
                                 })

        # 2. Render context options
        if context is not None:
            contextUrl = obj.absolute_url()
            selected = context.getLayout()
            defaultPage = context.getDefaultPage()
            layouts = context.getAvailableLayouts()

            if useSeparators:
                results.append({ 'title'       : _(u'label_current_item_views', default=u'Item display'),
                                 'description' : '',
                                 'action'      : None,
                                 'selected'    : False,
                                 'icon'        : None,
                                 'extra'       : {'id': 'contextHeader', 'separator': 'actionSeparator', 'class': ''},
                                 'submenu'     : None,
                                 })

            # If context is a default-page in a folder, that folder's views will
            # be shown. Only show context views if there are any to show.

            showLayouts = False
            if not isDefaultPage:
                showLayouts = True
            elif len(layouts) > 1:
                showLayouts = True

            if showLayouts and contextCanSetLayout:
                for id, title in contextLayouts:
                    results.append({ 'title'       : title,
                                     'description' : '',
                                     'action'      : '%s/selectViewTemplate?templateId=%s' % (contextUrl, id,),
                                     'selected'    : (defaultPage is None and id == selected),
                                     'icon'        : None,
                                     'extra'       : {'id': id, 'separator': None, 'class': ''},
                                     'submenu'     : None,
                                     })

            # Allow setting / changing the default-page, unless this is a
            # default-page in a parent folder.
            if not INonStructuralFolder.providedBy(obj):
                if defaultPage is None:
                    if contextCanSetDefaultPage:
                        results.append({ 'title'       : _(u'label_choose_item', default=u'Select a content item\nas default view...'),
                                         'description' : _(u'title_select_default_view_item', default=u'Select an item to be used as default view in this folder...'),
                                         'action'      : '%s/select_default_page' % (contextUrl,),
                                         'selected'    : False,
                                         'icon'        : None,
                                         'extra'       : {'id': 'contextSetDefaultPage', 'separator': 'actionSeparator', 'class': ''},
                                         'submenu'     : None,
                                         })
                else:
                    defaultPageObj = getattr(obj, defaultPage, None)
                    defaultPageTitle = u""
                    if defaultPageObj is not None:
                        if hasattr(aq_base(defaultPageObj), 'Title'):
                            defaultPageTitle = defaultPageObj.Title()
                        else:
                            defaultPageTitle = getattr(aq_base(defaultPageObj), 'title', u'')

                    results.append({ 'title'       : _(u'label_item_selected', default=u'Item: ${contentitem}', mapping={'contentitem' : escape(_safe_unicode(defaultPageTitle))}),
                                     'description' : '',
                                     'action'      : None,
                                     'selected'    : True,
                                     'icon'        : None,
                                     'extra'       : {'id': 'contextDefaultPageDisplay', 'separator': 'actionSeparator', 'class': ''},
                                     'submenu'     : None,
                                     })
                    if contextCanSetDefaultPage:
                        results.append({ 'title'       : _(u'label_change_item', default=u'Change content item\nas default view...'),
                                         'description' : _(u'title_change_default_view_item', default=u'Change the item used as default view in this folder'),
                                         'action'      : '%s/select_default_page' % (contextUrl,),
                                         'selected'    : False,
                                         'icon'        : None,
                                         'extra'       : {'id': 'contextChangeDefaultPage', 'separator': 'actionSeparator', 'class': ''},
                                         'submenu'     : None,
                                         })

        return results


class FactoriesSubMenuItem(BrowserSubMenuItem):
    implements(IFactoriesSubMenuItem)

    submenuId = 'plone_contentmenu_factory'
    order = 30

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')

    @property
    def extra(self):
        return {'id': 'plone-contentmenu-factories',
                'hideChildren': self._hideChildren()}

    @property
    def title(self):
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if showConstrainOptions or len(itemsToAdd) > 1:
            return _(u'label_add_new_item', default=u'Add new\u2026')
        elif len(itemsToAdd) == 1:
            fti=itemsToAdd[0][1]
            title = fti.Title()
            if isinstance(title, Message):
                title = translate(title, context=self.request)
            else:
                title = translate(_safe_unicode(title),
                                  domain='plone',
                                  context=self.request)
            return _(u'label_add_type', default='Add ${type}',
                     mapping={'type' : title})
        else:
            return _(u'label_add_new_item', default=u'Add new\u2026')

    @property
    def description(self):
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if showConstrainOptions or len(itemsToAdd) > 1:
            return _(u'title_add_new_items_inside_item', default=u'Add new items inside this item')
        elif len(itemsToAdd) == 1:
            return itemsToAdd[0][1].Description()
        else:
            return _(u'title_add_new_items_inside_item', default=u'Add new items inside this item')

    @property
    def action(self):
        addContext = self._addContext()
        if self._hideChildren():
            (addContext, fti) = self._itemsToAdd()[0]
            baseUrl = addContext.absolute_url()
            addingview = queryMultiAdapter((addContext, self.request), name='+')
            if addingview is not None:
                addview = queryMultiAdapter((addingview, self.request), name=fti.factory)
                if addview is not None:
                    return '%s/+/%s' % (baseUrl, fti.factory,)
            return '%s/createObject?type_name=%s' % (baseUrl, quote_plus(fti.getId()),)
        else:
            return '%s/folder_factories' % self.context_state.folder().absolute_url()

    @property
    def icon(self):
        if self._hideChildren():
            fti = self._itemsToAdd()[0][1]
            return fti.getIcon()
        else:
            return None

    def available(self):
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if self._addingToParent() and not self.context_state.is_default_page():
            return False
        return (len(itemsToAdd) > 0 or showConstrainOptions)

    def selected(self):
        return False

    @memoize
    def _addContext(self):
        return self.context_state.folder()

    @memoize
    def _itemsToAdd(self):
        context=self.context_state.folder()
        return [(context, fti) for fti in self._addableTypesInContext(context)]

    def _addableTypesInContext(self, addContext):
        allowed_types = _allowedTypes(self.request, addContext)
        constrain = IConstrainTypes(addContext, None)
        if constrain is None:
            return allowed_types
        else:
            locallyAllowed = constrain.getLocallyAllowedTypes()
            return [fti for fti in allowed_types if fti.getId() in locallyAllowed]

    @memoize
    def _addingToParent(self):
        return (self._addContext().absolute_url() != self.context.absolute_url())

    @memoize
    def _showConstrainOptions(self):
        addContext = self._addContext()
        constrain = ISelectableConstrainTypes(addContext, None)
        if constrain is None:
            return False
        elif constrain.canSetConstrainTypes() and constrain.getDefaultAddableTypes():
            return True
        elif len(constrain.getLocallyAllowedTypes()) < len(constrain.getImmediatelyAddableTypes()):
            return True

    @memoize
    def _hideChildren(self):
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        return (len(itemsToAdd) == 1 and not showConstrainOptions)


class FactoriesMenu(BrowserMenu):
    implements(IFactoriesMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        factories_view = getMultiAdapter((context, request), name='folder_factories')

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
            url = '%s/folder_factories' % (addContext.absolute_url(),)
            results.append({ 'title'       : _(u'folder_add_more', default=u'More\u2026'),
                             'description' : _(u'Show all available content types'),
                             'action'      : url,
                             'selected'    : False,
                             'icon'        : None,
                             'extra'       : {'id': 'more', 'separator': None, 'class': ''},
                             'submenu'     : None,
                            })

        constraints = ISelectableConstrainTypes(addContext, None)
        if constraints is not None:
            if constraints.canSetConstrainTypes() and constraints.getDefaultAddableTypes():
                url = '%s/folder_constraintypes_form' % (addContext.absolute_url(),)
                results.append({'title'       : _(u'folder_add_settings', default=u'Restrictions\u2026'),
                                'description' : _(u'title_configure_addable_content_types', default=u'Configure which content types can be added here'),
                                'action'      : url,
                                'selected'    : False,
                                'icon'        : None,
                                'extra'       : {'id': 'settings', 'separator': None, 'class': ''},
                                'submenu'     : None,
                                })

        return results


class WorkflowSubMenuItem(BrowserSubMenuItem):
    implements(IWorkflowSubMenuItem)

    MANAGE_SETTINGS_PERMISSION = 'Manage portal'

    title = _(u'label_state', default=u'State:')
    submenuId = 'plone_contentmenu_workflow'
    order = 40

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.tools = getMultiAdapter((context, request), name='plone_tools')
        self.context = context
        self.context_state = getMultiAdapter((context, request), name='plone_context_state')

    @property
    def extra(self):
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()
        return {'id'         : 'plone-contentmenu-workflow',
                'class'      : 'state-%s' % state,
                'state'      : state,
                'stateTitle' : stateTitle,}

    @property
    def description(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return _(u'title_change_state_of_item', default=u'Change the state of this item')
        else:
            return u''

    @property
    def action(self):
        if self._manageSettings() or len(self._transitions()) > 0:
            return self.context.absolute_url() + '/content_status_history'
        else:
            return ''

    @memoize
    def available(self):
        return (self.context_state.workflow_state() is not None)

    def selected(self):
        return False

    @memoize
    def _manageSettings(self):
        return self.tools.membership().checkPermission(WorkflowSubMenuItem.MANAGE_SETTINGS_PERMISSION, self.context)

    @memoize
    def _transitions(self):
        wf_tool = getToolByName(aq_inner(self.context), 'portal_workflow')
        return wf_tool.listActionInfos(object=aq_inner(self.context), max=1)

    @memoize
    def _currentStateTitle(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state


class WorkflowMenu(BrowserMenu):
    implements(IWorkflowMenu)

    # BBB: These actions (url's) existed in old workflow definitions
    # but were never used. The scripts they reference don't exist in
    # a standard installation. We allow the menu to fail gracefully
    # if these are encountered.

    BOGUS_WORKFLOW_ACTIONS = (
        'content_hide_form',
        'content_publish_form',
        'content_reject_form',
        'content_retract_form',
        'content_show_form',
        'content_submit_form',
    )

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []
        context = aq_inner(context)

        wf_tool = getToolByName(context, 'portal_workflow')
        workflowActions = wf_tool.listActionInfos(object=context)

        locking_info = queryMultiAdapter((context, request), name='plone_lock_info')
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        for action in workflowActions:
            if action['category'] != 'workflow':
                continue

            cssClass = 'kssIgnore'
            actionUrl = action['url']
            if actionUrl == "":
                actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'])
                cssClass = ''

            description = ''

            transition = action.get('transition', None)
            if transition is not None:
                description = transition.description

            for bogus in self.BOGUS_WORKFLOW_ACTIONS:
                if actionUrl.endswith(bogus):
                    if getattr(context, bogus, None) is None:
                        actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'],)
                        cssClass =''
                    break

            if action['allowed']:
                results.append({ 'title'       : action['title'],
                                 'description' : description,
                                 'action'      : actionUrl,
                                 'selected'    : False,
                                 'icon'        : None,
                                 'extra'       : {'id': 'workflow-transition-%s' % action['id'], 'separator': None, 'class': cssClass},
                                 'submenu'     : None,
                                 })

        url = context.absolute_url()

        if len(results) > 0:
            results.append({ 'title'        : _(u'label_advanced', default=u'Advanced...'),
                             'description'  : '',
                             'action'       : url + '/content_status_history',
                             'selected'     : False,
                             'icon'         : None,
                             'extra'        : {'id': 'advanced', 'separator': 'actionSeparator', 'class': 'kssIgnore'},
                             'submenu'      : None,
                            })

        if getToolByName(context, 'portal_placeful_workflow', None) is not None:
            results.append({ 'title'       : _(u'workflow_policy', default=u'Policy...'),
                             'description' : '',
                             'action'      : url + '/placeful_workflow_configuration',
                             'selected'    : False,
                             'icon'        : None,
                             'extra'       : {'id': 'policy', 'separator': None, 'class': 'kssIgnore'},
                             'submenu'     : None,
                            })

        return results
