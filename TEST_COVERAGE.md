# TEST_COVERAGE

## Scope and Method (2026-05-22)

This document is an assessment/plan only. No test source files in the repository were modified.

I used `mini-moul.sh` (the `mini` alias is not available in this shell) as the runtime reference and ran:

- `./mini-moul.sh --target 42piscine/C00 --no-norminette --no-color`
- `./mini-moul.sh --target 42piscine/C01 --no-norminette --no-color`
- ... through `C09`

I also ran controlled probes from `/tmp` copies of `42piscine/C07` to validate diagnostic weaknesses (array diff behavior, false-positive conditions, and output formatting defects) without touching repository test sources.

---

## Baseline Runner Status (Current 42piscine)

| Assignment | Result | Key Notes |
|---|---:|---|
| C00 | 88/100 | `ex08` missing in student tree |
| C01 | 100/100 | all current tests pass |
| C02 | 92/100 | `ex11` warning-only `-Werror` fallback in student code, `ex12` placeholder/fails |
| C03 | 100/100 | all current tests pass |
| C04 | 100/100 | all current tests pass |
| C05 | 88/100 | `ex08` missing in student tree |
| C06 | 100/100 | all current tests pass |
| C07 | 100/100 | `ex04` warning-only `-Werror` fallback in student code |
| C08 | 100/100 | all current tests pass |
| C09 | N/A | runner reports tests unavailable |

Note: warning-only `-Werror` fallbacks shown above for `C02/ex11` and `C07/ex04` are student-file issues; they are not test harness compile bugs.

---

## Cross-Cutting Issues (Affect Multiple Exercises)

### 1) Output capture and diff quality is inconsistent

- Many tests still capture output via `output.txt` + `fgets`, which is fragile for binary/null-byte cases and newline-bound outputs.
- Failure reporting is uneven: some tests print full useful context, some print only a scalar or a generic sentence.
- Color escapes are printed by C test binaries directly, so `--no-color` still shows ANSI sequences in failure details.

### 2) Resource/memory hygiene issues in harness code

- `C06` tests leak memory in `modify_string()` helper return values (never freed).
- `C03/ex00` uses `strdup` in test data without freeing.
- Some tests do not check `open`/`fopen`/`dup`/`dup2` return values before use.

### 3) Placeholder or unavailable tests remain

- `C02/ex12` and `C05/ex08` are placeholders.
- `C09` has no tests in `mini-moul/tests` yet.

### 4) Subject-coverage gaps remain in several exercises

- Important edge cases (limits/overflow/whitespace variants/null behavior/malloc failure paths) are still missing in parts of C02-C07.

### 5) Optional C++ modernization path is viable

- A C++ test harness can improve diagnostics, memory safety, RAII cleanup, and vector/string diffs while still testing C student code via `extern "C"` wrappers.
- This can be done incrementally exercise-by-exercise so behavior/scoring does not change substantially.

---

## Assignment-by-Assignment, Exercise-by-Exercise Review

## C00

### ex00 `ft_putchar.c`

- Current status: PASS.
- Current checks: multiple character cases including `'\0'` and `\xFF`.
- Issues:
  - Uses `fgets` on captured file; not binary-safe for null byte validation.
  - `"\0"` expected string is effectively empty string; does not prove a byte was emitted.
- Plan:
  - Switch output capture to pipe + byte-count comparison.
  - Add explicit byte-length assertion (`1` byte for each call).

### ex01 `ft_print_alphabet.c`

- Current status: PASS.
- Current checks: exact single expected alphabet string.
- Issues:
  - Single case only.
  - `fgets`/file-based capture pattern.
- Plan:
  - Keep same behavior check; migrate to shared capture helper.
  - Add explicit output length assertion (`26`).

### ex02 `ft_print_reverse_alphabet.c`

- Current status: PASS.
- Current checks: exact reverse alphabet string.
- Issues: same capture fragility as ex01.
- Plan: same as ex01.

### ex03 `ft_print_numbers.c`

- Current status: PASS.
- Current checks: exact `0123456789`.
- Issues: same capture fragility as ex01.
- Plan: same as ex01.

### ex04 `ft_is_negative.c`

