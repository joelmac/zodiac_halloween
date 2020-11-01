from . import Zodiac
import graph_tool as gt
from graph_tool.all import *
from random import shuffle,choices,random
from math import log
from copy import copy
consonants = "bcdfghjklmnpqrstvwxz".upper()
vowels = "aeiouy".upper()
alphabet =list("abcdefghijklmnopqrstuvwxyz".upper())
shuffle(alphabet)
from termcolor import colored

z_340, z_340_chars = Zodiac.z340()
z_408, z_408_chars = Zodiac.z408()

chars = z_408_chars
chars = z_340_chars
symbols = z_340
char_freq = {}
symbol_indices = {}
for i,symbol in enumerate(symbols):
    char_freq[symbol] = char_freq.get(symbol,0) +1
    symbol_indices[symbol] = symbol_indices.get(symbol,[]) + [i]

vertex_list = list(chars)
vertex_list.sort()
g= Graph(directed=False)
g.add_vertex(len(vertex_list))
for i in range(1,len(z_340)):
    v_ind_1 = vertex_list.index(z_340[i-1])
    v_ind_2 = vertex_list.index(z_340[i])
    e = g.edge(v_ind_1,v_ind_2)
    if e is None:
        g.add_edge(v_ind_1,v_ind_2)

cliques = list(gt.topology.max_cliques(g))


#chars.sort(key=lambda s: char_freq[s],reverse=True)

