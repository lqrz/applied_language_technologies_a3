__author__ = 'root'

import codecs
from collections import Counter
import time
from collections import defaultdict
import sys
from itertools import chain

def satC1(de_pos, en_pos, en_alignment_dict):
    '''
    check that no English words in the phrase pair are aligned to words outside it
    :param de_pos:
    :param en_pos:
    :param en_alignment_dict:
    :return: whether it satisfies the condition
    '''

    # return len(map(lambda e:set(en_alignment_dict[e])-set(de_pos), en_pos)) == 0

    # min_one = False
    min_one = False

    # alignments associated with en positions
    for en in en_pos:
        # de positions associated with the english word
        for a in en_alignment_dict[en]:
            min_one = True
            if a not in de_pos:
                return False

    return min_one

    # check = True
    # min_one = False
    #
    # # alignments associated with en positions
    # for en in en_pos:
    #     # de positions asociated with the english word
    #     for a in en_alignment_dict[en]:
    #         min_one = True
    #         check = check and (True if a in de_pos else False)
    #
    # return check and min_one

def satC2(de_pos, en_pos, de_alignment_dict):
    '''
    check that no foreign words in the phrase pair are aligned to words outside it
    :param de_pos:
    :param en_pos:
    :param de_alignment_dict:
    :return: whether it satisfies the condition
    '''

    min_one = False

    # alignments associated with en positions
    for de in de_pos:
        for a in de_alignment_dict[de]:
            min_one = True
            if a not in en_pos:
                return False

    return min_one

    # check = True
    # min_one = False
    #
    # # alignments associated with en positions
    # for de in de_pos:
    #     for a in de_alignment_dict[de]:
    #         min_one = True
    #         check = check and (True if a in en_pos else False)
    #
    # return check and min_one

def alignments2Words(positions, de_sent, en_sent):
    '''
    Translates positions to words
    :param positions: positions of the german and english sentence
    :param de_sent: german sentence
    :param en_sent: english sentence
    :return: phrase tuple in words
    '''
    return (' '.join(map(de_sent.__getitem__, positions[0])), ' '.join(map(en_sent.__getitem__, positions[1])))

def update_word_count(de_sent, en_sent, en_alignment_dict):
    '''
    updates word counts. Used to compute lexical probabilities.
    :param de_sent:
    :param en_sent:
    :param en_alignment_dict:
    :param de_alignment_dict:
    :return: True
    '''

    global de_word_freq
    global en_word_freq
    global joint_word_freq

    # aligned deutsch words
    de_aligned_total = set()

    for en_word_idx, en_word in enumerate(en_sent):
        en_word_freq[en_word] += 1

        for de_word_idx in en_alignment_dict[en_word_idx]:
            de_word_freq[de_sent[de_word_idx]] += 1
            joint_word_freq[(de_sent[de_word_idx], en_word)] += 1

        if not en_alignment_dict[en_word_idx]:
            # aligned to NULL
            joint_word_freq[(nil, en_word)] += 1
            de_word_freq[nil] += 1 #TODO: or en_word_freq[nil] ?

        de_aligned_total = de_aligned_total.union(en_alignment_dict[en_word_idx])

    for de_word_idx in set(range(len(de_sent))).difference(de_aligned_total):
        en_word_freq[nil] += 1
        joint_word_freq[(de_sent[de_word_idx], nil)] += 1

    return


def compute_lexical_prob(phrase_aligns, f_start, e_start, f_word_freq, f_phrase, e_phrase, direct):
    '''
    computes the lexical probability of a phrase
    :param phrase_aligns: dictionary of {source positions : list of foreign aligned positions}
    :param f_start: starting position of the foreign phrase in the original sentence
    :param e_start: starting position of the source phrase in the original sentence
    :param f_word_freq: foreign word count
    :param f_phrase: foreign phrase
    :param e_phrase: source phrase
    :return: lex probability of the phrase
    '''

    global joint_word_freq

    prob = 1
    for e_pos, f_aligns in phrase_aligns.iteritems():
        if f_aligns:
            if direct:
                prob *= sum(map(lambda x: joint_word_freq[(f_phrase[x - f_start], e_phrase[e_pos - e_start])] \
                                      / float(f_word_freq[f_phrase[x - f_start]]), f_aligns)) / float(len(f_aligns))
            else:
                prob *= sum(map(lambda x: joint_word_freq[(f_phrase[e_pos - f_start], e_phrase[x - e_start])] \
                                      / float(f_word_freq[e_phrase[x - e_start]]), f_aligns)) / float(len(f_aligns))
        else:
            if direct:
                prob *= joint_word_freq[(nil, e_phrase[e_pos - e_start])] / float(f_word_freq[nil])
            else:
                prob *= joint_word_freq[(f_phrase[e_pos - f_start], nil)] / float(f_word_freq[nil])

    return prob

