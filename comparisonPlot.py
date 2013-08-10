def comparisonPlot(wordTups,word1,word2,axisSize,selectedWords=[]):

    import pickle
    from pylab import *
    import matplotlib.pyplot as plt
   
    if selectedWords:
        wordTups = [tup for tup in wordTups if tup[0] in selectedWords]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("PMI(w," + word1 + ")",color='r',size=20)
    ax.set_ylabel("PMI(w,'Congress')",color='b',size=20)
    ax.set_title(word1 +" vs. "+ word2 + " Word Associations",size=22)

    ax.scatter([tup[1] for tup in wordTups],[tup[2] for tup in wordTups],marker=None)

    for tup in wordTups:
        if tup[1]>tup[2]:
            color = 'r'
        else:
            color = 'b'
        
        plt.annotate(
            tup[0],
            xy = (tup[1],tup[2]),xytext=(5,5),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            color=color)
    ax.axis(axisSize)
    ax.plot([-2,7],[-2,7],'k--')
    plt.show()
