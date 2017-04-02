'''
Created on 18-Jul-2016

@author: Nikhil.Pandey
Crawler Update
'''

import logging
import re
import os
import pandas as pd
import feedparser as fd
import csv
import time
from goose import Goose
from datetime import datetime

class Crawl:
        
    def __init__(self, inputfile, outputfile, logfile, errorSites, lastSite, articleLog):
        logging.basicConfig(filename=logfile, level=logging.INFO)
        self.ferror = open(errorSites, 'a')
        self.articleLog = articleLog
        self.lastSite = lastSite
        self.outputfile = outputfile
        self.Sites = pd.read_csv(inputfile)["Links"].tolist()
        self.Tags = pd.read_csv(inputfile)["Type"].tolist()
        self.process(self.Sites)
        
    def clean(self, text):
        return ''.join([i if ord(i) < 128 else ' ' for i in text])
    
    def process(self, Sites):
        for index in range(len(Sites)):
            site = Sites[index]
            tag = self.Tags[index]
            logging.info(str(datetime.now()) + " Processing Site " + self.clean(site))
            try:
                entries = fd.parse(site).entries
                pattern = re.compile(u'<\/?\w+\s*[^>]*?\/?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
                for entry in entries:
                    title = "NA"
                    description = "NA"
                    link = "NA"
                    published = "NA"
                    articleContent = "NA"
                    category = "NA"
                    if "published" in entry:
                        published = self.clean(entry['published']) 
                    if "title" in entry:
                        title = self.clean(entry['title'])
                    if "description" in entry:
                        description = pattern.sub(u" " , self.clean(entry['description']))
                    if "category" in entry:
                        category = self.clean(entry['category'])
                    if "link" in entry:
                        link = self.clean(entry['link'])
                        try:
                            gooseObj = Goose()
                            article = gooseObj.extract(url=link)
                            articleContent = self.clean(article.title) + self.clean(article.cleaned_text)
                        except:
                            articleContent = ' '
                    entry_value_list = [title, description , link , published , category , articleContent, tag]
                    
                    if not os.path.isfile(self.outputfile):
                        with open(self.outputfile, 'ab') as csvFile:
                            csvWriter = csv.writer(csvFile, delimiter="," , quotechar='"', quoting=csv.QUOTE_ALL)
                            csvWriter.writerow(["ArticleTitle", "Summary", "Link", "Timestamp", "Category", "ArticleStory", "Label"])

                    with open(self.outputfile, 'ab') as csvFile:
                        csvWriter = csv.writer(csvFile, delimiter="," , quotechar='"', quoting=csv.QUOTE_ALL)
                        csvWriter.writerow(entry_value_list)
                    logging.info(str(datetime.now()) + ' Successfully Processed ' + self.clean(site))
            except:
                logging.info(str(datetime.now()) + ' Failed Processing ' + self.clean(site))
                self.ferror.write(str(datetime.now()) + ' Failed Processing ' + self.clean(site) + '\n')
            finally:
                with open(self.lastSite, 'w') as flast:
                    flast.write(str(datetime.now()) + ' Last Processed Site ' + self.clean(site) + '\n')
        self.ferror.close()
        
        
if __name__ == '__main__':
    
    while True:
        inputf = "D:/Projects/Darwin/InputSites.csv"
        outputf = "D:/Projects/Darwin/CrawlerOutput.csv" 
        logf = "D:/Projects/Darwin/Log Data/mainLogger.log"
        errorf = "D:/Projects/Darwin/Log Data/ErrorSites.log" 
        lastf = "D:/Projects/Darwin/Log Data/LastSite.log"
        articlef = "D:/Projects/Darwin/Log Data/ArticleLogger.log"
        Crawl(inputf, outputf, logf, errorf, lastf, articlef)
        timegap = (18 * 60 * 60)  # Sleep for 18 Hours 
        time.sleep(timegap)
