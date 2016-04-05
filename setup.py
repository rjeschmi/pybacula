"""Setup script for Bacula database API"""


from setuptools import setup, find_packages

setup(
    name="bacula",
    version="0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bacula = bacula.main:bacula_cmd',
        ]
    },
)