- Current status: PASS.
- Current checks: positive/negative/zero and int bounds.
- Issues:
  - Compares only first output character via `strncmp(..., 1)`.
  - Extra unexpected output can still pass.
- Plan:
  - Require exact one-character output and exact byte length.

### ex05 `ft_print_comb.c`

- Current status: PASS.
- Current checks: full expected output string.
- Issues:
  - One monolithic comparison only; failure diff is unreadably large.
- Plan:
  - Keep exact-output requirement.
  - Improve diff output by showing first mismatch index + short surrounding slice.

### ex06 `ft_print_comb2.c`

- Current status: PASS.
- Current checks: full expected output string.
- Issues:
  - Same monolithic-diff readability issue as ex05.
- Plan:
  - Same targeted mismatch reporting as ex05.

### ex07 `ft_putnbr.c`

- Current status: PASS.
- Current checks: `0`, `INT_MIN`, `INT_MAX`, `42`, `-42`.
- Issues:
  - File + `fgets` capture pattern.
- Plan:
  - Keep cases; migrate to byte-exact capture helper.

### ex08 `ft_print_combn.c`

- Current status: MISSING in current student tree.
- Current checks in harness: `n=2` and `n=3` long expected strings.
- Issues:
  - Not currently exercised against user code.
  - Diff readability will be poor for long outputs.
- Plan:
  - Keep existing two cases as baseline.
  - Add compact mismatch diagnostics; later extend with boundary `n=1` and `n=9`.

---

## C01

### ex00 `ft_ft.c`

- Current status: PASS.
- Current checks: single pointer write to `42`.
- Issues: very narrow coverage.
- Plan: add at least 1-2 additional initial values.

### ex01 `ft_ultimate_ft.c`

- Current status: PASS.
- Current checks: one deep-pointer chain.
- Issues: narrow coverage, no negative/zero initial value variants.
- Plan: add extra value variants while preserving function contract.

### ex02 `ft_swap.c`

- Current status: PASS.
- Current checks: several numeric pairs.
- Issues:
  - Does not test aliasing case (`a == b` same pointer).
  - Message text suggests overflow case but values are equal and non-extreme.
- Plan:
  - Add same-pointer alias case.
  - Clarify test descriptions.

### ex03 `ft_div_mod.c`

- Current status: PASS.
- Current checks: positive divisions.
- Issues: no negative operand cases; no explicit behavior guard around division by zero.
- Plan:
  - Add signed operand combinations.
  - Keep division-by-zero out unless subject explicitly defines handling.

### ex04 `ft_ultimate_div_mod.c`

- Current status: PASS.
- Current checks: positive divisions.
- Issues: same as ex03.
- Plan: same as ex03.

### ex05 `ft_putstr.c`

- Current status: PASS.
- Current checks: empty, long, special characters.
- Issues: file + `fgets` capture pattern.
- Plan: migrate to shared byte capture helper.

### ex06 `ft_strlen.c`

- Current status: PASS.
- Current checks: empty, small, long, embedded-null literal case.
- Issues: generally fine; no randomized coverage.
- Plan:
  - Keep current deterministic set.
  - Optional fuzz/differential add-on against libc `strlen` (bounded input set).

### ex07 `ft_rev_int_tab.c`

- Current status: PASS.
- Current checks: one fixed 6-element array.
- Issues:
  - Only one scenario.
  - Failure message gives no expected/got element diff.
- Plan:
  - Add cases for size `0`, size `1`, odd/even lengths, duplicates.
  - Print first mismatch index and both arrays.

### ex08 `ft_sort_int_tab.c`

- Current status: PASS.
- Current checks: one fixed 6-element array.
- Issues:
  - Very narrow coverage.
  - Failure text incorrectly says `Failed to reverse tab.`
  - No expected/got detailed diff.
- Plan:
  - Add already-sorted, reverse-sorted, duplicates, negatives.
  - Improve failure diagnostics to indexed array diff.

---

## C02

### ex00 `ft_strcpy.c`

- Current status: PASS.
- Current checks: simple copy content checks.
- Issues:
  - Does not verify return pointer identity (`return == dest`).
  - Small case set.
- Plan:
  - Add pointer identity assertion and empty-source case.

### ex01 `ft_strncpy.c`

