import nltk
from nltk.collocations import *
bigram_measures = nltk.collocations.BigramAssocMeasures() #for convenience

text1 = "I do not like green eggs and ham, I do not like them Sam I am!"
text2 = "Today you are you! That is truer than true! There is no one alive who is you-er than you!"
text3 = "You know you're in love when you can't fall asleep because reality is finally better than your dreams."

text1_coll = [(word,'nerd') for word in nltk.wordpunct_tokenize(text1)]
text2_coll = [(word,'geek') for word in nltk.wordpunct_tokenize(text2)]
text3_coll = [(word,'nerd') for word in nltk.wordpunct_tokenize(text3)]

word_fd = nltk.FreqDist(nltk.wordpunct_tokenize(text1 + ' ' + text2 + ' ' + text3))
nerd_fd = nltk.FreqDist(text1_coll + text3_coll)
geek_fd = nltk.FreqDist(text2_coll)

nerd_finder = BigramCollocationFinder(word_fd,nerd_fd)
geek_finder = BigramCollocationFinder(word_fd,geek_fd)

nerd_scored = nerd_finder.score_ngrams(bigram_measures.raw_freq)
geek_scored = geek_finder.score_ngrams(bigram_measures.raw_freq)

print nerd_scored
print geek_scored
