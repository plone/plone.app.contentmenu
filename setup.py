from setuptools import find_packages
from setuptools import setup


version = "3.0.0a3"
long_description = open("README.rst").read() + "\n"
long_description += open("CHANGES.rst").read()

setup(
    name="plone.app.contentmenu",
    version=version,
    description="Plone's content menu implementation",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="plone contentmenu menu",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.contentmenu",
    license="GPL version 2",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            "plone.app.testing",
            "plone.app.contenttypes",
        ]
    ),
    install_requires=[
        "setuptools",
        "plone.base",
        "plone.locking",
        "plone.memoize",
        "plone.app.content >=2.0a3",
        "plone.protect >= 3.0.0a1",
    ],
)