- Current status: PASS.
- Current checks: `n` smaller/equal/greater than source length.
- Issues:
  - Does not assert zero-padding bytes when `n > src_len`.
- Plan:
  - Validate post-copy buffer bytes beyond first null.

### ex02 `ft_str_is_alpha.c`

- Current status: PASS.
- Current checks: alpha/non-alpha examples.
- Issues: no explicit empty-string case.
- Plan: add empty-string should return `1`.

### ex03 `ft_str_is_numeric.c`

- Current status: PASS.
- Current checks: numeric/non-numeric examples.
- Issues: no explicit empty-string case.
- Plan: add empty-string case.

### ex04 `ft_str_is_lowercase.c`

- Current status: PASS.
- Current checks: lowercase/non-lowercase examples.
- Issues: no explicit empty-string case.
- Plan: add empty-string case.

### ex05 `ft_str_is_uppercase.c`

- Current status: PASS.
- Current checks: uppercase/non-uppercase examples.
- Issues: no explicit empty-string case.
- Plan: add empty-string case.

### ex06 `ft_str_is_printable.c`

- Current status: PASS.
- Current checks: printable and control-char sample.
- Issues: no explicit empty-string case.
- Plan: add empty-string case.

### ex07 `ft_strupcase.c`

- Current status: PASS.
- Current checks: lowercase/mixed/symbol combos.
- Issues:
  - No assertion that returned pointer equals input pointer.
- Plan:
  - Add pointer identity assertion.
  - Add already-uppercase idempotence case.

### ex08 `ft_strlowcase.c`

- Current status: PASS.
- Current checks: uppercase/mixed/symbol combos.
- Issues: same as ex07.
- Plan: same as ex07.

### ex09 `ft_strcapitalize.c`

- Current status: PASS.
- Current checks: decent baseline including punctuation and spacing.
- Issues:
  - Known digit-boundary gap (`123AA`-style expectation).
- Plan:
  - Add digit-transition edge cases.

### ex10 `ft_strlcpy.c`

- Current status: PASS.
- Current checks: truncation and return length cases.
- Issues:
  - Missing explicit `size == 0` case.
  - Not checking destination untouched semantics when size is zero.
- Plan:
  - Add `size==0` with pre-filled destination sentinel.
  - Add more boundary cases around `size==1` and exact-fit lengths.

### ex11 `ft_putstr_non_printable.c`

- Current status: PASS with compiler warning report (`-Werror` fallback path).
- Current checks: multiple printable/non-printable conversion cases.
- Issues in test file:
  - One case label/value mismatch (`"\x01"` description, but source is `"\t01"`).
  - Duplicated conceptual cases.
  - File/`fgets` output capture style.
- Plan:
  - Normalize/unique case list.
  - Keep exact byte-string expectation checks.
  - Move to shared capture helper for consistency.

### ex12 `ft_print_memory.c`

- Current status: FAIL (placeholder test intentionally fails).
- Current checks: none substantive.
- Issues:
  - Placeholder (`Sorry. Test not yet implemented`).
  - Includes student file directly; if student has `main`, compile conflicts occur.
- Plan:
  - Replace with deterministic real tests:
    - return pointer equals input pointer
    - `size==0` emits nothing
    - known formatting sample(s), line count, printable/non-printable encoding
  - Ensure harness compiles regardless of student-added debug `main` (or explicitly reject with clear reason).

---

## C03

### ex00 `ft_strcmp.c`

- Current status: PASS.
- Current checks: broad case set including embedded-null literals.
- Issues:
  - Uses `strdup` in test data and never frees it.
- Plan:
  - Free dynamic test strings before exit.
  - Optional: validate sign behavior rather than exact difference where subject allows flexibility.

### ex01 `ft_strncmp.c`

- Current status: PASS.
- Current checks: many `n` and string-shape scenarios.
- Issues:
  - Comparator asserts sign class (negative/zero/positive), not exact numeric diff.
  - Good for portability, but can still miss exact-byte-diff bugs if strictness is desired.
- Plan:
  - Keep sign-based default (non-breaking).
  - Add optional strict mode for exact `unsigned char` subtraction parity.

### ex02 `ft_strcat.c`

