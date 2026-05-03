# Style Categories

This document defines the six style error categories used in the dataset. The names below are the final ones approved by the Sui Foundation reviewer in February 2026. Use these exact names when labelling samples.

Every sample is labelled with one primary category. A snippet may visibly contain more than one issue, in which case the labelling should reflect the most prominent one. If two distinct issues are both worth capturing, the same snippet can appear in the dataset under two separate rows with different labels.

## StyleError/InconsistentNaming

Identifiers in Move follow conventions that depend on the kind of identifier.

- Functions: `snake_case`
- Local variables: `snake_case`
- Modules: `snake_case`
- Structs: `PascalCase`
- Regular constants: `UPPER_SNAKE_CASE`
- Error constants: prefixed with `E` followed by `UPPER_SNAKE_CASE`, for example `E_INVALID_AMOUNT`

A sample belongs in this category when one or more identifiers visibly deviates from the convention for its kind. Examples include functions written in `PascalCase`, structs in `snake_case`, regular constants in `camelCase`, or error constants without the `E` prefix.

## StyleError/Spacing

Whitespace conventions inside expressions, calls, and type constraints.

A sample belongs in this category when whitespace is missing or extraneous around binary operators (`+`, `=`, `*`, etc.), after commas in argument lists or type parameter lists, or inside type constraint expressions like `copy + drop + store`. Spacing inside angle-bracketed type parameters (`<T0, T1>` rather than `<T0,T1>`) also belongs here.

## StyleError/IncorrectIndentation

Indentation in Move follows a four-space convention. Tabs are not used.

A sample belongs in this category when the indentation visibly uses two-space, six-space, or eight-space units, or when indentation is inconsistent across sibling lines within the same block. The convention is multiples of four spaces relative to the enclosing block.

## StyleError/MissingDocumentation

Public functions, public structs, and modules in Move should be preceded by a triple-slash documentation comment (`///`) describing what they do. Inline `//` comments are not documentation; they are inline notes.

A sample belongs in this category when a public function, public struct, or module is declared without a preceding `///` documentation comment. Test-only functions (those marked `#[test_only]`) are still expected to be documented if declared `public`.

## StyleError/InconsistentImportOrdering

`use` declarations in Move should be grouped by source.

- Standard library imports (`std::*`) come first
- Framework imports (`sui::*`) come next, separated from the previous group by a blank line
- Project-specific imports come last, separated from the previous group by a blank line
- Within each group, imports are usually written in alphabetical order

A sample belongs in this category when `use` declarations are interleaved across these groups without separation, or when the groups appear in the wrong order.

## StyleError/InconsistentFunctionSignature

Function signatures that are short fit on one line. Function signatures with more than two or three parameters, or with long parameter types, should be broken across multiple lines with each parameter on its own indented line.

A sample belongs in this category when a long function signature is forced onto a single line, making it hard to read, or when the multi-line break is applied inconsistently (some parameters on the same line as the function name, others on separate lines).
