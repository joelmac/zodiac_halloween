from copy import copy
import textwrap
import argparse
from random import shuffle,choices,random
from Classes.ScoreVisitor import ScoreVisitor
from Classes.Node import Node
from Classes import Zodiac
from enum import Enum
from bisect import bisect,bisect_left,bisect_right


class ZodiacPuzzle(Enum):
    Z340 = 'z_340'
    Z408 = 'z_408'
    
    def __init__(self,s):
        if s == 'z_340':
            self.text = "Zodiac 340"
        if s == 'z_408':
            self.text = "Zodiac 408"


parser = argparse.ArgumentParser(description="Listen to the Zodiac.")
parser.add_argument('cipher', type=ZodiacPuzzle, choices=ZodiacPuzzle)
args = parser.parse_args()
cipher = args.cipher
print(cipher.value)

#f = open('resources/z408.txt',mode='r')
if cipher== ZodiacPuzzle.Z340:
    cipher_text,chars = Zodiac.z340();
else:
    cipher_text,chars = Zodiac.z408();

class TreeOfKnowledge(object):

    def __init__(self,cipher_text,num_states=2000,score_visitor=ScoreVisitor(),root_node=None):
        self.states = []
        self._scores = []
        self.num_states = num_states
        self.scorer = score_visitor
        self.solved = False
        self._seen_at_depth = {}
        self.min_depth = 0
        for i in range(65):
            self._seen_at_depth[i] = set()
        self._depths = {}
        if root_node is None:
            self.insert_node(Node(cipher_text))
        else:
            self.insert_node(root_node)
        return

    def depths(self):
        return self._depths

    def rescore(self):
        self.states.sort(key=lambda v: v.score, reverse=True)
        return

    def prune(self):
        #if our score is less than the node max score just throw it out
        #if len(self.states) < self.num_states:
        #    return
        #else:
        #    for i,state in enumerate(self.states[self.num_states:]):
        #        del self.states[self.num_states]
        return

    def remove_node(self,state):
        remove_index = bisect_left(self._scores,state._score)
        offset = 0
        #print(len(self.states))
        #for i in range(-1,2):
        #    if (remove_index + i >= 0) and (remove_index + i < len(self.states)):
        #        print(remove_index + i)
        #        if self._scores[remove_index+i] == state._score:
        #            offset = i
        depth = len(state.substitutions)
        self._depths[depth] = self._depths.get(depth,0) - 1
        if self._depths[depth] < 0:
            print("The number of nodes at this depth is negative!")
            print("Just popped\n {}".format(' '.join(state.colored_state_text())))
            #input()
        popped_state = self.states.pop(remove_index+offset)
        #for k,v in state.substitutions.items():
        #    print(state.substitutions[k])
        #    print(popped_state.substitutions[k])
        #    print(self._scores)
        #    assert(state.substitutions[k] == popped_state.substitutions[k])
        #for k,v in state.substitutions.items():
        #    had_correct_key = True
        #    if state.substitutions[k] != answer_key[k]:
        #        had_correct_key = False
        #        break
        #if had_correct_key:
        #    state.symbol_feas

        _= self._scores.pop(remove_index+offset)
        #assert(state._score == self._scores.pop(remove_index+offset))
        if self.min_depth == depth:
            self._seen_at_depth[depth] = set()
        if self._depths[depth] == 0:
            self.min_depth = min([k for k,v in self._depths.items() if v>0])
            if self.min_depth == depth:
                self._seen_at_depth[depth] = set()
            del self._depths[depth]
        return

    def insert_node(self,state):
        if state.hash() in self._seen_at_depth[len(state.substitutions)]:
            return
        insert_index = bisect(self._scores,state._score)
        depth = len(state.substitutions)
        self._scores.insert(insert_index,state._score)
        self.states.insert(insert_index,state)
        self._depths[depth] = self._depths.get(depth,0) + 1
        self._seen_at_depth[len(state.substitutions)].add(state.hash())
        return


    #to do implement branching visitor
    def next(self):
        r = random()
        branch_state = self.states[0]
        if r < .85:
            branch_state = self.states[-1]
        elif r < .70:
            branch_state = choices(self.states[:self.num_states//10],k=1)[0]
        else:
            d = self.depths()
            min_depth = min([k for k,v in d.items() if v>0])
            for state in self.states:
                if len(state.substitutions) == min_depth:
                    branch_state = state
                    break
        if len(branch_state.substitutions) == 0:
            descendants = branch_state.generate_descendants(scorer=self.scorer,use_first=True)
            for desc in descendants:
                self.insert_node(desc)
        elif len(branch_state.substitutions) == len(chars):
            print("SOLVED!")
            input()
            self.solved = True
            return
        else:
            descendants = branch_state.generate_descendants(scorer=self.scorer)
            for desc in descendants:
                self.insert_node(desc)
        self.remove_node(branch_state)
        #self.rescore()
        #self.states.sort(key= lambda state: state.score,reverse=True)
        #self.prune()
        return

root_node = Node(cipher_text)
head_start = {
        '9': 'I',
        '%': 'L',
        'P': 'I',
        '/':'K',
        'Z':'E',
        'k':'I',
        'O':'N',
        'R':'G',
        '=':'P',
        'p':'E'
        }
head_start = {
        '+': 'L',
        'p': 'K',
        'O': 'I',
        }

head_start = {
        '+': 'L',
        'p': 'F',
        'O': 'I',
        '7': 'E',
        'J': 'R',
        '^': 'E',
        }

head_start = {
        'H': 'T',
        'E': 'H',
        'R': 'I',
        '>': 'S',
        'p': 'I',
        'l': 'S',
        '^': 'T',
        'V': 'H',
        'P': 'E',
        }

head_start = {
        'H': 'I',
        'E': 'A',
        'R': 'M',
        '+': 'L',
        }

head_start = {
        '|': 'T',
        '5': 'H',
        'F': 'E',
        '+': 'T',
        'p': 'A',
        'H': 'I',
        'O': 'S',
        }

head_start = {
        '6': 'B',
        '9': 'E',
        'S': 'C',
        'y': 'A',
        '#': 'U',
        '+': 'S',
        'N': 'E',
        }
head_start = {
        'H': 'I',
        'E': 'A',
        'R': 'M',
        '>': 'T',
        'p': 'H',
        'l': 'E',
        #'^': 'T',
        #'V': 'U',
        #'P': 'L',
        #'k': 'Z',
        #'|': 'O',
        #'1': 'D',
        #'L': 'I',
        #'T': 'A',
        #'G': 'C',
        }
#head_start = {
#       '+': 'N',
##        }
#head_start = {
#       '+': 'N',
#        }

#head_start = {}
answer_key = {
        '9': 'I',
        '%': 'L',
        'P': 'I',
        '/':'K',
        'Z':'E',
        'k':'I',
        'U':'I',
        'O':'N',
        'R':'G',
        '=':'P',
        'p':'E',
        'X':'O',
        '=':'P',
        'B':'L',
        'W':'E',
        'V':'B',
        '+':'E',
        'e':'C',
        'G':'A',
        'Y':'U',
        }
for k,v in head_start.items():
    root_node.update_state(k,v)
#root_node.substitutions = answer_key
print(' '.join(root_node.colored_state_text()))

T = TreeOfKnowledge(cipher_text,num_states=35000000,root_node=root_node)
#T = TreeOfKnowledge(cipher_text,num_states=350000)
#T.rescore()

import time
last_clock = time.time()
speed = 0
last_speed = 0
for i in range(10000000):
    d = T.depths()
    #if i<=3:
    #    print(len(T.states))
    #    input()
    #    for state in T.states:
    #        print("State: {}".format(state.substitutions))
    #input()
    if len(T.states) == 1 or T.solved:
        f = open("output/screen_candy.txt",mode='w')
        f.write("  " + "-.-"*10)
        f.write("\n ")
        f.write(' '.join(T.states[-1].colored_state_text()))
        f.write("  " + ".-."*10)
        f.write("\n"*1)
        f.write(str(cipher.text) + "\n")
        f.write("Evaluating {} states ({} n/s):\n".format(len(T.states),last_speed))
        for i in range(50):
            if i in d:
                f.write("{} nodes at depth {}\n".format(d[i],i))
        f.close()
        #input()
    speed +=1
    curr_time = time.time()
    if curr_time > last_clock + 1/3.:
        f = open("output/screen_candy.txt",mode='w')
        f.write("  " + "-.-"*10)
        f.write("\n ")
        f.write(' '.join(T.states[-1].colored_state_text()))
        f.write("  " + ".-."*10)
        f.write("\n"*1)
        f.write(str(cipher.text) + "\n")
        f.write("Evaluating {} states ({} n/s):\n".format(len(T.states),last_speed*3.))
        for i in range(50):
            if i in d:
                f.write("{} nodes at depth {}\n".format(d[i],i))
        f.close()
        last_clock = curr_time
        last_speed = speed
        speed = 0
    elif max(T.depths().keys()) > 47:
        f = open("output/screen_candy.txt",mode='w')
        f.write("  " + "-.-"*10)
        f.write("\n ")
        s = T.states[0]
        for state in T.states:
            if len(state.substitutions) > 35:
                s = state
        f.write(' '.join(s.colored_state_text()))
        f.write("  " + ".-."*10)
        f.write("\n"*1)
        f.write(str(cipher.text) + "\n")
        f.write("Evaluating {} states ({} n/s):\n".format(len(T.states),last_speed*3.))
        for i in range(50):
            if i in d:
                f.write("{} nodes at depth {}\n".format(d[i],i))
        f.write("DISPLAYING NODE OF DEPTH GREATER THAN 35, MUST PUSH ENTER TO CONTINUE")
        f.close()
        last_clock = curr_time
        last_speed = speed
        speed = 0
        input()
    T.next()