def update_phrase_counts(de_phrase_str, en_phrase_str):
    '''
    updates word and phrase counts
    :param de_phrase_str:
    :param en_phrase_str:
    :return: True
    '''

    global joint_freq
    global de_freq
    global en_freq

    t = (de_phrase_str, en_phrase_str)
    joint_freq[t] += 1
    de_freq[de_phrase_str] += 1
    en_freq[en_phrase_str] += 1

    return

def save_data(t):
    '''
    print data to output files
    :param t: phrase tuple
    :return: True
    '''

    global f_ext_out
    global f_phrase_out
    global f_lex_out
    global f_comb_out
    global lex_e
    global lex_f
    global phrase_probs
    global joint_freq
    global de_freq
    global en_freq

    base = ''
    base += t[0]
    base += ' ||| '
    base += t[1]
    base += ' ||| '

    freq_str = str(de_freq[t[0]])
    freq_str += ' '
    freq_str += str(en_freq[t[1]])
    freq_str += ' '
    freq_str += str(joint_freq[t])

    trans_str = str(phrase_probs[t][0])
    trans_str += ' '
    trans_str += str(phrase_probs[t][1])

    prob_str = trans_str
    prob_str += ' '
    prob_str += str(lex_f[t])
    prob_str += ' '
    prob_str += str(lex_e[t])

    f_ext_out.write(base + freq_str + '\n')
    f_phrase_out.write(base + trans_str + '\n')
    f_lex_out.write(base + prob_str + '\n')
    f_comb_out.write(base + prob_str + ' ||| ' + freq_str + '\n')

    return


def extract_phrases(line_en, line_de, line_align, max_phrase_len):
    '''
    Extracts phrases from a bitext sentence.

    '''

    start = time.time()

    data_alignments = defaultdict(list)

    # resulting phrases
    phrases = []
    phrases_str = set()

    phrases_begin = defaultdict(list)
    phrases_end = defaultdict(list)

    # print 'Extracting phrases for sentence: %s\n' %line_en

    # read english line
    en_sent = line_en.strip().split()  # whitespace tokenization

    # read deutsch line
    de_sent = line_de.strip().split()  # whitespace tokenization

    en_alignment_dict = defaultdict(list)
    de_alignment_dict = defaultdict(list)

    for de_a, en_a in map(lambda x: x.split('-'), line_align.strip().split()):
        de_alignment_dict[int(de_a)].append(int(en_a))
        en_alignment_dict[int(en_a)].append(int(de_a))

    # update_word_count(de_sent, en_sent, en_alignment_dict)

    # generate all possible deutsch phrases
    de_candidate_phrases = [range(i, i + j + 1) for i, _ in enumerate(de_sent) \
                            for j in range(min([len(de_sent), max_phrase_len, len(de_sent) - i]))]

    # generate all possible english phrases
    en_candidate_phrases = [range(i, i + j + 1) for i, _ in enumerate(en_sent) \
                            for j in range(min([len(en_sent), max_phrase_len, len(en_sent) - i]))]

    for en_cand in en_candidate_phrases:
        for de_f in de_candidate_phrases:
            if satC1(de_f, en_cand, en_alignment_dict) and satC2(de_f, en_cand, de_alignment_dict):

                translation = alignments2Words((de_f, en_cand), de_sent, en_sent)
                if translation not in phrases_str:
                    phrases_str.add(translation)
                    phrases.append((de_f, en_cand))

                de_phrase_alignments = {pos: de_alignment_dict[pos] for pos in de_f}
                en_phrase_alignments = {pos: en_alignment_dict[pos] for pos in en_cand}
                data_alignments[(translation[0], translation[1])].append(
                    (de_phrase_alignments, en_phrase_alignments))

                phrases_begin[min(en_cand)].append((de_f, en_cand))
                phrases_end[max(en_cand)].append((de_f, en_cand))

                # update_phrase_counts(translation[0], translation[1])

    # print('Tuned elapsed time: ', time.time() - start)
    # print 'Total nr of extracted phrases: ', len(phrases)

    return phrases_str, phrases, data_alignments, de_alignment_dict, en_alignment_dict, phrases_begin, phrases_end


