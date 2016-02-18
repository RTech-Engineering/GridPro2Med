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

import sys
from gp2med.Block import Block
from gp2med.Patch import Patch
from gp2med.InputError import InputError
from gp2med.Connectivity import Connectivity
import MEDLoader as ml


def getLine(f):
    while True:
        line = f.readline()
        if len(line) == 0 or line[0] != "#":
            break
    return line


class MultiBlock(object):

    def __init__(self):
        self.blocks = []
        self.patches = []

    def readGridPro(self, filename, args):
        blockCount = 0
        cellCount = 0
        nodeCount = 0
        # read grid file
        f = open(filename)
        line = getLine(f)

        while len(line) > 0:
            print line
            I, J, K = line.split()
            I = int(I)
            J = int(J)
            K = int(K)
            b = Block(blockCount, cellCount, nodeCount, I, J, K, args)
            b.read(f)
            self.blocks.append(b)
            line = getLine(f)

            # increment blck blockCount
            blockCount = blockCount + 1
            cellCount = cellCount + b.getCellCount()
            nodeCount = nodeCount + b.getNodeCount()
        f.close()
        print len(self.blocks)

        # read BC into a dictionary "id, name"
        self.bcMappings = Connectivity.parseBC(filename + ".conn")

        # read connectivity file
        f = open(filename + ".conn")
        line = getLine(f)
        checkNumberBlocks = int(line.split()[0])
        if (checkNumberBlocks != len(self.blocks)):
            # TODO InputError class
            raise InputError("The number of blocks in the connectivity file \
            does not match the number of blocks in the grid file " + filename)

        for n in range(0, len(self.blocks)):
            line = getLine(f)
            b, faces, blockBC = Connectivity().convertLine(line)
            # we cound b from 0, in file from 1....
            b = int(b) - 1
            self.blocks[b].setBC(blockBC)
            for face in faces:
                print face
                bc = face.bc
                if face.isPeriodic or face.isInternal:
                    if face.isPeriodic:
                        print 'Periodic BC not treated yet'
                        sys.exit(1)
                    else:
                        print("create Internal Patch ",
                              face.isPeriodic, face.isInternal)
                        patch = Patch(
                            0,
                            self.blocks[n],
                            face.side,
                            self.blocks[
                                face.neighbor - 1],
                            face.axisMap,
                            face.isPeriodic,
                            face.periodicSide)
                else:  # external BC
                    print("create External Patch ",
                          face.isPeriodic, face.isInternal, face.side)
                    patch = Patch(
                        face.indexSurface,
                        self.blocks[n],
                        face.side,
                        None,
                        "123",
                        False,
                        0)
                    # add to BC map if it the id is not found
                    if bc in self.bcMappings:
                        print("The boundary condition for surface ",
                              bc, " is ", self.bcMappings[bc])
                    else:
                        self.bcMappings[bc] = "surface-%03d" % bc
                self.patches.append(patch)
        f.close()

        # unify the nodes between connected blocks
        # an equivalence is made, nodes with equivalent nodes are eliminated
        # and their IDs replace by the equivalent node
        for p in self.patches:
            p.makeNodesUnique()

        print "Number of cells = ", self.getTotalCells()
        print "Number of nodes = ", self.getTotalNodes()
        print "Number of unique nodes = ", self.getTotalUniqueNodes()

        # renumber node indices
        count = 0
        for b in self.blocks:
            count = b.renumberNodes(count)

    def getTotalCells(self):
        count = 0
        for b in self.blocks:
            count = count + b.getCellCount()
        return count

    def getTotalNodes(self):
        count = 0
        for b in self.blocks:
            count = count + b.getNodeCount()
        return count

    def getTotalUniqueNodes(self):
        count = 0
        for b in self.blocks:
            count = count + b.getUniqueNodeCount()
        return count

    def writeMED(self, filename):
        volumeMesh = ml.MEDCouplingUMesh("filename", 3)
        # get total size
        nCells = self.getTotalCells()
        nNodes = self.getTotalUniqueNodes()
        print "writing ", nCells, " cells and  ", nNodes, " nodes"
        # allocate nodes and cells

        # add all unique nodes to the mesh structure
        coords = []
        for b in self.blocks:
            b.addNodes(volumeMesh, coords)

        coordsArr = ml.DataArrayDouble(coords, nNodes, 3)
        volumeMesh.setCoords(coordsArr)

        # add all the volumeCells to the mesh structure
        volumeMesh.allocateCells(nCells)
        for b in self.blocks:
            b.addVolumeCells(volumeMesh)
        volumeMesh.finishInsertingCells()

        # create the 2D mesh
        surfaceMesh, desc, descIndx, revDesc, revDescIndx = \
            volumeMesh.buildDescendingConnectivity()

        mm = ml.MEDFileUMesh()
        mm.setMeshes([volumeMesh, surfaceMesh])

        # add the boundary conditions
        # loop over bcMappings
        groups = []
        print "add the boundary conditions"
        print self.bcMappings
        for bcMap in self.bcMappings:
            print "adding", bcMap, self.bcMappings[bcMap]
            # loop over patches that contain the key
            faceIds = []
            for p in self.patches:
                b = p.hostBlock
                if p.bc == bcMap:
                    print("CHECK bc matches", bcMap, p.bc,
                          "block: ", b,
                          "face:", p.hostFace)
                    faceIds = faceIds + b.getFaceCells(surfaceMesh, p.hostFace)

            print("contains ", len(faceIds), "nodes")
            # create a group with the face ids
            group = ml.DataArrayInt(faceIds)
            group.setName(self.bcMappings[bcMap])
            # add to the list of groups
            groups.append(group)

        mm.setGroupsAtLevel(-1, groups)
        print("Finally writing the file")

        # write volumeMesh structure to file
        ml.MEDLoader.WriteUMesh(filename, volumeMesh, True)

        # write all meshes to file
        # 2 means we overwrite the file
        mm.write(filename, 2)
