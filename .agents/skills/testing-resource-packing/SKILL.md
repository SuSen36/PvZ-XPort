---
name: testing-resource-packing
description: Test PvZ-XPort resource submodule packing and staging. Use when verifying res/ submodule, main.pak generation, loose properties copying, platform resource staging changes, or CMake auto-initialization of the resource submodule.
---

# Testing PvZ-XPort resource packing

## Devin Secrets Needed

- None for local fake-resource CMake tests.
- Real PvZ resources are not stored in Devin secrets; if full gameplay validation is needed, ask the user for a legal private `res/` source or access to the private resource submodule.

## Local environment

- Repo path is typically `/home/ubuntu/repos/PvZ-XPort`.
- Use CMake + Ninja + Python 3.
- PR packaging code paths:
  - `resources/resource-pack.json`
  - `tools/pack_resources.py`
  - `tools/stage_resources.cmake`
  - `CMakeLists.txt` function `pvz_configure_resources`

## Auto-init resource submodule smoke test

Use this when CMake submodule initialization logic changes:

```bash
BRANCH=$(git -C /home/ubuntu/repos/PvZ-XPort branch --show-current)
RUN_DIR="/home/ubuntu/pvz-auto-init-$(date +%s)"
git clone --branch "$BRANCH" --no-recurse-submodules \
  /home/ubuntu/repos/PvZ-XPort "$RUN_DIR"
test ! -e "$RUN_DIR/res/properties"
cmake -S "$RUN_DIR" -B "$RUN_DIR/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release 2>&1 | tee "$RUN_DIR/configure.log"
grep -F "Resource submodule is not initialized; running git submodule update --init --recursive res" \
  "$RUN_DIR/configure.log"
test -d "$RUN_DIR/res/properties"
cmake --build "$RUN_DIR/build" --target pvz-pack-resources 2>&1 | tee "$RUN_DIR/pack.log"
grep -F "Packed 3026 files" "$RUN_DIR/pack.log"
test -s "$RUN_DIR/build/generated/resources/main.pak"
```

Expected result: a fresh clone without `--recurse-submodules` configures successfully, initializes `res`, and packs real resources.

To verify non-git/source-archive fallback, clone with `--no-recurse-submodules`, move `.git` aside, configure, and build `pvz-pack-resources`. Expected result: configure warns that submodule initialization failed, `pvz-pack-resources` exits 0, `resource-pack.stamp` mentions missing source resources, and no stale `main.pak` exists.

## Fake resource fixture

Create a temporary resource source with one packable file and one loose properties file:

```bash
RUN_DIR="/home/ubuntu/pvz-pack-e2e-$(date +%s)"
RES_DIR="$RUN_DIR/res"
BUILD_DIR="$RUN_DIR/build"
mkdir -p "$RES_DIR/properties" "$RES_DIR/images"
printf '<ResourceManifest/>\n' > "$RES_DIR/properties/resources.xml"
printf 'fake-image-data\n' > "$RES_DIR/images/test.txt"
```

## Primary pack + stage test

```bash
cmake -S /home/ubuntu/repos/PvZ-XPort -B "$BUILD_DIR" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPVZ_RESOURCE_SOURCE_DIR="$RES_DIR"
cmake --build "$BUILD_DIR" -j"$(nproc)"
```

Verify:

```bash
test -s "$BUILD_DIR/generated/resources/main.pak"
test -f "$BUILD_DIR/generated/resources/properties/resources.xml"
grep -F "packed 1 files from $RES_DIR" "$BUILD_DIR/generated/resources/resource-pack.stamp"
cmp -s "$BUILD_DIR/generated/resources/main.pak" "$BUILD_DIR/main.pak"
cmp -s "$BUILD_DIR/generated/resources/properties/resources.xml" "$BUILD_DIR/properties/resources.xml"
```

Expected results:

- `generated/resources/main.pak` exists and is non-empty.
- `generated/resources/properties/resources.xml` exists and contains `<ResourceManifest/>`.
- Linux desktop staging places byte-identical `main.pak` and `properties/` next to the executable.

## Missing source test

```bash
RUN_DIR="/home/ubuntu/pvz-pack-missing-$(date +%s)"
BUILD_DIR="$RUN_DIR/build"
MISSING_DIR="$RUN_DIR/does-not-exist"
mkdir -p "$RUN_DIR"
cmake -S /home/ubuntu/repos/PvZ-XPort -B "$BUILD_DIR" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPVZ_RESOURCE_SOURCE_DIR="$MISSING_DIR"
cmake --build "$BUILD_DIR" --target pvz-pack-resources
```

Verify:

```bash
test -f "$BUILD_DIR/generated/resources/resource-pack.stamp"
grep -F "missing source resources" "$BUILD_DIR/generated/resources/resource-pack.stamp"
test ! -e "$BUILD_DIR/generated/resources/main.pak"
```

Expected result: missing or empty `res/` exits 0 and does not leave a stale `main.pak`.

## Platform staging reference

- Android: `android/app/src/main/assets/`
- iOS: `$<TARGET_BUNDLE_DIR:pvz-portable>`
- macOS: `$<TARGET_BUNDLE_CONTENT_DIR:pvz-portable>/Resources`
- Web/Emscripten: virtual filesystem root `/` via `--preload-file <generated/resources>@/`
- Linux/Windows desktop: `$<TARGET_FILE_DIR:pvz-portable>`
- Switch: `<build-dir>/switch/PvZPortable`
- 3DS: `<build-dir>/3ds/PvZPortable`

## Limitations

- Fake resources prove the pack/stage pipeline, not full gameplay startup.
- Full validation on Android/iOS/macOS/Web/Switch/Windows needs the matching toolchain/device and legal real resources.
