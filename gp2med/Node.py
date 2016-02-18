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

import math
import sys
import traceback


class Node(object):

    def __init__(self, x, y, z, isBoundary, nodeId):
        self.nodeId = nodeId
        self.x = x
        self.y = y
        self.z = z
        self.isBoundary = isBoundary
        self.equivalent = None

    def __str__(self):
        return "Node id =" + repr(self.nodeId) + ", x=" + repr(self.x) + \
            ", y=" + repr(self.y) + ", z=" + repr(self.z)

    def setId(self, nodeId):
        self.nodeId = nodeId

    def getId(self):
        if self.equivalent is None:
            return self.nodeId
        else:
            return self.equivalent.getId()

    def getEquivalent(self):
        return self.equivalent

    def setEquivalent(self, n2):

        if n2 == self:
            print 'Internal error: trying to equivalence node with itself '
            traceback.print_stack()
            sys.exit(1)

        n1 = self
        while (n1.getEquivalent() is not None):
            n1 = n1.getEquivalent()

        if n1.nodeId > n2.nodeId:
            n1.equivalent = n2
        else:
            n2.equivalent = n1

    def distance(self, n2):
        dx = self.x - n2.x
        dy = self.y - n2.y
        dz = self.z - n2.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)
