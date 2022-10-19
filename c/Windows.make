# Usage:
# make all     # compile all binary
# make clean  # remove ALL binaries and objects
# NB! Do not put spaces after commas
.PHONY = clean build test
uniq = $(if $1,$(firstword $1) $(call uniq,$(filter-out $(firstword $1),$1)))
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

NAME=binary-parser
NAME_ENTRY = main.c

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
	ARTIFACT := $(DIR_BUILD)$(TEST_TARGET).exe
	CFLAGS += -g
	CFLAGS += -DLOG_TEST
	CFLAGS += -O0
	CFLAGS += -ftest-coverage
	CFLAGS += -fprofile-arcs
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm
	LDFLAGS += -lgcov --coverage

	# Files to run cover for
	COVERS := $(FILES_SOURCES:%.c=%.gcda)

	# Filter out the main and set new target
	FILES_SOURCES := $(filter-out $(call rwildcard, $(DIR_SOURCE),*$(NAME_ENTRY)),$(FILES_SOURCES))
	FILES_SOURCES += $(call rwildcard, $(DIR_TESTS),$(TEST_TARGET).c)

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
	rm *.gcov

build: $(ARTIFACT)

all: clean build

test: 
	#export GCOV_PREFIX_STRIP=1 && export GCOV_PREFIX=$(DIR_BUILD)
	
	./$(ARTIFACT)
	$(TOOL_GCOV) $(addprefix $(DIR_BUILD),$(COVERS)) -p
	mv *gcov $(DIR_BUILD)


#########################
# 	Building Rules	    #
#########################

# Create Build Folders
$(DIRS_OBJECTS): $(LIBS)
	@echo "[Creating Directories]"
	${TOOL_MKDIR} $(DIRS_OBJECTS)

# Link Objects to Artefact
$(ARTIFACT): $(DIRS_OBJECTS) $(FILES_OBJECTS)
	@echo "[$(ARTIFACT)]"
	${TOOL_CC} ${LDFLAGS} -o $@ $(addprefix $(DIR_BUILD),$(FILES_OBJECTS))

# Generate Objects for Linking
%.o: %.c
	@echo "[$@]"
	$(TOOL_CC) $(CFLAGS) -c $< -o $(DIR_BUILD)$@








