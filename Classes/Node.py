class Node(object):

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
                    S = Node(self.cipher_text)
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
