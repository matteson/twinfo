from classes import PMICalc
from classes import FreqCompilation

minTime = 1374144994
maxTime = 1374719947

geekResultStore = []
nerdResultStore = []

while minTime<maxTime:

    freqGeek = FreqCompilation('nerdgeek.db',where='geek and time>{} and time<{}'.format(minTime,minTime+86400))
    freqNerd = FreqCompilation('nerdgeek.db',where='nerd and time>{} and time<{}'.format(minTime,minTime+86400))
    freqCorp = FreqCompilation('corpusTweets.db',where='time>{} and time<{}'.format(minTime,minTime+86400))

    freqGeek.compileFreq()
    freqNerd.compileFreq()
    freqCorp.compileFreq()

    blockedWords = [u'geek',u'geeks',u'geeky',
                    u'nerd',u'nerds',u'nerdy']


    pmiGeek = PMICalc(freqGeek.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)
    pmiNerd = PMICalc(freqNerd.getFreq(),freqCorp.getFreq(),blockedWords,minHits=15)

    pmiGeek.calcPMI()
    pmiNerd.calcPMI()

    geekResult = pmiGeek.getPMI()
    nerdResult = pmiNerd.getPMI()

    geekResultStore.append(geekResult)
    nerdResultStore.append(nerdResult)

    minTime = minTime+86400

    print '\n\n', 'Geeky:', '\n'
    for tup in geekResult[0:20]:
        print tup[0], '\t\t', tup[1]

    print '\n\n', 'Nerdy:', '\n'
    for tup in nerdResult[0:20]:
        print tup[0], '\t\t', tup[1]

    print '==============================================='
