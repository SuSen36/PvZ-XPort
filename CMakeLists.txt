cmake_minimum_required(VERSION 3.5...4.0)

option(PVZ_ENABLE_OPENMPT "Enable optional libopenmpt support for MO3/tracker music" OFF)

if((DEFINED CMAKE_TOOLCHAIN_FILE AND CMAKE_TOOLCHAIN_FILE MATCHES "([/\\\\]|^)vcpkg\\.cmake$") OR DEFINED VCPKG_TOOLCHAIN)
	set(VCPKG_MANIFEST_MODE ON CACHE BOOL "Use vcpkg manifest mode to install dependencies from vcpkg.json")
	if(PVZ_ENABLE_OPENMPT)
		if(DEFINED VCPKG_MANIFEST_FEATURES AND NOT VCPKG_MANIFEST_FEATURES STREQUAL "")
			list(FIND VCPKG_MANIFEST_FEATURES "openmpt" _pvz_openmpt_feature_index)
			if(_pvz_openmpt_feature_index EQUAL -1)
				set(VCPKG_MANIFEST_FEATURES "${VCPKG_MANIFEST_FEATURES};openmpt" CACHE STRING "vcpkg manifest features" FORCE)
			endif()
		else()
			set(VCPKG_MANIFEST_FEATURES "openmpt" CACHE STRING "vcpkg manifest features" FORCE)
		endif()
	endif()
endif()

project(pvz-portable LANGUAGES C CXX ASM)

find_package(Python3 COMPONENTS Interpreter)
find_package(Git QUIET)

option(BUILD_STATIC "Static link for a standalone exe (Windows, non-MSVC)" OFF)
if(BUILD_STATIC)
	if(WIN32 AND NOT MSVC)
		set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
		set(BUILD_SHARED_LIBS OFF)
		add_link_options(-static)
	elseif(MSVC)
		message(WARNING "BUILD_STATIC is not supported for MSVC. Use a vcpkg -static triplet instead.")
		set(BUILD_STATIC OFF)
	else()
		message(WARNING "BUILD_STATIC is only supported on Windows with MinGW-based toolchains.")
		set(BUILD_STATIC OFF)
	endif()
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if (CMAKE_GENERATOR MATCHES "Ninja")
	set(CMAKE_CXX_SCAN_FOR_MODULES OFF)
endif()

if(MSVC)
	if(DEFINED VCPKG_TARGET_TRIPLET AND VCPKG_TARGET_TRIPLET MATCHES "-static")
		set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
	elseif(DEFINED VCPKG_TARGET_TRIPLET)
		set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL$<$<CONFIG:Debug>:Debug>")
	endif()
endif()

