import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "readme.md").read_text()

# This call to setup() does all the work
setup(
    name="security-checkin",
    version="0.511",
    description="Keep track of contact with remote teams",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/stevetasticsteve/SecurityCheckin",
    author="Stephen Stanley",
    author_email="info@realpython.com",
    license="GPL version 3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    packages=["checkin", "checkin.UI", "checkin.function", "checkin.icons"],
    include_package_data=True,
    install_requires=["PyQt5"],
    entry_points={
        "console_scripts": [
            "security-checkin=checkin.__main__:main",
        ]
    },
)

