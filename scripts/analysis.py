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

    def s(self,resultsfile,writeresults):
        saveresults = open(resultsfile,'w')
        saveresults.write(writeresults)
        saveresults.close()
    def e(self,resultsfile):
        if(os.path.exists(resultsfile)):
            while(input('Output file already exists and will be overwritten. Continue? y/n: ') != 'y'):
                sys.exit()
    def getVocInter(self,interval,data):
        return { k: v for k,v in data.items() if (interval[0] <= v[1] <= interval[1]) }
    def morphInfo(self,mdata):
        mdict = defaultdict(list)
        for k, (a,v,i,m) in mdata.items():
            for mk,mv in m.items():
                mdict[mk].append(mv)
        return(mdict)
        
    def runVocab(self,resultsfile='./jaccard_vocab.tsv'):
        self.e(resultsfile)
        writeresults = 'Language\tNWords\tLevel\tJaccard\tNKids\n'
        for f in self.files:
            cdi = CDIVocab(f,self.intervals,self.condition)
            cdi.readCdi()
            bins = [(intv,self.getVocInter(intv,cdi.vocabdata)) for intv in self.intervals]
            js = [(intv,jac(kbin),len(kbin)) for intv,kbin in bins if len(kbin) > 0]
            for l,result in enumerate(js):
                def p(intv): return str(intv[0]) + '-' + str(intv[1])
                ln = [cdi.language, p(result[0]),l+1,round(np.mean(result[1]),3),result[2]]
                writeresults += '\t'.join(map(str,ln))+'\n'
        self.s(resultsfile,writeresults)

    def runAge(self,resultsfile='./jaccard_age.tsv'):
        def getMonth(age,data):
            return (age,{k:(a,v,i) for k, (a,v,i) in data.items() if a == age })
        self.e(resultsfile)
        writeresults = 'Language\tAge\tJaccard\tNKids\n'
        for f in self.files:
            cdi = CDIVocab(f,self.intervals,self.condition)
            cdi.readCdi()
            ages = sorted(list(set([a for k, (a,v,i) in cdi.vocabdata.items()])))
            bins = [getMonth(age,cdi.vocabdata) for age in ages]
            js = [(age,jac(kbin),len(kbin)) for age,kbin in bins]
            for result in js:
                ln = [cdi.language,result[0],round(np.mean(result[1]),3),result[2]]
                writeresults += '\t'.join(map(str,ln))+'\n'
        self.s(resultsfile,writeresults)

    def runMorph(self,resultsfile='./morphology.csv'):
        fileItems = {'amenglish_ws':['item_686','item_687','item_688','item_689'], \
                 'danish_ws':['item_731','item_732','item_733'], \
                 'norwegian_ws':['item_737','item_738','item_739','item_740','item_741','item_742']}
        self.e(resultsfile)
        # morphosyntax items are not similar across languages and need to be handled individually
        morphFiles = [f for f in self.files if f.split('/')[-1] in\
                ['amenglish_ws.csv','norwegian_ws.csv','danish_ws.csv']]
        writeresults = 'Language\tNWords\tLevel\tItem\tResponse\tNKids\tQuestion\n'
        for f in morphFiles:
            itemList = fileItems[f.split('/')[-1][:-4]]
            cdi = CDIVocab(f,self.intervals,self.condition)
            cdi.readCdi(itemList)
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
        self.s(resultsfile,writeresults)
        
def jac(data):
    kids = list(data.keys())
    def j(x,y):
        return len(x.intersection(y)) / len(x.union(y))
    return [j(set(data[kids[a]][2]),set(data[kids[b]][2])) for a,b in combinations(range(len(kids)),2)]

class CDIVocab:
    def __init__(self, filepath, intervals, condition):
        self.intervals = intervals
        self.condition = condition
        self.language = filepath.split('/')[-1][:-4]
        print(self.language+'...')
        self.filepath = filepath
        self.vocabdata = None
        self.morphdata = None

    def readCdi(self,itemList=None):
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
        dat = {} # key = child, value = (age, {item:(word,category)}, {morphitem:morphvalue} )
        for l in cdidata[1:]:
            if ((l[valueIdx] == 'produces') & (l[typeIdx]== 'word')) & self.condition(l[catIdx]):
                kid = l[idIdx]
                if kid in dat:
                    dat[kid][1][l[itemIdx]] = (l[defIdx],l[catIdx])
                else:
                    dat[kid] = ( int(l[ageIdx]), {l[itemIdx]:(l[defIdx],l[catIdx])}, {})
            elif itemList and l[valueIdx]: # morphology questions
                if l[itemIdx] in itemList:
                    mitm = '___'.join([l[itemIdx],l[defIdx]])
                    if kid in dat:
                        dat[kid][2][mitm] = l[valueIdx]
                    else:
                        dat[kid] = (int(l[ageIdx]), {}, {mitm:l[valueIdx]})

        vd = {k:(a,len(i),list(i.keys())) for k, (a,i,m) in dat.items() } # {child: (age, vocabsize, [items])}
        self.vocabdata = vd

        if itemList:
            md = {k:(a,len(i),i,m) for k, (a,i,m) in dat.items() if len(i)>0}
            self.morphdata = md
        return vd
        
if __name__ == "__main__":
    corpusdir = '/path/to/corpora/cdidata/words_sentences'
    tc = JaccardData(corpusdir, 'all') #all, verbs, nouns
    #tc.runAge(resultsfile='../data/jaccard_all_byAge.csv')
    #tc.runVocab(resultsfile='../data/jaccard_all_byVocab.csv')
    tc.runMorph(resultsfile='../data/cdi_morphology.csv')
