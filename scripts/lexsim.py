### Author: Caitlin Richter
### 28 Feb. 2021
### University of Pennsylvania

from cdifunctions import *

def wholeVocabJaccard(corpusdir):
    jc = JaccardData(corpusdir)
    jc.runAge(resultsfile = '../data/jaccard_all_byAge.csv')
    jc.runVocab(resultsfile = '../data/jaccard_all_byVocab.csv')

def partVocabJaccard(corpusdir):
    verbIntervals = [(1,5), (6,10), (11,20), (21,35), (36,55), (56,85), (86,125), (126,175), (176,200)]
    verbFilter = lambda wordCategory: wordCategory == 'action_words'
    vjc = JaccardData(corpusdir, verbFilter,verbIntervals)
    vjc.runVocab(resultsfile = '../data/jaccard_verbs_byVocab.csv')

    nounIntervals = [(1,7), (8,17), (19,30), (31,45), (46,65), (66,90), (91,120), (121,160), (161,200), (201,250), (251,999)]
    nouns = ['animals','vehicles','toys','food_drink','clothing','body_parts','household','furniture_rooms','outside', 'places']
    nounFilter = lambda wordCategory: wordCategory in nouns
    njc = JaccardData(corpusdir,nounFilter,nounIntervals)
    njc.runVocab(resultsfile = '../data/jaccard_nouns_byVocab.csv')

def morphology(corpusdir,dataset=None):
    mh = JaccardData(corpusdir)
    # Morphosyntax items are very different on each CDI and best to refer to by ID
    # This implementation is for items with < not yet, sometimes, often > responses
    morphItems = {'amenglish_ws':['item_686','item_687','item_688','item_689'], \
                 'danish_ws':['item_731','item_732','item_733'], \
                 'norwegian_ws':['item_737','item_738','item_739','item_740','item_741','item_742']}
    mh.runMorph(morphItems,resultsfile='../data/cdi_morphology.csv')

def firstWords(corpusdir):
    languages = ['amenglish_ws','auenglish_ws','danish_ws','mxspanish_ws','norwegian_ws']
    fw = FirstWords(corpusdir,languages,prefix='../data/')
    fw.runFW()

def syntacticBootstrapping(corpusdir):
    searchterms = {'amenglish_ws' : ['throw', 'drink (action)', 'wish', 'kick'], \
                    'danish_ws' : ['kaste', 'drikke', 'ønske', 'sparke'], \
                'norwegian_ws' : ['kaste','drikke (action)', 'ønske','sparke']}
    wl = WhenLearn(corpusdir, searchterms, resultsfile = '../data/when_learned_words.csv')
    wl.runSynBoot()

def lexicalSelection(corpusdir):
    languages=['amenglish_ws','auenglish_ws','danish_ws','mxspanish_ws','norwegian_ws']
    ls = LexSelect(corpusdir, languages, resultsfile='../data/lexical_selection.csv')
    ls.runLexSelec()

if __name__ == "__main__":
    corpusdir = '/path/to/corpora/cdidata/words_sentences'
    wholeVocabJaccard(corpusdir)
    partVocabJaccard(corpusdir)
    morphology(corpusdir)
    firstWords(corpusdir)
    syntacticBootstrapping(corpusdir)
    lexicalSelection(corpusdir)
