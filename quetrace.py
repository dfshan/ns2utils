#!/usr/bin/env python2.7
''' The routines used for analyzing queue trace file
'''
import os

def get_arate(fname, gran=1e-5):
    ''' Get arrival rate of a particular queue from ns2's queue trace file

    Args:
        fname: queue trace file name (just 1 queue)
        gran: sample interval when calculating throughput, in seconds

    Returns:
        A list, contains the data as: [(time, arriving rate), (time, arriving rate), ..., ]
        The arriving rate is in Mbps
    '''
    data = open(fname).readlines()
    data = [item.split() for item in data]
    etime = float(data[-1][1])
    num = int(etime/gran)
    res = [[i*gran, 0] for i in range(0, num+1)]
    for item in data:
        if item[0] != '+':
            continue
        time = float(item[1])
        size = int(item[5])
        res[int(time/gran)][1] += size
    return [(item[0], item[1]*8/gran/1000000) for item in res]

if __name__ == '__main__':
    arates = get_arate(r'ns2/que.tr')
    fp = open('ns2/throughput', 'w')
    for arate in arates:
        fp.write('%.6f %.6f\n' % (arate[0], arate[1]))
    fp.close()
