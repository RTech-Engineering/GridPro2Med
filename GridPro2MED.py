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

# This tool use MEDCoupling module from SALOME project
# see http://salome-platform.org
"""CLI Script function for converting files.

"""

from gp2med.MultiBlock import MultiBlock
from gp2med import __version__
import argparse

version = __version__


def run_convert():
    """CLI Script function for converting files.
    """
    parser = argparse.ArgumentParser(description='Convert GridPro multiblock \
                                     mesh to MED file for Code-Saturn')
    parser.add_argument("inputfile", help="GridPro input file")
    parser.add_argument("outputfile", help="MED outputfile")

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-c", "--coarse", help="coarsen mesh N levels",
                        type=int, default=1)
    parser.add_argument("-x", "--extrude", help="extrude distance for 2D mesh",
                        type=float, default=1.0)

    args = parser.parse_args()

    inputfile = args.inputfile
    outputfile = args.outputfile
    if args.verbose:
        print "verbosity turned on"
    print "coarsening ", args.coarse
    print "2D extrusion", args.extrude

    # read multiblock structured mesh in GridPro format
    mblock = MultiBlock()

    mblock.readGridPro(inputfile, args)
    mblock.writeMED(outputfile)


if __name__ == '__main__':
    run_convert()
