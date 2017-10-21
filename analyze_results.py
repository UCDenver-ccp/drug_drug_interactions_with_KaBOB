import pandas as pd
import numpy as np
import operator

from collections import Counter

df = pd.read_csv('drug-drug-interactions.csv', header=1, sep=",", usecols=[1,2,4,5,7], names=['d1','p1','p_step','p2','d2'], dtype={'d1':'str', 'p1':'str', 'p_step':'str', 'p2':'str', 'd2':'str'})

# distinct reactome pathway steps
p_steps = df.p_step.unique()
print len(p_steps)

# distinct drugs
d1s = df.d1.unique()
d2s = df.d2.unique()
ds = np.concatenate((d1s, d2s))
print len(set(ds))

counts = Counter(df.p_step)

nr_p450_steps = 0
for key in counts.keys():
    if 'CYP1' in key or 'CYP2' in key or 'CYP3' in key or 'CYPI' in key or 'P450' in key:
        print "%s\t%s" % (key, counts[key])
        nr_p450_steps += counts[key]
print nr_p450_steps

sorted_pairs = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
for pair in sorted_pairs:
    print '%s\t%s' % (pair[0], pair[1])

