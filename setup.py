#!/usr/bin/env python

from setuptools import setup, find_packages

import version_check.config


setup(name='version-check',
      version=version_check.config.VERSION,
      description='Version Checking tool for SaltStack PRs',
      author='Nicole Thomas',
      author_email='nicole@saltstack.com',
      url='https://github.com/rallytime/version-check.git',
      packages=find_packages(),
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
      ],
      install_requires=['tornado'],
      entry_points='''
        [console_scripts]
        version-check= version_check.cli:main
      ''')