file(GLOB SOURCES
	src/*.cpp
	src/SexyAppFramework/*.cpp
	src/SexyAppFramework/graphics/*.cpp
	src/SexyAppFramework/imagelib/*.cpp
	src/SexyAppFramework/misc/*.cpp
	src/SexyAppFramework/paklib/*.cpp
	src/SexyAppFramework/sound/*.cpp
	src/SexyAppFramework/widget/*.cpp
	src/SexyAppFramework/fcaseopen/*.c
	src/Sexy.TodLib/*.cpp
	src/Lawn/*.cpp
	src/Lawn/Widget/*.cpp
	src/Lawn/System/*.cpp
)

# these files are included and must not be built in the project
list(REMOVE_ITEM SOURCES
	${CMAKE_CURRENT_SOURCE_DIR}/src/Sexy.TodLib/TodDrawTriangle.cpp
	${CMAKE_CURRENT_SOURCE_DIR}/src/Sexy.TodLib/TodDrawTriangleInc.cpp
)

set(LOW_MEMORY OFF CACHE BOOL "Enable low memory mode")
set(DOWNSCALE_COUNT 1 CACHE STRING "Image downscale count")
if(NINTENDO_SWITCH)
	list(APPEND SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/switch/Window.cpp
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/switch/Input.cpp
	)
	list(APPEND PLAT_INCLUDES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/switch
	)
elseif(NINTENDO_3DS)
	set(LOW_MEMORY ON)
	set(DOWNSCALE_COUNT 2)
	ctr_add_shader_library(colored ${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds/graphics/colored.v.pica)
	ctr_add_shader_library(textured ${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds/graphics/textured.v.pica)
	dkp_add_embedded_binary_library(shaders colored textured)
	list(APPEND SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds/graphics/Window.cpp
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds/graphics/GLInterface.cpp
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds/Input.cpp
	)
	list(APPEND PLAT_INCLUDES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/3ds
	)
elseif(EMSCRIPTEN)
	list(APPEND SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/emscripten/Window.cpp
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/default/Input.cpp
	)
	list(APPEND PLAT_INCLUDES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/emscripten
	)
else()
	list(APPEND SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/default/Window.cpp
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/default/Input.cpp
	)
	list(APPEND PLAT_INCLUDES
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/platform/default
	)
endif()

if(CMAKE_BUILD_TYPE AND CMAKE_BUILD_TYPE MATCHES "^[Dd][Ee][Bb][Uu][Gg]$")
	set(WIN_CONSOLE_DEFAULT ON)
	set(PVZ_DEBUG_DEFAULT ON)
else()
	set(WIN_CONSOLE_DEFAULT OFF)
	set(PVZ_DEBUG_DEFAULT OFF)
endif()

option(PVZ_DEBUG "Enable _PVZ_DEBUG macro to enable cheats, hidden features, etc." ${PVZ_DEBUG_DEFAULT})
option(LIMBO_PAGE "Enable limbo page to access hidden levels" ON)
option(CONSOLE "Show console on Windows" ${WIN_CONSOLE_DEFAULT})
option(DO_FIX_BUGS "Define DO_FIX_BUGS macro (Community fixes for original game bugs of 1.2.0.1073 GOTY Edition)" OFF)
option(PVZ_AUTO_PACK_RESOURCES "Pack resources from the res submodule during build" ON)
option(PVZ_AUTO_INIT_RESOURCE_SUBMODULE "Automatically initialize the res submodule when configuring resources" ON)
set(PVZ_RESOURCE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/res" CACHE PATH "PvZ resource submodule path")
set(PVZ_PACKED_RESOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/resources")

function(pvz_maybe_init_resource_submodule)
	if(NOT PVZ_AUTO_PACK_RESOURCES OR NOT PVZ_AUTO_INIT_RESOURCE_SUBMODULE)
		return()
	endif()
	if(NOT PVZ_RESOURCE_SOURCE_DIR STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/res")
		return()
	endif()
	if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.gitmodules")
		return()
	endif()
	if(EXISTS "${PVZ_RESOURCE_SOURCE_DIR}/properties")
		return()
	endif()
	if(NOT Git_FOUND)
		message(WARNING "Git was not found; cannot initialize the res submodule automatically.")
		return()
	endif()

	message(STATUS "Resource submodule is not initialized; running git submodule update --init --recursive res")
	execute_process(
		COMMAND "${GIT_EXECUTABLE}" submodule update --init --recursive res
		WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
		RESULT_VARIABLE _pvz_submodule_result
		OUTPUT_VARIABLE _pvz_submodule_stdout
		ERROR_VARIABLE _pvz_submodule_stderr
	)
	if(NOT _pvz_submodule_result EQUAL 0)
		message(WARNING "Failed to initialize res submodule automatically; resource packing will be skipped if res stays empty.\n${_pvz_submodule_stdout}\n${_pvz_submodule_stderr}")
	elseif(NOT EXISTS "${PVZ_RESOURCE_SOURCE_DIR}/properties")
		message(WARNING "res submodule initialized, but properties/ was not found; resource packing may be skipped.")
	else()
		message(STATUS "Resource submodule initialized at ${PVZ_RESOURCE_SOURCE_DIR}")
	endif()
endfunction()

function(pvz_configure_resources target)
	if(NOT PVZ_AUTO_PACK_RESOURCES)
		return()
	endif()

	pvz_maybe_init_resource_submodule()

	if(NOT Python3_Interpreter_FOUND)
		message(WARNING "Python3 was not found; skipping automatic resource packing.")
		return()
	endif()

	set(_resource_config "${CMAKE_CURRENT_SOURCE_DIR}/resources/resource-pack.json")
	set(_resource_stamp "${PVZ_PACKED_RESOURCE_DIR}/resource-pack.stamp")
	set(_resource_pak "${PVZ_PACKED_RESOURCE_DIR}/main.pak")
	file(MAKE_DIRECTORY "${PVZ_PACKED_RESOURCE_DIR}")

	add_custom_target(pvz-pack-resources ALL
		COMMAND "${Python3_EXECUTABLE}"
			"${CMAKE_CURRENT_SOURCE_DIR}/tools/pack_resources.py"
			--config "${_resource_config}"
			--source "${PVZ_RESOURCE_SOURCE_DIR}"
			--out "${PVZ_PACKED_RESOURCE_DIR}"
			--stamp "${_resource_stamp}"
		BYPRODUCTS
			"${_resource_stamp}"
			"${_resource_pak}"
		DEPENDS
			"${CMAKE_CURRENT_SOURCE_DIR}/tools/pack_resources.py"
			"${CMAKE_CURRENT_SOURCE_DIR}/tools/stage_resources.cmake"
			"${_resource_config}"
		WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
		COMMENT "Packing PvZ resources from ${PVZ_RESOURCE_SOURCE_DIR}"
		VERBATIM
	)

	add_dependencies(${target} pvz-pack-resources)

	if(ANDROID)
		set(_stage_dir "${CMAKE_CURRENT_SOURCE_DIR}/android/app/src/main/assets")
	elseif(EMSCRIPTEN)
		target_link_options(${target} PRIVATE
			"SHELL:--preload-file ${PVZ_PACKED_RESOURCE_DIR}@/"
		)
		set(_stage_dir "")
	elseif(IOS)
		set(_stage_dir "$<TARGET_BUNDLE_DIR:${target}>")
	elseif(APPLE)
		set(_stage_dir "$<TARGET_BUNDLE_CONTENT_DIR:${target}>/Resources")
	elseif(NINTENDO_SWITCH)
		set(_stage_dir "${CMAKE_CURRENT_BINARY_DIR}/switch/PvZPortable")
	elseif(NINTENDO_3DS)
		set(_stage_dir "${CMAKE_CURRENT_BINARY_DIR}/3ds/PvZPortable")
	else()
		set(_stage_dir "$<TARGET_FILE_DIR:${target}>")
	endif()

	if(_stage_dir)
		add_custom_target(pvz-stage-resources ALL
			COMMAND "${CMAKE_COMMAND}"
				"-DSOURCE_DIR=${PVZ_PACKED_RESOURCE_DIR}"
				"-DDEST_DIR=${_stage_dir}"
				-P "${CMAKE_CURRENT_SOURCE_DIR}/tools/stage_resources.cmake"
			DEPENDS
				pvz-pack-resources
				${target}
			COMMAND_EXPAND_LISTS
			COMMENT "Staging PvZ resources to ${_stage_dir}"
			VERBATIM
		)
	endif()
endfunction()

if(EMSCRIPTEN)
	list(PREPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/CMake")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -sUSE_SDL=2 -sUSE_ZLIB=1 -sUSE_LIBPNG=1 -sUSE_LIBJPEG=1 -sUSE_OGG=1 -sUSE_VORBIS=1 -sUSE_MPG123=1")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -sUSE_SDL=2 -sUSE_ZLIB=1 -sUSE_LIBPNG=1 -sUSE_LIBJPEG=1 -sUSE_OGG=1 -sUSE_VORBIS=1 -sUSE_MPG123=1")
else()
	find_package(Threads REQUIRED)
	find_package(ZLIB REQUIRED)
	find_package(JPEG REQUIRED)
	find_package(PNG REQUIRED)
	find_package(SDL2 REQUIRED)
endif()

function(_pvz_patch_sdl2_iface_libs target)
	get_target_property(_libs ${target} INTERFACE_LINK_LIBRARIES)
	if(NOT _libs)
		return()
	endif()
	set(_patched)
	foreach(_lib IN LISTS _libs)
		if(_lib STREQUAL "SDL2::SDL2")
			list(APPEND _patched SDL2::SDL2-static)
		else()
			list(APPEND _patched "${_lib}")
		endif()
	endforeach()
	set_target_properties(${target} PROPERTIES INTERFACE_LINK_LIBRARIES "${_patched}")
endfunction()

if(BUILD_STATIC AND TARGET SDL2::SDL2-static)
	if(TARGET SDL2::SDL2main)
		_pvz_patch_sdl2_iface_libs(SDL2::SDL2main)
	endif()
	set(SDL2_LINK_TARGET SDL2::SDL2-static)
else()
	set(SDL2_LINK_TARGET SDL2::SDL2)
endif()

set(SDL_MIXER_X_STATIC ON CACHE BOOL "Build static library of SDL Mixer X")
set(SDL_MIXER_X_SHARED OFF CACHE BOOL "Build shared library of SDL Mixer X")
set(USE_OPENMPT ${PVZ_ENABLE_OPENMPT} CACHE BOOL "SDL Mixer X OpenMPT" FORCE)
set(USE_MIDI OFF CACHE BOOL "SDL Mixer X midi")
set(USE_MODPLUG OFF CACHE BOOL "SDL Mixer X modplug")
set(USE_XMP OFF CACHE BOOL "SDL Mixer X xmp")
set(USE_OPUS OFF CACHE BOOL "SDL Mixer X opus")
set(USE_DRFLAC OFF CACHE BOOL "SDL Mixer X flac")
set(USE_PXTONE OFF CACHE BOOL "SDL Mixer X pxtone")
set(USE_MP3_DRMP3 ON CACHE BOOL "SDL Mixer X dr_mp3" FORCE)
set(USE_MP3_MPG123 OFF CACHE BOOL "SDL Mixer X mpg123" FORCE)
set(USE_OGG_VORBIS_STB ON CACHE BOOL "SDL Mixer X stb_vorbis" FORCE)
add_subdirectory(src/SexyAppFramework/sound/SDL-Mixer-X)

# Patch SDL-Mixer-X's transitive SDL2 dep without touching vendored CMake files
if(BUILD_STATIC AND TARGET SDL2::SDL2-static)
	_pvz_patch_sdl2_iface_libs(SDL2_mixer_ext_Static)
endif()

# Android requires a shared library loaded by SDLActivity; other platforms use an executable.
if(ANDROID)
	add_library(pvz-portable SHARED ${SOURCES})
elseif(IOS)
	add_executable(pvz-portable MACOSX_BUNDLE ${SOURCES})
else()
	add_executable(pvz-portable ${SOURCES})
endif()

target_include_directories(pvz-portable PRIVATE
	${PLAT_INCLUDES}
	${PROJECT_SOURCE_DIR}/src
	${PROJECT_SOURCE_DIR}/src/SexyAppFramework
	${PROJECT_SOURCE_DIR}/src/SexyAppFramework/sound/SDL-Mixer-X/include
	${SDL2_INCLUDE_DIRS}
)
target_compile_definitions(pvz-portable PRIVATE
	$<$<BOOL:${PVZ_DEBUG}>:_PVZ_DEBUG>
	$<$<BOOL:${LIMBO_PAGE}>:_PVZ_LIMBO_PAGE>
	$<$<BOOL:${DO_FIX_BUGS}>:DO_FIX_BUGS>
)
target_compile_features(pvz-portable PRIVATE cxx_std_20)

if (LOW_MEMORY)
	target_compile_definitions(pvz-portable PRIVATE LOW_MEMORY)
endif()
target_compile_definitions(pvz-portable PRIVATE IMG_DOWNSCALE=${DOWNSCALE_COUNT})

if(EMSCRIPTEN)
	set_property(TARGET pvz-portable APPEND PROPERTY LINK_DEPENDS
		"${CMAKE_CURRENT_SOURCE_DIR}/wasm/shell.html"
	)
	target_link_libraries(pvz-portable PRIVATE
		SDL2_mixer_ext_Static
	)
	target_link_options(pvz-portable PRIVATE
		"SHELL:-sUSE_SDL=2"
		"SHELL:-sUSE_ZLIB=1"
		"SHELL:-sUSE_LIBPNG=1"
		"SHELL:-sUSE_LIBJPEG=1"
		"SHELL:-sASYNCIFY"
		"SHELL:-sALLOW_MEMORY_GROWTH=1"
		"SHELL:-sMAXIMUM_MEMORY=1073741824"
		"SHELL:-sFORCE_FILESYSTEM=1"
		"SHELL:-sEXPORTED_RUNTIME_METHODS=[\"FS\",\"callMain\"]"
		"SHELL:-sINVOKE_RUN=0"
		"SHELL:-lidbfs.js"
		"SHELL:--shell-file ${CMAKE_CURRENT_SOURCE_DIR}/wasm/shell.html"
	)
	set_target_properties(pvz-portable PROPERTIES SUFFIX ".html")
else()
	target_link_libraries(pvz-portable PRIVATE
		SDL2_mixer_ext_Static 
		PNG::PNG
		JPEG::JPEG
		ZLIB::ZLIB
		SDL2::SDL2main
		${SDL2_LINK_TARGET}
		Threads::Threads
	)
endif()

if (WIN32)
	if(MSVC)
		target_compile_options(pvz-portable PRIVATE /utf-8)
	endif()

	target_sources(pvz-portable PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/LawnProject.rc)

	set_source_files_properties(
		${CMAKE_CURRENT_SOURCE_DIR}/src/SexyAppFramework/LawnProject.rc
		PROPERTIES
			COMPILE_DEFINITIONS "APP_ICON_PATH=\"${CMAKE_CURRENT_SOURCE_DIR}/icon.ico\""
			OBJECT_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/icon.ico"
	)

	target_link_libraries(pvz-portable PRIVATE ws2_32 user32 gdi32 winmm imm32 shlwapi)
	target_compile_definitions(pvz-portable PRIVATE WINDOWS)

	if(NOT CONSOLE)
		if(MSVC)
			set_target_properties(pvz-portable PROPERTIES WIN32_EXECUTABLE TRUE)
		else()
			target_link_options(pvz-portable PRIVATE -mwindows)
		endif()
	endif()
elseif (NINTENDO_SWITCH)
	target_link_libraries(pvz-portable PRIVATE GLESv2 EGL glapi drm_nouveau)

	nx_generate_nacp(pvz-portable.nacp
		NAME "PvZ Portable"
		AUTHOR "wszqkzqk, etc., a community-driven port"
		VERSION "0.1"
	)

	nx_create_nro(pvz-portable
		NACP pvz-portable.nacp
		ICON ${CMAKE_CURRENT_SOURCE_DIR}/icon-switch.jpg
	)
elseif (NINTENDO_3DS)
	target_link_libraries(pvz-portable PRIVATE citro3d shaders)

	ctr_generate_smdh(pvz-portable.smdh
		NAME "PvZ Portable"
		DESCRIPTION "A community-driven re-implementation of Plants vs. Zombies GOTY Edition"
		AUTHOR "wszqkzqk, etc., a community-driven port"
		VERSION "0.1"
		ICON "${CMAKE_CURRENT_SOURCE_DIR}/icon-3ds.png"
	)

	ctr_create_3dsx(pvz-portable
		SMDH pvz-portable.smdh
	)
elseif (ANDROID)
	target_link_libraries(pvz-portable PRIVATE GLESv2 EGL android log)
	set_target_properties(pvz-portable PROPERTIES OUTPUT_NAME "main")
elseif (IOS)
	target_link_libraries(pvz-portable PRIVATE
		"-framework Foundation"
		"-framework UIKit"
		"-framework OpenGLES"
		"-framework QuartzCore"
		"-framework CoreGraphics"
		"-framework CoreMotion"
		"-framework GameController"
		"-framework AVFoundation"
		"-framework AudioToolbox"
		"-framework Metal"
	)

	set_target_properties(pvz-portable PROPERTIES
		MACOSX_BUNDLE TRUE
		MACOSX_BUNDLE_GUI_IDENTIFIER "io.github.wszqkzqk.pvz-portable"
		MACOSX_BUNDLE_BUNDLE_NAME "PvZ Portable"
		MACOSX_BUNDLE_BUNDLE_VERSION "0.1"
		MACOSX_BUNDLE_SHORT_VERSION_STRING "0.1"
		MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/ios/Info.plist.in"
		XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"
		XCODE_ATTRIBUTE_IPHONEOS_DEPLOYMENT_TARGET "15.0"
		XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "io.github.wszqkzqk.pvz-portable"
		XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "-"
		XCODE_ATTRIBUTE_ASSETCATALOG_COMPILER_APPICON_NAME "AppIcon"
	)

	# Add launch storyboard to the bundle
	if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/ios/LaunchScreen.storyboard")
		target_sources(pvz-portable PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/ios/LaunchScreen.storyboard")
		set_source_files_properties("${CMAKE_CURRENT_SOURCE_DIR}/ios/LaunchScreen.storyboard"
			PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
	endif()

	# Add asset catalog (app icon)
	if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/ios/Assets.xcassets")
		target_sources(pvz-portable PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/ios/Assets.xcassets")
		set_source_files_properties("${CMAKE_CURRENT_SOURCE_DIR}/ios/Assets.xcassets"
			PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
	endif()
endif()

pvz_configure_resources(pvz-portable)
