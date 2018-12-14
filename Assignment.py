__author__ = 'Wout'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib.request


nrOfDocs = 50
query = "house+concrete+wood"
query_for_code = "house concrete wood"



def create_url(query,method):
    webpage = 'http://api.nordlys.cc/er?'
    query = "q="+query
    amount = "&1st_num_docs="+str(nrOfDocs)
    method = '&model='+method
    url = webpage+query+amount+method

    req = urllib.request.Request(url,
                                 headers={'User-Agent': "Magic Browser"})
    webpage = urllib.request.urlopen(req)
    web_str = webpage.read().decode("utf-8")

    f = open("hallo" + ".txt", "w+")
    f.write(web_str)
    f.close()

create_url('house+concrete+wood', 'lm')





docList = [i for i in range(4*nrOfDocs+7)]
#print (docList)
for i in docList:
    if ((i%4 == 0 and i!= 0) and i != nrOfDocs*4+4):
        docList.remove(i)

#print(docList)

data = pd.read_csv('hallo.txt', delimiter='\n', header = None, skiprows=docList, names=['results'])
data['results'] = data['results'].str[17:-3]
#print (data)

queries = pd.read_csv(r'DBpedia-Entity/collection/v2/queries-v2.txt', sep='\t', header=None, names = ['query_ID', 'query'])

q = queries[queries['query']==query_for_code]
q = q.iloc[0]['query_ID']
print(q)


qrels = pd.read_csv('qrels-v2.txt', delim_whitespace=True, header = None, skiprows=docList, names=['ID', 'niks', 'naam', 'relevance'])

qrels = qrels.loc[qrels['ID'] == q]
optimalQrels = qrels
optimalQrels = optimalQrels.drop(columns=['ID', 'niks'])
#optimalQrels = optimalQrels['relevance'].astype(int)
optimalQrels= optimalQrels.sort_values(['relevance'], ascending=False)
optimalQrels = optimalQrels.head(nrOfDocs)
#print(optimalQrels.shape)


qrels = qrels.loc[qrels['naam'].isin(data['results'])]
qrels = qrels.drop(columns=['ID', 'niks'])
#print(qrels)

data['rel'] = 0
for i,result in enumerate(data['results']):
    for j,naam in enumerate( qrels['naam']):
        if(result == naam):
            data.at[i, 'rel'] = qrels.iloc[j]['relevance']
#data['rel'] = qrels['relevance']
data = data.drop(columns=['results'])
#data = np.array(data)
dcg = []
odcg = []
ndcg = []
for i,rel in enumerate(data['rel']):
    if(i==0):
        dcg.append(rel)
    else:
        dcg.append(dcg[-1] + rel/np.log(i+1))

for i,rel in enumerate(optimalQrels['relevance']):
    if(i==0):
        odcg.append(rel)
    else:
        odcg.append(odcg[-1] + rel/np.log(i+1))
#print(data)
print(dcg)
print(odcg)
for i in range(nrOfDocs):
    ndcg.append(dcg[i]/odcg[i])
print(ndcg)
plt.plot(range(nrOfDocs), ndcg)
plt.show()

