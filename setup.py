#!/usr/bin/python2
# -*- coding: utf-8 -*-
# Copyright (C) 2016  R.Tech
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this code; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See https://github.com/RTech-Engineering
#
# Author : Martin Spel (R.Tech)
# Contributor : Philippe Makowski (R.Tech)

# This tool use MEDCoupling module from SALOME project
# see http://salome-platform.org

"""CLI Script function for converting files.

"""
from setuptools import setup, find_packages
from gp2med import __version__

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering',
    'Intended Audience :: Science/Research ',
]

setup(name='gridpro2med',
      version=__version__,
      description='CLI Script function for converting files.',
      url='https://github.com/RTech-Engineering',
      classifiers=classifiers,
      keywords=['GridPro', 'SALOME'],
      license='LGPLv3',
      author='Martin Spel',
      long_description='Convert GridPro multiblock \
		        mesh to MED file for Code-Saturn',
      py_modules=['GridPro2MED'],
      install_requires=['numpy', ],
      setup_requires=[],
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      package_data={'': ['LICENSE', '*.md'],
                    },
      use_2to3=False,
      zip_safe=False,
      entry_points={'console_scripts': [
            'gridpro2med = GridPro2MED:run_convert',
        ],
       },
      )
