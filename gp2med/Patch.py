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

# from Block import Block
import sys


def sgn(x):
    if x > 2:
        return -1
    else:
        return 1


def side(x, y):
    if x % 3 == y:
        return 1
    else:
        return 0


class Patch(object):

    def __init__(self, bc, hostBlock, hostFace, donorBlock,
                 orientation, isPeriodic, periodicSide):
        self.bc = bc
        self.hostBlock = hostBlock
        # 0 .. 5: imin, imax, jmin, jmax, kmin, kmax
        self.hostFace = hostFace
        self.donorBlock = donorBlock
        self.orientation = orientation
        self.isPeriodic = isPeriodic
        self.periodicSide = periodicSide
        self.isInternal = (self.bc == 0)
        # preparation
        self.direction = hostFace / 2  # IDIR, JDIR, KDIR = 0, 1, 2
        # maximum number of cells
        Imax = hostBlock.I - 1
        Jmax = hostBlock.J - 1
        Kmax = hostBlock.K - 1

        lowDonor = [0, 0, 0]
        highDonor = [Imax, Jmax, Kmax]
        if hostFace == 0:
            lowHost = [0, 0, 0]
            highHost = [0, Jmax, Kmax]
#            nrFaces = Jmax * Kmax
        if hostFace == 1:
            lowHost = [Imax, 0, 0]
            highHost = [Imax, Jmax, Kmax]
#            nrFaces = Jmax * Kmax
        if hostFace == 2:
            lowHost = [0, 0, 0]
            highHost = [Imax, 0, Kmax]
#            nrFaces = Imax * Kmax
        if hostFace == 3:
            lowHost = [0, Jmax, 0]
            highHost = [Imax, Jmax, Kmax]
#            nrFaces = Imax * Kmax
        if hostFace == 4:
            lowHost = [0, 0, 0]
            highHost = [Imax, Jmax, 0]
#            nrFaces = Imax * Jmax
        if hostFace == 5:
            lowHost = [0, 0, Kmax]
            highHost = [Imax, Jmax, Kmax]
