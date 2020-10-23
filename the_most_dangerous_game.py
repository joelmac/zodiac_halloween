from copy import copy
from random import shuffle
from bisect import bisect
f = open('z340.txt',mode='r')
z_340 = f.read().replace("\n","")
f.close()
f = open('words_alpha.txt',mode='r')
words_complete = []
for line in f:
    words_complete.append(line.replace("\n","").upper())



chars = {}
for c in z_340:
    chars[c] = chars.get(c,0)+1

consonants = "bcdfghjklmnpqrstvwxz".upper()
vowels = "aeiouy".upper()
alphabet =list("abcdefghijklmnopqrstuvwxyz".upper())
shuffle(alphabet)

most_common_words = ['the'.upper(),'of'.upper(),'end'.upper(),'to'.upper(),'in'.upper(),'is'.upper(),'you'.upper(),'that'.upper(),'it'.upper(),'he'.upper(),'was'.upper(),'for'.upper(),'on'.upper(),'are'.upper(),'as'.upper(),'with'.upper(),'his'.upper(),'they'.upper(),'at'.upper(),'the'.upper(),'this'.upper(),'have'.upper(),'from'.upper(),'or'.upper(),'one'.upper(),'had'.upper(),'by'.upper(),'word'.upper(),'but'.upper(),'not'.upper(),'what'.upper(),'all'.upper(),'were'.upper(),'we'.upper(),'when'.upper(),'your'.upper(),'can'.upper(),'said'.upper(),'there'.upper(),'use'.upper(),'an'.upper(),'each'.upper(),'which'.upper(),'she'.upper(),'do'.upper(),'how'.upper(),'their'.upper(),'if'.upper(),'kill'.upper()]


unstarts = ['BX','CJ','CV','CX','DX','FQ','FX','GQ','GX','HX','JC','JF','JG','JQ','JS','JV','JW','JX','JZ','KQ','KX','MX','PX','PZ','QB','QC','QD','QF','QG','QH','QJ','QK','QL','QM','QN','QP','QS','QT','QV','QW','QX','QY','QZ','SX','VB','VF','VH','VJ','VM','VP','VQ','VT','VW','VX','WX','XJ','XX','ZJ','ZQ','ZX']

chars = []
for c in z_340:
    if c not in chars:
        chars.append(c)

def check_start(candidate):
    insertion_point = bisect(words_complete,candidate)
    for j in range(-1,2):
        if insertion_point + j >0 and insertion_point + j < len(words_complete):
            if candidate in words_complete[insertion_point + j]:
                #print("{} is in {}".format(candidate,words_complete[insertion_point +j]))
                return True
    return False



class State(object):

    def __init__(self,cipher_text):
        
        self.cipher_text = cipher_text
        self.substitutions = {}
        self.divisions = [0]
        return

    def update_state(self,c_1,r_1):
        if c_1 not in chars:
            print("{} is not in the cipher_text".format(c_1))
        self.substitutions[c_1] = r_1
        return 

    def state_text(self):
        state_text = ['*']*len(self.cipher_text)
        for s,v in enumerate(self.substitutions):
            indices = [True if v==self.cipher_text[i] else False for i in range(len(self.cipher_text))]
            for index,value in enumerate(indices):
                if value == True:
                    state_text[index] = self.substitutions[v]
        return state_text

    def pretty_print(self):
        t = self.state_text()
        if len(self.divisions) > 0:
            for i in range(1,len(self.divisions)):
                print(''.join(t[self.divisions[i-1]:self.divisions[i]]))
            print(''.join(t[self.divisions[-1]:]))
        else:
            print(t)
        return

    def feasible_breaks(self,starting_break=0):
        #print("inside feasible breaks on starting_break {}".format(starting_break))
        #print("Calling forced breaks")
        #print(self.divisions)
        t = self.state_text()
        break_descendants = []
        #print("Divisions:")
        #print(self.divisions)
        if starting_break >= len(self.divisions):
            #should test if self is feasible
            return [self]
        if starting_break == len(self.divisions)-1:
            potential_wordspace = t[self.divisions[starting_break]:]
        else:
            potential_wordspace = t[self.divisions[starting_break]:self.divisions[starting_break+1]]
        #get the wordspace up to the first wildcard
        if '*' in potential_wordspace:
            wildcard_index = potential_wordspace.index('*')
        else:
            wildcard_index = len(potential_wordspace)
        if wildcard_index == 0:
            if starting_break == len(self.divisions)-1:
                return [self]
        #the text up to the wild card must be the start of a word, or otherwise contain a word and have a missing space
        #first check if it is the start of a word
        candidate_start = ''.join(potential_wordspace[:wildcard_index])
        if len(candidate_start) > 0:
            is_candidate = check_start(candidate_start)
        else:
            is_candidate=False
        if is_candidate:
            return self.feasible_breaks(starting_break=starting_break+1)
        is_space = False
        for word in words_complete:
            if starting_break < len(self.divisions) - 1:
                if len(word) == self.divisions[starting_break + 1] - self.divisions[starting_break]:
                    continue
            if word in candidate_start[:len(word)]:
                is_space = True
                #print("{} is in {}, attempting break at {}".format(word,candidate_start,len(word)))
                S = State(self.cipher_text)
                S.substitutions = copy(self.substitutions)
                S.divisions = copy(self.divisions) + [self.divisions[starting_break] + len(word)]
                F = S.feasible_breaks(starting_break=starting_break +1)
                #print(F)
                break_descendants += F
        return break_descendants


    def generate_descendants(self):
        descendants = []
        for char in chars:
            if char not in self.substitutions:
                #if len(self.substitutions.keys()) == 0:
                #    for r in "I":
                #        S = State(self.cipher_text)
                #        S.substitutions = copy(self.substitutions)
                #        S.divisions = copy(self.divisions)
                #        S.divisions += [1]
                #        S.update_state(char,r)
                #        starting_break = 0
                #        replace_index = self.cipher_text.index(char)
                #        for index,value in enumerate(self.divisions):
                #            if value < replace_index:
                #                starting_break=index
                #        feasible_descendants = S.feasible_breaks(starting_break=starting_break)
                #        descendants += feasible_descendants
                #    break
                shuffle(alphabet)
                for r in alphabet:
                    S = State(self.cipher_text)
                    S.substitutions = copy(self.substitutions)
                    S.divisions = copy(self.divisions)
                    S.update_state(char,r)
                    starting_break = 0
                    replace_index = self.cipher_text.index(char)
                    for index,value in enumerate(self.divisions):
                        if value < replace_index:
                            starting_break=index
                    feasible_descendants = S.feasible_breaks(starting_break=starting_break)
                    descendants += feasible_descendants
                break
        return descendants



