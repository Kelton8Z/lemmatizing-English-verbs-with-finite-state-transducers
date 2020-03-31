import pywrapfst as fst
from fststr import fststr
import copy
class Lemmatizer():
  def generateFst(self,data,st):
      lines = []
      lineLst = data.split("\n")
      count = 0
      for line in lineLst:
          curFst = ""
          stemNinf = line.split(",")[:2]
          curFst = "0\n" # 0 as final state
          curFst += "0 0 <other> <other>\n"
          stem = stemNinf[0]
          if stem == "":
              return rootFst
          #print("stem: %s",stem)
          #if len(stemNinf)>1:
          inf = stemNinf[1]
          #print("inf: %s",inf)
          for i in range(len(stem)):
              curFst += str(i)
              curFst += " "
              curFst += str(i+1)
              curFst += " "
              if i >= len(inf):
                  curFst += "<epsilon>"
              else:
                  curFst += inf[i]
              curFst += " "
              curFst += stem[i]
              curFst += "\n"
          infLen = len(inf)
          stemLen = len(stem)
          index = stemLen
          if stemLen > infLen:
              continue
          else:
              toBeReplaced = inf[stemLen:]
              for i,s in enumerate(toBeReplaced):
                  index = i+stemLen
                  curFst += str(index)
                  curFst += " "
                  curFst += str(index+1)
                  curFst += " "
                  curFst += s
                  curFst += " "
                  curFst += "<epsilon>"
                  curFst += "\n"
          curFst += str(index+1)
          curFst += " "
          curFst += "0"
          curFst += " "
          curFst += "<#>"
          curFst += " "
          curFst += "+Known"
          compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
          #print("curFst",curFst)
          compiler.write(curFst)
          other = compiler.compile()
          fststr.expand_other_symbols(other)
          if count==0:
              rootFst = other
          else :
              rootFst = rootFst.union(other)
          count += 1
      return rootFst
# TODO: Implement the in vocab FST
  def get_in_vocab_fst(self):
      with open("in_vocab_dictionary_verbs.txt","r") as f:
          data = f.read()
      st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
      fsT = self.generateFst(data,st)
      return fsT
  def __init__(self):
    # TODO: Implement the OOV FSTs in the text files
    # Reading a FST from an empty file will throw an error
    # Pre Process: Add <#> to end of word
    pre_process_fst = self.get_compiler_from_file_name('fsts/pre-process.txt')
    # Get in vocabulary FST
    in_vocab_fst = self.get_in_vocab_fst()
    # Get out of vocabulary FST
    # General FST to add morpheme boundary to: ed, s, en, ing
    general_fst = self.get_compiler_from_file_name('fsts/general-morph.txt')
    #general_fst = general_fst.invert()
    # Allomorphic rules:
    consonant_doubling_fst = self.get_compiler_from_file_name('fsts/consonant-doubling.txt')
    e_deletion_fst = self.get_compiler_from_file_name('fsts/silent-e-deletion.txt')
    e_insertion_fst = self.get_compiler_from_file_name('fsts/e-insertion.txt')
    y_replacement_fst = self.get_compiler_from_file_name('fsts/y-replacement.txt')
    k_insertion_fst = self.get_compiler_from_file_name('fsts/k-insertion.txt')
    # OPTIONAL: You can implement rules in reverse and then call .invert() on the FST
    #consonant_doubling_fst = consonant_doubling_fst.invert()
    e_deletion_fst = e_deletion_fst.invert()
    e_insertion_fst = e_insertion_fst.invert()
    y_replacement_fst = y_replacement_fst.invert()
    k_insertion_fst = k_insertion_fst.invert()
    # Post Process: Remove suffixes
    keep = self.get_compiler_from_file_name('fsts/keep.txt')
    post_process_fst = self.get_compiler_from_file_name('fsts/post-process.txt')

    oov = consonant_doubling_fst
    oov.union(e_deletion_fst)
    oov.union(e_insertion_fst)
    oov.union(y_replacement_fst)
    oov.union(k_insertion_fst)
    oov.union(keep)
    # Assemble final FST
    # TODO: use FST operations on your FSTs to create the result FST
    oov = self.compose_fst(general_fst,oov)
    oov = self.compose_fst(oov,post_process_fst)
    oov.union(post_process_fst)
    oov.union(in_vocab_fst)
    #self.res_fst = consonant_doubling_fst.union(e_insertion_fst.union(k_insertion_fst.union(y_replacement_fst.union(e_deletion_fst))))
    #self.res_fst = oov
    self.res_fst = self.compose_fst(pre_process_fst,oov)

    self.inverted_res_fst = copy.deepcopy(self.res_fst).invert()
  # Get FST from file_name
  def get_compiler_from_file_name(self, file_name):
    st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
    compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
    in_file = open(file_name)
    fst_file = in_file.read()
    print(fst_file, file=compiler)
    c = compiler.compile()
    fststr.expand_other_symbols(c)
    in_file.close()
    return c
  # Composes fsts such that fst_a is executed first, and output is used as input for fst_b
  # output = fst_b(fst_a(input))
  def compose_fst(self, fst_a, fst_b):
    return fst.compose(fst_a.arcsort(sort_type="olabel"), fst_b.arcsort(sort_type="ilabel"))
  # Run FST on input word
  def run_fst(self, in_word, compiler):
    return fststr.apply(in_word, compiler)
  def lemmatize(self, input_word):
    out = list(set(self.run_fst(input_word, self.res_fst)))
    return out
  def delemmatize(self, input_word):
    return list(set(self.run_fst(input_word, self.inverted_res_fst)))
# How to run the lemmatizer:
# DO NOT INCLUDE THIS IN YOUR SUBMISSION
# Gradescope will throw an error with any print statements
#L = Lemmatizer()
#print(L.lemmatize('fox<^>s<#>')) # Test for e-insertion rule
#print(L.lemmatize('squigging'))
#print(L.delemmatize('squig+Guess'))