#            nrFaces = Imax * Jmax

        if self.isPeriodic or self.isInternal:
            # other (positive direction) is determined by examining
            # the orientation:
            # convert char to integer
            # the string in the blk.tmp.conn file has value from 1-6 for the
            # orientation, in character form
            # the orientationValue we want to be in  the range 0-5, so we
            # extract one from the converted value
            orientationVal = int(orientation[self.direction]) - 1

            otherDir = (orientationVal % 3)  # [0 .. 2: i,j,k]

            if orientationVal <= 2:
                if hostFace == 0 or hostFace == 2 or hostFace == 4:
                    donorFace = 2 * otherDir + 1
                else:
                    donorFace = 2 * otherDir

            else:  # the indices are opposite:
                if hostFace == 0 or hostFace == 2 or hostFace == 4:
                    donorFace = 2 * otherDir
                else:
                    donorFace = 2 * otherDir + 1

            # now we fill the 3x3 tranformation matrix A.
            # A is used to compute the donor block local indices (id, jd, kd)
            # as a function of the host block indices (i,j,k) as in:

            a = int(orientation[0]) - 1  # range [0..5] meaning i,j,k,-i,-j,-k
            b = int(orientation[1]) - 1  # range [0..5] meaning i,j,k,-i,-j,-k
            c = int(orientation[2]) - 1  # range [0..5] meaning i,j,k,-i,-j,-k

            A = [[0] * 3] * 3
            A[0][0] = sgn(a) * side(a, 0)
            A[0][1] = sgn(b) * side(b, 0)
            A[0][2] = sgn(c) * side(c, 0)
            A[1][0] = sgn(a) * side(a, 1)
            A[1][1] = sgn(b) * side(b, 1)
            A[1][2] = sgn(c) * side(c, 1)
            A[2][0] = sgn(a) * side(a, 2)
            A[2][1] = sgn(b) * side(b, 2)
            A[2][2] = sgn(c) * side(c, 2)

            if donorFace == 0 or donorFace == 1:
                if donorFace == 1:
                    lowDonor[0] = donorBlock.I - 1
            else:
                if A[0][0] + A[0][1] + A[0][2] < 0:
                    lowDonor[0] = donorBlock.I - 1

            if donorFace == 2 or donorFace == 3:
                if donorFace == 3:
                    lowDonor[1] = donorBlock.J - 1
            else:
                if A[1][0] + A[1][1] + A[1][2] < 0:
                    lowDonor[1] = donorBlock.J - 1

            if donorFace == 4 or donorFace == 5:
                if donorFace == 5:
                    lowDonor[2] = donorBlock.K - 1
            else:
                if A[2][0] + A[2][1] + A[2][2] < 0:
                    lowDonor[2] = donorBlock.K - 1

            highDonor[0] = (lowDonor[0] + A[0][0] *
                            (highHost[0] - lowHost[0]) + A[0][1] * (
                             highHost[1] - lowHost[1]) + A[0][2] * (
                             highHost[2] - lowHost[2]))
            highDonor[1] = (lowDonor[1] + A[1][0] *
                            (highHost[0] - lowHost[0]) + A[1][1] * (
                             highHost[1] - lowHost[1]) + A[1][2] * (
                             highHost[2] - lowHost[2]))
            highDonor[2] = (lowDonor[2] + A[2][0] *
                            (highHost[0] - lowHost[0]) + A[2][1] * (
                             highHost[1] - lowHost[1]) + A[2][2] * (
                             highHost[2] - lowHost[2]))

            # print "The lowDonor is ", lowDonor , " and highDonor is " ,
            # highDonor

            # store in class variable
            self.lowHost = lowHost
            self.highHost = highHost
            self.lowDonor = lowDonor
            self.highDonor = highDonor
            self.A = A

            n1 = hostBlock.getNode(lowHost[0], lowHost[1], lowHost[2])
            n2 = donorBlock.getNode(lowDonor[0], lowDonor[1], lowDonor[2])
            distance = n1.distance(n2)

            if distance > 1e-6:
                print 'Problems !!!!!'
                print "Node 1: ", n1
                print "Node 2: ", n2
                sys.exit(1)

    def __repr__(self):
        return "Patch hostBlock" + \
            repr(self.hostBlock) + " host face " + \
            repr(self.hostFace) + " BC " + repr(self.bc)

    def getBC(self):
        return self.bc

    def countBC(self, BC):
        # TODO
        return 0

    def makeNodesUnique(self):
        if not self.isInternal:
            return

        lowHost = self.lowHost
        highHost = self.highHost
        lowDonor = self.lowDonor
#        highDonor = self.highDonor
        A = self.A

        for k in range(lowHost[2], highHost[2] + 1):
            for j in range(lowHost[1], highHost[1] + 1):
                for i in range(lowHost[0], highHost[0] + 1):
                    hostNode = self.hostBlock.getNode(i, j, k)
                    idonor = (lowDonor[0] + A[0][0] * (i - lowHost[0]) +
                              A[0][1] * (j - lowHost[1]) +
                              A[0][2] * (k - lowHost[2]))
                    jdonor = (lowDonor[1] + A[1][0] * (i - lowHost[0]) +
                              A[1][1] * (j - lowHost[1]) +
                              A[1][2] * (k - lowHost[2]))
                    kdonor = (lowDonor[2] + A[2][0] * (i - lowHost[0]) +
                              A[2][1] * (j - lowHost[1]) +
                              A[2][2] * (k - lowHost[2]))
                    donorNode = self.donorBlock.getNode(idonor, jdonor, kdonor)

                    if hostNode.nodeId < donorNode.nodeId:
                        donorNode.setEquivalent(hostNode)

        return
