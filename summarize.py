from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk.data

class SimpleSummarizer:

	def reorder_sentences( self, output_sentences, inputF ):
		output_sentences.sort( lambda s1, s2:
			inputF.find(s1) - inputF.find(s2) )
		return output_sentences
	
	def get_summarized(self, inputF, num_sentences ):
		tokenizer = RegexpTokenizer('\w+')
		base_words = [word.lower()
			for word in tokenizer.tokenize(inputF)]
		words = [word for word in base_words if word not in stopwords.words()]
		word_frequencies = FreqDist(words)
		most_frequent_words = [pair[0] for pair in
			word_frequencies.items()[:100]]
		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		actual_sentences = sent_detector.tokenize(inputF)
		working_sentences = [sentence.lower()
			for sentence in actual_sentences]
		output_sentences = []

		for word in most_frequent_words:
			for i in range(0, len(working_sentences)):
				if (word in working_sentences[i]
				  and actual_sentences[i] not in output_sentences):
					output_sentences.append(actual_sentences[i])
					break
				if len(output_sentences) >= num_sentences: break
			if len(output_sentences) >= num_sentences: break
		return self.reorder_sentences(output_sentences, inputF)
	
	def summarize(self, inputF, num_sentences):
		return " ".join(self.get_summarized(inputF, num_sentences))
