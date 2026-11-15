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
    # No multiCMD: statblk carries its own copy (the embedded block in statblk.py) and runs it wherever an installed one is
    # older than that copy, missing or does not import, so a requirement would guarantee nothing; and pip 9 (stock on EL7
    # and EL8) upgrading an old multiCMD for it stopped `pip3 install -U statblk` (docs/lessons.md, 2026-11-14).
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
