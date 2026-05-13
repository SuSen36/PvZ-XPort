---
name: testing-pvz-xport-cmake
description: Test PvZ-XPort CMake builds, resource packing/staging, and vcpkg dependency detection. Use when validating resource pipeline, desktop builds, or Windows CLion/vcpkg dependency fixes.
---

# PvZ-XPort CMake / Resource / vcpkg Testing

## Devin Secrets Needed

None for shell-only CMake/resource tests.

If future tests need private resource repository access beyond normal git auth, request a repo-scoped secret or confirm git access first. Do not print or commit credentials.

## Baseline setup

1. Work in the `SuSen36/PvZ-XPort` checkout.
2. Initialize resources when testing the real resource pipeline:
   ```bash
   git submodule update --init --recursive res
   ```
3. Prefer shell commands for CMake/build tests. Only record the desktop if launching the app UI.
4. Check PR CI with the built-in git PR checks tool; this repo may have no CI checks.

## Linux desktop build regression

Use this to verify CMake/build changes do not break the default non-vcpkg Linux path:

```bash
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-linux-regression \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPVZ_AUTO_PACK_RESOURCES=OFF
cmake --build /path/to/PvZ-XPort/build-linux-regression --target pvz-portable -j$(nproc)
git -C /path/to/PvZ-XPort diff --check
git -C /path/to/PvZ-XPort status --short
```

Expected:
- Configure exits 0.
- `pvz-portable` links successfully.
- `git diff --check` exits 0.
- Working tree is clean except intentional edits.

## vcpkg / CLion dependency detection simulation

Use this when validating fixes for Windows commands that pass `-DCMAKE_TOOLCHAIN_FILE=.../vcpkg.cmake`.

On Linux, create a fake toolchain path to prove the project selects the vcpkg CONFIG-package branch:

```bash
mkdir -p /home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems
printf '# fake vcpkg toolchain\n' > /home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems/vcpkg.cmake
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-vcpkg-toolchain-path-test \
  -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems/vcpkg.cmake \
  -DPVZ_AUTO_PACK_RESOURCES=OFF 2>&1 | tee /home/ubuntu/pvz-vcpkg-fake/configure.log
```

Expected in a fake toolchain environment:
- Configure exits non-zero because no real vcpkg package configs exist.
- The log contains `Could not find a package configuration file provided by "Vorbis"`.
- The log does **not** contain `Could not find OGG_LIBRARY`.

Interpretation:
- `VorbisConfig.cmake` missing means CMake reached the vcpkg CONFIG package path.
- `OGG_LIBRARY` missing means the project fell back to raw non-vcpkg `find_library` and the CLion/vcpkg detection is likely broken.

## Real resource packing/staging smoke test

Use this when `res/` contains unpacked resources and the CMake resource pipeline changed:

```bash
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-resource-test \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release
cmake --build /path/to/PvZ-XPort/build-resource-test -j$(nproc)
```

Expected:
- `build-resource-test/generated/resources/main.pak` exists and is non-empty.
- `build-resource-test/generated/resources/properties/` exists.
- Desktop staged `main.pak` and `properties/` exist next to `pvz-portable`.
- Generated and staged `main.pak` are byte-identical.
- `res/` remains clean and does not gain generated archives.

Useful checks:

```bash
find /path/to/PvZ-XPort/res -iname '*.pak' -o -iname '*.7z' -o -iname '*.zip'
cmp /path/to/PvZ-XPort/build-resource-test/generated/resources/main.pak \
    /path/to/PvZ-XPort/build-resource-test/main.pak
find /path/to/PvZ-XPort/build-resource-test/generated/resources/properties -type f | wc -l
```

## Missing-resource pipeline behavior

When testing graceful behavior without a resource submodule, configure with a missing source directory:

```bash
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-no-res-test \
  -G Ninja \
  -DPVZ_RESOURCE_SOURCE_DIR=/home/ubuntu/nonexistent-pvz-res
cmake --build /path/to/PvZ-XPort/build-no-res-test --target pvz-pack-resources
```

Expected:
- Target exits 0.
- Stamp/log mentions missing source resources.
- No stale `main.pak` remains from an earlier successful pack.

## Reporting

For shell-only tests, do not record the desktop. Provide command output snippets or rendered screenshots of terminal logs in the test report.

When testing an open PR, post one PR comment with:
- Escalations and environment limits first.
- One bullet per assertion with Passed/Failed/Untested.
- Evidence images or concise log excerpts.
- Link to the Devin session.
