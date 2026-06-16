from setuptools import setup
from statblk import version

setup(
    name='statblk',
    version=version,
    description='Gather essential disk and partition info for block devices and print it in a nice table',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Yufei Pan',
    author_email='pan@zopyr.us',
    url='https://github.com/yufei-pan/statblk',
    py_modules=['statblk'],
    entry_points={
        'console_scripts': [
            'statblk=statblk:main',
        ],
    },
    install_requires=[
        'multiCMD>=1.47',
        'argparse',
    ],
    extras_require={
        'completion': [
            'argcomplete',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
    ],
    python_requires='>=3.6',
	license='GPLv3+',
)
