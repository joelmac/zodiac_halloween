from copy import copy
import textwrap
from random import shuffle,choices,random
from bisect import bisect
from Classes.ScoreVisitor import ScoreVisitor
from Classes.Node import Node

#f = open('resources/z408.txt',mode='r')
f = open('resources/z340.txt',mode='r')
z_340 = f.read().replace("\n","")
f.close()
f = open('resources/words_alpha.txt',mode='r')
words_complete = []
for line in f:
    words_complete.append(line.replace("\n","").upper())
f.close()
f = open('resources/letter.txt',mode='r')
for line in f:
    words_complete+=line.replace("\n","").upper().split(" ")
f.close()

words_complete.sort()

words_complete_rev = [word[::-1] for word in words_complete]
words_complete_rev.sort()

consonants = "bcdfghjklmnpqrstvwxz".upper()
vowels = "aeiouy".upper()
alphabet =list("abcdefghijklmnopqrstuvwxyz".upper())
shuffle(alphabet)

most_common_words = ['the'.upper(),'end'.upper(),'you'.upper(),'that'.upper(),'he'.upper(),'was'.upper(),'for'.upper(),'are'.upper(),'with'.upper(),'his'.upper(),'they'.upper(),'the'.upper(),'this'.upper(),'have'.upper(),'from'.upper(),'one'.upper(),'had'.upper(),'word'.upper(),'but'.upper(),'not'.upper(),'what'.upper(),'all'.upper(),'were'.upper(),'when'.upper(),'your'.upper(),'can'.upper(),'said'.upper(),'there'.upper(),'use'.upper(),'each'.upper(),'which'.upper(),'she'.upper(),'how'.upper(),'their'.upper(),'kill'.upper(),'like'.upper()]

chars = []
for c in z_340:
    if c not in chars:
        chars.append(c)

def is_words(candidate):
    #Checks to see if the candidate string is a list of words
    if is_word(candidate):
        return True
    else:
        val = False
        for k in range(1,len(candidate)):
            if is_word(candidate[:k]):
                val = val or is_words(candidate[k:])
                if val:
                    return val
    return val


def is_word(candidate):
    #checks to see if the candidate string is a single word
    insertion_point = bisect(words_complete,candidate)
    for j in range(-1,2):
        if insertion_point + j >0 and insertion_point + j < len(words_complete):
            if candidate==words_complete[insertion_point + j]:
                return True
    return False

def check_start(candidate):
    #Checks to see if the candidate string could be the start of a word
    #does not consider adding spaces or clipping the string
    insertion_point = bisect(words_complete,candidate)
    for j in range(-1,2):
        if insertion_point + j >0 and insertion_point + j < len(words_complete):
            if candidate in words_complete[insertion_point + j][:len(candidate)]:
                #print("{} is the beginning of {}".format(candidate,words_complete[insertion_point +j]))
                return True
    return False

def check_end(candidate):
    #Checks to see if the candidate string could be the end of a word
    #does not consider adding spaces or clipping the string
    r_candidate = candidate[::-1]
    insertion_point = bisect(words_complete_rev,r_candidate)
    for j in range(-1,2):
        if insertion_point + j >0 and insertion_point + j < len(words_complete_rev):
            if r_candidate in words_complete_rev[insertion_point + j][:len(r_candidate)]:
                return True
    return False

def _single_in_a_row(state_text):
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


#someone give me a cool halloween name for the methods
def check_gibber_feasibility(gibber,starts_with_word=False,ends_with_word=False):
    s = _single_in_a_row(gibber)
    for letter in s:
        if s[letter] > 3:
            return False
    if is_words(gibber):
        return True
    if starts_with_word == False and ends_with_word == False:
        for word in words_complete:
            if starts_with_word==False and ends_with_word == False:
                if gibber in word:
                    return True
    if ends_with_word == False:
        if check_start(gibber):
            return True
    if starts_with_word == False:
        if check_end(gibber):
            return True
    #sometimes we can clip off the end of another word at the beginning of our gibberish to make it intelligible
    #other cases:
    #   -clip off the beginning of a word (on the right)
    for left_division in range(1,len(gibber)):
        start_fragment = gibber[:left_division]
        valid = False
        if starts_with_word == False:
            if check_end(start_fragment):
                valid = valid or check_gibber_feasibility(gibber[left_division:],starts_with_word=True,ends_with_word=ends_with_word)
        if valid:
            return valid
    return False


