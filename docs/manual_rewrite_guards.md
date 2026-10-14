# Manual rewrite guards (research utility)

Experimental helper only. Does **not** change the frozen E8/E9/E10 evaluation
paths, evaluation sets, or the production Saleem integration.

## Usage

```bash
python scripts/try_saleem_safe.py --style saudi_colloquial --retry-on-guard
# Type multiple lines, finish with :end on its own line
python scripts/try_saleem_safe.py --style saudi_colloquial --required-term 'هلوسة' --text '...'
python -m unittest discover -s tests -p 'test_output_guards.py' -v
```

Specify `--required-term` **only after the term is independently verified
against Siwar and approved by the selector**. No gold labels are injected
automatically. Passing the guard checks lexical presence only; it does not
prove that a term is semantically appropriate. In ambiguous situations it may
be better to omit the term.

The optional retry makes at most one extra generation request. If checks
still fail, the output is rejected and shown only for debugging on stderr.
The rule-based Saudi check flags only a small list of obvious Egyptian forms;
it cannot certify dialect or preservation of meaning. Newline check catches
only loss of **all** line breaks, not every paragraph boundary.

No API calls are made by the unit tests. The actual model still requires the
local environment key and live inference to measure practical improvement.
