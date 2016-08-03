"""\
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))
from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    sys.exit(os.system('python setup.py sdist upload'))


with open("requirements.txt") as req_file:
    requires = [req for req in req_file]


setup(
    name='gardenbot',
    version='0.1.0b',
    description='Bot to help with gardening tasks',
    long_description=__doc__,
    author='Daniel DeSousa',
    author_email='gardenbot@daniel.desousa.cc',
    url='http://github.com/dandesousa/gardenbot',
    license='CC0 1.0 Universal',
    platforms='any',
    test_suite="tests.test_suite.test_all",
    packages=find_packages(exclude=["tests"]),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    zip_safe=False,
    entry_points={'console_scripts': ['gardenbot = gardenbot.command:main']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
