import pickle
from pylab import *
import matplotlib.pyplot as plt

## selected words
# select some more words particularly in [2,7,2,7]
words = ['ale', 'bbq', 'cans', 'cheap', 'chocolate', 'club', 'cold', 'collection', 'cool',
         'cork', 'craft', 'expensive', 'fine', 'float', 'free', 'french', 'german',
         'grape', 'pizza', 'pong', 'red', 'root', 'tasting', 'tequila', 'white',
         'alcohol','sip','glass','drink']

out = pickle.load(open('/Users/Andrew/twitter_app/outUnion.p','rb'))

out = [tup for tup in out if tup[0] in words]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel("PMI(w,'wine')",color='r',size=20)
ax.set_ylabel("PMI(w,'beer')",color='b',size=20)
ax.set_title("Wine vs. Beer Word Associations",size=22)

ax.scatter([tup[1] for tup in out],[tup[2] for tup in out],marker=None)

for tup in out:
    if tup[1]>tup[2]:
        color = 'r'
    else:
        color = 'b'
    
    plt.annotate(
        tup[0],
        xy = (tup[1],tup[2]),xytext=(5,5),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        color=color)
ax.axis([-2, 7.5, -2, 7.5])
ax.plot([-2,7],[-2,7],'k--')
#ax.axis([1, 3,4,7])
plt.show()




