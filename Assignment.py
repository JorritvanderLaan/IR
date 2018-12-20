__author__ = 'Wout'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib.request


nrOfDocs = 20

# Splitting the queries in the four categories.

query_for_code_List = pd.read_csv('queries-v2.txt', delimiter='\t', header = None, names=['ID', 'queryNames'])
INEX_query_for_code_List = query_for_code_List[query_for_code_List['ID'].str.contains("INEX_LD")].drop(columns=['ID']).reset_index(drop=True)
SemSearch_query_for_code_List = query_for_code_List[query_for_code_List['ID'].str.contains("SemSearch_ES")].drop(columns=['ID']).reset_index(drop=True)
QALD2_query_for_code_List = query_for_code_List[query_for_code_List['ID'].str.contains("QALD2")].drop(columns=['ID']).dropna().reset_index(drop=True)
ListSearch_query_for_code_List = query_for_code_List[query_for_code_List['ID'].str.contains("INEX_XER|SemSearch_LS|TREC")].drop(columns=['ID']).reset_index(drop=True)

# Replace spaces with '+'.

INEX_queryList = INEX_query_for_code_List.replace(' ', '+', regex=True)
SemSearch_queryList = SemSearch_query_for_code_List.replace(' ', '+', regex=True)
QALD2_queryList = QALD2_query_for_code_List.replace(' ', '+', regex=True)
ListSearch_queryList = ListSearch_query_for_code_List.replace(' ', '+', regex=True)


# Function which uses restful API to get search results, and saves it to a txt file.

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


def doStuff(query_for_code):

    # Remove lines from txt file we do not need
    docList = [i for i in range(4*nrOfDocs+7)]
    for i in docList:
        if ((i%4 == 0 and i!= 0) and i != nrOfDocs*4+4):
            docList.remove(i)


    # Read results into dataframe
    data = pd.read_csv('hallo.txt', delimiter='\n', header = None, skiprows=docList, names=['results'])
    data['results'] = data['results'].str[17:-3]

    # Get code corresponding to query
    queries = pd.read_csv('queries-v2.txt', sep='\t', header=None, names = ['query_ID', 'query'])

    q = queries[queries['query']==query_for_code]
    q = q.iloc[0]['query_ID']

    qrels = pd.read_csv('qrels-v2.txt', delim_whitespace=True, header = None, skiprows=docList, names=['ID', 'niks', 'naam', 'relevance'])

    # Get all labeled results
    qrels = qrels.loc[qrels['ID'] == q]

    optimalQrels = qrels
    optimalQrels = optimalQrels.drop(columns=['ID', 'niks'])
    optimalQrels= optimalQrels.sort_values(['relevance'], ascending=False)
    if len(optimalQrels['relevance']) >= nrOfDocs:
        optimalQrels = optimalQrels.head(nrOfDocs)

    qrels = qrels.loc[qrels['naam'].isin(data['results'])]
    qrels = qrels.drop(columns=['ID', 'niks'])

    data['rel'] = 0
    for i,result in enumerate(data['results']):
        for j,naam in enumerate(qrels['naam']):
            if(result == naam):
                data.at[i, 'rel'] = qrels.iloc[j]['relevance']
            # else:
            #     data.at[i,'rel'] = 0


    data = data.drop(columns=['results'])

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

    if len(odcg)<nrOfDocs:
        for i in range(nrOfDocs-len(odcg)):
            odcg.append(odcg[-1])

    for i in range(nrOfDocs):
        ndcg.append(dcg[i]/odcg[i])

    return ndcg


def test(queryCategory, query_for_code_category, method):

    average_ndcg = []
    for i, query in enumerate(queryCategory['queryNames']):
        query_for_code = query_for_code_category['queryNames'][i]
        #query = queryCategory['queryNames'][i]
        create_url(query, method)
        result = doStuff(query_for_code)
        average_ndcg.append(result)
        print(i)
    #print('mean = ',np.mean(average_ndcg, axis=0))
    #print('standard deviation = ',np.std(average_ndcg, axis=0))
    return average_ndcg

print('INEX:')
#Inex = test(INEX_queryList, INEX_query_for_code_List, 'lm')
# print('SemSearch:')
# SemSearch = test(SemSearch_queryList, SemSearch_query_for_code_List, 'lm')
# print('Qald2:')
# QALD = test(QALD2_queryList, QALD2_query_for_code_List, 'lm')
# print('ListSearch:')
# ListSearch = test(ListSearch_queryList, ListSearch_query_for_code_List, 'lm')

#print(Inex)


Inex = np.array(Inex)
mean = np.mean(Inex,axis=0)
std = np.std(Inex,axis=0)

print(mean)
print(std)

plt.plot(range(nrOfDocs),mean)
plt.show()
