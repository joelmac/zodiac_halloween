
def gibber_jabber(self,state):
    #runs several tests to decide if the text is clearly gibberish.
    #scores text with fewer wildcards (but not gibberish) higher
    #scores text with words (but not gibberish) higher
    #scores text that is clearly gibberish as 0.
    state_text = state.state_text()
    subs = state.substitutions
    targets = set(subs.values())
    symbols = set(subs.keys())
    symbol_score = len(targets) + len(symbols)
    pre_score = len(''.join(state_text).replace("*",""))


    total_consonants = self._total_consonants(state_text)

    word_frequency = self._check_common_words(state_text)
    total_frequency = 0.
    frequency_score = 0.
    for k,v in word_frequency.items():
        if len(k) > 2:
            frequency_score = frequency_score + (v*len(k)*len(k))
            total_frequency = total_frequency + 1
    return total_consonants + (frequency_score/600.) + 100*word_frequency['KILL'] + 100*word_frequency['LIKE']


class ScoreVisitor(object):

    def __init__(self):

        return

    def visit_node(self,node):
        node._score = 1
        return 

    def visit_nodes(self,nodes):
        score = len(nodes)
        for node in nodes:
            node._score=10./score + len(node.substitutions)/1.
        return


class HeuristicScoreVisitor(ScoreVisitor):

    def __init__(self):
        super().__init__()
        return

class NeuralScoreVisitor(ScoreVisitor):

    def __init__(self,neural_network=None):
        super().__init__()

    #TODO visit node classes
