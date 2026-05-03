# Move Style Error Data Collection

This repository contains the rules and Python code I used to collect the Move style error dataset described in my BSc dissertation, *AI-Based Code Style Enforcement with CodeLlama* (Mediterranean College, University of Derby, 2026). The work was done as part of a Sui Academic Research collaboration aimed at fine-tuning a Move-specific code language model.

The dataset itself is archived separately on Zenodo and is currently under embargo. The DOI is `10.5281/zenodo.19682589`. This repository contains only the collection code and the annotation rules, not the data.

## What this repository is

When I started the project, I had to figure out how to gather a few hundred Move code samples that contained style issues, label them across six categories, and write a short corrective comment for each one. Doing this by hand from scratch would have meant manually browsing dozens of Sui ecosystem repositories, opening hundreds of `.move` files, and copying snippets into a spreadsheet one at a time.

Instead, I wrote a small set of Python scripts that automated the mechanical parts: cloning repositories, scanning their Move source files, identifying candidate snippets that matched each style category, and using a local Ollama instance to draft an initial Output/Fix comment for each candidate. I then reviewed every candidate by hand, kept the ones that were genuinely useful, edited the drafted comments where needed, and submitted batches to the Sui Foundation for validation.

This repository is the code and the rules I used. It is published so that the workflow is reproducible and so that the next student picking up this kind of work has a starting point.

## How I worked

The collection workflow had four stages.

**Stage 1: Define the rules.** Before writing any code, I wrote out what counted as a style issue in each of six categories, what a good corrective comment looks like, and what kinds of samples to avoid. These rules sit in [`rules/`](rules/) and were the first thing the scanning code referenced.

**Stage 2: Clone the repos.** [`src/clone_repos.py`](src/clone_repos.py) reads a list of Sui ecosystem repository URLs and clones each one into a local working directory. The list I used is in `repos.txt`.

**Stage 3: Scan for candidates.** [`src/scan_for_candidates.py`](src/scan_for_candidates.py) walks every cloned repository, opens each `.move` file, and applies pattern-based heuristics to flag snippets that look like they might match each style category. The output is a CSV of candidate snippets with a suggested category. The script does **not** decide whether a snippet is genuinely a style issue. It surfaces candidates for human review.

**Stage 4: Draft the Output/Fix column.** [`src/generate_outputs.py`](src/generate_outputs.py) takes the candidate CSV and sends each row through a local Ollama instance running the `codellama:instruct` model. The model generates a draft corrective comment, which gets written into the Output/Fix column. The drafts were then reviewed and edited by hand before submission to Sui.

After stage 4, the workflow becomes manual: I read every candidate, decided whether to keep it, edited the drafted comment if needed, and added it to the shared working sheet. The Sui Foundation team reviewed batches at the end of each month and left comments on rows that needed correction. Those corrections were applied across the sheet for consistency.

The final dataset of 368 samples reflects what survived all of this filtering. A large fraction of the candidates the scanner produced were discarded.

## The role of Claude Code

The Python scripts in this repository were developed with the assistance of Anthropic's Claude Code during the project. The annotation rules in `rules/` and the editorial decisions about which samples to keep, how to label them, and how to phrase the final Output/Fix comments were my own. The final dataset was reviewed and approved by a Sui Foundation representative.

I am noting this directly because that is how the work was actually done, and because for a project like this, reproducibility means describing the real workflow rather than a tidied-up version of it.

## Repository structure

```
.
├── README.md                       # this file
├── rules/
│   ├── categories.md               # the six style categories defined
│   ├── annotation_standards.md     # how to write the Output/Fix column
│   └── examples.md                 # example annotated samples
├── src/
│   ├── clone_repos.py              # clones a list of Sui repos locally
│   ├── scan_for_candidates.py      # scans cloned repos for candidate snippets
│   └── generate_outputs.py         # generates draft Output/Fix via Ollama
├── repos.txt                       # list of repo URLs to clone
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Prerequisites

- Python 3.9 or later
- Git installed and on the system path
- [Ollama](https://ollama.ai) installed locally
- The `codellama:instruct` model pulled into Ollama:

  ```
  ollama pull codellama:instruct
  ```

  This downloads the 7B instruction-following variant, which is what I used. Other variants can be substituted by editing the `MODEL` constant in `generate_outputs.py`.

## Running the pipeline

Install dependencies:

```
pip install -r requirements.txt
```

Edit `repos.txt` if needed (the default list mirrors what was used for the original dataset).

Run the three scripts in order:

```
python src/clone_repos.py --input repos.txt --output ./cloned/
python src/scan_for_candidates.py --input ./cloned/ --output candidates.csv
python src/generate_outputs.py --input candidates.csv --output candidates_with_drafts.csv
```

After the third script completes, you have a CSV of candidate snippets with draft Output/Fix comments. From there, the work is human review: open the CSV, evaluate each candidate, edit the drafts, discard anything that does not represent a real style issue, and copy the survivors into a working sheet.

## Disk space warning

Cloning the Sui ecosystem repos pulls down a substantial amount of code. The scanning script only reads `.move` files, but `git clone` brings down everything in each repository, including build artefacts, tests, and other language sources. Plan for several gigabytes of disk in the `./cloned/` directory. The directory can be deleted once `scan_for_candidates.py` has finished.

## What the scanner looks for

The scanner uses simple text-based heuristics, not a Move parser. For each style category it applies a small set of regex patterns to flag candidates:

- **InconsistentNaming**: identifiers that do not match the expected case for their kind. Functions in PascalCase, error constants without the E prefix, structs in snake_case, and so on.
- **Spacing**: missing spaces around operators, after commas, or in type constraint expressions.
- **IncorrectIndentation**: lines whose leading whitespace is not a multiple of four spaces.
- **MissingDocumentation**: public functions, modules, or structs not preceded by a `///` comment.
- **InconsistentImportOrdering**: `use` blocks where standard library imports are not separated from framework imports by a blank line.
- **InconsistentFunctionSignature**: function declarations longer than 100 characters that are not broken across multiple lines.

The heuristics are deliberately permissive. They flag plausible candidates rather than confirmed violations. The reviewer is expected to filter out false positives.

## Why this is not fully automated

A few notes on the boundaries of what is and is not in this repository, because they matter.

The scanner does not decide whether a candidate is genuinely a style issue. Style is contextual, and the same code pattern can be acceptable in one place and a violation in another. Deciding which candidates to keep requires reading the surrounding code and understanding Move conventions. That is the human's job.

Ollama drafts the Output/Fix text, but the drafts were not used as-is. Some were edited heavily, some were rewritten, some were discarded entirely. The final corrective comments in the dataset reflect human editorial work on top of the model's drafts. The Sui Foundation reviewer validated that final wording, not the raw model output.

If you publish a dataset based on this code without doing the manual review and submitting for external validation, the result will not be comparable to the dataset described in the dissertation. The pipeline is one half of the workflow. The other half is judgement.

## Citing the dataset

If you use the workflow or refer to the resulting dataset, please cite:

> Zerkidis, D. (2026) *Move Style Error Dataset: 368 Annotated Move Code Samples for Style Enforcement Evaluation* [Data set]. Zenodo. doi: 10.5281/zenodo.19682589.

## License

MIT. See [`LICENSE`](LICENSE).
