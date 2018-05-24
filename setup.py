from io import open

from setuptools import find_packages, setup

with open('telego/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

REQUIRES = []

setup(
    name='telego',
    version=version,
    author='GYCHEN',
    author_email='gy.chen@gms.nutc.edu.tw',
    maintainer='GYCHEN',
    maintainer_email='gy.chen@gms.nutc.edu.tw',
    url='https://github.com/gy-chen/telego',
    install_requires=REQUIRES,
    packages=find_packages()
)
