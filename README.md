<div align="center">

# Fossil Fuel Prices and Capital Cost

### A Machine Learning–Driven Study on Energy Transition

**Shilin Ou · Luyao Zhang · Ming-Chun Huang**<br>
Duke Kunshan University

<p>
  <a href="https://openreview.net/forum?id=ary7hTgqkx"><img alt="Read the paper" src="https://img.shields.io/badge/Paper-OpenReview-8B1E3F?style=for-the-badge"></a>
  <a href="docs/publications/fossil-fuel-wacc-poster.pdf"><img alt="View the poster" src="https://img.shields.io/badge/Poster-PDF-1F5C99?style=for-the-badge"></a>
  <a href="docs/publications/README.md"><img alt="Publication archive" src="https://img.shields.io/badge/Publication_Archive-Details-4B5563?style=for-the-badge"></a>
</p>

<p>
  <a href="#research-overview">Overview</a> ·
  <a href="#repository-structure">Repository</a> ·
  <a href="code">Code</a> ·
  <a href="data">Data</a>
</p>

</div>

---

## Official publication links

- [AAAI-26 AI for Environmental Science Workshop](https://sites.google.com/view/ai4es/home)
- [Read the paper](https://openreview.net/forum?id=ary7hTgqkx)
- [Citation and publication details](docs/publications/README.md) · [BibTeX](CITATION.bib)

## Research overview

This repository supports a study of how fossil-fuel price volatility propagates through inflation and the weighted average cost of capital (WACC) for energy-transition projects. The analysis uses a three-stage modeling pipeline: fossil-fuel price forecasting, inflation prediction, and sector- and region-level WACC estimation.

The public artifact is organized to keep the manuscript, presentation materials, code, and data documentation directly connected. The links above open the official paper record and presentation materials; the folders below contain the corresponding computational materials.

## Research outputs

| Output | Description | Access |
|---|---|:---:|
| Research paper | Official AAAI-26 AI4ES paper record | [OpenReview](https://openreview.net/forum?id=ary7hTgqkx) |
| Academic poster | One-page visual summary | [PDF](docs/publications/fossil-fuel-wacc-poster.pdf) |
| Publication archive | Official paper links and citation | [Open](docs/publications/README.md) |

## Repository structure

| Component | Contents |
|---|---|
| [`code/`](code) | Analysis notebooks, implementation notes, prerequisites, expected outputs, and system configuration |
| [`data/`](data) | Dataset sources, preprocessing steps, and the data dictionary |
| [`docs/publications/`](docs/publications) | Official paper links, citation, and poster |

## Reproducibility guide

- Start with the [`code` overview](code#overview) for the analytical workflow.
- Review [`code` prerequisites](code#prerequisites) before running the notebooks.
- Consult the [`data` documentation](data) for provenance and preprocessing details.
- Use the [`System Configuration Report`](code/System%20Configuration%20Report.ipynb) when comparing environments.

## Acknowledgments

We thank the open-source software community and the maintainers of the World Bank datasets, TensorFlow, scikit-learn, and pandas that support this research.
