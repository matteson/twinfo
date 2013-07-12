from classes import PMICalc

comp = PMICalc('geekNerdTweets.db','corpusTweets.db',minHits=5)
comp.compileFreq()
#comp.genProbs()
#comp.genPMI()

print '\n\n', 'Geeky:', '\n'
for tup in comp.geekPMI[0:30]:
    print tup[0], '\t\t', tup[1]

print '\n\n', 'Nerdy:', '\n'
for tup in comp.nerdPMI[0:30]:
    print tup[0], '\t\t', tup[1]
