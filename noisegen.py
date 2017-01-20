import random
import time
import string

class noisegen(object):
    isverbose = False
    time_stamp = time.time()

    log_file = open("noisegen"+str(time_stamp)+".log", "w") if isverbose==True else []
    letters = string.printable

    def __init__(self):
        """
        Constructor

        >>> from noisegen import noisegen
        >>> ng = noisegen()
        """
        if self.isverbose:
            print >> self.log_file, "In 'noisegen' class"


    def omit_1_let(self, text):
        if len(text.strip()) == 0:
            return text
        l = len(text)
        r = random.randint(0, l - 1)
        if self.isverbose: print "l = %s, r = %s" % (l, r)
        return text[0:r] + text[r + 1:]

    def omit_let(self, text, k=1):
        """
        Skip letter (omission), e.g., Chicago -> Chicgo

        Deletion
        """
        for m in xrange(k):
            new_text = self.omit_1_let(text)
            if new_text == text:
                return text
            else:
                text = new_text

        return text


    def double_1_let(self, text):
        if len(text.strip()) == 0:
            return text
        l = len(text)
        r = random.randint(0, l - 1)
        if self.isverbose: print "l = %s, r = %s" % (l, r)
        return text[0:r] + text[r] + text[r:]

    def double_let(self, text,k=1):
        """
        Double letters, e.g., Chicago -> Chhicago

        Insertion
        """
        for m in xrange(k):
            text = self.double_1_let(text)

        return text


    def skip_1_space(self, text):
        if len(text)==0:
            return text

        idx = [j for j in range(len(text)) if text.startswith(' ', j)]
        l = len(idx)
        if self.isverbose:
            print "idx = %s, l = %s" % (idx, l)

        if l == 0:
            return text
        if l == 1:
            i = idx[0]
            if self.isverbose: print "i = %s" % (i)
        else:
            r = random.randint(0, l - 1)
            i = idx[r]
            if self.isverbose: print "r = %s, i = %s" % (r, i)
        return text[0:i] + text[i + 1:]


    def skip_space(self, text, k=1):
        """
        Skip spaces, e.g., Chicago IL -> ChicagoIL

        Deletion
        """
        for m in xrange(k):
            new_text = self.skip_1_space(text)
            if new_text == text:
                return text
            else:
                text = new_text

        return text


    def tran_1_lets(self, text):
        if len(text.strip()) == 0:
            return text
        l = len(text)
        r = random.randint(0, l - 1)
        if self.isverbose: print "l = %s, r = %s" % (l, r)
        return text[0:r - 1] + text[r] + text[r - 1] + (text[r + 1:] if r + 1 <= l - 1 else "")


    def tran_lets(self, text, k=1):
        """
        Transposed character, e.g., Chicago -> hCicago

        Permutation
        """
        for m in xrange(k):
            text = self.tran_1_lets(text)

        return text


    def wrong_1_let(self, text):
        if len(text) == 0:
            return text
        l = len(text)
        r = random.randint(0, l - 1)
        if self.isverbose: print "l = %s, r = %s" % (l, r)
        return text[0:r] + random.choice(self.letters) + \
               (text[r + 1:] if r + 1 <= l - 1 else "")

    def wrong_let(self, text, k=1):
        """
        Wrong key, e.g., Chicago -> Cgicago

        Mutation
        """
        for m in xrange(k):
            text = self.wrong_1_let(text)

        return text


    def insert_1_let(self, text):
        if len(text) == 0:
            return random.choice(self.letters)
        l = len(text)
        r = random.randint(0, l - 1)
        if self.isverbose: print "l = %s, r = %s" % (l, r)
        return text[0:r] + random.choice(self.letters) + text[r:]

    def insert_let(self, text, k):
        """
        Inserted key, e.g., Chicago -> Choicago

        Insertion
        """
        for m in xrange(k):
            text = self.insert_1_let(text)

        return text

    def call_method(self, t=1, text="", k=1):
        text_ = ""
        if t == 1:
            text_ = self.omit_let(text, k)
        elif t == 2:
            text_ = self.double_let(text, k)
        elif t == 3:
            text_ = self.skip_space(text, k)
        elif t == 4:
            text_ = self.tran_lets(text, k)
        elif t == 5:
            text_ = self.wrong_let(text, k)
        elif t == 6:
            text_ = self.insert_let(text, k)

        return text_

"""

Phonetics
"""




if __name__=='__main__':
    """
    To get help:

    $python noisegen.py -h

    Example:

    $python noisegen.py --t 2 --s "55 E Monroe Ave Chicago IL 660603" --k 2
    555E Monroe Ape Chicago IL .60603

    """
    text =  "55 E Monroe Ave Chicago IL 60603"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--t', '--type of errors', type=int, default=1, help='1: omit letter (default); 2: repeat a letter; 3: skip a space; 4: transpose two letters; 5: a wrong letter;  6: insert a letter', metavar='t')
    parser.add_argument('--s', '--string of text', type=str, default=text, help='string of input text', metavar='text')
    parser.add_argument('--k', '--number of errors', type=str, default="1", help='number of errors', metavar='r')
    args = parser.parse_args()
    t = args.t
    text = args.s
    k = int(args.k)

    ng = noisegen()
    if ng.isverbose: print "t = %s, text = %s, k = %s\n" % (t, text, k)
    random.seed(0)
    text_ = ng.call_method(t,text,k)

    print text_
