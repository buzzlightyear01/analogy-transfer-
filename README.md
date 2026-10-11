# Beyond Mapping: A Theory-Grounded Framework for Evaluating Analogical Transfer in Language Models

English ACL review manuscript based on a thesis about measuring analogy effects,
structural transfer, and diagnosis of retrieval, mapping, schema induction,
and adaptation in language models.

- `acl_latex.tex`: main manuscript, using the official ACL anonymous review style.
- `sections/`: five main sections, limitations, ethical considerations, and appendix.
- `acl_latex.pdf`: compiled review copy; eight main pages, eleven pages total in the initial version.
- `custom.bib`: references selected from the thesis bibliography.
- `figures/`: compact figures derived from retained experimental audits.
- `scripts/build_figures.py`: figure-generation source; requires the original thesis workspace's audit files.
- `PAPER_NOTES_FA.md`: Persian notes on chapter correspondence and numerical provenance.
- `reference/acl_template_original.tex`: retained original ACL example.

## Build

Use pdfLaTeX and BibTeX, or:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build acl_latex.tex
```

Copy `build/acl_latex.pdf` to `acl_latex.pdf` after successful compilation and visual verification.
On Overleaf, select `acl_latex.tex` as the main file and pdfLaTeX as the compiler.
The checked-in figures allow the manuscript to compile without the original thesis workspace.

The official ACL style files originate from https://github.com/acl-org/acl-style-files.
This is a research manuscript draft; the authors must review the text and evidence before submission.
