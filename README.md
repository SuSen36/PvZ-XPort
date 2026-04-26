# PvZ-Portable

<div align="center">
  <img src="icon-readme.png" alt="PvZ-Portable" width="450">
</div>

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/wszqkzqk/PvZ-Portable)

一个**跨平台**、社区驱动的《植物大战僵尸：年度版》(Plants vs. Zombies: Game of the Year Edition) 重实现项目，旨在将植物大战僵尸**100% 原汁原味的体验**带给每一个平台。

| 🌿 原汁原味 | 🎮 便携式 | 🛠️ 开源 |
| :---: | :---: | :---: |
| 几乎 100% 的游戏玩法还原 | 支持 32/64 位系统<br>可在 Linux、Windows、macOS、Android、iOS、WebAssembly、Switch 等平台运行 | OpenGL ES 2.0 & SDL |

🌐 **不想安装？** [直接在浏览器中体验！](https://wszqkzqk.github.io/pvz-portable-wasm/pvz-portable.html)（你仍然需要自己的游戏数据文件。）

**⚠️ 注意事项：**

* 本仓库**不包含**任何 PopCap Games 或 Electronic Arts 拥有的版权游戏资源（如图像、音乐或字体）。用户必须从**合法购买的**《植物大战僵尸：年度版》副本中提供自己的 `main.pak` 和 `properties/` 文件夹。
* 代码库是基于社区研究（如[植物大战僵尸吧](https://tieba.baidu.com/f?ie=utf-8&kw=%E6%A4%8D%E7%89%A9%E5%A4%A7%E6%88%98%E5%83%B5%E5%B0%B8)、[PVZ Wiki](https://wiki.pvz1.com/doku.php?id=home) 和 [PvZ Tools](https://pvz.tools/memory/)）的手动重实现。它使用 SDL2 和 OpenGL ES 2.0（兼容桌面端 OpenGL 2.1）等可移植后端编写。作者（wszqkzqk）**从未对程序进行逆向工程**；作者仅根据公开信息和游戏测试编写代码。此外，通过逆向工程直接生成的代码也**不会被接受**。
* 本项目仅用于**教育目的**，专注于**跨平台移植技术**、引擎现代化，以及学习经典游戏逻辑如何适配各种硬件架构（如 Nintendo Switch、3DS）。
* 非商业性：本项目未获得 PopCap Games 或 Electronic Arts 的关联、授权或认可。
* 项目图标和平台特定标志由我（wszqkzqk）在 AI 图像生成工具的辅助下创建，并非 PopCap/EA 的官方资源。
* 要使用本项目进行游戏，你**必须**通过在 [EA 官网](https://www.ea.com/games/plants-vs-zombies/plants-vs-zombies) 或 [Steam](https://store.steampowered.com/app/3590/Plants_vs_Zombies_GOTY_Edition/) 购买来获取原始游戏文件。

## 功能特性

- [x] 使用 SDL + OpenGL ES 2.0 渲染（桌面端 OpenGL 2.1 回退）
  - 同时支持**调整窗口大小**，这是原版游戏所不具备的功能
  - **为什么选择 OpenGL ES 2.0？** GLES 2.0 是几乎所有现代 GPU API 的公共子集——每个桌面端 OpenGL 2.1+ 驱动、移动端 GPU 和游戏主机都原生支持它。这意味着游戏可以在任何地方**开箱即用**，无需额外依赖。[ANGLE](https://chromium.googlesource.com/angle/angle) 也可以可选地用于将调用转换为 DirectX/Metal/Vulkan。
- [x] 基于 [SDL Mixer X](https://github.com/WohlSoft/SDL-Mixer-X) 实现跨平台音频系统
  - 本项目使用了 SDL Mixer X 的一个分支，该分支通过 libopenmpt 添加了对 MO3 格式的兼容性。此分支位于 SexyAppFramework/sound/SDL-Mixer-X
- [x] 通过禁用缓存为内存极其有限的主机平台节省更多内存
- [x] **兼容**原版 PvZ 年度版的***全局用户数据***（玩家信息、冒险进度、金币、禅境花园等，存储在 `user*.dat` 中）
  - [x] 在保持兼容性的同时修复 2038 年问题
- [x] **便携式关卡存档**格式 `.v4` 支持（在 Windows、Linux、macOS、Android、Switch 等平台之间**共享关卡存档**）
  - [x] 支持将 `.v4` 存档文件导出/导入为人类可读的 YAML 格式，便于编辑
- [x] 使用 `std::thread` 实现跨平台多线程支持
- [x] 使用 `std::filesystem` 实现跨平台文件系统支持
- [x] 程序内部统一使用 UTF-8 编码
- [x] **多语言支持**：支持来自各种语言官方年度版的游戏资源数据，包括**中文、德语、西班牙语、法语和意大利语**。
- [x] 32 位和 64 位构建支持
- [x] 不同 CPU 架构支持（i686、x86_64、aarch64、riscv64、loongarch64 等）
- [x] 所有平台的 Unicode 路径支持
- [x] 不同字节序支持（小端和大端）
  - [x] 跨字节序的存档数据兼容性
  - 理论上支持大端平台，但由于缺乏硬件而未经测试

本项目支持以下平台（包括但不限于）：

| 平台 | 数据路径 | 状态 |
|------|----------|------|
| Linux | 可执行文件目录（资源）；每用户应用数据路径用于可写文件 | ✅ 可用 |
| Windows | 可执行文件目录（资源）；每用户应用数据路径用于可写文件 | ✅ 可用 |
| macOS | 可执行文件目录（资源）；每用户应用数据路径用于可写文件 | ✅ 可用 |
| BSD 系列 | 可执行文件目录（资源）；每用户应用数据路径用于可写文件 | ✅ 可用（至少在 FreeBSD 上验证过） |
| Haiku | 可执行文件目录（资源）；每用户应用数据路径用于可写文件 | ⚠️ 部分可用：无音乐 |
| Android | `Android/data/io.github.wszqkzqk.pvzportable/files/` | ✅ 可用 |
| iOS / iPadOS | App Documents 目录（Files 应用） | ✅ 可用（仅限侧载；未签名 IPA） |
| Web (WASM) | 浏览器 IndexedDB（存档）；运行时上传资源 | ✅ 可用（需要 HTTP 服务器） |
| Nintendo Switch | sdmc:/switch/PvZPortable | ✅ 在真机上可用。Kenji-NX 启动时崩溃。 |
| Nintendo 3DS | sdmc:/3ds/PvZPortable | ⚠️ Old 3DS 内存可能不足，New 3DS 勉强可用（已停止维护） |

要运行游戏，你需要 PvZ 年度版的游戏数据。将 `main.pak` 和 `properties/` 文件夹放在 `pvz-portable` 可执行文件旁边（游戏会相对于可执行文件的目录搜索资源）。如果你愿意，也可以使用解压的数据代替 `main.pak`。

关于可写数据和缓存的说明：

- 游戏默认从可执行文件目录读取资源（如 `main.pak` 和 `properties/`），因此你可以从任何工作目录启动二进制文件，它仍然能找到这些资源。
- 每用户的可写文件（设置、存档、编译缓存、截图）存储在 **操作系统推荐的应用数据路径**中。当前构建下，这些位于 `io.github.wszqkzqk/PvZPortable` 下，包含以下子文件夹：
  - `userdata/` — 玩家存档文件。
  - `cache64/` 如果你使用 64 位版本，或 `cache32/` 如果你使用 32 位版本 — 编译后的二进制缓存（重新动画 / 编译定义）。这些缓存是**本地启动产物**（**原生布局**），不是可移植文件；当缓存/模式检查失败时，游戏会透明地从源数据重新编译。
  - `registry.regemu` — 设置/注册表模拟。

示例：

- Linux: `~/.local/share/io.github.wszqkzqk/PvZPortable/`
- Windows: `%APPDATA%\io.github.wszqkzqk\PvZPortable\`
- macOS: `~/Library/Application Support/io.github.wszqkzqk/PvZPortable/`

你可以通过命令行参数自定义这些路径：
- `-resdir="<path>"`：设置**资源目录**（`main.pak` 和 `properties/` 所在的位置）。这只影响游戏查找资源的位置，不影响保存数据的位置。
- `-savedir="<path>"`：设置**存档数据目录**（设置、存档、缓存和截图的存储位置）。这将覆盖默认的操作系统推荐的应用数据路径。

**注意：** 你**必须**使用 `-param="<你的路径>"` 格式。空格分隔的值（如 `-resdir path`）**不被支持**。

### Android 特别说明

从 [Releases](https://github.com/wszqkzqk/PvZ-Portable/releases) 页面下载 APK 或自行构建。由于本项目**不包含**任何游戏资源，你需要从**合法购买的**《植物大战僵尸：年度版》副本中**导入游戏资源**。

#### 首次启动

1. **安装 APK**（你可能需要启用"允许安装未知来源应用"）。
2. **启动应用** — 由于没有找到游戏资源，**资源导入界面**将自动出现。
3. **导入游戏资源**，选择以下任一方式：
   - 包含 `main.pak` 和 `properties/` 的 **ZIP 文件**（可以在 ZIP 根目录或一个包装目录内，例如 `PvZ/main.pak`）。
   - 直接包含 `main.pak` 和 `properties/` 的**文件夹**，或其直接子文件夹包含这些文件。
4. 导入成功后点击**开始游戏**。

#### 后续管理数据

长按启动器上的应用图标以访问**管理数据**快捷方式，这将打开资源管理界面，你可以重新导入资源、导出存档或导入存档。

#### 注意

- 需要 Android 9.0+。预构建的 APK 仅限 arm64-v8a，但**你可以根据需要为其他架构构建**。
- 所有数据存储在 `Android/data/io.github.wszqkzqk.pvzportable/files/` 中。不需要额外的存储权限 — 应用对所有导入和导出操作都使用**存储访问框架 (SAF)**。
- 存档数据与桌面版本互通。详情请参阅[存档数据兼容性章节](#save-data-compatibility-user-data-and-mid-level-saves)。
- Android 移植是本项目**跨平台移植研究**的一部分。它保留了原始游戏的 4:3 宽高比和基于鼠标的输入模型 — **没有针对触摸屏进行 UI 优化**。SDL2 会自动将触摸事件映射到鼠标输入，因此游戏可以游玩但并非为移动端人体工程学设计。

### iOS / iPadOS 特别说明

从 [Releases](https://github.com/wszqkzqk/PvZ-Portable/releases) 页面下载未签名的 IPA，或使用 `ios/build-ios.sh` 自行构建。IPA 必须侧载 — 常见方法包括 [AltStore](https://altstore.io/)、[TrollStore](https://github.com/opa334/TrollStore)，或通过免费 Apple ID 直接从 Xcode 部署。

#### 导入游戏资源

应用的 Documents 文件夹通过 iTunes/Finder 文件共享和 iOS Files 应用暴露（`UIFileSharingEnabled`）。将 `main.pak` 和 `properties/` 文件夹直接放入应用的 Documents 目录中（在 Files 应用中显示为 "PvZ Portable"）。

#### 注意

- 需要 iOS 15.0+ (arm64)。
- 免费 Apple ID 签名将在 7 天后过期；TrollStore 安装是永久的。
- 与 Android 移植相同的触摸转鼠标映射和宽高比行为。

### 在浏览器中运行 (WebAssembly)

**[▶ 在线体验](https://wszqkzqk.github.io/pvz-portable-wasm/pvz-portable.html)** — 打开链接，从 ZIP 包或 `main.pak` 加上 `properties/` 文件夹加载你合法购买的游戏资源，然后点击**开始游戏**。所有文件保留在你的浏览器本地，**永远不会上传到任何服务器**（托管站点纯粹是静态的）。存档数据存储在你浏览器的 IndexedDB 中，可以通过屏幕上的按钮从 ZIP 或文件夹导入，或导出为 ZIP。

你也可以[下载 WASM 构建](https://github.com/wszqkzqk/PvZ-Portable/releases) 并自行托管。注意 HTML 文件必须通过 HTTP 提供服务（例如 `python3 -m http.server`）— 由于浏览器安全限制，直接作为本地文件打开将无法工作。

## 游戏版本兼容性

本项目针对《植物大战僵尸》**年度版 1.2.0.1073 英文版**（独立的 PopCap 发行版）设计和测试。**非英文年度版**（基于 1.2.0.1073 的 1.2.0.1093 德语/西班牙语/法语/意大利语版或 1.1.0.1056 中文版）以及 **Steam 年度版 1.2.0.1096** 也完全可以游玩 — 所有游戏机制都能正常工作。唯一的区别是由于不同版本间字符串键重命名导致的轻微 UI 文本外观问题，这些问题可以**轻松修复**，只需用户通过自定义 `properties/default.xml`（见下方）即可。

**建议：** 使用 **1.2.0.1073 英文版**资源包以获得最佳的**开箱即用**体验。

<details>
<summary>已知与非 1.2.0.1073 英文版资源的视觉差异（点击展开）</summary>

| 问题（仅限非 1.2.0.1073 英文版） | 原因 |
| :---: | :---: |
| **图鉴蓝色描述文本缺失** | 在 1.2.0.1096 中，纯文本介绍段落从 `[XXX_DESCRIPTION]` 中分离出来，移到了新的 `[XXX_DESCRIPTION_HEADER]` 键。引擎只读取 `[XXX_DESCRIPTION]`，所以标题文本从未显示。 |
| **"重新开始"按钮标签缺失** | 用于按钮标签的键 `[RESTART_LEVEL]` 在 1.2.0.1096 中被重命名为 `[RESTART_LEVEL_BUTTON]`。 |
| **未遇到的僵尸显示 `???`** 而非 `(尚未遇到)` | 字符串 `[NOT_ENCOUNTERED_YET]` 的值在 1.2.0.1096 中更改为 `???`；旧文本被移到了新键 `[NOT_ENCOUNTERED_YET_DESCRIPTION]`。 |
| **疯狂戴夫的植物出售价格显示为正确值的 1/10** | 在 1.2.0.1073 中，字符串模板 `[CRAZY_DAVE_1700]` 在 `{SELL_PRICE}` 后包含尾随的 `0`（即 `${SELL_PRICE}0`），因为引擎传递的是除以 10 后的价格。在 1.2.0.1096 中尾随的 `0` 被移除了，所以显示的价格变成了预期金额的 1/10。 |

以上所有问题都可以通过在与游戏数据一起放置的 `properties/default.xml` 文件中添加缺失或修正的字符串条目来解决。
</details>

### 多语言支持

PvZ-Portable 支持来自**非英文版**《植物大战僵尸》**年度版**的游戏资源数据。引擎处理 BOM 编码的文本文件并将传统的 Windows-1252 编码转换为 UTF-8，因此本地化文件将被正确加载。如果游戏数据中存在 `properties/default.xml` 和/或 `properties/Layout.xml`，它们将在 `LawnStrings.txt` **之后**加载，并且可以覆盖任何字符串值。这两个文件都是可选的；当不存在时，使用内置的英文默认值。

由于 `default.xml` 的优先级高于 `LawnStrings.txt`，用户也可以**创建或编辑自己的 `properties/default.xml`** 来添加或覆盖任何字符串键，从而无需修改引擎即可轻松修复特定版本的显示问题。

## 依赖项

在 PC 上构建之前，确保已安装必要的依赖项：

- **构建工具**：`CMake`、`Ninja`、支持 **C++20** 的 C/C++ 编译器（例如 `gcc`、`clang`、`MSVC`）（还需要支持 C++20 的标准库实现，如 `libstdc++`、`libc++` 或 MSVC STL）
- **图形**：`OpenGL ES 2.0` 或 `OpenGL 2.1+`（通过 SDL2 在运行时自动检测）
- **音频**：`libopenmpt`、`libogg`、`libvorbis`、`mpg123`
- **图像**：`libpng`、`libjpeg-turbo`
- **窗口/输入**：`SDL2`

### Arch Linux

你可以使用以下命令安装所需的依赖项：

```bash
sudo pacman -S --needed base-devel cmake libjpeg-turbo libogg libopenmpt libpng libvorbis mpg123 ninja sdl2-compat
```

### Debian/Ubuntu

你可以使用以下命令安装所需的依赖项：

```bash
sudo apt install cmake ninja-build libogg-dev libjpeg-dev libopenmpt-dev libpng-dev libvorbis-dev libmpg123-dev libsdl2-dev
```

### Windows (MSYS2 UCRT64)

你可以使用以下命令安装所需的依赖项：

```bash
pacman -S --needed base-devel mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-libjpeg-turbo mingw-w64-ucrt-x86_64-libopenmpt mingw-w64-ucrt-x86_64-libogg mingw-w64-ucrt-x86_64-libpng mingw-w64-ucrt-x86_64-libvorbis mingw-w64-ucrt-x86_64-mpg123 mingw-w64-ucrt-x86_64-ninja mingw-w64-ucrt-x86_64-SDL2
```

### macOS (Homebrew)

你可以使用 [Homebrew](https://brew.sh/) 安装所需依赖项：

```bash
brew install cmake dylibbundler jpeg-turbo libogg libopenmpt libpng libvorbis mpg123 ninja sdl2
```

## 构建说明

在 `CMakeLists.txt` 文件所在的位置运行以下命令（假设已安装 CMake 和其他依赖项）：

```bash
cmake -G Ninja -B build
```

```bash
cmake --build build
```

### 性能优化

建议使用 **Release** 构建类型以获得最佳性能，因为这通常意味着编译器优化：

```bash
cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release
```

对于高级用户，你也可以指定 `CFLAGS` 和 `CXXFLAGS` 来启用架构特定的优化（例如 `-march=native` 以充分利用 CPU 的指令集）：

```bash
cmake -G Ninja -B build -DCMAKE_C_FLAGS="-march=native" -DCMAKE_CXX_FLAGS="-march=native" -DCMAKE_BUILD_TYPE=Release
```

### 配置选项

你可以通过在第一个 `cmake` 命令中添加选项来自定义游戏功能：

| 选项             | 默认值                                                 | 描述                                                                        |
|:---------------|:-------------------------------------------------------|:----------------------------------------------------------------------------|
| `PVZ_DEBUG`    | `OFF`<br>(当 `CMAKE_BUILD_TYPE` 为 `Debug` 时为 `ON`)   | 启用**作弊键**、调试显示和其他调试功能。                                                    |
| `LIMBO_PAGE`   | `ON`                                                   | 启用对包含隐藏关卡的 limbo 页面的访问。                                                   |
| `DO_FIX_BUGS`  | `OFF`                                                  | 对官方 1.2.0.1073 年度版的"bug"应用社区修复。[^1] 然而，这些"bug"通常被许多玩家**视为"特性"**。 |
| `CONSOLE`      | `OFF`<br>(当 `CMAKE_BUILD_TYPE` 为 `Debug` 时为 `ON`)   | 显示控制台窗口（仅限 Windows）。                                                      |
| `BUILD_STATIC` | `OFF`                                                  | 静态链接以创建独立可执行文件（仅限基于 MinGW 工具链的 Windows）。MSVC 请改用 vcpkg `-static` triplet。 |

[^1]: 当前 `DO_FIX_BUGS` 包含以下修复：
    - 修复蹦极僵尸在"我是僵尸"模式下重复掉落阳光/物品的问题。
    - 使魅惑的巨人砸向敌方僵尸而非植物。
    - 使魅惑的巨人投掷魅惑的小鬼僵尸（修复缩放、生命值和方向问题）。
    - 使魅惑的巨人能够在"砸罐子"模式中砸碎罐子。
    - 使魅惑的豌豆/加特林头僵尸向前射击而非向后射击。
    - 使魅惑的火爆辣椒/窝瓜僵尸伤害敌方僵尸而非植物。
    - 修复魅惑窝瓜僵尸追踪和砸向敌方僵尸的坐标问题。
    - 使魅惑的火爆辣椒僵尸正确清除僵王博士的技能（冰球/火球）和梯子逻辑。
    - 同步舞王僵尸动画（修复"女仆"位移 bug）。
    - 修复梯子僵尸手臂恢复的视觉故障。
    - 修复僵王博士的攻击（房车、火球/冰球）和召唤范围覆盖 6 泳道（泳池）关卡的问题。

示例：在 **Release 构建**中手动启用 `PVZ_DEBUG`，以便在使用优化性能的同时使用**作弊键**：

```bash
cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release -DPVZ_DEBUG=ON
```

如果运行这些命令未能成功构建，请创建 issue 并详细描述你的问题。

## 存档数据兼容性（用户数据和关卡存档）

PvZ-Portable 使用两种不同类型的存档数据：

1.  **全局用户数据**（`users.dat`、`user1.dat` 等）：
    *   存储玩家信息、冒险进度、金币、禅境花园等。
    *   **完全兼容**原版 PC 游戏格式。
    *   设计上已经是可移植的（使用显式序列化）。

2.  **关卡存档状态**（`game1_0.v4` 等，旧版 `game1_0.dat` 等）：
    *   存储"保存并退出"使用时关卡的精确状态（僵尸、投射物、植物等）。
    *   游戏现在默认**只**写入 `*.v4` 文件：
        *   `*.v4` 文件：**便携式格式**。在不同平台之间分享这些文件以传输进度是完全**支持的**。
        *   `*.v4` 文件可以使用随附脚本 `scripts/pvzp-v4-converter.py` 导出/导入为人类可读的 YAML 格式以便编辑。

## 许可证

本项目的源代码根据 [GPL v3.0 License](LICENSE) 分发。

## 致谢

- 所有在这个精彩项目中工作过或正在积极工作的贡献者，特别是 [@Headshotnoby](https://www.github.com/headshot2017) 和 [@Patoke](https://www.github.com/Patoke) 他们的基础工作。