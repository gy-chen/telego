from io import open
from setuptools import find_packages, setup
from babel.messages import frontend as babel

with open('telego/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

REQUIRES = [
    'gomill',
    'python-telegram-bot',
    'Babel',
    'python-dotenv'
]

setup(
    name='telego',
    version=version,
    author='GYCHEN',
    author_email='gy.chen@gms.nutc.edu.tw',
    maintainer='GYCHEN',
    maintainer_email='gy.chen@gms.nutc.edu.tw',
    url='https://github.com/gy-chen/telego',
    install_requires=REQUIRES,
    packages=find_packages(),
    cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog
    },
    entry_points={
        'console_scripts': [
            'telego=telego.telegram:main',
        ],
    },
    package_data={
        'telego': ['telegram/translations/zh_TW/LC_MESSAGES/*'],
    },
)
