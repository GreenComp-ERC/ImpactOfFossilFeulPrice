# Contributing computational research improvements

This personal repository is the staging location for a **code-only** contribution to [GreenComp-ERC/ImpactOfFossilFeulPrice](https://github.com/GreenComp-ERC/ImpactOfFossilFeulPrice). The accepted-paper manuscript, posters, figures and slide sources belong to separate research-publication workflows and must not be included in computational contribution patches.

## Contribution scope

**In scope:** Python scripts, existing model notebooks where portability or correctness is improved, unit tests, environment setup, data-provenance guides, reproducibility documentation, and validation workflows.

**Out of scope for this contribution:** `conference/**`, LaTeX manuscripts, PDF manuscripts, publications and their visual assets, unverified regenerated scientific claims, and third-party copyrighted content.

## Contributor checks

1. Start from a clean branch and preserve the original upstream datasets and archived-model outputs.
2. For each numerical or methodological change, document the original behavior, corrected behavior, scientific interpretation, and whether published numbers must be updated.
3. Run `python -m pip install -r code/requirements-revision.txt`, then `python -m unittest discover -s code -p "test_*.py" -v`.
4. Run `python code/revision_experiments.py` in a disposable checkout. Compare derived outputs numerically rather than assuming bytewise equality between platforms.
5. Check `git diff --name-only` and ensure no `conference/`, `*.tex`, `*.pdf`, or other manuscript/presentation file enters the change set.
6. Provide a change summary identifying tests, inputs, expected output changes, limitations, and license or third-party rights concerns.

## Scientific reproducibility principles

- Distinguish **observations**, **projections**, **archived fitted models**, and **new validation results**.
- Do not compare a saved model forecast to a strict fixed-origin baseline as if both shared an independently verified training split.
- Never infer causal effects from predictive association, in-sample R², or preliminary Granger p-values.
- Preserve units, sample windows, preprocessing, random seeds where known, and regional mappings.
- A passing diagnostic CI run is evidence for the *diagnostic scripts*, not proof of exact neural-network training replication.

## Organizational transfer

First review the changed files in this personal repository. Copy or selectively port only the intended computational paths onto a branch in the organization repository, review the diff, and run its CI before proposing a pull request. Avoid wholesale copying of `conference/` or history rewriting. Repository licensing should be decided by the rights holders; a public repository without an explicit license does not automatically grant reuse rights.
