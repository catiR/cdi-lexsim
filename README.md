# cdi-lexsim
Uses 'Full Child-by-Word Data' Words & Sentences forms, 
downloaded from Wordbank on 26 February 2021:
http://wordbank.stanford.edu/analyses?name=instrument_data

## Usage

#### To compute Jaccard similarities for children's full vocabularies, grouping by age and by vocabulary size:

```python
jc = JaccardData('path/to/data', 'all')
jc.runAge()
jc.runVocab()
```

#### To compute similarities of children's verb or noun inventories, grouping by total vocabulary size:

```python
vjc = JaccardData('path/to/data', 'verbs')
vjc.runVocab()
njc = JaccardData('path/to/data', 'nouns')
njc.runVocab()
```

#### To view acquisition of morphological elements as a function of vocabulary size:

```python
jc = JaccardData('path/to/data', 'all')
jc.runMorph()
```


#### To view detailed comparison of children's earliest words:

```python
fw = FirstWords('path/to/data')
fw.runFW()
```

#### To check predictions of syntactic bootstrapping by comparing acquisition trends for selected words:

* define a list of words to search for in each language

```python
wl = WhenLearn('path/to/data',searchterms)
wl.runSynBoot()
```
