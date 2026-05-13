---
name: testing-resource-manager
description: Test the PvZ Portable startup resource manager gate. Use when verifying changes to main.pak/properties detection, resource folder behavior, or platform startup resource prompts.
---

# Testing PvZ Portable Resource Manager

## Devin Secrets Needed

- None for local Linux desktop testing.
- Real PvZ GOTY resources are not stored as secrets; if full gameplay startup is required, ask the user to provide legal test resources or run that portion themselves.

## Local Desktop Gate Test

1. Build the app first, typically with:
   ```bash
   cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
   cmake --build build -j"$(nproc)"
   ```
2. Create an empty resource directory under the home directory, not `/tmp`, so evidence survives VM restarts:
   ```bash
   mkdir -p "$HOME/pvz-test-missing-resources"
   rm -rf "$HOME/pvz-test-missing-resources"/*
   ```
3. Launch the binary with the test resource directory:
   ```bash
   DISPLAY=:0 ./build/pvz-portable -resdir=$HOME/pvz-test-missing-resources
   ```
4. Expected missing-resource behavior:
   - A dialog titled `PvZ Portable Resource Manager` appears.
   - The message includes the selected resource path.
   - The message instructs the user to place `main.pak` and `properties/`.
   - Buttons include `Open Folder` and `Quit`.
   - `README.txt` is created in the selected resource directory.
5. Click `Open Folder` during GUI testing to verify the folder opens and `README.txt` is visible.

## Resource-Present Gate Test Without Real Assets

1. Create dummy required entries:
   ```bash
   mkdir -p "$HOME/pvz-test-present-resources/properties"
   : > "$HOME/pvz-test-present-resources/main.pak"
   ```
2. Launch:
   ```bash
   DISPLAY=:0 ./build/pvz-portable -resdir=$HOME/pvz-test-present-resources
   ```
3. Expected behavior:
   - The resource-manager dialog should not appear.
   - The app should continue into the normal resource loading path.
   - With dummy resources, a later error such as missing `properties/resources.xml` may occur; that can be acceptable when the assertion is only the startup gate.

## Recording Guidance

- Record GUI tests only for the visible missing-resource prompt and folder-open flow.
- Before recording on Linux, maximize the active window with `wmctrl` if available:
  ```bash
  sudo apt-get install -y wmctrl 2>/dev/null
  wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
  ```
- Annotate at least:
  - setup: launching with empty resource directory
  - test start: missing resources should show the resource manager
  - assertion: dialog title/path/buttons visible
  - assertion: folder opens and README exists

## Reporting

- Be explicit if real game resources were unavailable and full gameplay startup was not tested.
- Include screenshots of the dialog, opened resource folder, and any downstream error from the dummy resource-present run.
- Mention whether CI checks were present; this repo may have zero checks on some PRs.