class Node(object):

    def __init__(self,cipher_text,state_text=None,symbol_feas=None):
        self.cipher_text = cipher_text
        self.substitutions = {}
        if symbol_feas is None:
            self.symbol_feas = {}
            for symbol in chars:
                self.symbol_feas[symbol] = set(alphabet)
        else:
            self.symbol_feas = symbol_feas

        self.divisions = [0]
        self._latest_symbol = None
        self._score = 0
        self._state_text = state_text
        return

    def hash(self):
        s = ""
        for symbol in symbols:
            if symbol in self.substitutions:
                s += symbol
                s += self.substitutions[symbol]
        return hash(s)//1e12

    def get_branch_clique(self):
        lowest_score = 9999999
        candidate_clique = []
        for clique in cliques:
            symbols_left = sum([1 for c in clique if vertex_list[c] not in self.substitutions])
            if symbols_left > 0:
                #score = sum([log(len(self.symbol_feas[vertex_list[c]])) for c in clique if vertex_list[c] not in self.substitutions])/(symbols_left**2)
                min_score = min([(len(self.symbol_feas[vertex_list[c]])) for c in clique if vertex_list[c] not in self.substitutions]) - 1
                score = sum([(len(self.symbol_feas[vertex_list[c]]))*symbols_left for c in clique if vertex_list[c] not in self.substitutions])/(symbols_left**2)
                if min_score == 0:
                    score = 0.
                if score < lowest_score:
                    lowest_score = score
                    candidate_clique = [vertex_list[c] for c in clique]
                if score == 0:
                    return candidate_clique
        return candidate_clique


    @property
    def score(self):
        return self._score

    def accept(self,visitor):
        visitor.visit_node(self)
        return

    @property
    def state_text(self):
        if self._state_text is None:
            state_text = ['*']*len(self.cipher_text)
            for char,value in self.substitutions.items():
                indices = symbol_indices[char]
                for ind in indices:
                    state_text[ind] = value
            self._state_text = state_text
        return ''.join(self._state_text)

    def colored_state_text(self,color='white',highlights='on_magenta'):
        if self._state_text is None:
            state_text = ['*']*len(self.cipher_text)
            for char,value in self.substitutions.items():
                indices = symbol_indices[char]
                for ind in indices:
                    state_text[ind] = value
            self._state_text = state_text
        if self._latest_symbol is not None and color is not None:
            to_display = copy(self._state_text)
            for ind in symbol_indices[self._latest_symbol]:
                to_display[ind] = colored(to_display[ind],color,highlights,attrs=['bold'])
            for line_break in range(16,len(to_display),17):
                to_display[line_break] = to_display[line_break] + "\n"
            return to_display
        return self._state_text

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
        #almost an entirely different method if we have a specific symbol to include
        ret = []
        start_indices = []
        if char is None:
            curr_word = ""
            has_char = False
            for i,v in enumerate(self.cipher_text[:-19]):
                letter = self.substitutions.get(v,' ')
                if letter != " ":
                    curr_word += letter
                else:
                    if len(curr_word) > 0:
                        ret += [curr_word]
                        start_indices += [i - len(curr_word)]
                    curr_word = ""
                    has_char = False
        else:
            used_indices = set()
            for sym_ind in symbol_indices[char]:
                #if sym_ind not in used_indices and sym_ind < len(self.cipher_text[:-18]):
                if sym_ind not in used_indices and sym_ind < len(self.cipher_text):
                    #extract the gibber at sym_ind
                    l_shift = 0
                    r_shift = 0
                    for l_value in range(1,sym_ind+1):
                        if self.cipher_text[sym_ind - l_value] not in self.substitutions:
                            break
                        else:
                            used_indices.add(sym_ind-l_value)
                            l_shift += 1
                    #for r_value in range(1,len(self.cipher_text[:-18]) - sym_ind):
                    for r_value in range(1,len(self.cipher_text) - sym_ind):
                        if self.cipher_text[sym_ind + r_value] not in self.substitutions:
                            break
                        else:
                            used_indices.add(sym_ind+r_value)
                            r_shift += 1
                    ret += [self.state_text[sym_ind - l_shift:sym_ind + r_shift + 1]]
                    start_indices += [sym_ind - l_shift]
            return ret,start_indices
        return ret,start_indices

    def feasible_gibs(self,char=None):
        gibs,start_indices = self.extract_gibs(char=char)
        for i,gib in enumerate(gibs):
            #if i==0 and first_gib_included:
            #    if Zodiac.check_gibber_feasibility(gib,starts_with_word=True)==False:
            #        return False
            if Zodiac.check_gibber_feasibility(gib)==False:
                #print("Ruled out due to gib {}".format(gib))
                return False
        return True

    def cover_gibs(self,char=None,early_breaks=True):
        gibs,start_indices = self.extract_gibs(char=char)
        for i,gib in enumerate(gibs):
            if len(gib) < 3:
                continue
            if start_indices[i] == 0:
                #print("Getting covers for {}, (starts with word)".format(gib))
                (covers_1,covers_2) = Zodiac.get_gibber_covers(gib,True,False)
            else:
                #print("Getting covers for {}".format(gib))
                (covers_1,covers_2) = Zodiac.get_gibber_covers(gib,False,False)
            covers_1 = covers_1.upper()
            covers_2 = covers_2.upper()
            #if len(covers_1) == 0 or len(covers_2) == 0:
                #print("{} had no valid covers".format(gib))
            start_index = start_indices[i]
            if start_index > 0:
                left_symbol = self.cipher_text[start_index-1]
                self.symbol_feas[left_symbol] = self.symbol_feas[left_symbol].intersection(set(covers_1))
            if start_index + len(gib) < len(self.cipher_text):
                right_symbol = self.cipher_text[start_index+len(gib)]
                self.symbol_feas[right_symbol] = self.symbol_feas[right_symbol].intersection(set(covers_2))
            if early_breaks:
                min_len = min([len(v) for k,v in self.symbol_feas.items()])
                if min_len == 0:
                    return self.symbol_feas
        return self.symbol_feas


    def generate_descendants(self,scorer=None,use_first=False):
        descendants = []
        l_vowels = list(vowels)
        l_consonants = list(consonants)
        letters =  l_vowels + l_consonants
        #want to do this only with latest symbol
        if self._latest_symbol is None:
            feas_branches = self.cover_gibs()
        else:
            feas_branches = self.cover_gibs(char=self._latest_symbol)
        least_feasible = 100
        second_least_feasible = 100
        branch_symbol = None
        branch_candidates = set(alphabet)
        least_feasible_value = min([len(v) for v in feas_branches.values()])
        if least_feasible_value==0:
            return []
        best_clique = self.get_branch_clique()
        for symbol in best_clique:
        #for symbol,feas_set in feas_branches.items():
            feas_set = self.symbol_feas[symbol]
            if symbol not in self.substitutions:
                if len(feas_branches[symbol])< least_feasible:
                    second_least_feasible = least_feasible
                    least_feasible = len(feas_branches[symbol])
                    branch_symbol = symbol
                    branch_candidates = feas_branches[symbol]
                    if least_feasible == 1:
                        break
                    elif least_feasible == 0:
                        return []
                elif len(feas_branches[symbol]) < second_least_feasible:
                    second_least_feasible = len(feas_branches[symbol])
        #check to see if there is a symbol sandwiched between two gibbers
        for symbol,ind in symbol_indices.items():
            if least_feasible_value < 5:
                break
            found_symbol = False
            if symbol not in self.substitutions:
                for i in ind:
                    if i > 0 and i < len(self.cipher_text) - 1:
                        if self.cipher_text[i-1] in self.substitutions and self.cipher_text[i+1] in self.substitutions and len(feas_branches[symbol]) < 26:
                            branch_symbol = symbol
                            branch_candidates = feas_branches[symbol]
                            found_symbol = True
                            break
            if found_symbol:
                break

        branch_point_descendants = []
        char = branch_symbol
        for r in branch_candidates:
            replace_index = self.cipher_text.index(char)
            S = Node(self.cipher_text,symbol_feas=copy(self.symbol_feas))
            S.substitutions = copy(self.substitutions)
            S.divisions = copy(self.divisions)
            S.update_state(char,r)
            branch_point_descendants.append(S)
            if scorer is None or True:
                for node in branch_point_descendants:
                    r = random()
                    node._score = 1./second_least_feasible + len(self.substitutions) + round(r,10)
                    #node._score = 1./second_least_feasible
                    #node._score = len(self.substitutions) + round(r,10)
            else:
                scorer.visit_nodes(branch_point_descendants)
        shuffle(branch_point_descendants)
        return branch_point_descendants

    def update_state(self,c_1,r_1,update_text=True):
        self._latest_symbol = c_1
        if c_1 not in chars:
            print("{} is not in the cipher_text".format(c_1))
        self.substitutions[c_1] = r_1
        if self._state_text is not None:
            for ind in symbol_indices[c_1]:
                self._state_text[ind] = r_1
        return 
