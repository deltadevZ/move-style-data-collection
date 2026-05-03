# Annotation Standards

This document describes how the Output/Fix column should be written. The standards below were refined through several rounds of Sui Foundation feedback and reflect what the reviewer asked for in practice.

## What the Output/Fix column is for

Each row in the dataset has three columns: Code, Label, and Output/Fix. The Output/Fix column contains a short corrective comment written for a developer reading the code, not a compiler-style error message.

The intent is for the corrective comment to read like a code review note that a thoughtful colleague would leave. It identifies what is wrong and how to fix it, briefly, in plain English.

## Format

The corrective comment should be one to three sentences. It should:

- Name the kind of issue at the start (for example, "Spacing issue in function `foo`:" or "Documentation issue:")
- Identify the specific construct affected (the function name, the variable name, the operator, etc.)
- State what to change in concrete terms

Code identifiers and code fragments inside the corrective comment should be wrapped in backticks.

## Examples of good corrective comments

> Spacing issue in function `add`: add spaces around `+` in `copy+ drop` to read `copy + drop`.

> Documentation issue: add `///` doc comment above public function `transfer_funds()` describing its purpose and parameters.

> Naming convention issue: rename `EInvalidAmount` to `E_INVALID_AMOUNT` to follow the `E_` + UPPER_SNAKE_CASE convention for error constants.

> Indentation issue in function `validate()`: use 4-space indentation instead of 2 spaces (multiples of 4).

> Import organisation issue: group `std::vector` imports before `sui::object` imports, separated by a blank line.

These are short, specific, instructive, and refer to actual identifiers in the snippet.

## Examples of corrective comments to avoid

The following styles do not match what the reviewer asked for.

**Compiler-style messages.** Do not write the corrective comment as if it came from a compiler:

> error: expected space at line 3, column 12

This is not how a developer reviewer would phrase feedback.

**Line numbers.** Snippets are extracts, so absolute line numbers are meaningless. Refer to identifiers and constructs instead of "line 4" or "line 12".

**Vague advice.** "Fix the formatting" or "improve the code style" do not tell the developer what to change. Be specific about which construct needs which change.

**Long explanations.** A corrective comment is a code review note, not a tutorial. One to three sentences. If a sample needs a paragraph of explanation, the snippet is probably too complicated to be a useful single-issue example.

## Sublabel consistency

Once a sublabel has been chosen, use the exact same spelling for every sample of that kind. The dataset will be used as training input for a fine-tuning workflow, and inconsistent labels (`StyleError/Naming` vs `StyleError/InconsistentNaming` vs `StyleError/Naming_Convention`) will be treated as different categories by the model.

The six approved sublabels are listed in [`categories.md`](categories.md). Use exactly those strings.

## Submission and review

Samples were submitted in batches to the Sui Foundation working sheet. The reviewer left comments on rows that needed correction, on a sampling basis. The expectation was:

1. Apply the correction to the row that received a comment
2. Apply the same correction pattern to similar rows in the same batch, even if those rows did not receive an individual comment

This kept the dataset internally consistent and reduced the review load on the Sui team.
