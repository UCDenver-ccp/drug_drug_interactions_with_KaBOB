import os
import pandas as pd
import re
import urllib

from itertools import permutations
from time import sleep

CSV_RESULTS_FROM_KABOB = 'drug-drug-interactions.csv'
OUTPUT_FILE = 'RxNav_output.txt'
NOVEL_OUTPUT_FILE = 'RxNav_potentially_novel.txt'

o_file = open(OUTPUT_FILE, 'w')
novel_file = open(NOVEL_OUTPUT_FILE, 'w')

data_df = pd.read_csv(CSV_RESULTS_FROM_KABOB, usecols=[1, 4, 7], \
                        names=['drug1', 'pathway_step', 'drug2'], \
                        dtype={'drug1':'str', 'pathway_step':'str', 'drug2':'str'})
data_iter = data_df.itertuples()
for potential_inter in data_iter:
    drug1_rxcuis = []
    drug2_rxcuis = []

    drug1_ids = os.popen('curl --silent "https://rxnav.nlm.nih.gov/REST/drugs?name=%s" | xml fo | grep rxcui' % urllib.quote(potential_inter.drug1)).read()
    sleep(0.1)
    if drug1_ids != '\n' and drug1_ids != '':
        drug1_rxcuis = re.findall('.*>(\d+)<.*', drug1_ids)
    else:
        o_file.write('%s <-> %s (%s): UNKNOWN, no RxCUIs found for %s\n' % (potential_inter.drug1, potential_inter.drug2, potential_inter.pathway_step, potential_inter.drug1))
        continue

    drug2_ids = os.popen('curl --silent "https://rxnav.nlm.nih.gov/REST/drugs?name=%s" | xml fo | grep rxcui' % urllib.quote(potential_inter.drug2)).read()
    sleep(0.1)
    if drug2_ids != '\n' and drug2_ids != '':
        drug2_rxcuis = re.findall('.*>(\d+)<.*', drug2_ids)
    else:
        o_file.write('%s <-> %s (%s): UNKNOWN, no RxCUIs found for %s\n' % (potential_inter.drug1, potential_inter.drug2, potential_inter.pathway_step, potential_inter.drug2))
        continue

    pairings = [[zip(drug1_rxcuis, drug2_rxcui)] for drug2_rxcui in drug2_rxcuis]
    found = False
    for pair in pairings[0][0]:
        interactions = os.popen('curl --silent "https://rxnav.nlm.nih.gov/REST/interaction/list?rxcuis=%s+%s" | xml fo | grep description' % (pair[0], pair[1])).read()
        sleep(0.1)
        if interactions != '\n' and interactions != '':
            o_file.write('%s <-> %s (%s): Found at least one interaction\n' % (potential_inter.drug1, potential_inter.drug2, potential_inter.pathway_step))
            found = True
            continue
    if not found:
        o_file.write('%s <-> %s (%s): NO MENTIONS!!!!\n' % (potential_inter.drug1, potential_inter.drug2, potential_inter.pathway_step))
        novel_file.write('%s <-> %s (%s)\n' % (potential_inter.drug1, potential_inter.drug2, potential_inter.pathway_step))

o_file.close()
novel_file.close()
