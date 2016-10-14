#!/usr/bin/env python

import numpy as np
import sys, ConfigParser, collections, os
sys.dont_write_bytecode = True

class DatasetProvider:
  """THYME relation data"""
    
  def __init__(self, path):
    """Make alphabets"""

    # various alphabets
    self.label2int = {}
    self.left2int = {}
    self.middle2int = {}
    self.right2int = {}

    labels = []  # classes as list
    lefts = []   # left regions
    middles = [] # middle regions
    rights = []  # right regions
    
    for line in open(path):
      label, left, middle, right = line.strip().split('|')
      labels.append(label)
      lefts.extend(left.split())
      middles.extend(middle.split())
      rights.extend(right.split())

    self.left2int = make_alphabet(lefts)
    self.left2int['oov_word'] = 0
    self.middle2int = make_alphabet(middles)
    self.middle2int['oov_word'] = 0
    self.right2int = make_alphabet(rights)
    self.right2int['oov_word'] = 0

    index = 0 # index classes
    for label in set(labels):
      self.label2int[label] = index
      index = index + 1
      
  def load(self, path, left_maxlen=float('inf'),
             middle_maxlen=float('inf'), right_maxlen=float('inf')):
    """Convert sentences (examples) into lists of indices"""

    # lists of int sequences
    lefts = []
    middles = []
    rights = []
    labels = []
    
    for line in open(path):
      label, left, middle, right = line.strip().split('|')
      lefts.append(convert_to_ints(left, self.left2int, left_maxlen))
      middles.append(convert_to_ints(middle, self.middle2int, middle_maxlen))
      rights.append(convert_to_ints(right, self.right2int, right_maxlen))
      labels.append(self.label2int[label])

    return lefts, middles, rights, labels

def convert_to_ints(text, alphabet, maxlen=float('inf')):
  """Turn text into a sequence of integers"""
  
  result = []
  for token in text.split():
    if token in alphabet:
      result.append(alphabet[token])
    else:
      result.append(alphabet['oov_word'])
      
  if len(result) > maxlen:
    return result[0:maxlen]
  else:
    return result

def make_alphabet(tokens):
  """Map tokens to integers sorted by frequency"""
  
  token2int = {} # key: token, value: int
  index = 1 # start from 1 (zero reserved)
  
  # tokens will be indexed by frequency
  counts = collections.Counter(tokens)
  for token, count in counts.most_common():
    token2int[token] = index
    index = index + 1
    
  return token2int
  
if __name__ == "__main__":
  
  cfg = ConfigParser.ConfigParser()
  cfg.read(sys.argv[1])
  base = os.environ['DATA_ROOT']
  train_file = os.path.join(base, cfg.get('data', 'train'))
  test_file = os.path.join(base, cfg.get('data', 'test'))

  dataset = DatasetProvider(test_file)
  x1, x2, x3, y = dataset.load(test_file)
  print 'first 10 examples:', x2[:10]
  print 'time dist alphabet len:', len(dataset.left2int)

  l = ['one', 'two', 'three', 'one', 'four', 'three', 'one']
  print 'corpus:', l
  alphabet = make_alphabet(l)
  print 'alphabet:', alphabet
  print 'int sequence:', convert_to_ints('one two', alphabet)
  
