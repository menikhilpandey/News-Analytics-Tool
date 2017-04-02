'''
Created on 18-Jul-2016

@author: Nikhil.Pandey

Module for testing sufficiency of Training Data
'''

import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support

class TrainingDataCheck:
    
    def __init__(self, trainFile):
        self.training_data = pd.read_csv(trainFile)
        self.process(self.training_data)
    
    def process(self, training_data):
        text = training_data.apply(self.concatenateData, axis =1)
        labels = training_data['Label'].tolist()
        TextLabelTuple = zip(text,labels)
        pipeline = Pipeline([
                             ('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier()),
                             ])

        initial = 50
        results = []
        while initial<=len(training_data):
            Sample1 = random.sample(TextLabelTuple,initial)
            Sample2 = list(TextLabelTuple)
            for item in Sample1:
                Sample2.remove(item)
            X_train = [item[0] for item in Sample1]
            Y_train = [item[1] for item in Sample1]
            X_test  = [item[0] for item in Sample2]
            Y_test  = [item[1] for item in Sample2]
            pipeline.fit(X_train,Y_train)
            predicted = pipeline.predict(X_test)
            results.append((initial,precision_recall_fscore_support(predicted,Y_test)))
            initial+=50
        self.plot(results)
    
    def concatenateData(self,TrainData):
        return str(TrainData['ArticleTitle'])+str(TrainData['Summary'])+str(TrainData['ArticleStory'])
    
    def plot(self,results):
        xplot = [i[0] for i in results]
        yplot1 = [(i[1][0][0]+i[1][0][1])/2.0 for i in results]
        yplot2 = [(i[1][1][0]+i[1][1][1])/2.0 for i in results]
        yplot3 = [(i[1][2][0]+i[1][2][1])/2.0 for i in results]

        fig,axes = plt.subplots(1,3, figsize=(10,4))
        axes[0].plot(xplot,yplot1)
        axes[0].set_title('Precision')
        axes[1].plot(xplot,yplot2)
        axes[1].set_title('Recall')
        axes[2].plot(xplot,yplot3)
        axes[2].set_title('F-Score')
        plt.show()


if __name__ == '__main__':
    inputfile = 'D:/Projects/Darwin/TrainData.csv'
    TrainingDataCheck(inputfile)
