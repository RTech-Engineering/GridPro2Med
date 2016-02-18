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


class Face(object):

    def __init__(self, side, faceType, indexSurface, neighbor, axisMap):
        self.side = side
        self.faceType = faceType
        self.indexSurface = int(indexSurface)
        self.bc = abs(self.indexSurface)
        self.neighbor = int(neighbor)
        self.axisMap = axisMap
        self.isInternal = faceType == 'b' or self.neighbor != 0
        self.isInternalSurface = self.isInternal and faceType == 's'
        self.isPeriodic = faceType == 'p'
        if indexSurface < 0:
            self.periodicSide = -1
        else:
            self.periodicSide = 1

    def __str__(self):
        return "type=" + self.faceType + " indexSurface= " + \
            repr(self.indexSurface) + " neighbor= " + \
            repr(self.neighbor) + " " + self.axisMap
