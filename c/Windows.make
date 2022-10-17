# Usage:
# make all     # compile all binary
# make clean  # remove ALL binaries and objects
# NB! Do not put spaces after commas
.PHONY = clean build test
uniq = $(if $1,$(firstword $1) $(call uniq,$(filter-out $(firstword $1),$1)))
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))

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
DIR_SOURCE :=Src/
DIR_LIBS := Libs/
DIR_INCLUDES := Inc/
DIR_BUILD := Build/$(FLAVOR)/
DIR_DEPS := Deps/
DIR_TESTS :=Tests/

FILES_SOURCES = $(call rwildcard, $(DIR_SOURCE),*.c)

# Compilation
CONF_BUILD_DATE =$$(date +'%Y%m%d')
CFLAGS=-DBUILD_DATE=$(CONF_BUILD_DATE) 
LDFLAGS =


#########################
# 		FLAVORS			#
#########################
ifeq ($(FLAVOR),Debug)
	CFLAGS += -I$(DIR_INCLUDES)
	CFLAGS += -g
	CFLAGS += -Wall
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm
	ARTIFACT := $(DIR_BUILD)$(NAME)_debug.exe

else ifeq ($(FLAVOR),Run)
	CFLAGS += -I$(DIR_INCLUDES)
	CFLAGS += -O0
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm
	ARTIFACT := $(DIR_BUILD)$(NAME).exe

else ifeq ($(FLAVOR),Test)
	CFLAGS += -g
	CFLAGS += -DLOG_TEST
	CFLAGS += -I$(DIR_INCLUDES)
	CFLAGS += -O0
	CFLAGS += -ftest-coverage
	CFLAGS += -fprofile-arcs
	LDFLAGS += -L"$(DIR_LIBS)"
	LDFLAGS += -lm
	LDFLAGS += -lgcov --coverage

	# Files to run cover for
	COVERS = $(FILES_SOURCES:%.c=%.gcda)

	# Select Test Target
	FILES_SOURCES := $(filter-out $(wildcard */$(NAME_ENTRY)), $(FILES_SOURCES))
	FILES_SOURCES += $(call rwildcard, $(DIR_TESTS),$(TEST_TARGET).c)

	ARTIFACT := $(DIR_BUILD)$(TEST_TARGET).exe

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
	#export GCOV_PREFIX_STRIP=1 && export GCOV_PREFIX=$(DIR_BUILD) &&
	./$(ARTIFACT)
	$(TOOL_GCOV) $(addprefix $(DIR_BUILD),$(COVERS))

#########################
# 	Building Rules	    #
#########################

# Create Build Folders
$(DIRS_OBJECTS): $(LIBS)
	@echo "-- Creating Directories --"
	${TOOL_MKDIR} $(DIRS_OBJECTS)

# Link Objects to Artefact
$(ARTIFACT): $(DIRS_OBJECTS) $(FILES_OBJECTS)
	@echo "-- Creating Exe $(ARTIFACT) --"
	${TOOL_CC} ${LDFLAGS} -o $@ $(addprefix $(DIR_BUILD),$(FILES_OBJECTS))

# Generate Objects for Linking
%.o: %.c
	@echo "-- Creating Object $@ --"
	$(TOOL_CC) $(CFLAGS) -c $< -o $(DIR_BUILD)$@








