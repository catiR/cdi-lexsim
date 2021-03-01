# cdi-lexsim
Uses 'Full Child-by-Word Data' Words & Sentences forms, 
downloaded from Wordbank on 26 February 2021:
http://wordbank.stanford.edu/analyses?name=instrument_data

## Usage

Edit lexsim.py to modify inputs like languages, word categories, or words of interest.


#### To compute Jaccard similarities for children's full vocabularies, grouping by age and by vocabulary size:

```python
wholeVocabJaccard('/path/to/data')
```

#### To compute similarities of children's verb and noun inventories, grouped by total vocabulary size:

```python
partVocabJaccard('/path/to/data')
```

#### To view acquisition of morphological elements as a function of vocabulary size:

```python
morphology('/path/to/data')
```

#### To view detailed comparison of children's earliest words:

```python
firstWords('/path/to/data')
```

#### To look for phonological (lexical) selection based on word onsets:

* Pronunciation keys for 6 language varieties are provided in /resources
* US English and Australian English source: [CMU Pronouncing Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict)
* Danish source: [Sprakbanken](https://openslr.org/8/)
* Mexican Spanish source: [Santiago Spanish Lexicon](https://www.openslr.org/34/)
* Norwegian source: [g2p-no](https://github.com/peresolb/g2p-no) NoFAbet edition of [NST lexicon](https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-23/)
* Missing entries added by hand for all languages.

```python
lexicalSelection('/path/to/data')
```

#### To check predictions of syntactic bootstrapping by comparing acquisition trends for selected words:

* define a list of words to search for in each language

```python
syntacticBootstrapping('/path/to/data')
```
