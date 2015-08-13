from setuptools import setup, find_packages

version = '2.0.10.dev0'
long_description = open("README.rst").read()
long_description += "\n"
long_description += open("CHANGES.rst").read()

setup(name='plone.app.contentmenu',
      version=version,
      description="Plone's content menu implementation",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='plone contentmenu menu',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.contentmenu',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
              'plone.app.testing',
          ]
          ),
      install_requires=[
          'setuptools',
          'plone.locking',
          'plone.memoize',
          'plone.app.content >=2.0a3',
          'zope.browsermenu',
          'zope.component',
          'zope.contentprovider',
          'zope.interface',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.publisher',
          'Acquisition',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFPlone',
          'Zope2',
      ],
      )
