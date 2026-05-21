# Upstream Issue Baseline

This file is a triaged baseline for improving `mini-moulinette`.

Scope of review:
- Upstream repo: `k11q/mini-moulinette`
- Reviewed inventory: `17` open issues, `2` closed issues, `10` open PRs, `11` closed PRs
- Goal: keep the actionable signal, discard noise, and map each real problem to existing upstream issues/PRs where possible

Triage rules:
- Keep it if it points to a real test bug, a real coverage gap, a real runner/usability problem, or a feature that materially improves correctness.
- Reject it if it is only a complaint, a user-code bug, a duplicate with no added value, or an obsolete shell-only concern with no relevance to the Python runner.

## Active Backlog

### C03/ex05 `ft_strlcat`: harness allocation bug and missing return-value checks

- Upstream refs:
  - [Issue #23](https://github.com/k11q/mini-moulinette/issues/23)
  - [Issue #29](https://github.com/k11q/mini-moulinette/issues/29)
  - [Issue #35](https://github.com/k11q/mini-moulinette/issues/35)
  - [PR #20](https://github.com/k11q/mini-moulinette/pull/20)
  - [PR #26](https://github.com/k11q/mini-moulinette/pull/26)
  - [PR #36](https://github.com/k11q/mini-moulinette/pull/36)
  - [PR #38](https://github.com/k11q/mini-moulinette/pull/38)
  - [PR #39](https://github.com/k11q/mini-moulinette/pull/39)
  - [PR #41](https://github.com/k11q/mini-moulinette/pull/41)
- Assessment:
  - This is a real harness bug.
  - The original test allocated `dest` from `strlen(test.dest) + 1`, which is smaller than the buffer size that valid `strlcat` implementations are allowed to write into.
  - That can segfault even for correct student code.
  - The harness also does not check the return value semantics of `strlcat`, only the mutated string.
- Local status:
  - The buffer-sizing bug is already fixed in this fork.
  - The missing return-value checks are still open.
- Recommended approach:
  - Keep the `dest` buffer sized to at least `size` bytes.
  - Add return-value assertions using the real `strlcat` contract: expected return is `initial_dest_len + src_len`, regardless of truncation.
  - Rebase the return-value work from [PR #26](https://github.com/k11q/mini-moulinette/pull/26) on top of the correct allocation fix from [PR #41](https://github.com/k11q/mini-moulinette/pull/41).
- Notes on upstream PR quality:
  - [PR #41](https://github.com/k11q/mini-moulinette/pull/41) is the correct allocation fix.
  - [PR #20](https://github.com/k11q/mini-moulinette/pull/20) still allocates too little.
  - [PR #36](https://github.com/k11q/mini-moulinette/pull/36), [PR #38](https://github.com/k11q/mini-moulinette/pull/38), and [PR #39](https://github.com/k11q/mini-moulinette/pull/39) are incomplete duplicates.

### C07/ex04 `ft_convert_base`: missing zero-case coverage

- Upstream refs:
  - [Issue #14](https://github.com/k11q/mini-moulinette/issues/14)
  - [PR #15](https://github.com/k11q/mini-moulinette/pull/15)
- Assessment:
  - Real coverage gap.
  - Current tests cover positive, negative, invalid `base_from`, and invalid `base_to`, but not `nbr = "0"`.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add the `0` conversion case from [PR #15](https://github.com/k11q/mini-moulinette/pull/15).
  - Keep this separate from broader `ft_convert_base` improvements.

### C05/ex05 `ft_sqrt`: missing `INT_MAX` / worst-case runtime coverage

- Upstream refs:
  - [PR #16](https://github.com/k11q/mini-moulinette/pull/16)
- Assessment:
  - Real coverage and performance gap.
  - Naive linear scans can timeout or run unreasonably long on large inputs.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add the `2147483647 -> 0` case from [PR #16](https://github.com/k11q/mini-moulinette/pull/16).
  - Keep the runner timeout in place, but add this case so poor implementations fail deterministically for the right reason.

### C04/ex03 `ft_atoi`: incomplete whitespace coverage

- Upstream refs:
  - [PR #17](https://github.com/k11q/mini-moulinette/pull/17)
- Assessment:
  - Real coverage gap.
  - The exercise points to `isspace(3)`, but the current test only exercises regular spaces.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add `\f \n \r \t \v` coverage from [PR #17](https://github.com/k11q/mini-moulinette/pull/17).

### C05/ex02 and C05/ex03: missing `0^0` edge case

- Upstream refs:
  - [Issue #27](https://github.com/k11q/mini-moulinette/issues/27)
  - [PR #28](https://github.com/k11q/mini-moulinette/pull/28)
- Assessment:
  - Real coverage gap.
  - Current tests check `power == 0`, but only with non-zero base.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add the `0^0 -> 1` case from [PR #28](https://github.com/k11q/mini-moulinette/pull/28) to both exercises.

### C02/ex09 `ft_strcapitalize`: missing digit-to-uppercase transition case

- Upstream refs:
  - [Issue #31](https://github.com/k11q/mini-moulinette/issues/31)
- Assessment:
  - Real coverage gap.
  - The current tests do not check that letters immediately following digits stay within the same word and get lowercased.
  - Example: `123AA` should become `123aa`, not `123Aa`.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add one or two compact cases around digit boundaries, not just the exact user example.

### C07/ex03 `ft_strjoin`: missing standalone include/prototype hygiene

- Upstream refs:
  - [Issue #33](https://github.com/k11q/mini-moulinette/issues/33)
- Assessment:
  - Real test weakness.
  - The harness includes standard headers before including the student file, so missing includes in student code can be masked.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Add a standalone compile step for student source files, not just the harness-included build.
  - This is especially useful for catching missing headers for `malloc`, `free`, `write`, and similar functions.

### C03/ex02 `ft_strcat`: missing explicit NUL-termination validation

- Upstream refs:
  - [Issue #11](https://github.com/k11q/mini-moulinette/issues/11)
- Assessment:
  - Plausible and useful.
  - The current test can let a missing trailing `\0` slip through because the destination array is initialized in a way that may already leave zero bytes after the copied content.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Fill destination buffers with non-zero sentinel bytes before the call.
  - Assert both content and exact terminator placement.
  - This same technique is useful for other string exercises.

### C02/ex10 `ft_strlcpy`: coverage still incomplete after the earlier merged fix

- Upstream refs:
  - [PR #8](https://github.com/k11q/mini-moulinette/pull/8)
  - [Issue #42](https://github.com/k11q/mini-moulinette/issues/42)
- Assessment:
  - Real ongoing gap.
  - [PR #8](https://github.com/k11q/mini-moulinette/pull/8) fixed important baseline behavior, but [Issue #42](https://github.com/k11q/mini-moulinette/issues/42) shows there are still missed cases.
- Local status:
  - Partially addressed historically, but still not robust.
- Recommended approach:
  - Differential-test against a known-good `strlcpy` reference or libc-compatible shim.
  - Add more cases for `size == 0`, `size == 1`, source shorter than size, source longer than size, and random fuzz inputs.

### C02/ex12 `ft_print_memory`: tests are still placeholders

- Upstream refs:
  - [Issue #40](https://github.com/k11q/mini-moulinette/issues/40)
  - [PR #34](https://github.com/k11q/mini-moulinette/pull/34)
- Assessment:
  - Real missing coverage.
  - The current test file is effectively unimplemented.
- Local status:
  - Still a placeholder in this fork.
- Recommended approach:
  - Replace the placeholder with deterministic tests for:
    - return value is the original pointer
    - no output for size `0`
    - correct line count for `size`
    - stable formatting for printable and non-printable bytes
  - Treat [PR #34](https://github.com/k11q/mini-moulinette/pull/34) as an idea source, not a merge candidate.

### C05/ex08 `ft_ten_queens_puzzle`: tests are still placeholders

- Upstream refs:
  - [PR #34](https://github.com/k11q/mini-moulinette/pull/34)
- Assessment:
  - Real missing coverage.
  - The current test file is effectively unimplemented.
- Local status:
  - Still a placeholder in this fork.
- Recommended approach:
  - Add at least:
    - return value `724`
    - emitted line count `724`
    - minimal format sanity on printed solutions
  - Again, use [PR #34](https://github.com/k11q/mini-moulinette/pull/34) only as input for manual review.

### Forbidden-function detection is missing

- Upstream refs:
  - [Issue #30](https://github.com/k11q/mini-moulinette/issues/30)
- Assessment:
  - This is a real functionality gap, not a false report.
  - The current project mostly checks behavior and norm, not whether forbidden libc functions were used.
- Local status:
  - Still open in this fork.
- Recommended approach:
  - Compile student sources to objects and inspect unresolved symbols with `nm -u` or equivalent.
  - Maintain per-exercise allowlists.
  - Keep this separate from behavior tests; it is a policy/static-analysis feature.

### Lowercase folder names / more flexible target naming

- Upstream refs:
  - [Issue #18](https://github.com/k11q/mini-moulinette/issues/18)
  - [PR #13](https://github.com/k11q/mini-moulinette/pull/13)
- Assessment:
  - Real usability request, but lower priority than correctness gaps.
  - The Python runner already reduces the pain somewhat via `--target`.
- Local status:
  - Still strict in this fork.
- Recommended approach:
  - If this is implemented, do it explicitly in the Python CLI:
    - case-insensitive assignment detection, or
    - `--assignment` independent of directory name
  - Do not reuse [PR #13](https://github.com/k11q/mini-moulinette/pull/13) as-is.

## Historical Issues Already Resolved Upstream

These are real problems, but they are not good future work items unless this fork is missing the upstream change.

### Shell portability and hardcoded-path problems

- Upstream refs:
  - [PR #3](https://github.com/k11q/mini-moulinette/pull/3)
  - [PR #4](https://github.com/k11q/mini-moulinette/pull/4)
  - [PR #21](https://github.com/k11q/mini-moulinette/pull/21)
- Assessment:
  - Real historical problems in the shell runner.
- Local status:
  - Largely superseded by the Python runner in this fork.
- Notes:
  - Only preserve relevant lessons for the compatibility wrapper: no hardcoded home path, clean target detection, no platform-specific shell assumptions.

### C07/ex04 invalid-base coverage

- Upstream refs:
  - [Issue #5](https://github.com/k11q/mini-moulinette/issues/5)
  - [PR #6](https://github.com/k11q/mini-moulinette/pull/6)
- Assessment:
  - Real and already fixed upstream.

### C07/ex04 optional `ft_convert_base2.c`

- Upstream refs:
  - [PR #7](https://github.com/k11q/mini-moulinette/pull/7)
- Assessment:
  - Real and already fixed upstream.

### C02/ex02 missing invalid alpha-range coverage

- Upstream refs:
  - [PR #10](https://github.com/k11q/mini-moulinette/pull/10)
  - [PR #24](https://github.com/k11q/mini-moulinette/pull/24)
- Assessment:
  - Real issue.
  - [PR #10](https://github.com/k11q/mini-moulinette/pull/10) is the meaningful merged fix.
  - [PR #24](https://github.com/k11q/mini-moulinette/pull/24) is a weaker duplicate.

### C03/ex04 `ft_strstr` missing case

- Upstream refs:
  - [PR #12](https://github.com/k11q/mini-moulinette/pull/12)
- Assessment:
  - Real and already fixed upstream.

## Reviewed and Rejected

These were looked at and intentionally excluded from the actionable backlog.

### Non-actionable issues

- [Issue #2](https://github.com/k11q/mini-moulinette/issues/2)
  - Junk content, no technical value.
- [Issue #9](https://github.com/k11q/mini-moulinette/issues/9)
  - Generic complaint about `C00/ex06`; no reproducible harness bug is established.
- [Issue #14](https://github.com/k11q/mini-moulinette/issues/14)
  - Most of the body is the reporter discovering a bug in their own `C07/ex03` implementation.
  - Only the later zero-case note for `ft_convert_base` is actionable, and that is already tracked above.
- [Issue #19](https://github.com/k11q/mini-moulinette/issues/19)
  - Incorrect report.
  - `strncmp("Hello", "Hellz", 4)` should return `0`, so the cited test is not wrong.
- [Issue #22](https://github.com/k11q/mini-moulinette/issues/22)
  - Maintainer search, not a product issue.
- [Issue #25](https://github.com/k11q/mini-moulinette/issues/25)
  - The sample `ft_print_combn` implementation itself appears buggy; there is not enough evidence of a harness defect.
- [Issue #29](https://github.com/k11q/mini-moulinette/issues/29)
  - Keep only the `C03/ex05` portion.
  - The `C03/ex04` part is too vague and has no concrete fix.
- [Issue #32](https://github.com/k11q/mini-moulinette/issues/32)
  - Complaint with no actionable technical content.

### PRs that should not be merged as-is

- [PR #13](https://github.com/k11q/mini-moulinette/pull/13)
  - Does not really solve lowercase-path support.
  - Changes UX and shell flow in a way that is obsolete for the Python runner.
- [PR #20](https://github.com/k11q/mini-moulinette/pull/20)
  - Incomplete `C03/ex05` fix.
- [PR #24](https://github.com/k11q/mini-moulinette/pull/24)
  - Duplicate of already-merged `C02/ex02` work.
- [PR #34](https://github.com/k11q/mini-moulinette/pull/34)
  - Large mixed patch with valuable ideas but too broad to merge blindly.
  - Also touches obsolete shell behavior.
- [PR #36](https://github.com/k11q/mini-moulinette/pull/36)
  - Incomplete duplicate of the `C03/ex05` buffer fix.
- [PR #38](https://github.com/k11q/mini-moulinette/pull/38)
  - Duplicate of [PR #36](https://github.com/k11q/mini-moulinette/pull/36).
- [PR #39](https://github.com/k11q/mini-moulinette/pull/39)
  - Duplicate of [PR #36](https://github.com/k11q/mini-moulinette/pull/36).

## Recommended Next Work Order

If continuing test improvements in this fork, the highest-value order is:

1. Finish `C03/ex05` by adding return-value assertions on top of the already-correct buffer sizing.
2. Replace the placeholder tests in `C02/ex12` and `C05/ex08`.
3. Add the small deterministic coverage gaps:
   - `C07/ex04` zero case
   - `C05/ex05` `INT_MAX`
   - `C04/ex03` full whitespace set
   - `C05/ex02` and `C05/ex03` `0^0`
   - `C02/ex09` digit-boundary capitalization
4. Add standalone student-source compilation checks to catch missing includes.
5. Decide whether forbidden-function detection belongs in scope for this fork.
