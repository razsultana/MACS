# Time-stamp: <2011-03-22 17:06:58 Tao Liu>

"""Module Description

Copyright (c) 2008 Tao Liu <taoliu@jimmy.harvard.edu>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included with
the distribution).

@status:  experimental
@version: $Revision$
@author:  Tao Liu
@contact: taoliu@jimmy.harvard.edu
"""

# ------------------------------------
# python modules
# ------------------------------------
import os
import sys
import re
import shutil
from MACS14.IO.cFeatIO import WigTrackI
from MACS14.IO.BinKeeper import BinKeeperI

import time
# ------------------------------------
# constants
# ------------------------------------

# ------------------------------------
# Misc functions
# ------------------------------------

# ------------------------------------
# Classes
# ------------------------------------

class WiggleIO:
    """File Parser Class for Wiggle File.

    Note: Only can be used with the wiggle file generated by pMA2C or
    MACS. This module can not be univerally used.

    Note2: The positions in Wiggle File must be sorted for every
    chromosome.

    Example:
    >>> from Cistrome.CoreLib.Parser import WiggleIO
    >>> w = WiggleIO('sample.wig')
    >>> bk = w.build_binKeeper()
    >>> wtrack = w.build_wigtrack()    
    """
    def __init__ (self,f):
        """f must be a filename or a file handler.
        
        """
        if type(f) == str:
            self.fhd = open(f,"r")
        elif type(f) == file:
            self.fhd = f
        else:
            raise Exception("f must be a filename or a file handler.")

    def build_wigtrack (self):
        """Use this function to return a WigTrackI.

        """
        data = WigTrackI()
        add_func = data.add_loc
        chrom = "Unknown"
        span = 0
        pos_fixed = 0      # pos for fixedStep data 0: variableStep, 1: fixedStep
        for i in self.fhd:
            if i.startswith("track"):
                continue
            elif i.startswith("#"):
                continue
            elif i.startswith("browse"):
                continue
            elif i.startswith("variableStep"): # define line
                pos_fixed = 0
                chromi = i.rfind("chrom=")  # where the 'chrom=' is
                spani = i.rfind("span=")   # where the 'span=' is
                if chromi != -1:
                    chrom = i[chromi+6:].strip().split()[0]
                else:
                    chrom = "Unknown"
                if spani != -1:
                    span = int(i[spani+5:].strip().split()[0])
                else:
                    span = 0
            elif i.startswith("fixedStep"):
                chromi = i.rfind("chrom=")  # where the 'chrom=' is
                starti = i.rfind("start=")  # where the 'chrom=' is
                stepi = i.rfind("step=")  # where the 'chrom=' is
                spani = i.rfind("span=")   # where the 'span=' is
                if chromi != -1:
                    chrom = i[chromi+6:].strip().split()[0]
                else:
                    raise Exception("fixedStep line must define chrom=XX")
                if spani != -1:
                    span = int(i[spani+5:].strip().split()[0])
                else:
                    span = 0
                if starti != -1:
                    pos_fixed = int(i[starti+6:].strip().split()[0])
                    if pos_fixed < 1:
                        raise Exception("fixedStep start must be bigger than 0!")
                else:
                    raise Exception("fixedStep line must define start=XX")
                if stepi != -1:
                    step = int(i[stepi+5:].strip().split()[0])
                else:
                    raise Exception("fixedStep line must define step=XX!")
            else:                       # read data value
                if pos_fixed:           # fixedStep
                    value = i.strip()
                    add_func(chrom,int(pos_fixed),float(value))
                    pos_fixed += step
                else:                   # variableStep
                    try:
                        (pos,value) = i.split()
                    except ValueError:
                        print i,pos_fixed
                    add_func(chrom,int(pos),float(value))
        data.span = span
        self.fhd.seek(0)
        return data

    def build_binKeeper (self,chromLenDict={},binsize=200):
        """Use this function to return a dictionary of BinKeeper
        objects.

        chromLenDict is a dictionary for chromosome length like

        {'chr1':100000,'chr2':200000}

        bin is in bps. for detail, check BinKeeper.
        """
        data = {}
        chrom = "Unknown"
        pos_fixed = 0
        for i in self.fhd:
            if i.startswith("track"):
                continue
            elif i.startswith("browse"):
                continue
            elif i.startswith("#"):
                continue
            elif i.startswith("variableStep"): # define line
                pos_fixed = 0
                chromi = i.rfind("chrom=")  # where the 'chrom=' is
                spani = i.rfind("span=")   # where the 'span=' is
                if chromi != -1:
                    chrom = i[chromi+6:].strip().split()[0]
                else:
                    chrom = "Unknown"
                if spani != -1:
                    span = int(i[spani+5:].strip().split()[0])
                else:
                    span = 0

                chrlength = chromLenDict.setdefault(chrom,250000000) + 10000000
                data.setdefault(chrom,BinKeeperI(binsize=binsize,chromosomesize=chrlength))
                add = data[chrom].add

            elif i.startswith("fixedStep"):
                chromi = i.rfind("chrom=")  # where the 'chrom=' is
                starti = i.rfind("start=")  # where the 'chrom=' is
                stepi = i.rfind("step=")  # where the 'chrom=' is
                spani = i.rfind("span=")   # where the 'span=' is
                if chromi != -1:
                    chrom = i[chromi+6:].strip().split()[0]
                else:
                    raise Exception("fixedStep line must define chrom=XX")
                if spani != -1:
                    span = int(i[spani+5:].strip().split()[0])
                else:
                    span = 0
                if starti != -1:
                    pos_fixed = int(i[starti+6:].strip().split()[0])
                    if pos_fixed < 1:
                        raise Exception("fixedStep start must be bigger than 0!")
                else:
                    raise Exception("fixedStep line must define start=XX")
                if stepi != -1:
                    step = int(i[stepi+5:].strip().split()[0])
                else:
                    raise Exception("fixedStep line must define step=XX!")
                chrlength = chromLenDict.setdefault(chrom,250000000) + 10000000
                data.setdefault(chrom,BinKeeperI(binsize=binsize,chromosomesize=chrlength))
                
                add = data[chrom].add

            else:                       # read data value
                if pos_fixed:           # fixedStep
                    value = i.strip()
                    add(int(pos_fixed),float(value))
                    pos_fixed += step
                else:                   # variableStep
                    try:
                        (pos,value) = i.split()
                    except ValueError:
                        print i,pos_fixed
                    add(int(pos),float(value))

        self.fhd.seek(0)
        return data

