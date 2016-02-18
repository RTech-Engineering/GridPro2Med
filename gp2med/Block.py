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

from gp2med.Node import Node
import MEDCoupling as mc


class Block(object):

    def __init__(self, blockId, cellStart, nodeStart, I, J, K, args):
        self.blockId = blockId
        self.cellStart = cellStart
        self.nodeStart = nodeStart
        self.I = I
        self.J = J
        self.K = K
        self.Icell = I - 1
        self.Jcell = J - 1
        self.Kcell = K - 1
        self.BC = -1
        self.nodes = []
        self.args = args

    def __repr__(self):
        return repr(self.blockId)

    def getId(self):
        return self.blockId

    def getCellCount(self):
        return self.Icell * self.Jcell * self.Kcell

    def getUniqueNodeCount(self):
        count = 0
        for n in self.nodes:
            if n.equivalent is None:
                # node is unique
                count = count + 1
        return count

    def getNodeCount(self):
        return len(self.nodes)

    def setBC(self, BC):
        self.BC = BC

    def read(self, f):
        I = self.I
        J = self.J
        K = self.K
        # for 2D case we need to extrude one node in z direction
        is2D = (K == 1)

        print 'coarsen', self.args.coarse

        coarsenI = 1
        coarsenJ = 1
        coarsenK = 1
        if self.args.coarse > 1:
            print 'coarsen', self.args.coarse
            coarsenI = self.args.coarse
            coarsenJ = self.args.coarse
            coarsenK = self.args.coarse

        # limit the coarsenings until we reach the possible
        while coarsenI > 1 and (self.I - 1) % coarsenI != 0:
            coarsenI -= 1
        while coarsenJ > 1 and (self.J - 1) % coarsenJ != 0:
            coarsenJ -= 1
        while coarsenK > 1 and (self.K - 1) % coarsenK != 0:
            coarsenK -= 1

        print 'coarsening is ', coarsenI, coarsenJ, coarsenK

        for i in range(0, I):
            for j in range(0, J):
                for k in range(0, K):
                    isBoundary = ((I > 1 and (i == 0 or i == I - 1)) or
                                  (J > 1 and (j == 0 or j == J - 1)) or
                                  (K > 1 and (k == 0 or k == K - 1)))

                    line = f.readline()
                    x, y, z = line.split()
                    x = float(x)
                    y = float(y)
                    z = float(z)
                    # the id is build from local position and start of node
                    nodeId = len(self.nodes) + self.nodeStart
                    # append nodes locally
                    # skip storage of node base on coarsening
                    if (i % coarsenI == 0 and j % coarsenJ == 0 and
                       k % coarsenK == 0):
                        self.nodes.append(Node(x, y, z, isBoundary, nodeId))
                        if is2D:
                            self.nodes.append(
                                Node(
                                    x,
                                    y,
                                    z +
                                    self.args.extrude,
                                    isBoundary,
                                    nodeId))
        # recompute block size based on coarsening
        self.Icell = self.Icell / coarsenI
        self.Jcell = self.Jcell / coarsenJ
        self.Kcell = self.Kcell / coarsenK
        print 'cells now:', self.Icell, self.Jcell, self.Kcell
        self.I = self.Icell + 1
        self.J = self.Jcell + 1
        self.K = self.Kcell + 1
        if is2D:
            self.K = 2
            self.Kcell = 1

    def renumberNodes(self, count):
        for n in self.nodes:
            if n.equivalent is None:
                # node is unique
                n.setId(count)
                count = count + 1
            else:
                # node is equivalent to other one, we change the id
                n.setId(n.equivalent.getId())
        return count

    def addNodes(self, coords):
        # add nodes of current block to mesh
        # we add only the nodes which have no equivalence
        for n in self.nodes:
            if n.equivalent is None:
                coords.append(n.x)
                coords.append(n.y)
                coords.append(n.z)

    def getNode(self, i, j, k):
        J = self.J
        K = self.K
        localIndex = i * J * K + j * K + k

        return self.nodes[localIndex]

    def getNodeId(self, i, j, k):
        # create node index
        node = self.getNode(i, j, k)
        return node.getId()

    def addVolumeCells(self, mesh):
        Icell = self.Icell
        Jcell = self.Jcell
        Kcell = self.Kcell
        for k1 in range(0, Kcell):
            k2 = k1 + 1
            for j1 in range(0, Jcell):
                j2 = j1 + 1
                for i1 in range(0, Icell):
                    i2 = i1 + 1
                    conn = []
                    # order taken from Description du fichier de maillage de
                    # Code_Aster, Jacques PELLET U3.01.00
                    conn.append(self.getNodeId(i1, j1, k1))
                    conn.append(self.getNodeId(i2, j1, k1))
                    conn.append(self.getNodeId(i2, j2, k1))
                    conn.append(self.getNodeId(i1, j2, k1))
                    conn.append(self.getNodeId(i1, j1, k2))
                    conn.append(self.getNodeId(i2, j1, k2))
                    conn.append(self.getNodeId(i2, j2, k2))
                    conn.append(self.getNodeId(i1, j2, k2))
                    mesh.insertNextCell(mc.NORM_HEXA8, 8, conn)

    def getFaceCells(self, mesh, side):
        faceList = []
        direction = side / 2
        print 'getFaceCells ', side, direction
        if direction == 0:
            if side == 0:
                i = 0
            else:
                i = self.I - 1
            for k1 in range(0, self.Kcell):
                k2 = k1 + 1
                for j1 in range(0, self.Jcell):
                    j2 = j1 + 1
                    # order taken from Description du fichier de maillage de
                    # Code_Aster, Jacques PELLET U3.01.00
                    id1 = self.getNodeId(i, j1, k1)
                    id2 = self.getNodeId(i, j1, k2)
                    id3 = self.getNodeId(i, j2, k2)
                    id4 = self.getNodeId(i, j2, k1)
                    faceIds = mesh.getCellIdsFullyIncludedInNodeIds(
                        [id1, id2, id3, id4])
                    if len(faceIds) != 1:
                        print "Internal error occured"
                    faceList.append(faceIds[0])
        if direction == 1:
            if side == 2:
                j = 0
            else:
                j = self.J - 1
            for k1 in range(0, self.Kcell):
                k2 = k1 + 1
                for i1 in range(0, self.Icell):
                    i2 = i1 + 1
                    # order taken from Description du fichier de maillage de
                    # Code_Aster, Jacques PELLET U3.01.00
                    id1 = self.getNodeId(i1, j, k1)
                    id2 = self.getNodeId(i1, j, k2)
                    id3 = self.getNodeId(i2, j, k2)
                    id4 = self.getNodeId(i2, j, k1)
                    faceIds = mesh.getCellIdsFullyIncludedInNodeIds(
                        [id1, id2, id3, id4])
                    if len(faceIds) != 1:
                        print "Internal error occured"
                    faceList.append(faceIds[0])
        if direction == 2:
            if side == 4:
                k = 0
            else:
                k = self.K - 1
            for j1 in range(0, self.Jcell):
                j2 = j1 + 1
                for i1 in range(0, self.Icell):
                    i2 = i1 + 1
                    # order taken from Description du fichier de maillage de
                    # Code_Aster, Jacques PELLET U3.01.00
                    id1 = self.getNodeId(i1, j1, k)
                    id2 = self.getNodeId(i1, j2, k)
                    id3 = self.getNodeId(i2, j2, k)
                    id4 = self.getNodeId(i2, j1, k)
                    faceIds = mesh.getCellIdsFullyIncludedInNodeIds(
                        [id1, id2, id3, id4])
                    if len(faceIds) != 1:
                        print "Internal error occured"
                    faceList.append(faceIds[0])
        return faceList

    def outputNodes(self):
        for n in self.nodes:
            print n

    def countFaceCells(self, side):
        direction = side % 2
        if direction == 0:
            return self.Jcell * self.Kcell
        if direction == 1:
            return self.Icell * self.Kcell
        if direction == 2:
            return self.Icell * self.Jcell
