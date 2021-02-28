import codecs,glob,sys,os
import numpy as np
from itertools import combinations
from collections import defaultdict

class JaccardData:
    def __init__(self, corpusdir,vocabsubset):
        all_intervals = [(1,10), (11,25), (26,50), (51,100), (101,175), (176,250), \
                (251,350), (351,450), (451,550), (551,650), (651,999)]
        verb_intervals = [(1,5), (6,10), (11,20), (21,35), (36,55), \
                (56,85), (86,125), (126,175), (176,200)]
        noun_intervals = [(1,7), (8,17), (19,30), (31,45), (46,65), (66,90), \
                (91,120), (121,160), (161,200), (201,250), (251,999)]
        def all_filter(category):
            return category != 'sounds'
        def verb_filter(category):
            return category == 'action_words'
        def noun_filter(category):
            nouns = ['animals','vehicles','toys','food_drink','clothing','body_parts',\
                    'household','furniture_rooms','outside', 'places']
            return category in nouns
        self.files = sorted(glob.glob(corpusdir + '/*.csv'))
        try:
            self.intervals = {'all':all_intervals,'verbs':verb_intervals,'nouns':noun_intervals}[vocabsubset]
        except:
            print('Undefined vocabulary subset! Choose: all, nouns, verbs.')
            sys.exit()
        self.condition = {'all':all_filter,'verbs':verb_filter,'nouns':noun_filter}[vocabsubset]

    def getVocInter(self,interval,data):
        return { k: v for k,v in data.items() if (interval[0] <= v[1] <= interval[1]) }
    def morphInfo(self,mdata):
        mdict = defaultdict(list)
        for k, (a,v,i,m) in mdata.items():
            for mk,mv in m.items():
                mdict[mk].append(mv)
        return(mdict)
        
    def runVocab(self,resultsfile='./jaccard_vocab.tsv'):
        e(resultsfile)
        writeresults = 'Language\tNWords\tLevel\tJaccard\tNKids\n'
        for f in self.files:
            cdi = CDIVocab(f,self.condition)
            cdi.readCdi(analysis='j')
            bins = [(intv,self.getVocInter(intv,cdi.jvocabdata)) for intv in self.intervals]
            js = [(intv,jac(kbin),len(kbin)) for intv,kbin in bins if len(kbin) > 0]
            for l,result in enumerate(js):
                def p(intv): return str(intv[0]) + '-' + str(intv[1])
                ln = [cdi.language, p(result[0]),l+1,round(np.mean(result[1]),3),result[2]]
                writeresults += '\t'.join(map(str,ln))+'\n'
        s(resultsfile,writeresults)

    def runAge(self,resultsfile='./jaccard_age.tsv'):
        def getMonth(age,data):
            return (age,{k:(a,v,i) for k, (a,v,i) in data.items() if a == age })
        e(resultsfile)
        writeresults = 'Language\tAge\tJaccard\tNKids\n'
        for f in self.files:
            cdi = CDIVocab(f,self.condition)
            cdi.readCdi(analysis='j')
            ages = sorted(list(set([a for k, (a,v,i) in cdi.jvocabdata.items()])))
            bins = [getMonth(age,cdi.jvocabdata) for age in ages]
            js = [(age,jac(kbin),len(kbin)) for age,kbin in bins]
            for result in js:
                ln = [cdi.language,result[0],round(np.mean(result[1]),3),result[2]]
                writeresults += '\t'.join(map(str,ln))+'\n'
        s(resultsfile,writeresults)

    def runMorph(self,resultsfile='./morphology.csv'):
        fileItems = {'amenglish_ws':['item_686','item_687','item_688','item_689'], \
                 'danish_ws':['item_731','item_732','item_733'], \
                 'norwegian_ws':['item_737','item_738','item_739','item_740','item_741','item_742']}
        e(resultsfile)
        # morphosyntax items are not similar across languages and need to be handled individually
        morphFiles = [f for f in self.files if f.split('/')[-1] in\
                ['amenglish_ws.csv','norwegian_ws.csv','danish_ws.csv']]
        writeresults = 'Language\tNWords\tLevel\tItem\tResponse\tNKids\tQuestion\n'
        for f in morphFiles:
            itemList = fileItems[f.split('/')[-1][:-4]]
            cdi = CDIVocab(f,self.condition)
            cdi.readCdi(itemList,'m')
            bins = [(intv,self.getVocInter(intv,cdi.morphdata)) for intv in self.intervals]            
            ms = [(intv,self.morphInfo(kbin)) for intv,kbin in bins if len(kbin) > 0]
            for l,result in enumerate(ms):
                def p(intv): return str(intv[0]) + '-' + str(intv[1])
                ln = [cdi.language, p(result[0])]
                for itm in result[1].keys():
                    ln2 = ln + [l+1,itm.split('___')[0]]
                    for response in ['never','sometimes','often']:
                        ln3=ln2+[response,result[1][itm].count(response),itm.split('___')[1]]
                        writeresults += '\t'.join(map(str,ln3))+'\n'
        s(resultsfile,writeresults)
        