- Current status: PASS.
- Current checks: basic concatenation cases.
- Issues:
  - No explicit NUL-placement validation beyond `strcmp`.
  - No return-pointer identity assertion.
- Plan:
  - Pre-fill buffers with non-zero sentinels, assert terminator location.
  - Check returned pointer equals destination.

### ex03 `ft_strncat.c`

- Current status: PASS.
- Current checks: core concat scenarios.
- Issues:
  - No return-pointer identity assertion.
  - Limited boundary coverage for `n=0`.
- Plan:
  - Add `n=0` and pointer identity assertions.

### ex04 `ft_strstr.c`

- Current status: PASS.
- Current checks: found/not-found/empty-needle examples.
- Issues:
  - For `NULL` expected output, diagnostics print `%s` pointers (fragile/misleading).
  - No pointer-identity check for empty needle (`result == str`).
- Plan:
  - Improve null-safe diagnostics.
  - Add pointer identity assertion for empty needle.

### ex05 `ft_strlcat.c`

- Current status: PASS.
- Current checks: destination string outcomes.
- Issues:
  - Return value semantics are not asserted.
- Plan:
  - Add return-value contract checks (`initial_dest_len + src_len`).
  - Preserve current content checks.

---

## C04

### ex00 `ft_strlen.c`

- Current status: PASS.
- Current checks: same baseline as C01/ex06.
- Issues: acceptable baseline; could be expanded.
- Plan: optional differential/randomized add-on.

### ex01 `ft_putstr.c`

- Current status: PASS.
- Current checks: multiple strings.
- Issues: file/`fgets` capture style.
- Plan: migrate to shared capture helper.

### ex02 `ft_putnbr.c`

- Current status: PASS.
- Current checks: good boundary values.
- Issues: file/`fgets` capture style.
- Plan: migrate to shared capture helper.

### ex03 `ft_atoi.c`

- Current status: PASS.
- Current checks: broad set including signs and boundary values.
- Issues:
  - Whitespace coverage does not fully include all `isspace` variants.
  - Overflow expectations are platform-specific style checks.
- Plan:
  - Add `\f\n\r\t\v` cases.
  - Keep overflow checks but document intended interpretation clearly.

### ex04 `ft_putnbr_base.c`

- Current status: PASS.
- Current checks: valid bases, invalid bases, INT bounds, zero.
- Issues: file/`fgets` capture style only.
- Plan: migrate to shared capture helper and improve diff slicing for long outputs.

### ex05 `ft_atoi_base.c`

- Current status: PASS.
- Current checks: few valid signed conversions.
- Issues:
  - Limited invalid-base/invalid-input coverage.
- Plan:
  - Add duplicate-char base, `+/-` in base, whitespace-only input, invalid-digit termination, zero case.

---

## C05

### ex00 `ft_iterative_factorial.c`

- Current status: PASS.
- Current checks: small positive values, negative, 10.
- Issues: no upper-bound overflow/limit behavior checks.
- Plan: add near-overflow boundaries (`12`, `13`) with expected subject behavior.

### ex01 `ft_recursive_factorial.c`

- Current status: PASS.
- Current checks: same as ex00.
- Issues: same as ex00.
- Plan: same as ex00.

### ex02 `ft_iterative_power.c`

- Current status: PASS.
- Current checks: positive, negative exponent.
- Issues: missing `0^0` edge case.
- Plan: add `base=0, power=0` expected `1` per current project interpretation.

### ex03 `ft_recursive_power.c`

- Current status: PASS.
- Current checks: same pattern as ex02.
- Issues: missing `0^0` edge case.
- Plan: same as ex02.

### ex04 `ft_fibonacci.c`

- Current status: PASS.
- Current checks: small indices and negative input.
- Issues: no medium/high index validation.
- Plan: add representative larger safe index cases (e.g., 20, 30) within int range.

### ex05 `ft_sqrt.c`

- Current status: PASS.
- Current checks: small values and negative input.
- Issues:
  - Missing large worst-case input (`INT_MAX`) performance/correctness coverage.
- Plan:
  - Add `2147483647 -> 0` case.

### ex06 `ft_is_prime.c`

- Current status: PASS.
- Current checks: basic small primes/composites.
- Issues: limited larger prime/composite coverage.
- Plan:
  - Add medium/large boundary values and semiprimes.