if __name__ == '__main__':

    start = time.time()

    # debug file paths
    en_filepath = 'prueba.en'
    de_filepath = 'prueba.de'
    align_filepath = 'prueba.aligned'
    # output_filepath = 'prueba.output'

    if len(sys.argv) == 4:
        en_filepath = sys.argv[1]
        de_filepath = sys.argv[2]
        align_filepath = sys.argv[3]
    elif len(sys.argv) > 1:
        print 'Error in params'
        exit()

    # max phrase length
    max_phrase_len = 7

    # file objects
    f_en = codecs.open(en_filepath, 'rb', encoding='utf-8')
    f_de = codecs.open(de_filepath, 'rb', encoding='utf-8')
    f_align = open(align_filepath, 'rb')
    # f_ext_out = codecs.open('phrase_extraction.out', 'wb', encoding='utf-8')
    # f_phrase_out = codecs.open('phrase_probs.out', 'wb', encoding='utf-8')
    # f_lex_out = codecs.open('lexical_probs.out', 'wb', encoding='utf-8')
    # f_comb_out = codecs.open('combined.out', 'wb', encoding='utf-8')

    # lexical probabilities
    word_probs = dict()

    # word counters
    de_word_freq = Counter()
    en_word_freq = Counter()
    joint_word_freq = Counter()

    # phrase counters
    joint_freq = Counter()
    de_freq = Counter()
    en_freq = Counter()

    # probability results
    phrase_probs = dict()
    lex_e = defaultdict(int)
    lex_f = defaultdict(int)

    # NULL word
    nil = '##NULL##'

    phrases_str, phrases, data_alignments = extract_phrases(f_en, f_de, f_align, max_phrase_len)

    print 'Computing probabilities \n'
    # compute probabilities
    for i,(de_phrase_str,en_phrase_str) in enumerate(phrases_str):
        t = (de_phrase_str, en_phrase_str)
        assert joint_freq[t] > 0, 'Error in joint freq count'
        assert en_freq[en_phrase_str] > 0, 'Error in en freq count'
        assert de_freq[de_phrase_str] > 0, 'Error in de freq count'

        p_f_e = joint_freq[t] / float(en_freq[en_phrase_str])
        p_e_f = joint_freq[t] / float(de_freq[de_phrase_str])
        phrase_probs[t] = (p_f_e, p_e_f)

        # compute lex probabilities
        for de_phrase_aligns, en_phrase_aligns in data_alignments[t]:
            de_start = min(de_phrase_aligns.keys())
            en_start = min(en_phrase_aligns.keys())

            prob = compute_lexical_prob(en_phrase_aligns, de_start, en_start, de_word_freq, de_phrase_str.split(), en_phrase_str.split(), True)
            lex_e[t] = max([prob, lex_e[t]])

            prob = compute_lexical_prob(de_phrase_aligns, de_start, en_start, en_word_freq, de_phrase_str.split(), en_phrase_str.split(), False)
            lex_f[t] = max([prob, lex_f[t]])

        if (i+1) % 100 == 0:
            sys.stdout.write(str(i+1) + ' out of ' + str(len(phrases_str)) + '\r')
            sys.stdout.flush()

    print 'Saving to file \n'
    for de_phrase_str,en_phrase_str in phrases_str:
        t = (de_phrase_str, en_phrase_str)
        # save_output
        save_data(t)

    print 'End'