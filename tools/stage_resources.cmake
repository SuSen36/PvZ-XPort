if(NOT DEFINED SOURCE_DIR OR NOT DEFINED DEST_DIR)
	message(FATAL_ERROR "SOURCE_DIR and DEST_DIR are required")
endif()

if(NOT EXISTS "${SOURCE_DIR}/main.pak")
	message(STATUS "No packed main.pak found in ${SOURCE_DIR}; skipping resource staging")
	return()
endif()

file(MAKE_DIRECTORY "${DEST_DIR}")
file(COPY_FILE "${SOURCE_DIR}/main.pak" "${DEST_DIR}/main.pak" ONLY_IF_DIFFERENT)

if(EXISTS "${SOURCE_DIR}/properties")
	file(REMOVE_RECURSE "${DEST_DIR}/properties")
	file(COPY "${SOURCE_DIR}/properties" DESTINATION "${DEST_DIR}")
endif()
