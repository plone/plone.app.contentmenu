# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '2.2.4'
long_description = open('README.rst').read() + '\n'
long_description += open('CHANGES.rst').read()

setup(
    name='plone.app.contentmenu',
    version=version,
    description='Plone\'s content menu implementation',
    long_description=long_description,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'Framework :: Zope2',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='plone contentmenu menu',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.app.contentmenu',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
            'plone.app.contenttypes',
            'six',
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
        'plone.protect >= 3.0.0a1',
        'Zope2',
    ],
)
