#!/usr/bin/env python2.7
''' The routines used for analyzing queue trace file
'''
import os


def parse_line(line):
    """ Parse a queue trace line into a dict
    """
    line = line.split()
    result = {}
    if len(line) < 12:
        return result
    result["event"] = line[0]
    result["time"] = float(line[1])
    result["from"] = int(line[2])
    result["to"] = int(line[3])
    result["type"] = line[4]
    result["size"] = int(line[5])
    result["flags"] = line[6]
    result["fid"] = int(line[7])
    result["src"] = line[8]
    result["dst"] = line[9]
    result["seqnum"] = int(line[10])
    result["pktid"] = int(line[11])
    return result

def is_enqueue(record):
    if isinstance(record, dict):
        return record["event"] == "+"
    elif isinstance(record, str):
        return record.split()[0] == '+'
    else:
        return False

def is_drop(record):
    if isinstance(record, dict):
        return record["event"] == "d"
    elif isinstance(record, str):
        return record.split()[0] == 'd'
    else:
        return False

def ismatch(record, **kwargs):
    for key in kwargs:
        if (key in record) and (record[key] != kwargs[key]):
            return False
    return True

def get_dropping_rate(qfname, **kwargs):
    dnum, total = 0, 0
    with open(qfname) as ifp:
        for line in ifp:
            if line.lstrip()[0] == "#":
                continue
            record = parse_line(line)
            if len(record) == 0:
                continue
            if not ismatch(record, **kwargs):
                continue
            if is_enqueue(record):
                total += 1
            if is_drop(record):
                dnum += 1
    return 1.0 * dnum / total


def get_retrans_rate(qfname, **kwargs):
    rnum = len(get_retrans_from_file(qfname, **kwargs))
    total = len(get_enque(qfname, **kwargs))
    return 1.0 * rnum / total



def get_retrans_from_file(qfname, **kwargs):
    result = []
    snd_nxt = -1

    def ismatch(record):
        for key in kwargs:
            if (key in record) and (record[key] != kwargs[key]):
                return False
        return True

    with open(qfname) as ifp:
        for line in ifp:
            if line.lstrip()[0] == '#':
                continue
            record = parse_line(line)
            if len(record) == 0 or record["event"] != '+':
                continue
            if not ismatch(record):
                continue
            if snd_nxt == -1:
                snd_nxt = record["seqnum"] + 1
                continue
            if record["seqnum"] < snd_nxt:
                result.append(record)
            else:
                snd_nxt = record["seqnum"] + 1
    return result

def get_enque(fname, **kwargs):
    ''' Filter the queue trace file, only output enqueue trace

    Args:
       fname: queue trace file

    Returns:
        A list of enqueue records
    '''
    result = []
    with open(fname) as fp:
        for line in fp:
            record = parse_line(line)
            if len(record) == 0:
                continue
            if not ismatch(record, **kwargs):
                continue
            if is_enqueue(record):
                result.append(record)
    return result

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