def jac(data):
    kids = list(data.keys())
    def j(x,y):
        return len(x.intersection(y)) / len(x.union(y))
    return [j(set(data[kids[a]][2]),set(data[kids[b]][2])) for a,b in combinations(range(len(kids)),2)]
def s(resultsfile,writeresults):
    saveresults = open(resultsfile,'w')
    saveresults.write(writeresults)
    saveresults.close()
def e(resultsfile):
    if(os.path.exists(resultsfile)):
        while(input('Output file already exists and will be overwritten. Continue? y/n: ') != 'y'):
            sys.exit()

class CDIVocab:
    def __init__(self, filepath, condition=lambda x: True):
        self.condition = condition
        self.language = filepath.split('/')[-1][:-4]
        print(self.language+'...')
        self.filepath = filepath
        self.vocabdata = None
        self.morphdata = None

    def readCdi(self,itemList=None,analysis='v'):
        with open(self.filepath) as handle:
            cdidata = handle.read()
        # normalise language data
        cdidata = cdidata.replace('"','').replace("'",'').replace('Upa, upa', 'Upa upa').splitlines()
        cdidata = [l.split(',') for l in cdidata]
        idIdx = cdidata[0].index('data_id')
        ageIdx = cdidata[0].index('age')
        valueIdx = cdidata[0].index('value')
        itemIdx = cdidata[0].index('item_id')
        typeIdx = cdidata[0].index('type')
        catIdx = cdidata[0].index('category')
        defIdx = cdidata[0].index('definition')

        def __makeJdict():
            dat = {}
            for l in cdidata[1:]:
                if ((l[valueIdx] == 'produces') & (l[typeIdx]== 'word')) & self.condition(l[catIdx]):
                    kid = l[idIdx]
                    if kid in dat:
                        dat[kid][1].append(l[itemIdx])
                    else:
                        dat[kid] = (int(l[ageIdx]), [l[itemIdx]])
            return {k:(a,len(i),i) for k, (a,i) in dat.items()}

        def __makeMdicts():
            dat = {}
            for l in cdidata[1:]:
                if ((l[valueIdx] == 'produces') & (l[typeIdx]== 'word')) & self.condition(l[catIdx]):
                    kid = l[idIdx]
                    if kid in dat:
                        dat[kid][1][l[itemIdx]] = (l[defIdx],l[catIdx])
                    else:
                        dat[kid] = (int(l[ageIdx]), {l[itemIdx]:(l[defIdx],l[catIdx])}, {})
                elif l[valueIdx] and (l[itemIdx] in itemList):
                    mitm = '___'.join([l[itemIdx],l[defIdx]])
                    if kid in dat:
                        dat[kid][2][mitm] = l[valueIdx]
                    else:
                        dat[kid] = (int(l[ageIdx]), {}, {mitm:l[valueIdx]})
            vd = {k:(a,len(i),list(i.keys())) for k, (a,i,m) in dat.items() } # {child: (age, vocabsize, [items])}
            md = {k:(a,len(i),i,m) for k, (a,i,m) in dat.items() if len(i)>0}
            return vd,md

        def __makeFWdict():
            dat = {}
            for l in cdidata[1:]:
                if (l[valueIdx] == 'produces') & (l[typeIdx] == 'word'):
                    kid = l[idIdx]
                    if kid in dat:
                        dat[kid][1].append(l[itemIdx])
                        dat[kid][2].append((l[defIdx],l[catIdx]))
                    else:
                        dat[kid] = (int(l[ageIdx]), [l[itemIdx]], [(l[defIdx],l[catIdx])])
            return {k:(a,len(i),w) for k, (a,i,w) in dat.items()}

        def __makeWLdict():
            dat = {}
            for l in cdidata[1:]:
                if ((l[valueIdx] == 'produces') & (l[typeIdx]== 'word')) & self.condition(l[catIdx]):
                    kid = l[idIdx]
                    if kid in dat:
                        dat[kid][1].append(l[itemIdx])
                        dat[kid][2].append(l[defIdx])
                    else:
                        dat[kid] = (int(l[ageIdx]), [l[itemIdx]], [l[defIdx]])
            return {k:(a,len(i),w) for k, (a,i,w) in dat.items()}

        if analysis == 'j':
            vd = __makeJdict()
            self.jvocabdata = vd
        if analysis == 'm':
            vd,md = __makeMdicts()
            self.mvocabdata = vd
            self.morphdata = md
        if analysis == 'fw':
            fwd = __makeFWdict()
            self.firstwdata = fwd
        if analysis == 'wl':
            wld = __makeWLdict()
            self.whenlearndata = wld


