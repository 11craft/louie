from setuptools import find_packages, setup

from louie import version

README = open("README.rst", "r").read()

setup(
    name=version.NAME,
    version=version.VERSION,
    description=version.DESCRIPTION,
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="",
    author="Patrick K. O'Brien and contributors",
    url="https://github.com/11craft/louie/",
    download_url="https://pypi.python.org/pypi/Louie",
    license="BSD",
    packages=find_packages(exclude=["doc", "examples", "tests"]),
    zip_safe=False,
    package_data={
        # -*- package_data: -*-
    },
    python_requires=">=3.6",
)
