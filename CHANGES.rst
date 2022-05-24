Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.0a3 (2022-05-24)
--------------------

New features:


- Reimplement dropout toolbar submenus and collapsed icons
  [petschki] (#35)


Bug fixes:


- Remove alt tags from icons within links.
  [agitator] (#38)


3.0.0a2 (2022-05-15)
--------------------

Breaking changes:


- Use plone.base. Remove six and Archetypes specific code.
  [jensens] (#34)


Bug fixes:


- Fixed permission handling on browser:menuItem [iham] (#26) (#26)
- Fix contentview actions without submenu
  [petschki] (#36)


3.0.0a1 (2022-04-04)
--------------------

Breaking changes:


- Changes for new Plone 6 toolbar.
  [petschki] (#30)
- Use Plone 6 icon resolver and SVG icons.
  [agitator] (#30)


2.3.4 (2021-09-15)
------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [ericof] (#31)


2.3.3 (2021-06-30)
------------------

Bug fixes:


- Updated README.rst.
  [ksuess, jensens] (#1)


2.3.2 (2020-07-17)
------------------

Bug fixes:


- Fix review state icon position in toolbar when the user doesn't have the permission to change the review state.
  This fixes https://github.com/plone/plonetheme.barceloneta/issues/110
  [vincentfretin] (#29)


2.3.1 (2020-03-21)
------------------

Bug fixes:


- Minor packaging updates. [various] (#1)


2.3.0 (2019-06-27)
------------------

New features:


- Add support for Python 3.8 [pbauer] (#25)


2.2.4 (2018-09-23)
------------------

Bug fixes:

- Fix sorting of portletmanager-menuitems in py3.
  [pbauer]


2.2.3 (2018-02-05)
------------------

Bug fixes:

- Use ``get_installer`` in tests.  [maurits]


2.2.2 (2017-02-12)
------------------

Bug fixes:

- Fix portlets ZCML title registration.
  [gforcada]

2.2.1 (2016-11-10)
------------------

Bug fixes:

- Don't extract dynamic messages with i18ndude.
  [vincentfretin]


2.2 (2016-11-01)
----------------

New features:

- Make portlet manager names translatable. Add an "All" option for portlet
  manager management.
  [alecm]

- Display menu reorganization. Selected view/item should be on top of section
  and headings should appear as headings.
  [alecm]

- Add ability to specify a short title for the collapsed sidebar by setting
  extras['shortTitle'], in the same way as stateTitle.
  [MatthewWilkes]

Bug fixes:

- Add default icon for top-level toolbar entries
  [alecm]

- Code cleanup.
  [gforcad]


2.1.9 (2016-10-03)
------------------

New features:

- Documentation in README added.
  [jensens]

Bug fixes:

- Minor code cleanup, some micro-optimizations.
  [jensens]


2.1.8 (2016-05-26)
------------------

Fixes:

- Optimized display menu's check for `index_html`.
  [davisagli]


2.1.7 (2016-02-19)
------------------

Fixes:

- Fixed test (don't expect role from pac-tests).  [pbauer]


2.1.6 (2015-08-20)
------------------

- Fix: Permission check ``ManageWorkflowPolicies`` was always on fallback to
  ``ManagerPortal``. Now checks the correct permission after using the
  pkg_resources.get_distribution api for checking (never catch an ImportError).
  [jensens]

- pep8, zca decorators, plone code conventions
  [jensens]

- do not open manage portlets in a modal
  [vangheem]


2.1.5 (2015-07-18)
------------------

- hide submenu so screen readers do not read full contents every time
  [vangheem]

- get rid of "more options", reorder menu, show actions in
  folder contents, better accessibility.
  [vangheem]


2.1.4 (2015-05-05)
------------------

- Rerelease due to double distribution ending up on PyPI.
  [maurits]


2.1.3 (2015-05-04)
------------------

- Change test-setup to allow testing AT and DX.
  [pbauer]

- Fix Dexterity tests to use plone.app.contenttypes' browser layer. Fix tests
  to work with new plone.app.contenttypes unified view names.
  [thet]

- Don't show the menu-item to add content to a folderish default_page if no
  content can be added to it.
  [pbauer]

- pat-modal pattern has been renamed to pat-plone-modal
  [jcbrand]


2.1.2 (2014-10-23)
------------------

- Fix "Manage Portlets" menus not appearing for "Site Administrators".
  [@rpatterson]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project.
  [albertcasado, sneridagh]

- New toolbar markup based in ul li tags for the contentActions menus.
  [albertcasado, sneridagh]


2.1.1 (2014-04-13)
------------------

- Add csrf tokens to menu urls that need it.
- Allow custom modal attributes for more links
  [do3cc]


2.1.0 (2014-02-26)
------------------

- Add markup changes related to new Barceloneta theme.
  [bloodbare]


2.0.9 (2014-01-27)
------------------

- Don't break if there's no portal_actionicons tool.
  [davisagli]

- Ported tests to plone.app.testing
  [tomgross]


2.0.8 (2013-03-05)
------------------


2.0.7 (2012-12-09)
------------------

- add prefix to id tag for display menu dropdown items, fixes #11927 and #10894
  [maartenkling]

2.0.6 (2012-07-02)
------------------

- Use zope.browsermenu and remove Zope 2.12 BBB code.
  [hannosch]

2.0.5 (2012-02-07)
------------------

- Restore the workflow menu on the folder contents page as it is the
  only way to change the state of the folder when it has a default
  page.  Improves the fix to http://dev.plone.org/plone/ticket/8908.
  [rossp]

2.0.4 - 2011-07-04
------------------

- Set height/width of contentmenu icons through browser menu code.
  [thomasdesvenain]

2.0.3 - 2011-05-12
------------------

- We need permission to see Placeful policy in workflow menu.
  [thomasdesvenain]

2.0.2 - 2011-01-03
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Add test coverage for factory expression context when a front-page object is
  used for a folder.  Fix in plone.app.content.
  [rossp]

- Fix the addContext in the FactoriesSubMenuItem to make it possible to add
  content to a folderish object that set as the default view on its parent folder.
  This closes http://dev.plone.org/plone/ticket/10953.
  [WouterVH]


2.0.1 - 2010-07-18
------------------

- Update license to GPL version 2 only.
  [hannosch]


2.0 - 2010-07-01
----------------

- Adding "deactivated" class to menus by default, so they won't flicker on load.
  This fixes http://dev.plone.org/plone/ticket/10470.
  [limi]


2.0b3 - 2010-06-13
------------------

- Added optional compatibility with zope.browsermenu.
  [hannosch]


2.0b2 - 2010-02-17
------------------

- Show "add new" menu when there are one or more addable types. Showing a link
  when only one type was addable caused conflicts with the dropdown JavaScript.
  Closes http://dev.plone.org/plone/ticket/10193.
  [esteele, davisagli]

- Query the types tool instead of the action tools to find add actions
  in FactoriesSubMenuItem. This fixes a discrepancy in action URLs.
  http://dev.plone.org/plone/ticket/10207
  [wichert]


2.0b1 - 2010-01-24
------------------

- Removed the checking for hideChildren when a single item is present, this
  makes the styling consistent again. The menu is really a one-item menu, and we
  put it in the header as a shortcut that you can click directly. This fixes
  http://dev.plone.org/plone/ticket/9735
  [limi]


2.0a2 - 2009-12-27
------------------

- Adjust factory menu to use the new getIconExprObject method.
  [hannosch]

- Removed no longer required zope.site dependency.
  [hannosch]

- Hide the actions, display and workflow menus on the folder contents page.
  This closes http://dev.plone.org/plone/ticket/8908.
  [hannosch]

- Avoid a bogus getToolByName indirection via getSite().
  [hannosch]

- Noted missing zope.publisher dependency and prefer absolute imports.
  [hannosch]

- Mark selected display always with 'actionMenuSelected' class and
  stop using bullet points. References
  http://dev.plone.org/plone/ticket/9894
  [dukebody]


2.0a1 - 2009-11-14
------------------

- Specified package dependencies and assorted cleanups.
  [hannosch]

- Avoid a deprecation warning for calling the ``actions`` method from the
  context_state state view without passing in an action category.
  [hannosch]

- Updated action and icon handling in the actions menu to take advantage of the
  icon being stored on the action itself.
  [hannosch]

- Added support for the new add_view_expr property available on FTIs. This can be
  used to construct a URL for add views.
  [optilude]


1.1.7 - 2009-03-07
------------------

- Made a test independent of an internal sort order.
  [hannosch]

- Escape the title of the defaultpage in the DisplayMenu. This fixes a potential
  xss attack and http://dev.plone.org/plone/ticket/8377.
  [csenger]

- Added the prefix "folder-" to the CSS id of the folder part of the view
  contentmenu. This closes http://dev.plone.org/plone/ticket/8375.
  [realefab]


1.1.6 - 2008-10-07
------------------

- Fix on factories menu, showing constrain options only when there are types to
  constrain. This closes http://dev.plone.org/plone/ticket/8213.
  [igbun]

- Fix non XML syntax compliant ids in contentmenus. This closes
  http://dev.plone.org/plone/ticket/8195
  [garbas,calvinhp]


1.1.5 - 2008-08-18
------------------

- Add a span with a "noMenuAction" class around disable menus, allowing them
  to be styled.
  [wichert]


1.1.3 - 2008-07-07
------------------

- Adjusted tests to reflect new behavior introduced by the last change.
  [hannosch]

- Do not show the display menu if it is disabled (i.e. there is an index_html
  item in the folder). The previous behavior was confusing for users: the
  description with the hint to remove the index_html object was never shown
  and users only got a unusable menu item. The new behavior makes the display
  menu consistent with other parts of the Plone UI.
  [wichert]

- Add an actionMenuSelected class to selected menu items so they can be
  styled (same class as used in Plone 2.5). Do not remove the <span>
  tag around the &bull; for selected items so it can be removed when
  proper CSS styling is used.
  [wichert]


1.0.7 - 2008-03-09
------------------

- Correct the content menu html: the icons in menus should have an empty
  alt-attribute since the alternative text if no image can be seen is the label
  of the menu item itself. Move the description to the title attribute so it
  still shows up as tooltip.
  [wichert]

- Fixed an issue with non ISelectableBrowserDefault aware content.
  This closes http://dev.plone.org/plone/ticket/7226.
  [deo]


1.0.6 - 2008-01-06
------------------

- Fixed display menu to show the default page title correctly when the
  default-page is not a contained content item with DC metadata fields.
  Thanks to George Lee for finding this.
  [optilude]


1.0.5 - 2008-01-02
------------------

- Fixed display menu to show the default page title when not currently
  viewing it as well as the display of markup contained in translations.
  This fixes http://dev.plone.org/plone/ticket/7281.
  [witsch]

- Removed loop that does nothing in plone.app.contentmenu.menu, in
  WorkflowMenu.getMenuItems().
  [dreamcatcher]

1.0.3 - 2007-11-09
------------------

- Fixed another translation problem in the factory menu when only one type
  was shown. This closes http://dev.plone.org/plone/ticket/7023.
  [hannosch]

- Fixed more translation problems with the display menu.
  This closes http://dev.plone.org/plone/ticket/6838 again and
  http://dev.plone.org/plone/ticket/7115 as well.
  [hannosch]

- Fixed display menu to properly show content item titles with non-ascii chars.
  This closes http://dev.plone.org/plone/ticket/6838.
  [hannosch]

- Do not show the add item menu anymore on normal content, but just on
  folderish and default pages. This closes
  http://dev.plone.org/plone/ticket/6744.
  [hannosch]

- Fixed variable name in the label_item_selected message id. This closes
  http://dev.plone.org/plone/ticket/6584.
  [hannosch]

- Normalized typeIds on the factories menu, as these are used as CSS ids
  and would otherwise fail W3C validation for types with a space in the
  name. This closes http://dev.plone.org/plone/ticket/6259.
  [hannosch]

- Set kssIgnore class on workflow actions that define their own screens.
  [ldr]


1.0b1 - 2007-03-05
------------------

- Initial package structure.
  [zopeskel]
