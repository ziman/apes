#!/usr/bin/env python3

import math
import sys
import csv
import collections

IMIN, IMAX = 0.5, 5.0

Item = collections.namedtuple('Item', 'x y i')
Group = collections.namedtuple('Group', 'loc items')

LOC = {'in': 'in', 'out': 'out', 'in/out': None}

def flatten(groups):
    return [i for g in groups for i in g.items]

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

def load_csv(fname):
    groups = []
    last_ts = None

    items = []
    loc = {}

    with open(root + '.csv') as f:
        cf = csv.DictReader(f)
        for row in cf:
            if not row['Pair'].strip():
                continue

            i = int(row.get('Proximity', row.get('Interaction')))
            if i == 0:
                continue  # skip zeroes

            try:
                x, y = map(str.strip, row['Pair'].replace('Mr ', 'Mr.').split())
            except ValueError as e:
                print(row['Pair'])
                raise e

            if x > y:
                x, y = y, x

            items.append(Item(x=x, y=y, i=i))

            cur_loc = LOC[row.get('Location', row.get('Position'))]
            loc[x] = cur_loc
            loc[y] = cur_loc

            cur_ts = row['Date'] + row['Time']
            if last_ts is None:
                last_ts = cur_ts
            elif cur_ts != last_ts:
                groups.append(Group(loc=loc, items=items))
                loc, items = {}, []
                last_ts = cur_ts
            else:
                pass # nothing to do

    return groups

def prune(dominant, groups, present):
    skipped = 0
    pruned_groups = []
    for group in groups:
        pruned_items = []
        dom_loc = group.loc.get(dominant)

        if dom_loc is None:
            relevance = sum(it.i for it in group.items)
            print('skipping %d items because %s is who knows where' % (relevance, dominant))
            skipped += relevance
            continue

        for item in group.items:
            int_loc = group.loc.get(item.x) or group.loc.get(item.y)
            if int_loc is None:
                print('skipping interaction %s-%s' % (item.x, item.y))
                skipped += 1
                continue

            if (int_loc == dom_loc) == present:
                pruned_items.append(item)

        if pruned_items:
            pruned_groups.append(Group(loc=group.loc, items=pruned_items))

    if skipped:
        print('--> total items skipped: %d' % skipped)

    return pruned_groups

if __name__ == '__main__':
    root = sys.argv[1]
    dominant = sys.argv[2]

    groups = load_csv(root + '.csv')

    write_output(root + '-all.csv', flatten(groups))
    write_output(root + '-dom-present.csv', flatten(prune(dominant, groups, present=True)))
    write_output(root + '-dom-absent.csv', flatten(prune(dominant, groups, present=False)))