### ex07 `ft_find_next_prime.c`

- Current status: PASS.
- Current checks: small values and negative input.
- Issues: limited larger input/performance coverage.
- Plan:
  - Add larger near-prime values and `INT_MAX` neighborhood behavior.

### ex08 `ft_ten_queens_puzzle.c`

- Current status: MISSING in current student tree; test is placeholder anyway.
- Current checks: none substantive.
- Issues:
  - Placeholder always fails (`Sorry, test not implemented yet`).
- Plan:
  - Implement real checks:
    - return value `724`
    - output line count `724`
    - basic format sanity per line.

---

## C06

### ex00 `ft_print_program_name.c`

- Current status: PASS.
- Current checks: runs copied/compiled student program, compares output.
- Issues:
  - Harness uses `system` + `popen` inside test binary (redundant and fragile).
  - `modify_string()` allocates without free (leak).
  - Error path contains unreachable cleanup after `exit`.
- Plan:
  - Replace shell-command strategy with direct `fork/execve` harness helper.
  - Remove dynamic-string leak path.
  - Keep same single-scenario behavior expectations.

### ex01 `ft_print_params.c`

- Current status: PASS.
- Current checks: single argv scenario.
- Issues:
  - Same `system`/`popen` and leak concerns as ex00.
  - No explicit check for missing/extra output lines count.
- Plan:
  - Move to structured argv runner helper.
  - Assert exact line count and content.

### ex02 `ft_rev_params.c`

- Current status: PASS.
- Current checks: single argv scenario.
- Issues: same as ex01.
- Plan: same as ex01.

### ex03 `ft_sort_params.c`

- Current status: PASS.
- Current checks: single argv scenario.
- Issues: same as ex01.
- Plan: same as ex01; add ties/duplicate-arg scenario.

---

## C07

### ex00 `ft_strdup.c`

- Current status: PASS.
- Current checks: empty/non-empty/long/embedded-null literal source.
- Issues:
  - Does not verify deep-copy pointer inequality (`result != src`).
  - `src == NULL` branch exists but is not exercised.
- Plan:
  - Add pointer inequality assertions.
  - Decide explicit policy for `NULL` input and test accordingly.

### ex01 `ft_range.c`

- Current status: PASS on current student code.
- Current checks: several min/max ranges and null-return cases.
- Critical issues (confirmed with `/tmp` probe):
  - `memcmp(result, expected, expected_size)` uses element count as bytes, not `expected_size * sizeof(int)`.
  - Test can falsely pass incorrect arrays.
  - Diagnostics print only one scalar (`*expected` and `result[i]`), not full array diff.
  - Success lines can print obviously wrong values while still reporting pass.
- Plan:
  - Fix byte count in comparison.
  - Replace scalar print with indexed/full-array diff helper.
  - Add targeted regression test to prevent this exact false-positive class.

### ex02 `ft_ultimate_range.c`

- Current status: PASS on current student code.
- Current checks: null/non-null paths and full-array mismatch display.
- Issues:
  - `expected_return` field is defined but not used for assertions.
  - No malloc-failure-path verification.
- Plan:
  - Assert return value explicitly against expected contract.
  - Optional malloc-failure simulation (like C08/ex04 style, lighter version).

### ex03 `ft_strjoin.c`

- Current status: PASS.
- Current checks: size 0/1/multi, empty strings, empty separator.
- Issues:
  - No include/prototype hygiene (student missing includes can be masked).
  - If function returns `NULL` unexpectedly, `strcmp` usage is unsafe.
- Plan:
  - Add standalone compile check for student source.
  - Add null-safe diagnostics and assert non-null where required.

### ex04 `ft_convert_base.c`

- Current status: PASS with compiler warning report (`-Werror` fallback path).
- Current checks: positive/negative conversion and invalid base cases.
- Issues:
  - Missing explicit zero-conversion case (`"0"`).
  - Coverage still narrow for whitespace/sign edge parsing.
- Plan:
  - Add zero-case.
  - Add compact signed/whitespace invalid-digit boundary cases.

### ex05 `ft_split.c`

