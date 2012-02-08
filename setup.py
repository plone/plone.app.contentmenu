from setuptools import setup, find_packages

version = '2.0.5'

setup(name='plone.app.contentmenu',
      version=version,
      description="Plone's content menu implementation",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='plone contentmenu menu',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.contentmenu',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
          'Products.PloneTestCase',
          ]
        ),
      install_requires=[
        'setuptools',
        'plone.locking',
        'plone.memoize',
        'plone.app.content >=2.0a3',
        'zope.component',
        'zope.contentprovider',
        'zope.interface',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.publisher',
        'zope.app.publisher',
        'Acquisition',
        'Products.CMFCore',
        'Products.CMFDynamicViewFTI',
        'Products.CMFPlone',
        'Zope2',
      ],
      )
