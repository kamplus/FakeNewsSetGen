# Fact-checking collector
import pandas as pd
import feedparser
import xml.sax.saxutils as saxutils
import ast
import re
from bs4 import BeautifulSoup
from datetime import date
import requests
    
class DataCollector:

    def __init__(self):
        pass

    def loadFile(name):
        return pd.read_csv("./Dataset/" + name + ".csv", header = 0, index_col=False, sep=',')

    def collectLinksFromFeed(url):
        d = feedparser.parse(url)
        links = []
        for entry in d.entries: links.append(entry.link)
        return links

    def saveFile(data, name):
        data.to_csv("./Dataset/" + name + ".csv", encoding='utf-8-sig', index=False)

    def updateFile(oldFile, additions):
        temp = pd.concat([oldFile, additions], ignore_index=True)
        temp = temp.drop_duplicates(keep='first', subset=['claimReviewed'])
        count=1
        for index, row in temp.iterrows():
            temp.set_value(index,'id', count)
            count=count+1
        return temp
    
    def re_char(str):
        return re.sub('[^A-Za-z0-9 \!\@\#\$\%\&\*\:\,\.\;\:\-\_\"\'\]\[\}\{\+\á\à\é\è\í\ì\ó\ò\ú\ù\ã\õ\â\ê\ô\ç\|]+', '',str)

    def preProcessing(str):
        newString = saxutils.unescape(str.replace('&quot;', ''))
        newString = re.sub('[^A-Za-z0-9 \!\@\#\$\%\&\*\:\,\.\;\:\-\_\"\'\]\[\}\{\+\á\à\é\è\í\ì\ó\ò\ú\ù\ã\õ\â\ê\ô\ç\|]+', '',newString)
        newDict = ast.literal_eval(newString)
        if "@graph" in newDict:
            newDict = newDict['@graph'][0]        
        return newDict

    def collectData(url, type):
        response = requests.get(url, timeout=30)
        content = BeautifulSoup(response.content, "html.parser")
        allData = []
        if (type=="virtualMedia"):
            try:                
                element = []
                element.append("99999999")
                element.append(url)
                element.append("Mídia Convencional")
                element.append(date.today())
                element.append(DataCollector.re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
                element.append(DataCollector.re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
                element.append(DataCollector.re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
                element.append("6")
                element.append("5")
                element.append("VERDADEIRO")
                allData.append(element)
                return allData
            except:
                pass
        for claimReview in content.findAll('script', attrs={"type": "application/ld+json"}):
            element = []
            try:
                claimDict = DataCollector.preProcessing(claimReview.get_text(strip=True))
                element.append("99999999")
                element.append(url)
                element.append(claimDict['author']['url'])
                element.append(claimDict['datePublished'])
                if (claimDict['claimReviewed']):
                    element.append(claimDict['claimReviewed'])
                else:   
                    element.append(DataCollector.re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
                try: element.append(claimDict['reviewBody'])
                except:
                    try:
                        element.append(claimDict['description'])
                    except:
                        element.append('Empty')
                element.append(DataCollector.re_char(content.title.get_text().replace('<title>','').replace('</title>','')))
                element.append(claimDict['reviewRating']['ratingValue'])
                element.append(claimDict['reviewRating']['bestRating'])
                element.append(claimDict['reviewRating']['alternateName'])
                allData.append(element)
            except:
                pass
        return allData

    @staticmethod
    def collect(agencies, virtualMedias, toprow):
        
        linksAgenciesList = []
        linksVirtualMediasList = []
        for url in agencies: linksAgenciesList.extend(DataCollector.collectLinksFromFeed(url))
        for url in virtualMedias: linksVirtualMediasList.extend(DataCollector.collectLinksFromFeed(url))
        print ("Number of Agencies links: {}".format(len(linksAgenciesList)))
        print ("Number of Virtual Medias links: {}".format(len(linksVirtualMediasList)))

        claimList = []
        count = 0
        for url in linksAgenciesList:
            count = count + 1
            print ("{} de {} > ".format(count,len(linksAgenciesList)) + url)
            lineList = DataCollector.collectData(url,"agency")
            for line in lineList: claimList.append(line)
        count=0
        for url in linksVirtualMediasList:
            count = count + 1
            print ("{} de {} > ".format(count,len(linksVirtualMediasList)) + url)
            lineList = DataCollector.collectData(url,"virtualMedia")
            for line in lineList: claimList.append(line)
            
        additions = pd.DataFrame(claimList, columns=toprow)

        oldFile = DataCollector.loadFile('LabeledNews')
        process1Update = DataCollector.updateFile(oldFile, additions)
        DataCollector.saveFile(process1Update, 'LabeledNews')
        
