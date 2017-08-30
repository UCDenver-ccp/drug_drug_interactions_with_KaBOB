#RUNS A SPARQL QUERY AND SAVES THE RESULTS AS A JSON FILE

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import socket

# Set the connection timeout as needed (some of these queries can run for a long time)
timeout = 432000    # 5 days, in seconds
socket.setdefaulttimeout(timeout)

endpoint = SPARQLWrapper('http://amc-tantor.ucdenver.pvt:10035/repositories/kabob-dev')
endpoint.setCredentials(user='better', passwd='better')
endpoint.setReturnFormat(JSON)

q = '''PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX kro: <http://kabob.ucdenver.edu/ro/>
PREFIX kbio: <http://kabob.ucdenver.edu/bio/>
PREFIX iaoreactome: <http://kabob.ucdenver.edu/iao/reactome/>
PREFIX iaodrugbank: <http://kabob.ucdenver.edu/iao/drugbank/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX franzOption_memoryLimit: <franz:60g>
PREFIX franzOption_memoryExhaustionWarningPercentage: <franz:90.0>
PREFIX franzOption_clauseReorderer: <franz:identity>
PREFIX franzOption_chunkProcessingAllowed: <franz:yes>

select ?drug ?target_protein ?p ?other_target ?drug2 {
#  bind(iaodrugbank:DRUGBANK_DB00571_ICE as ?drug1_ice) . # bind propanolol ICE to drug1_ice
#  ?drug1_ice obo:IAO_0000219 ?drug .
  ?drug  rdfs:subClassOf obo:CHEBI_23888 .          # a drug
  ?drug_entity rdfs:subClassOf ?drug .

  ?r4 owl:someValuesFrom ?drug_entity .
  ?r4 rdf:type owl:Restriction .
# ?r4 owl:onProperty obo:RO_0000057 .

  ?i rdfs:subClassOf ?r4 .
  ?i rdfs:subClassOf obo:GO_0005488 .     # binding
  ?i rdfs:subClassOf obo:MI_0407 .        # direct interaction
  ?i rdfs:subClassOf ?r3 .
  ?r3 owl:onProperty obo:RO_0000057 .     # has participant
  ?r3 rdf:type owl:Restriction .
  ?r3 owl:someValuesFrom ?t .

  ?t rdfs:subClassOf ?target_protein .
  ?target_protein rdfs:subClassOf obo:CHEBI_36080 .
  ?mol_superclass rdfs:subClassOf ?target_protein .
  ?mol_superclass iaoreactome:connectsTo ?prot_fd .  # reactome protein file data

  ?some_molecule rdfs:subClassOf* ?mol_superclass .
  ?r2 owl:someValuesFrom ?some_molecule .
  ?r2 owl:onProperty obo:RO_0000057 .                 # find participants in this reaction
  ?r2 rdf:type owl:Restriction .
  ?pathway_step rdfs:subClassOf ?r2 .

  ?r1 owl:someValuesFrom ?pathway_step.               # find a step in this pathway, either a subpathway or a biochemical reaction
  ?r1 owl:onProperty kro:has_proper_part .
  ?r1 rdf:type owl:Restriction .
  ?p rdfs:subClassOf ?r1 .
  ?p iaoreactome:connectsTo ?p_record .               # find a reactome pathway
  ?p_record rdf:type iaoreactome:PathwayFileData .    # you may not need this part

  ?p rdfs:subClassOf ?r_part .
  ?r_part rdf:type owl:Restriction .
  ?r_part owl:onProperty kro:has_proper_part .
  ?r_part owl:someValuesFrom ?other_pathway_step .

  ?other_pathway_step rdfs:subClassOf ?r_part2 .
  ?r_part2 rdf:type owl:Restriction .
  ?r_part2 owl:onProperty obo:RO_0000057 .
  ?r_part2 owl:someValuesFrom ?other_molecule .
  ?other_molecule rdfs:subClassOf* ?other_target .
  ?other_target rdfs:subClassOf obo:CHEBI_36080 .

  ?t2 rdfs:subClassOf ?other_target .
  ?r_part3 owl:someValuesFrom ?t2 .
  ?r_part3 rdf:type owl:Restriction .
  ?r_part3 owl:onProperty obo:RO_0000057 .

  ?interaction rdfs:subClassOf ?r_part3 .
  ?interaction rdfs:subClassOf ?r_part4 .
  ?r_part4 rdf:type owl:Restriction .
  ?r_part4 owl:onProperty obo:RO_0000057 .
  ?r_part4 owl:someValuesFrom ?drug2_sc .
  ?drug2_sc rdfs:subClassOf ?drug2 .
  ?drug2 rdfs:subClassOf obo:CHEBI_23888 .

  FILTER (?drug != ?drug2)
#  ?drug2_ice obo:IAO_0000219 ?drug2 .
} '''

#QUERY RESULTS
endpoint.setQuery(q)
res_q = endpoint.query().convert() #run query

#save query to a json file
with open('drug_reactome_drug_results.json', 'w') as outfile:
    json.dump(res_q, outfile)
