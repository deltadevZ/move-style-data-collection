# Example Annotated Samples

The following examples show what a finished sample looks like. Each one has the three columns: Code, Label, Output/Fix. These are formatted from production Sui code drawn from the same kinds of repositories the scanner targets.

## Example 1 — InconsistentNaming (function)

**Code:**
```move
public fun CreateUser(ctx: &mut TxContext, name: vector<u8>) {
    let user = User { id: object::new(ctx), name };
    transfer::transfer(user, tx_context::sender(ctx));
}
```

**Label:** `StyleError/InconsistentNaming`

**Output/Fix:**
> Naming convention issue: rename function `CreateUser` to `create_user` to follow the snake_case convention for Move functions.

---

## Example 2 — InconsistentNaming (error constant)

**Code:**
```move
const InvalidAmount: u64 = 1;
const NotEnoughBalance: u64 = 2;
```

**Label:** `StyleError/InconsistentNaming`

**Output/Fix:**
> Naming convention issue: rename `InvalidAmount` to `E_INVALID_AMOUNT` to follow the `E_` + UPPER_SNAKE_CASE convention for error constants.

---

## Example 3 — Spacing (operators)

**Code:**
```move
let total=price+tax;
let result=calculate(a,b,c);
```

**Label:** `StyleError/Spacing`

**Output/Fix:**
> Spacing issue: add spaces around `=`, `+`, and after commas in argument lists for readability.

---

## Example 4 — Spacing (type constraint)

**Code:**
```move
public fun add<T0: drop, T1: copy+ drop+ store>(a0: T0, a1: T1);
```

**Label:** `StyleError/Spacing`

**Output/Fix:**
> Spacing issue in function `add`: add spaces around `+` in `copy+ drop` to read `copy + drop`.

---

## Example 5 — IncorrectIndentation

**Code:**
```move
public fun process(value: u64): bool {
  let x = 5;
  if (value > x) {
    return true
  };
  false
}
```

**Label:** `StyleError/IncorrectIndentation`

**Output/Fix:**
> Indentation issue in function `process()`: use 4-space indentation instead of 2 spaces (multiples of 4).

---

## Example 6 — MissingDocumentation

**Code:**
```move
public fun transfer_coins(
    ctx: &mut TxContext,
    coin: Coin<SUI>,
    recipient: address
) {
    transfer::public_transfer(coin, recipient);
}
```

**Label:** `StyleError/MissingDocumentation`

**Output/Fix:**
> Documentation issue: add `///` doc comment above public function `transfer_coins()` describing its purpose and parameters.

---

## Example 7 — InconsistentImportOrdering

**Code:**
```move
use sui::object;
use std::vector;
use myproject::utils;
use sui::transfer;
use std::option;
use sui::tx_context;
```

**Label:** `StyleError/InconsistentImportOrdering`

**Output/Fix:**
> Import organisation issue: group `std::*` imports first, then `sui::*`, then project-specific imports, with a blank line between each group.

---

## Example 8 — InconsistentFunctionSignature

**Code:**
```move
public fun initialize(ctx: &mut TxContext, name: vector<u8>, symbol: vector<u8>, decimals: u8, supply: u64): TreasuryCap<COIN> {
```

**Label:** `StyleError/InconsistentFunctionSignature`

**Output/Fix:**
> Function signature style issue in `initialize`: break long parameter list across multiple lines for readability.

---

## A note on multi-issue snippets

The two-snippet rule applies here. If a snippet visibly contains both a missing documentation comment and an indentation issue, it can appear in the dataset twice with different labels. Both rows have the same Code, but the Label and Output/Fix differ. This way both training signals are preserved.

This is not the same as labelling a single row with two categories. Each row carries one primary label.
