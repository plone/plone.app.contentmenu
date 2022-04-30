from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class PloneAppContentmenu(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.contentmenu

        xmlconfig.file(
            "configure.zcml", plone.app.contentmenu, context=configurationContext
        )


PLONE_APP_CONTENTMENU_FIXTURE = PloneAppContentmenu()
PLONE_APP_CONTENTMENU_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTMENU_FIXTURE,), name="PloneAppContentmenu:Integration"
)
PLONE_APP_CONTENTMENU_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTMENU_FIXTURE,), name="PloneAppContentmenu:Functional"
)


# Dexterity test layers
PLONE_APP_CONTENTMENU_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContentmenuDX:Integration"
)
PLONE_APP_CONTENTMENU_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContentmenuDX:Functional"
)