class FirstWords:
    def __init__(self,corpusdir,prefix='',vsizes=[2,5,10,15,20],languages = None):
        files = glob.glob(corpusdir + '/*.csv')
        if not languages:
            languages = ['amenglish_ws','auenglish_ws','danish_ws','mxspanish_ws','norwegian_ws']
        self.files = sorted([fpath for fpath in files if fpath.split('/')[-1][:-4] in languages])
        self.vsizes = vsizes
        self.prefix=prefix

    def runFW(self):
        for f in self.files:
            language = f.split('/')[-1][:-4]
            resultsfile = self.prefix + language + '_firstwords.txt'
            e(resultsfile)
            cdi = CDIVocab(f)
            cdi.readCdi(analysis='fw')
            writeresults = 'FIRST WORDS: {}\n\n'.format(language)
            for vsize in self.vsizes:
                data = {k:v for k,v in cdi.firstwdata.items() if (vsize-1 <= v[1] <= vsize+1)}
                wlist = [j for w in [i for k, (a,v,i) in data.items()] for j in w]
                wset = set(wlist)
                ages = [a for k, (a,v,i) in data.items()]
                multis = [w for w in wset if wlist.count(w) >1]
                singles = [w for w in wset if wlist.count(w) ==1]
                writeresults+= '-- Vocabulary size {} words, sample {} children ({}-{}) months,'.format( \
                    vsize, len(data), min(ages), max(ages))
                writeresults+= 'mean {:.1f}) --\n#Children\tWord\tCategory\n'.format(np.mean(ages))
                writeresults += ''.join([str(wlist.count(w)) + '\t' + '\t'.join(w) + '\n' 
                    for w in sorted(multis, key=lambda wd: wlist.count(wd), reverse=True )])
                writeresults += '{} unique words in vocabularies; {} occur only once\n'.format(len(wset),len(singles))
                writeresults += ', '.join([ w[0]+' ('+w[1]+')' for w in sorted(singles, \
                    key=lambda wd: ''.join([wd[1],wd[0]]))]) + '\n\n'
            s(resultsfile,writeresults)

class WhenLearn:
    def __init__(self,corpusdir,searchterms,resultsfile='./syntactic_bootstrapping.tsv',intervals=None):
        if not intervals:
            intervals = [(1,10), (11,25), (26,50), (51,100), (101,175), (176,250), \
                (251,350), (351,450), (451,550), (551,650), (651,999)]
        self.intervals = intervals
        self.files = sorted(['{}/{}.csv'.format(corpusdir,k) for k in searchterms.keys()])
        self.searchterms = searchterms
        self.resultsfile = resultsfile

    def runSynBoot(self):
        e(self.resultsfile)
        writeresults = 'Language\tLevel\tNWords\tNKidsTotal\tNKidsInV\tNKidsOOV\tWord\n'
        for f in self.files:
            cdi = CDIVocab(f,condition=lambda x: x != 'sounds')
            cdi.readCdi(analysis='wl')
            language = f.split('/')[-1][:-4]
            terms = searchterms[language]
            for i,interval in enumerate(self.intervals):
                idct = {k:(a,v,w) for k, (a,v,w) in cdi.whenlearndata.items() if (interval[0] <= v <= interval[1])}
                ln = '{}\t{}\t{}-{}\t{}\t'.format(language,i+1,interval[0],interval[1],len(idct))
                for term in terms:
                    inv = {k:(a,v,w) for k, (a,v,w) in idct.items() if (term in w)}
                    writeresults += ln + '{}\t{}\t{}\n'.format(len(inv), len(idct)-len(inv),term)
        s(self.resultsfile,writeresults)

if __name__ == "__main__":
    corpusdir = '/path/to/corpora/cdidata/words_sentences'
    
    jc = JaccardData(corpusdir, 'all')
    jc.runAge(resultsfile='../data/jaccard_all_byAge.csv') #compute jaccard similarities
    jc.runVocab(resultsfile='../data/jaccard_all_byVocab.csv')
    vjc = JaccardData(corpusdir, 'verbs')
    vjc.runVocab(resultsfile='../data/jaccard_verbs_byVocab.csv')
    njc = JaccardData(corpusdir, 'nouns')
    njc.runVocab(resultsfile='../data/jaccard_nouns_byVocab.csv')

    jc.runMorph(resultsfile='../data/cdi_morphology.csv') #track morphology development

    fw = FirstWords(corpusdir,prefix='../data/') #compare first words
    fw.runFW()

    searchterms = {'amenglish_ws' : ['throw', 'drink (action)', 'wish', 'kick'], \
                    'danish_ws' : ['kaste', 'drikke', 'ønske', 'sparke'], \
                'norwegian_ws' : ['kaste','drikke (action)', 'ønske','sparke']}
    wl = WhenLearn(corpusdir, searchterms, resultsfile='../data/when_learned_words.csv')
    wl.runSynBoot()
