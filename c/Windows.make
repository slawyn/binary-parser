# Usage:
# make all     	-compile all binary
# make clean  	-remove ALL binaries and objects
# NB! Do not put spaces after commas

#########################
# 	Miscellaneous		#
#########################
.PHONY = clean build test
uniq = $(if $1,$(firstword $1) $(call uniq,$(filter-out $(firstword $1),$1)))
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))



#########################
# 		Project			#
#########################

NAME=binary-parser
NAME_ENTRY = main.c
NAME_CONFIG = config.h

#########################
# 		Tools			#
#########################
TOOL_MKDIR = mkdir -p
TOOL_CC = mingw32-gcc
TOOL_CP = cp
TOOL_GCOV = gcov


#########################
# 		Base Config		#
#########################
# Directories
DIR_PRJ_ROOT := 
DIR_SOURCE :=	$(DIR_PRJ_ROOT)Src/
DIR_LIBS := 	$(DIR_PRJ_ROOT)Libs/
DIR_INCLUDES := $(DIR_PRJ_ROOT)Inc/
DIR_BUILD := 	$(DIR_PRJ_ROOT)Build/$(FLAVOR)/
DIR_DEPS := 	$(DIR_PRJ_ROOT)Deps/
DIR_TESTS :=	$(DIR_PRJ_ROOT)Tests/

# Base Sources
FILES_SOURCES = $(call rwildcard, $(DIR_SOURCE),*.c)

# Shared Compiler Flags
CONF_BUILD_DATE =$$(date +'%Y%m%d')
CFLAGS = -DBUILD_DATE=$(CONF_BUILD_DATE) 
CFLAGS += -I$(DIR_INCLUDES)
CFLAGS += -Wall

# Shared Linker Flags
LDFLAGS =


#########################
# 		FLAVORS			#
#########################
ifeq ($(FLAVOR),Debug)
	ARTIFACT := $(DIR_BUILD)$(NAME).exe
	CFLAGS += -g
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm

else ifeq ($(FLAVOR),Run)
	ARTIFACT := $(DIR_BUILD)$(NAME).exe
	CFLAGS += -O0
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm

else ifeq ($(FLAVOR),Test)
	NAME = test-$(TEST_TARGET)
	ARTIFACT := $(DIR_BUILD)$(NAME).exe
	CFLAGS += -g
	#CFLAGS += -DLOG_DEBUG
	CFLAGS += -DSTATIC=
	CFLAGS += -DPROTOTYPE=extern
	CFLAGS += -O0
	CFLAGS += -ftest-coverage
	CFLAGS += -fprofile-arcs
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm
	LDFLAGS += -lgcov --coverage

	# Filter out the main 
	FILES_SOURCES := $(filter-out $(call rwildcard, $(DIR_SOURCE),*$(NAME_ENTRY)),$(FILES_SOURCES))

	# Set new target
	FILE_UNIT_TEST = $(call rwildcard, $(DIR_TESTS),$(NAME).c)
	FILE_TARGET =  $(call rwildcard, $(DIR_SOURCE),$(TEST_TARGET).c)
	FILES_SOURCES += $(FILE_UNIT_TEST)

	# Files to run cover for
	COVERS := $(FILE_TARGET:%.c=%.gcda)

	# Include Testing Dependencies
	FILES_UNITY := $(DIR_DEPS)Unity-master/src
	FILES_SOURCES += $(call rwildcard, $(FILES_UNITY),*.c)
	CFLAGS += -I$(FILES_UNITY)

endif

# All Objects
FILES_OBJECTS = $(FILES_SOURCES:%.c=%.o)
DIRS_OBJECTS = $(addprefix $(DIR_BUILD),$(call uniq, $(sort $(dir $(FILES_SOURCES)))))

#########################
# 		Commands		#
#########################
clean:
	@echo "-- Cleaning up --"
	rm -rvf $(DIR_BUILD)*

build: $(ARTIFACT)

all: clean build

test: 
	#export GCOV_PREFIX_STRIP=1 && export GCOV_PREFIX=$(DIR_BUILD)
	@echo "[RUNNING $(ARTIFACT)]"
	./$(ARTIFACT)
	$(TOOL_GCOV) $(addprefix $(DIR_BUILD),$(COVERS)) -p
	mv *gcov $(DIR_BUILD)


#########################
# 	Building Rules	    #
#########################

# Create Build Folders
$(DIRS_OBJECTS): $(LIBS)
	@echo "[CREATING Directories]"
	${TOOL_MKDIR} $(DIRS_OBJECTS)

# Link Objects to Artefact
$(ARTIFACT): $(DIRS_OBJECTS) $(FILES_OBJECTS)
	@echo "[LINKING $(ARTIFACT)]"
	${TOOL_CC} ${LDFLAGS} -o $@ $(addprefix $(DIR_BUILD),$(FILES_OBJECTS))

# Generate Objects for Linking
%.o: %.c
	@echo "[BUILDING $@]"
	$(TOOL_CC) $(CFLAGS) -c $< -o $(DIR_BUILD)$@








