import rs_zodiac
from bisect import bisect
consonants = "bcdfghjklmnpqrstvwxz".upper()
vowels = "aeiouy".upper()
alphabet =list("abcdefghijklmnopqrstuvwxyz".upper())

most_common_words = ['the'.upper(),'end'.upper(),'you'.upper(),'that'.upper(),'he'.upper(),'was'.upper(),'for'.upper(),'are'.upper(),'with'.upper(),'his'.upper(),'they'.upper(),'the'.upper(),'this'.upper(),'have'.upper(),'from'.upper(),'one'.upper(),'had'.upper(),'word'.upper(),'but'.upper(),'not'.upper(),'what'.upper(),'all'.upper(),'were'.upper(),'when'.upper(),'your'.upper(),'can'.upper(),'said'.upper(),'there'.upper(),'use'.upper(),'each'.upper(),'which'.upper(),'she'.upper(),'how'.upper(),'their'.upper(),'kill'.upper(),'like'.upper()]

gb = rs_zodiac.GibberChecker()
f = open('resources/words_alpha.txt',mode='r')
words_complete = []
for line in f:
    word = line.replace("\n","").upper()
    words_complete.append(word)
    gb.add_word(word)
for word in most_common_words:
    gb.add_word(word)
f.close()
f = open('resources/letter.txt',mode='r')
for line in f:
    words = line.replace("\n","").upper().split(" ")
    words_complete+=words
    for word in words:
        gb.add_word(word)
f.close()
words_complete.sort()
words_complete_rev = [word[::-1] for word in words_complete]
words_complete_rev.sort()

def z340():
    f = open('resources/z340.txt',mode='r')
    z_340 = f.read().replace("\n","")
    f.close()
    chars = []
    for c in z_340:
        if c not in chars:
            chars.append(c)
    return z_340,chars

def z408():
    f = open('resources/z408.txt',mode='r')
    z_408 = f.read().replace("\n","")
    f.close()
    chars = []
    for c in z_408:
        if c not in chars:
            chars.append(c)
    return z_408,chars


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

def _vowels_in_a_row(state_text):
    sequence_length = 0
    max_sequence_length = 0
    for i in range(len(state_text)):
        if state_text[i] not in vowels:
            sequence_length = 0
        else:
            sequence_length = sequence_length + 1
        if sequence_length > max_sequence_length:
            max_sequence_length = sequence_length
    return max_sequence_length

#someone give me a cool halloween name for the methods
def check_gibber_feasibility(gibber,starts_with_word=False,ends_with_word=False):
    s = _single_in_a_row(gibber)
    for letter in s:
        if s[letter] > 4:
            return False
    if s['I'] >= 3:
        return False
    if s['A'] >= 3:
        return False
    s = _vowels_in_a_row(gibber)
    if s > 4:
        return False
    return gb.check_gibber(gibber,starts_with_word,ends_with_word)

#this function is over 95% of the execution time
def get_gibber_covers(gibber,starts_with_word=False,ends_with_word=False):
    s = _single_in_a_row(gibber)
    for letter in s:
        if s[letter] > 4:
            return ('','')
    if s['I'] >= 3:
        return ('','')
    if s['A'] >= 3:
        return ('','')
    s = _vowels_in_a_row(gibber)
    if s > 4:
        return ('','')
    return gb.count_gibber(gibber,starts_with_word,ends_with_word)


'''
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
'''

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

if __name__ == "__main__":
    print(z340())
