# wateval

This repository provides a package which  pulls minimal required scripts
from automatic evaluation procedures enabled in the [WAT Leaderboard]()
for Indian language tasks.

There are sources taken from:

* [mosesdecoder 2.1.1](https://github.com/moses-smt/mosesdecoder/tree/RELEASE-2.1.1)
* [indic_nlp_library](https://github.com/anoopkunchukuttan/indic_nlp_library)

The licenses for the respective repositories and files apply to the
sources taken from each.

## Instructions

This is packaged as a python package, and supposed to work by itself.
You can use the `Evaluator` class in
[wateval/evaluate.py](./wateval/evaluate.py) or the command line
interface, which can be invoked as follows:

```bash
python3 -m wateval.evaluate \
    --hypothesis [HYP] \
    --references [REF1] [REF2] ... \
    [--lang [LANG-ISO-CODE]]
```

