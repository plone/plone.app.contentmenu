from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.app.contentmenu',
      version=version,
      description="Plone's content menu implementation",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='plone contentmenu menu',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/plone/plone.app.contentmenu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
