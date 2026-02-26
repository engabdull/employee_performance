from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__.py or hooks.py
from employee_performance import __version__ as version

setup(
    name="employee_performance",
    version=version,
    description="Employee Performance Dashboard",
    author="kareem",
    author_email="kareemtarekanwer@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
