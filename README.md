# Beyond Accuracy: Diagnosing Analogical Transfer in Language Models

ACL anonymous review manuscript derived from the user's thesis. The main text is
8 pages; the complete PDF is 12 pages including limitations, references and appendices.

- `acl_latex.tex` and `sections/`: manuscript source.
- `acl_latex.pdf`: compiled, visually inspected review copy.
- `analysis/inputs/`: minimal retained outcomes, assignment metadata, recorded stage templates and aggregates.
- `analysis/retained_results_audit.json`: offline analysis output and input hashes.
- `scripts/analyze_retained_results.py`: paired question/story analyses; no API calls.
- `scripts/build_figures.py`: figures from bundled counts.
- `scripts/framework_contracts.py`: recorded-contract rendering/continuation adapter, accepting a caller-supplied stateless completion function; not the historical API/retry implementation.
- `MANUSCRIPT_REVIEW_FA.md`: internal review of the written paper.
- `PAPER_NOTES_FA.md`: provenance and version notes.
- `planning/`: prior outline and outline-review records.

## Reproduce the offline analyses

```sh
python3 scripts/analyze_retained_results.py
python3 scripts/build_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build acl_latex.tex
```

Python analysis requires NumPy; figure generation also requires Matplotlib.
The bundled outcomes reproduce summaries without the original thesis workspace.
They do not recreate live API experiments or validate all semantic stage labels.
`--import-workspace` is only for importing retained results from the original local workspace.

On Overleaf, select `acl_latex.tex` as main and pdfLaTeX as compiler. Checked-in
figures allow compilation without Python. Official ACL style files are unchanged.
No model calls or new human annotations were made during this revision.
