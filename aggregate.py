#!/usr/bin/env python3

import math
import sys
import csv
import collections

IMIN, IMAX = 0.5, 5.0

Item = collections.namedtuple('Item', 'x y i')

def aggregate(items):
    result = collections.defaultdict(int)
    for item in items:
        result[(item.x, item.y)] += item.i
    return sorted(Item(x,y,i) for (x,y),i in result.items())

def scale(items, imin, imax):
    if not items:
        return items

    smin = min(it.i for it in items)
    smax = max(it.i for it in items)
    return [
        Item(it.x, it.y, imin + (imax - imin) * (it.i - smin) / (smax - smin))
        for it in items
    ]

def write_output(fname, items):
    with open(fname, 'w') as f:
        cf = csv.DictWriter(f, fieldnames=[
            'Vertex 1', 'Vertex 2', 'Color', 'Width',
        ])
        cf.writeheader()
        for item in scale(aggregate(items), IMIN, IMAX):
            if item.i == 0:
                continue

            cf.writerow({
                'Vertex 1': item.x,
                'Vertex 2': item.y,
                'Color': 'Black',
                'Width': item.i,
            })

if __name__ == '__main__':
    root = sys.argv[1]

    items = []
    with open(root + '.csv') as f:
        cf = csv.DictReader(f)
        for row in cf:
            if not row['Pair'].strip():
                continue

            i = int(row.get('Proximity', row.get('Interaction')))
            try:
                x, y = row['Pair'].replace('Mr ', 'Mr').split()
            except ValueError as e:
                print(row['Pair'])
                raise e

            if x > y:
                x, y = y, x

            items.append(Item(x=x, y=y, i=i))

    DOM = 'Popeye'
    write_output(root + '-all.csv', items)
    write_output(root + '-dom-present.csv', filter(lambda it: DOM in it, items))
    write_output(root + '-dom-absent.csv', filter(lambda it: DOM not in it, items))
