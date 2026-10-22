# ACAIT 2026 editable sources

The local manuscript specified by Shilin Ou is the authoritative input for this package. The original source snapshot is retained locally in `audit/original_manuscript_2026-10-22.zip`.

## Source links

- Paper Overleaf project (existing shared project): https://www.overleaf.com/project/6ad46327aacec45bf553b9c0
- Checked paper source: https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/tree/main/conference/ACAIT2026/paper
- Slides source: https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/tree/main/conference/ACAIT2026/slides
- A0 poster source: https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/tree/main/conference/ACAIT2026/poster
- Shared metadata, vector figures and plot data: https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/tree/main/conference/ACAIT2026/shared

## Import into Overleaf

The three ZIP files under `source_archives/` are self-contained. In Overleaf choose **New Project → Upload Project**, upload the relevant ZIP, and select `main.tex`. Use **pdfLaTeX** for the paper and **XeLaTeX** for slides and poster. The existing shared Overleaf project is unchanged; the checked local sources can be imported as new projects.

- [Paper source ZIP](https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/raw/refs/heads/main/conference/ACAIT2026/source_archives/ACAIT2026_Paper_Source.zip)
- [Slides source ZIP](https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/raw/refs/heads/main/conference/ACAIT2026/source_archives/ACAIT2026_Slides_Source.zip)
- [Poster source ZIP](https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice/raw/refs/heads/main/conference/ACAIT2026/source_archives/ACAIT2026_Poster_Source.zip)

## Local compilation

From the respective project folder:

```sh
# Paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
# Slides or poster
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

The shared figures are editable TikZ/PGFPlots sources, with precompiled vector PDFs included. Their source data are under `shared/data/`. To regenerate a chart, change into `shared/figures/` and compile its `.tex` file with pdfLaTeX. The TeX Gyre Heros font files, Metropolis, IEEEtran, TikZ/PGFPlots and `qrcode` are standard TeX Live packages. All four documents were built with TeX Live 2025.

## Open science and version correspondence

GitHub contains the corrected sensitivity code and results for this revision. The Hugging Face link, https://huggingface.co/datasets/global-nomad-nexus/ImpactOfFossilFuelPrice-WACC, is an archived dataset snapshot at commit `3ad6b5ba657f8c7d92538395a67a03761be8a533` (2026-08-02). It was not silently replaced. The corrected diagnostic outputs in this GitHub revision take precedence over older diagnostic copies in that snapshot.

The 15-minute presentation has an English speaker script in `slides/SPEAKER_NOTES.md`. The 15-slide talk is prepared for the confirmed 15-minute presentation slot. The dedicated authorship/acknowledgments slide was removed; full matching credit strings remain in the editable presenter notes. Three original scientific graphics from the paper are used in the deck, with native LaTeX corrections to the GPR label. The poster is A0 portrait, 841 × 1189 mm, to be printed at actual size.

## Audit

`audit/INTEGRITY_REPORT_zh.md` explains the evidence checks and necessary corrections. `audit/reference_verification.csv` records every retained reference and its supported scope; the evidence-depth column distinguishes full text, abstract and metadata-only checks. `audit/manuscript_integrity_corrections.diff` compares the checked manuscript with the original local snapshot. Downloaded third-party articles/reports and the original private source snapshot are retained locally and are not part of the public source release.

## Visual credits

ACAIT event logo: official 2026 conference website. Duke Kunshan University logo: supplied presentation template. Research diagrams and plots are editable vector artwork; numerical data derive from the supplied archived outputs and the corrected diagnostics. No illustrative photograph is presented as research evidence.
