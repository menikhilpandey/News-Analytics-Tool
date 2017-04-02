'''
Created on 18-Aug-2016

@author: Nikhil.Pandey
Multi Industry Classifier
'''
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

class Classifier:
    def __init__(self,trainFile,testFile,outputfile):
        self.pipeline = Pipeline([
                             ('vect', CountVectorizer(stop_words='english',ngram_range=(1,2))),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(class_weight='balanced')),
                             ])
        self.outputfile = outputfile
        self.training_data = pd.read_csv(trainFile)
        self.test_data = pd.read_csv(testFile)
        self.ProcessTrainData()
        self.writeOutputData()
    
    def concatenateData(self,TrainData):
        return str(TrainData['ArticleTitle'])+str(TrainData['Summary'])+str(TrainData['ArticleStory'])
    
    def ProcessTrainData(self):
        self.training_data["TextForClassification"] = self.training_data.apply(self.concatenateData, axis =1)
        labels = set(self.training_data['Label'].tolist())
        for label in labels:
            self.TrainOnLabel(label)
            self.predictLabel(label)
            
    def TrainOnLabel(self,label):
        trainingText = self.training_data["TextForClassification"]
        trainingLabels = [1 if i==label else 0 for i in self.training_data['Label'].tolist()]
        self.pipeline.fit(trainingText, trainingLabels)
        
    def predictLabel(self,label):
        testText = self.test_data.apply(self.concatenateData, axis =1)
        outputLabels = self.pipeline.predict(testText)
        self.test_data[label] = outputLabels
    
    def writeOutputData(self):
        self.test_data.to_csv(self.outputfile)
    

if __name__ == '__main__':
    trainFile = 'D:/Projects/Darwin/TrainData.csv'
    inputfile = 'D:/Projects/Darwin/CrawlerOutput.csv'
    outputfile = 'D:/Projects/Darwin/LabelOutput.csv'
    Classifier(trainFile,inputfile,outputfile)