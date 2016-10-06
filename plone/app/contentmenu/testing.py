# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

import pkg_resources


class PloneAppContentmenu(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.contentmenu
        xmlconfig.file('configure.zcml',
                       plone.app.contentmenu,
                       context=configurationContext)


class PloneAppContentmenuAT(PloneAppContentmenu):

    def setUpZope(self, app, configurationContext):
        # prepare installing Products.ATContentTypes
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')
        # prepare installing plone.app.collection
        try:
            pkg_resources.get_distribution('plone.app.collection')
            z2.installProduct(app, 'plone.app.collection')
        except pkg_resources.DistributionNotFound:
            pass

    def tearDownZope(self, app):
        try:
            pkg_resources.get_distribution('plone.app.collection')
            z2.uninstallProduct(app, 'plone.app.collection')
        except pkg_resources.DistributionNotFound:
            pass
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.ATContentTypes')
        z2.uninstallProduct(app, 'Products.Archetypes')

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        # install Products.ATContentTypes manually if profile is available
        # (this is only needed for Plone >= 5)
        profiles = [x['id'] for x in portal.portal_setup.listProfileInfo()]
        if 'Products.ATContentTypes:default' in profiles:
            applyProfile(portal, 'Products.ATContentTypes:default')

        # install plone.app.collections manually if profile is available
        # (this is only needed for Plone >= 5)
        if 'plone.app.collection:default' in profiles:
            applyProfile(portal, 'plone.app.collection:default')


PLONE_APP_CONTENTMENU_FIXTURE = PloneAppContentmenu()
PLONE_APP_CONTENTMENU_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTMENU_FIXTURE, ),
    name='PloneAppContentmenu:Integration')
PLONE_APP_CONTENTMENU_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTMENU_FIXTURE, ),
    name='PloneAppContentmenu:Functional')


# Dexterity test layers
PLONE_APP_CONTENTMENU_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE, ),
    name='PloneAppContentmenuDX:Integration')
PLONE_APP_CONTENTMENU_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE, ),
    name='PloneAppContentmenuDX:Functional')


# AT test layers
PLONE_APP_CONTENTMENU_AT_FIXTURE = PloneAppContentmenuAT()
PLONE_APP_CONTENTMENU_AT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTMENU_AT_FIXTURE, ),
    name='PloneAppContentmenuAT:Integration')
PLONE_APP_CONTENTMENU_AT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTMENU_AT_FIXTURE, ),
    name='PloneAppContentmenuAT:Functional')
