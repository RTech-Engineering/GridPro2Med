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

from gp2med.InputError import InputError
from gp2med.Face import Face


class Connectivity(object):

    @staticmethod
    def convertLine(line):
        words = line.split()
        if len(words) != 27:
            raise InputError("Error parsing line in connectivity file")

        b = words[1]
        #               type      index    neighbor      orientation
        face0 = Face(0, words[2], words[3], words[4], words[5])
        face1 = Face(1, words[6], words[7], words[8], words[9])
        face2 = Face(2, words[10], words[11], words[12], words[13])
        face3 = Face(3, words[14], words[15], words[16], words[17])
        face4 = Face(4, words[18], words[19], words[20], words[21])
        face5 = Face(5, words[22], words[23], words[24], words[25])
        blockBC = words[26]
        print 'Face 0', face0
        print 'Face 1', face1
        print 'Face 2', face2
        print 'Face 3', face3
        print 'Face 4', face4
        print 'Face 5', face5

        return b, [face0, face1, face2, face3, face4, face5], blockBC

    @staticmethod
    def parseBC(filename):
        bcMappings = dict()
        # read connectivity file
        f = open(filename)
        line = f.readline()
        i = 0
        while len(line) > 0:
            if "surf " in line and "label" in line:
                break
            line = f.readline()

        nrSurfaceLabels = int(line.split()[0])
        print "nrSurfaceLabels=", nrSurfaceLabels

        for i in range(0, nrSurfaceLabels):
            line = f.readline()
            name, surfaceId = line.split()
            surfaceId = int(surfaceId)
            bcMappings[surfaceId] = name

        f.close()
        return bcMappings