class TreeOfKnowledge(object):

    def __init__(self,cipher_text,num_states=2000):
        self.states = [State(cipher_text)]
        self.scores = {}
        self.num_states = num_states
        return

    def rescore(self):
        for state in self.states:
            if state not in self.scores:
                self.scores[state] = self.gibber_jabber(state)
        return

    def prune(self):
        #if our score is less than the node max score just throw it out
        if len(self.states) < self.num_states:
            return
        else:
            for i,state in enumerate(self.states[self.num_states:]):
                del self.scores[state]
                del self.states[self.num_states]
        return

    def next(self):
        #choose the highest score state
        highest_score = 0.0
        highest_state = 0.0
        for state in self.states:
            if self.scores[state] >= highest_score:
                highest_score = self.scores[state]
                highest_state = state
        #print("Highest state was {}".format(highest_state.state_text()))
        #input()
        self.states = self.states + highest_state.generate_descendants()
        self.scores.pop(highest_state)
        self.states.remove(highest_state)
        self.rescore()
        self.states.sort(key= lambda state: self.scores[state],reverse=True)
        self.prune()
        return

    def gibber_jabber(self,state):
        #runs several tests to decide if the text is clearly gibberish.
        #scores text with fewer wildcards (but not gibberish) higher
        #scores text with words (but not gibberish) higher
        #scores text that is clearly gibberish as 0.
        state_text = state.state_text()
        subs = state.substitutions
        targets = set(subs.values())
        symbols = set(subs.keys())
        pre_score = len("".join(state_text).replace("*",""))

        if self._check_unstart(state_text) == 0:
            return 0.0

        if len(targets) + 63 - len(symbols) < 21:
            return 0.0

        if self._total_vowels(state_text) + (340 - pre_score) < .3*340:
            return 0.0

        if self._total_consonants(state_text) + (340 - pre_score) < .5*340:
            return 0.0

        cons = self._consonants_subsequence_length(state_text)
        if cons > 5:
            return 0.0

        if not self._feasible_kill(state_text,spaces=3):
            return 0.0

        singles = self._single_in_a_row(state_text)
        if singles['Z'] >=3:
            return 0.0
        if singles['Y'] >=3:
            return 0.0
        if singles['B'] >=3:
            return 0.0
        if singles['V'] >=3:
            return 0.0
        if singles['I'] >=3:
            return 0.0
        if singles['P'] >=3:
            return 0.0
        if singles['A'] >=3:
            return 0.0
        if singles['U'] >=3:
            return 0.0
        if singles['R'] >=3:
            return 0.0
        for c in singles:
            if singles[c] >= 3:
                return 0.0

        frequency = self._frequency(state_text)
        common_letters = ['E','T','A','O','I','N','S','H','R','L']
        common_sum = 0.
        uncommon_sum = 0.
        for common_letter in common_letters:
            if frequency[common_letter] >= .20*len(state_text):
                return 0.0
            common_sum += frequency[common_letter]
        for c in frequency:
            if c not in common_letters and frequency[c] >= .15*len(state_text):
                return 0.0
            if c not in common_letters:
                uncommon_sum += frequency[c]
        if common_sum < uncommon_sum and pre_score > 80:
            return 0.0

        word_frequency = self._check_common_words(state_text)
        total_frequency = 0.
        frequency_score = 0.
        for k,v in word_frequency.items():
            frequency_score = frequency_score + (v*len(k))
            total_frequency = total_frequency + 1
        if pre_score/340. > .2:
            if total_frequency < 1:
                return 0.0

        return (pre_score / 340.) + (frequency_score/60.) + 100*word_frequency['KILL']

    def _feasible_kill(self,state_text,spaces=1):
        txt = ''.join(state_text)
        count = 0
        kill_strings = ['****','K***','*I**','**L*','***L','KI**','K*L*','K**L','*IL*','*I*L','**LL','KIL*','KI*L','K*LL','*ILL','KILL']
        for kill_string in kill_strings:
            count+= txt.count(kill_string)
            if count > spaces:
                return True
        return False

    def _total_vowels(self,state_text):
        count = 0
        for i in state_text:
            if i in vowels:
                count +=1
        return count

    def _total_consonants(self,state_text):
        count = 0
        for i in state_text:
            if i in consonants:
                count +=1
        return count


    def _bigram_score(self,state_text):
        return

    def _check_targets(self,state_text):
        targets = set(state_text)
        targets.remove('*')
        return len(targets)

    def _check_common_words(self,state_text):
        frequency = {}
        for word in most_common_words:
            frequency[word] = 0
        for word in most_common_words:
            if word in ''.join(state_text):
                frequency[word] = frequency[word] +1
        return frequency

    def _check_unstart(self,state_text):
        start = ''.join(state_text[0:2])
        if start in unstarts:
            #print("{} was in {}".format(start,unstarts))
            #input()
            return 0.
        start = state_text[0:4]
        for vowel in vowels:
            if vowel in start:
                return 1.
        return 0.


    def _consonants_subsequence_length(self,state_text):
        longest_sub_value = 0
        longest_sub_index = 0
        index = 0
        while index < len(state_text):
            if state_text[index] in consonants:
                j = 1
                while index + j < len(state_text) and state_text[index+j] in consonants:
                    j = j+1
                if j > longest_sub_value:
                    longest_sub_value = j
                    longest_sub_index = index
                index = index + (j+1)
            else:
                index = index + 1
        return longest_sub_value

    def _frequency(self,state_text):
        scores = {}
        for c in alphabet:
            scores[c] = 0
        for i in range(len(state_text)):
            if state_text[i] == '*':
                continue
            else:
                scores[state_text[i]] = scores[state_text[i]] + 1
        return scores


    def _single_in_a_row(self,state_text):
        scores = {}
        for c in alphabet:
            scores[c] = 0
        sequence_length = 1
        for i in range(len(state_text)-1):
            if state_text[i] == '*':
                continue
            if state_text[i] == state_text[i+1]:
                sequence_length = sequence_length + 1
            else:
                if sequence_length > scores[state_text[i]]:
                    scores[state_text[i]] = sequence_length
                sequence_length = 1
        return scores

    def vowel_subsequence_length(state_text):
        longest_sub_value = 0
        longest_sub_index = 0
        index = 0
        while index < len(state_text):
            if state_text[index] in vowels:
                j = 1
                while state_text[index+j] in vowels:
                    j = j+1
                if j > longest_sub_value:
                    longest_sub_value = j
                    longest_sub_index = index
                index = index + (j+1)
            else:
                index = index + 1
        return longest_sub_value

    def quad_kill(state_text):
        longest_sub_value = 0
        longest_sub_index = 0
        index = 0
        while index < len(state_text):
            if state_text[index] in consonants:
                j = 1
                while state_text[index+j] in consonants:
                    j = j+1
                if j > longest_sub_value:
                    longest_sub_value = j
                    longest_sub_index = index
                index = index + (j+1)
            else:
                index = index + 1
        return longest_sub_value





S = State(z_340)
T = TreeOfKnowledge(z_340,num_states=100000)
T.rescore()

for i in range(100000):
    T.next()
    print("Raw State:")
    print(T.states[0].state_text())
    print("State with Divisions:")
    T.states[0].pretty_print()
    print(T.states[0].divisions)
