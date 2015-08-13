#!/usr/bin/env python3

import sys
import csv
import collections

Item = collections.namedtuple('Item', 'x y i')

def aggregate(items):
    result = collections.defaultdict(int)
    for item in items:
        result[(item.x, item.y)] += item.i
    return [Item(x,y,i) for (x,y),i in result.items()]

def write_output(fname, items):
    with open(fname, 'w') as f:
        cf = csv.DictWriter(f, fieldnames=[
            'Vertex 1', 'Vertex 2', 'Color', 'Width',
        ])
        cf.writeheader()
        for item in aggregate(items):
            if item.i == 0:
                continue

            cf.writerow({
                'Vertex 1': item.x,
                'Vertex 2': item.y,
                'Color': 'Black',
                'Width': item.i,
            })

if __name__ == '__main__':
    items = []
    with open(sys.argv[1]) as f:
        cf = csv.DictReader(f)
        for row in cf:
            if not row['Pair'].strip():
                continue

            x, y = row['Pair'].split()
            if x > y:
                x, y = y, x
            items.append(Item(
                x=x, y=y, i=int(row['Interaction'])
            ))

    DOM = 'Popeye'
    write_output('all.csv', items)
    write_output('dom-present.csv', filter(lambda it: DOM in it, items))
    write_output('dom-absent.csv', filter(lambda it: DOM not in it, items))
