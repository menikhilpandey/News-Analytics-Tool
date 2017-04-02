'''
Created on 19-Jul-2016

@author: Nikhil.Pandey
Process Crawled Data
'''
import pandas as pd
import RAKE as rk
import summarize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support

class keywordGen:
    def __init__(self, stoplist, csvfile):
        self.data = pd.read_csv(csvfile)
        self.stoplist = stoplist
        self.keywordsl = None
        self.process(self.data)
    
    def process(self, data):
        keywordlist=[]
        rake_object = rk.Rake(self.stoplist)
        datalist = data.apply(self.concatenateData, axis =1)
        for item in datalist:
            keywords = rake_object.run(item)
            MaxSumWeights = int(0.8*sum([i[1] for i in keywords]))
            coveredWeights = 0
            toAppend = []
            for item in keywords:
                if int(coveredWeights)<=MaxSumWeights:
                    toAppend.append(item[0])
                    coveredWeights+=item[1]
                else:
                    break
            keywordlist.append(','.join(toAppend))
        self.keywordsl=keywordlist
        
    
    def concatenateData(self,TrainData):
        return str(TrainData['ArticleTitle'])+str(TrainData['Summary'])+str(TrainData['ArticleStory'])

class summaryGen:
    def __init__(self, csvfile, maxsens):
        self.data = pd.read_csv(csvfile)
        self.maxsens = maxsens
        self.summaryl = None
        self.process(self.data, self.maxsens)
        
    def process(self, data, maxkeys):
        ss = summarize.SimpleSummarizer()
        summarylist=[]
        datalist = data.apply(self.concatenateData, axis =1)
        for item in datalist:
            summary = ss.summarize(item, self.maxsens)
            summarylist.append(summary)
        self.summaryl=summarylist
            
    def concatenateData(self,TrainData):
        return str(TrainData['ArticleTitle'])+str(TrainData['Summary'])+str(TrainData['ArticleStory'])


class Predictor:
    def __init__(self, trainFile, testfile):
        self.training_data = pd.read_csv(trainFile)
        self.test_data = pd.read_csv(testfile)
        self.score = None
        self.predictedlabels = None
        self.process(self.training_data, self.test_data)
        
    def process(self, training_data, test_data):
        text = training_data.apply(self.concatenateData, axis =1)
        labels = training_data['Label'].tolist()
        TextLabelTuple = zip(text,labels)
        pipeline = Pipeline([
                             ('vect', CountVectorizer(stop_words='english',ngram_range=(1,2))),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(class_weight='balanced')),
                             ])
        
        X_train = [item[0] for item in TextLabelTuple]
        Y_train = [item[1] for item in TextLabelTuple]
        X_test = test_data.apply(self.concatenateData, axis =1)
        Y_test = test_data["Label"].tolist()
        pipeline.fit(X_train,Y_train)
        predicted = pipeline.predict(X_test)
        self.score = precision_recall_fscore_support(predicted,Y_test)
        self.predictedlabels = predicted
        
    def concatenateData(self,TrainData):
        return str(TrainData['ArticleTitle'])+str(TrainData['Summary'])+str(TrainData['ArticleStory'])


if __name__ == '__main__':
    trainfile = 'D:/Projects/Darwin/TrainData.csv'
    inputfile = 'D:/Projects/Darwin/CrawlerOutput.csv'
    outputfile = 'D:/Projects/Darwin/Processed.csv'
    
    data = pd.read_csv(inputfile)
    predlabels = Predictor(trainfile,inputfile).predictedlabels
    data["PredictedLabels"]=predlabels
    
    stoplist = "D:/Projects/Darwin/KeywordStopList.txt"
    keywordslst = keywordGen(stoplist, inputfile).keywordsl
    data["Keywords"]= keywordslst
    
    # Number of sentences that need to be included in summary.
    maxsens =2
    summarylst = summaryGen(inputfile,maxsens).summaryl
    data["ArticleSummary"]=summarylst
    
    data.to_csv(outputfile)
