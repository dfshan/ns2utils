#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' The routines used for analyzing queue trace file
'''


def parse_line(line):
    """ Parse a queue trace line into a dict
    """
    result = {}
    line = line.split()
    if len(line) < 5 or line[0][0] == "#":
        return result
    result["time"] = float(line[0])
    result["from"] = int(line[1])
    result["to"] = int(line[2])
    result["len_bytes"] = float(line[3])
    result["len_pkts"] = float(line[4])
    if len(line) < 11:
        return result
    result["arr_pkts"] = int(line[5])
    result["dep_pkts"] = int(line[6])
    result["drop_pkts"] = int(line[7])
    result["arr_bytes"] = int(line[8])
    result["dep_bytes"] = int(line[9])
    result["drop_bytes"] = int(line[10])
    return result