- Current status: PASS on current student code.
- Current checks: several split scenarios and array element comparisons.
- Issues (confirmed with `/tmp` probe):
  - Error printing for expected arrays can read past sentinel on one test case and display unrelated memory (`"(null)", "hello"` style output).
  - Diagnostic formatting is hard to read on null/non-null mismatch paths.
  - No allocation-failure-path checks.
- Plan:
  - Make expected arrays explicitly null-terminated and safely iterated.
  - Standardize array pretty-printer with bounds/sentinel guards.
  - Optional malloc-failure simulation for robustness.

---

## C08

### ex00 `ft.h`

- Current status: PASS.
- Current checks: double include, signature/typing compile checks.
- Issues: none significant.
- Plan: keep as-is; this is already strong for header contract validation.

### ex01 `ft_boolean.h`

- Current status: PASS.
- Current checks: macro values, EVEN behavior, message literals.
- Issues: none significant.
- Plan: keep as-is.

### ex02 `ft_abs.h`

- Current status: PASS.
- Current checks: base and expression cases to catch parenthesis issues.
- Issues: none significant.
- Plan: keep as-is.

### ex03 `ft_point.h`

- Current status: PASS.
- Current checks: include guard behavior and struct field usage.
- Issues: none major.
- Plan: optional extra compile-only checks for typedef/name strictness.

### ex04 `ft_strs_to_tab.c`

- Current status: PASS.
- Current checks: strong functional checks + tracked allocation failure cleanup checks.
- Issues: none major; this is currently the best-quality harness in project.
- Plan:
  - Preserve design as reference pattern for other memory-alloc exercises.

### ex05 `ft_show_tab.c`

- Current status: PASS.
- Current checks: robust stdout pipe capture; exact output and sentinel-stop behavior.
- Issues: none major.
- Plan:
  - Keep structure; reuse this capture pattern in older output-based exercises.

---

## C09

Current runner status: tests unavailable (`mini-moul/tests/C09` does not exist).

Student tree currently has:

- `ex00/libft_creator.sh` + `ft_putchar/ft_swap/ft_putstr/ft_strlen/ft_strcmp`
- `ex01/Makefile`
- `ex02/ft_split.c`

Plan (subject-driven, non-breaking with existing runner architecture):

- Add `mini-moul/tests/C09/ex00/`:
  - build script invocation checks, archive/object presence, symbol checks.
- Add `mini-moul/tests/C09/ex01/`:
  - Makefile target behavior checks (`all`, `clean`, `fclean`, `re`) and rebuild logic.
- Add `mini-moul/tests/C09/ex02/`:
  - functional split behavior tests plus memory hygiene checks (using C08/ex04 model where practical).

---

## Non-Breaking Upgrade Plan

## Phase 1: Diagnostics and Safety Foundation (No scoring model change)

- Introduce shared test helper(s) for:
  - stdout capture (pipe-based)
  - null-safe string compare and compact diff output
  - int-array compare with index/mismatch context
- Fix confirmed defects first:
  - C07/ex01 byte-count and array reporting
  - C07/ex05 expected-array printing safety
  - C06 helper leaks

## Phase 2: Placeholder Replacement

- Implement real tests for C02/ex12 and C05/ex08.
- Preserve one-binary-per-exercise structure and existing assignment/exercise naming.

## Phase 3: Targeted Edge-Case Coverage Expansion

- Add small deterministic cases already identified above (C04/ex03 whitespace set, C05/ex02-03 `0^0`, C05/ex05 `INT_MAX`, C07/ex04 zero-case, etc.).
- Keep each expansion minimal and additive to avoid behavior shocks.

## Phase 4: Optional C++ Harness Migration (Incremental)

- Migrate only where it materially improves reliability/diagnostics.
- Keep student code in C; call via `extern "C"` wrappers or direct include strategy.
- Preserve same pass/fail semantics and scoring to avoid breaking current UX.

---

## Success Criteria for Follow-Up Work

- No regression in assignment discovery, scoring model, or runner CLI behavior.
- Better failure readability (first mismatch index/context instead of giant blobs or scalar-only output).
- No known harness false-positive class remaining (especially C07/ex01).
- Placeholder exercises converted to real deterministic checks.
- Memory/resource hygiene warnings from harness code reduced/eliminated.
