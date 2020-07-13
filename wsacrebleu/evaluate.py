import os
import argparse
import langid
import sys
import subprocess as sp
from .indic_normalize \
        import IndicNormalizerFactory
from .indic_tokenize \
        import trivial_tokenize as tokenize
import warnings

def run_with_sp_and_return_stdout(cmd):
    output = None
    if sys.version_info[0] < 3:
        output = sp.check_output(cmd, shell=True)
    else:
        try:
            output = sp.run(cmd, shell=True, capture_output=True).stdout
        except:
            output = sp.run(cmd, stdout=sp.PIPE, shell=True).stdout
        output = output.decode("utf-8")
    return output



def compute_bleu(refs, hyp):
    _dir = os.path.dirname(os.path.abspath(__file__))
    moses_mbleu = os.path.join(_dir, 'generic', 'multi-bleu.perl')
    refs = ' '.join(refs)
    cmd = 'perl {} {} < {}'.format(moses_mbleu, refs, hyp)
    output = run_with_sp_and_return_stdout(cmd)
    return output

class Evaluator:
    def __init__(self, srcs, tgt, lang):
        self.srcs = srcs
        self.tgt = tgt
        self.lang = lang
        for src in self.srcs:
            lang = self.infer_langs(src)
            if self.lang == None:
                self.lang = lang
            if not (self.lang == lang):
                warnings.warn("Reference languages seem to be different, please check?")

        self.tgt_lang = self.infer_langs(self.tgt)
        if not(self.tgt_lang == self.lang):
                warnings.warn("Hypothesis Language seem to be different, please check?")


    @staticmethod
    def add_args(parser):
        parser.add_argument('--hypothesis', type=str, required=True)
        parser.add_argument('--references', type=str, nargs='+', required=True)
        parser.add_argument('--lang', type=str, default=None)

    @classmethod
    def build(cls, args):
        return cls(args.references, args.hypothesis, args.lang)
    

    def infer_langs(self, fname):
        first_line = next(open(fname)).strip()
        lang, logprob = langid.classify(first_line)
        return lang

    def run(self):
        tokenized_srcs = []
        for src in self.srcs:
            tokenized_file = self.normalize_and_tokenize(
                    self.lang, src)
            tokenized_srcs.append(tokenized_file)

        tokenized_tgt = self.normalize_and_tokenize(
                self.lang, self.tgt)

        bleu = compute_bleu(tokenized_srcs, tokenized_tgt)
        return {"BLEU": bleu}


    def normalize_and_tokenize(self, lang, fname):
        tokenized_file = fname.replace('/', '_')
        tokenized_file = os.path.join('/tmp', tokenized_file)


        if lang == 'en':
            dir_path = os.path.dirname(os.path.realpath(__file__))
            perl_tokenizer = os.path.join(dir_path, 'scripts', 'tokenizer.perl')
            cmd = 'perl {} -l en < {} > {}'.format(perl_tokenizer, fname, tokenized_file)
            output = run_with_sp_and_return_stdout(cmd)

        else:
            factory = IndicNormalizerFactory()
            normalizer = factory.get_normalizer(lang, remove_nuktas=False)
            with open(fname) as istream:
                with open(tokenized_file, 'w+') as ostream:
                    for line in istream:
                        line = line.strip()
                        line = normalizer.normalize(line)
                        tokens = tokenize(line, lang=self.lang)
                        tokenized_line = ' '.join(tokens)
                        ostream.write(tokenized_line + '\n')
                        # print(tokenized_line, file=ostream)
        return tokenized_file

def main():
    parser = argparse.ArgumentParser()
    Evaluator.add_args(parser)

    args = parser.parse_args()
    evaluator = Evaluator.build(args)
    stats = evaluator.run()
    for key, val in stats.items():
        print(key, val)

if __name__ == '__main__':
    main()
