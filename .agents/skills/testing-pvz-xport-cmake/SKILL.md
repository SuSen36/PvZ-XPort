---
name: testing-pvz-xport-cmake
description: Test PvZ-XPort CMake builds, resource packing/staging, and vcpkg dependency detection. Use when validating resource pipeline, desktop builds, Windows CLion/vcpkg dependency fixes, or simplified audio dependency changes.
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

## Bundled shared dependency / Android-relevant regression

Use this when validating changes to bundled dependencies, target aliases, or Android CI failures related to shared dependency builds. Android defaults `PVZ_BUILD_SHARED_DEPS=ON`, but the path can be smoke-tested on Linux without an Android toolchain by forcing shared bundled dependencies:

```bash
rm -rf /home/ubuntu/pvz-shared-deps-test
cmake -S /path/to/PvZ-XPort \
  -B /home/ubuntu/pvz-shared-deps-test \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPVZ_AUTO_PACK_RESOURCES=OFF \
  -DPVZ_BUILD_SHARED_DEPS=ON 2>&1 | tee /home/ubuntu/pvz-shared-configure.log
cmake --build /home/ubuntu/pvz-shared-deps-test --target pvz-portable -j2 2>&1 | tee /home/ubuntu/pvz-shared-build.log
grep -F "PVZ_BUILD_SHARED_DEPS:BOOL=ON" /home/ubuntu/pvz-shared-deps-test/CMakeCache.txt
test -x /home/ubuntu/pvz-shared-deps-test/pvz-portable
```

Expected:
- Configure exits 0.
- `CMakeCache.txt` contains `PVZ_BUILD_SHARED_DEPS:BOOL=ON`.
- The configure log does not contain old target-alias failures such as `ALIAS target "PNG::PNG" because target "png_static" does not already exist`.
- The build log shows shared dependency targets linking when applicable, for example `libs/libpng/libpng16.so`.
- `pvz-portable` exists and is executable.

If the target platform is macOS, Android, iOS, Windows, or WebAssembly, also use PR CI as the source of truth for platform-specific generator expressions, toolchains, packaging, and codesigning behavior that Linux cannot fully emulate.

## Simplified audio dependency checks

Use this when validating changes that reduce required audio packages. The default build should use SDL Mixer X built-in codecs and should not require `libogg`, `libvorbis`, `mpg123`, or `libopenmpt`.

```bash
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-audio-default \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPVZ_AUTO_PACK_RESOURCES=OFF 2>&1 | tee /tmp/pvz-audio-default-configure.log
cmake --build /path/to/PvZ-XPort/build-audio-default --target pvz-portable -j$(nproc)
```

Expected:
- Configure exits 0.
- The configure log contains `== using STB-Vorbis` and `== using DRMP3`.
- The configure/build logs do not contain `VorbisConfig.cmake`, `Could not find OGG_LIBRARY`, or `Could not find a package configuration file provided by "Vorbis"`.
- The configure summary shows `MPG123 is disabled` and, unless explicitly enabled, `OpenMPT is disabled`.

## vcpkg / CLion dependency detection simulation

Use this when validating Windows commands that pass `-DCMAKE_TOOLCHAIN_FILE=.../vcpkg.cmake`.

On Linux, create a fake toolchain path to prove the project detects the vcpkg toolchain path without requiring a real Windows setup:

```bash
mkdir -p /home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems
printf '# fake vcpkg toolchain\n' > /home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems/vcpkg.cmake
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-vcpkg-toolchain-path-test \
  -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems/vcpkg.cmake \
  -DPVZ_AUTO_PACK_RESOURCES=OFF 2>&1 | tee /home/ubuntu/pvz-vcpkg-fake/configure.log
```

Expected after simplified audio dependency changes:
- Configure exits 0.
- The log contains `== using STB-Vorbis` and `== using DRMP3`.
- The log does **not** contain `Could not find OGG_LIBRARY` or `Could not find a package configuration file provided by "Vorbis"`.
- `build-vcpkg-toolchain-path-test/CMakeCache.txt` contains `VCPKG_MANIFEST_MODE:BOOL=ON`.
- Default builds should not contain `VCPKG_MANIFEST_FEATURES:STRING=openmpt`.

Interpretation:
- `VCPKG_MANIFEST_MODE:BOOL=ON` means CMake detected the vcpkg toolchain path.
- Any `VorbisConfig.cmake` or `OGG_LIBRARY` failure means the top-level CMake is still hard-requiring removed audio packages.

## Optional OpenMPT / MO3 path

Use this when validating that MO3/tracker support remains available behind `PVZ_ENABLE_OPENMPT`:

```bash
cmake -S /path/to/PvZ-XPort \
  -B /path/to/PvZ-XPort/build-vcpkg-openmpt-test \
  -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=/home/ubuntu/pvz-vcpkg-fake/scripts/buildsystems/vcpkg.cmake \
  -DPVZ_AUTO_PACK_RESOURCES=OFF \
  -DPVZ_ENABLE_OPENMPT=ON 2>&1 | tee /home/ubuntu/pvz-vcpkg-fake/openmpt-configure.log
cmake --build /path/to/PvZ-XPort/build-vcpkg-openmpt-test --target pvz-portable -j$(nproc)
```

Expected:
- Configure exits 0 if OpenMPT is available in the test environment or via real vcpkg.
- `CMakeCache.txt` contains `USE_OPENMPT:BOOL=ON`.
- With a vcpkg toolchain path, `CMakeCache.txt` contains `VCPKG_MANIFEST_FEATURES:STRING=openmpt`.
- The configure log contains `== using libopenmpt ==` or `OpenMPT found` and lists MO3 in tracker formats.
- Build exits 0.

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

For long CMake builds, capture logs with `tee` or redirect output to a file and record a status file. If a high-parallelism build stops producing monitorable output, inspect the build log and process list before rerunning; it is usually safe to resume the same Ninja build directory with lower parallelism (for example `-j2`) and report that clearly.

When testing an open PR, post one PR comment with:
- Escalations and environment limits first.
- One bullet per assertion with Passed/Failed/Untested.
- Evidence images or concise log excerpts.
- Link to the Devin session.
