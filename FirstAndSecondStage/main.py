import sys
import pandas as pd
import feedparser
import xml.sax.saxutils as saxutils
import ast
import re
from bs4 import BeautifulSoup
import requests
import crawlerFactChecking as fact
import csv
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

if sys.version_info[0] >= 3:
    import crawlerTwitterWeb as craw
else:
    sys.exit()

def main():
	#Imput parameters
	agencies = ["https://checamos.afp.com/rss/1558/rss.xml","https://aosfatos.org/noticias/feed/", "https://piaui.folha.uol.com.br/lupa/feed/"]
	virtualMedias = ["https://g1.globo.com/rss/g1/tecnologia/", "https://g1.globo.com/rss/g1/educacao/", "https://g1.globo.com/rss/g1/economia/","https://noticias.r7.com/feed.xml"]
	toprow = ['id','URL', 'Author', 'datePublished', 'claimReviewed', 'reviewBody', 'title', 'ratingValue', 'bestRating', 'alternativeName']
	newStopWords = ['#Verificamos:','Checamos','Agência','Lupa','Pública','Aos','Fatos','fatos','Fake','FAKE','fake',',',':',';','mentira','verdade','falso','.','O','A','Os','As','Em','Na', 'No', '|', 'G1', 'g1']
	language = 'portuguese'
	since = "2000-01-01"
	until = "2020-08-01"
	maxTweets = 10000
        
	#Stage 1 - Identify Labeled News
	fact.DataCollector.collect(agencies, virtualMedias, toprow)

	#Stage 2 - Connect News with Propagation
	dataset = pd.read_csv("./Dataset/LabeledNews.csv", index_col=0, header = 0)
	toprow = ['id','news_url','title','tweet_ids']
	stop_words = set(stopwords.words(language)) 
	stop_words = stop_words.union(newStopWords)
	newsListFake = []
	newsListNotFake = []	
	for index, row in dataset.iterrows():
		word_tokens = word_tokenize(row[3])   
		filtered_sentence = []   
		for w in word_tokens: 
			if w not in stop_words: 
				filtered_sentence.append(w)
		filtered_sentence = [ele for ele in filtered_sentence if not ele.startswith("'")]	
		query = "abcekrkrmmtre bcertkmrekd cderektmrelkm deflkermt efgerktmrelk fghkerltrlket ghilerkngtlekrntlke"
		if (len(filtered_sentence) >=  60):
			filtered_sentence = filtered_sentence[0:15]
			query = re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', str(filtered_sentence))
		elif (len(query) >=  30):
			filtered_sentence = filtered_sentence[0:10]
			query = re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', str(filtered_sentence))
		elif (len(query) >= 8):
			filtered_sentence = filtered_sentence[0:8]
			query = re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', str(filtered_sentence))

		print (query)

		#Searching in twitter
		tweetCriteria = craw.manager.TweetCriteria().setQuerySearch(query +" -fake -filter:replies").setSince(since).setUntil(until).setMaxTweets(maxTweets)
		tweets = craw.manager.TweetManager.getTweets(tweetCriteria)
		concTweet = ""
		aux = row[8]
		for tweet in tweets:
			if (concTweet != ""):
				concTweet = concTweet + str("\t") + str(tweet.id)
			else:
				concTweet = str(tweet.id)
			
		line = []			
		line.append(index)
		line.append(row[0])
		line.append(row[3])
		line.append(concTweet)
		if (aux.upper()=="FALSO"):
			newsListFake.append(line)
		elif (aux.upper()=="VERDADEIRO"):
			newsListNotFake.append(line)

	process2ResultFake = pd.DataFrame(newsListFake, columns=toprow)
	process2ResultNotFake = pd.DataFrame(newsListNotFake, columns=toprow)
	process2ResultFake = process2ResultFake.set_index('id')
	process2ResultNotFake = process2ResultNotFake.set_index('id')
	process2ResultFake.to_csv("./Dataset/News_fake.csv", encoding='utf-8-sig', index=True)
	process2ResultNotFake.to_csv("./Dataset/News_notFake.csv", encoding='utf-8-sig', index=True)

if __name__ == '__main__':
	main()