class State(object):

    def __init__(self,cipher_text):
        self.cipher_text = cipher_text
        self.substitutions = {}
        self.divisions = [0]
        return

    def accept(self,visitor):
        visitor.visit_node(self)
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
            s = ''
            for i in range(1,len(self.divisions)):
                s+=" {}".format(''.join(t[self.divisions[i-1]:self.divisions[i]]))
            s += " <you can't quite make out the words... zodiac's gibberish>"
            #print(''.join(t[self.divisions[-1]:]))
            print(s)
        else:
            print("<gibberish>")
        return

    def extract_gibs(self,char=None):
        ret = []
        st = self.state_text()[:-30]
        gib_start = 0
        gib_end = gib_start+1
        first_gib_included = False
        if self.cipher_text[0] in self.substitutions:
            first_gib_included =True
        while gib_end < len(st):
            if self.cipher_text[gib_start] not in self.substitutions:
                gib_start = gib_start + 1
                gib_end = gib_start + 1
            else:
                while self.cipher_text[gib_end] in self.substitutions:
                    gib_end = gib_end + 1
                if char is None:
                    ret.append(''.join(st[gib_start:gib_end]))
                else:
                    if char in self.cipher_text[gib_start:gib_end]:
                        ret.append(''.join(st[gib_start:gib_end]))
                gib_start = gib_end
                gib_end = gib_start+1
        #cands = ''.join(self.state_text()[:-30]).split('*')
        #for cand in cands:
        #    if len(cand) > 1:
        #        ret.append(cand)
        return ret,first_gib_included

    def feasible_gibs(self,char=None):
        gibs,first_gib_included = self.extract_gibs(char=char)
        for i,gib in enumerate(gibs):
            if i==0 and first_gib_included:
                if check_gibber_feasibility(gib,starts_with_word=True)==False:
                    return False
            if check_gibber_feasibility(gib)==False:
                #print("Ruled out due to gib {}".format(gib))
                return False
        return True


    #method is FAR too complicated must be simplified
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

    def generate_descendants(self,scorer=None):
        descendants = []
        l_vowels = list(vowels)
        shuffle(l_vowels)
        l_consonants = list(consonants)
        shuffle(l_consonants)
        letters = l_consonants + l_vowels
        for char in chars:
            if char not in self.substitutions:
                branch_point_descendants = []
                for r in letters:
                    S = State(self.cipher_text)
                    S.substitutions = copy(self.substitutions)
                    S.divisions = copy(self.divisions)
                    S.update_state(char,r)
                    starting_break = 0
                    replace_index = self.cipher_text.index(char)
                    if S.feasible_gibs(char=char):
                        branch_point_descendants.append(S)
                        if len(branch_point_descendants) >= len(descendants) and len(descendants)>0:
                            break
                if scorer is None:
                    for node in branch_point_descendants:
                        node.score = 1./len(branch_point_descendants)
                    else:
                        scorer.visit_nodes(branch_point_descendants)
                if len(branch_point_descendants) <= 4:
                    return branch_point_descendants
                elif (len(branch_point_descendants) < len(descendants)) or len(descendants) == 0:
                    descendants = copy(branch_point_descendants)
        shuffle(descendants)
        return descendants

    def update_state(self,c_1,r_1):
        if c_1 not in chars:
            print("{} is not in the cipher_text".format(c_1))
        self.substitutions[c_1] = r_1
        return 



class TreeOfKnowledge(object):

    def __init__(self,cipher_text,num_states=2000,score_visitor=ScoreVisitor()):
        self.states = [State(cipher_text)]
        self.scores = {}
        self.num_states = num_states
        self.scorer = score_visitor
        return

    def depths(self):
        depths = {}
        for state in self.states:
            v = len(state.substitutions.keys())
            depths[v] = depths.get(v,0) + 1
        return depths

    def rescore(self):
        for state in self.states:
            if state not in self.scores:
                self.scores[state] = 0.
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

    def remove_node(self,state):
        del self.scores[state]
        self.states.remove(state)
        return


    #to do implement branching visitor
    def next(self):
        r = random()
        if r < .30:
            branch_state = self.states[0]
        elif r < .70:
            branch_state = choices(self.states[:self.num_states//10],k=1)[0]
        else:
            d = self.depths()
            min_depth = min(list(d.keys()))
            for state in self.states:
                if len(state.substitutions) == min_depth:
                    branch_state = state
                    break
        self.states = self.states + branch_state.generate_descendants(scorer=self.scorer)
        self.remove_node(branch_state)
        self.rescore()
        self.states.sort(key= lambda state: self.scores[state],reverse=True)
        self.prune()
        return



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
T = TreeOfKnowledge(z_340,num_states=50000)
T.rescore()

for i in range(20000):
    T.next()
    d = T.depths()
    f = open("output/screen_candy.txt",mode='w')
    f.write("\n")
    f.write("*-"*10)
    f.write("\n")
    f.write(textwrap.fill(''.join(T.states[0].state_text()),width=17))
    f.write("\n")
    f.write("*-"*10)
    f.write("\n"*1)
    #f.write("The Zodiac Tells you...")
    #T.states[0].pretty_f.write()
    f.write("Evaluating {} states:\n".format(len(T.states)))
    for i in range(50):
        if i in d:
            f.write("{} nodes at depth {}\n".format(d[i],i))
    f.close()
