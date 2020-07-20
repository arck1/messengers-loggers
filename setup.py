import os
from setuptools import find_packages, setup

VERSION = 0.1

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="messengers-loggers",
    version=VERSION,
    include_package_data=True,
    license="Apache-2.0 License",
    description="Messengers loggers",
    long_description=README,
    url="https://github.com/arck1/messengers-loggers",
    author="AidarRakhimov",
    author_email="a.v.rakhimov@gmail.com",
    platforms=["linux", "mac"],
    packages=find_packages(exclude=["tests*"]),
    test_suite="tests",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache-2.0 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=["requests"],
)
