# Usage:
# make        # compile all binary
# make clean  # remove ALL binaries and objects
# NB! Do not put spaces after commas
.PHONY = all clean
uniq = $(if $1,$(firstword $1) $(call uniq,$(filter-out $(firstword $1),$1)))
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))

NAME=parser

# Tools
TOOL_MKDIR = mkdir -p
TOOL_CC = mingw32-gcc
TOOL_CP = cp
TOOL_GCOV = gcov

# Directories
DIR_SOURCE :=Src/
DIR_LIBS := Libs/
DIR_INCLUDES := Inc/
DIR_BUILD := Build/$(FLAVOR)/

SOURCES = $(call rwildcard, $(DIR_SOURCE),*.c)
OBJECTS = $(SOURCES:%.c=%.o)
COVERS = $(SOURCES:%.c=%.gcda)
DEPS=
DIRS_OBJECTS = $(addprefix $(DIR_BUILD),$(call uniq, $(sort $(dir $(SOURCES)))))

# Compilation
CONF_BUILD_DATE =$$(date +'%Y%m%d')

ARTIFACT=
CFLAGS=-DBUILD_DATE=$(CONF_BUILD_DATE) 
LDFLAGS =

# Compiler flags
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
	ARTIFACT := $(DIR_BUILD)$(NAME).exe
endif



# Switches
clean:
	@echo "-- Cleaning up --"
	rm -rvf $(DIR_BUILD)*

build: $(ARTIFACT)

cover: 
	./$(ARTIFACT) Inputs/sdn3pd.s19
	$(TOOL_GCOV) $(addprefix $(DIR_BUILD),$(COVERS))

# Prepare Build Folder
$(DIRS_OBJECTS): $(LIBS)
	@echo "-- Creating Directories --"
	${TOOL_MKDIR} $(DIRS_OBJECTS)

# Link artefact
$(ARTIFACT): $(DIRS_OBJECTS) $(LIBS) $(OBJECTS)
	@echo "-- Creating Exe $(ARTIFACT) --"
	${TOOL_CC} ${LDFLAGS} -o $@ $(addprefix $(DIR_BUILD),$(OBJECTS))

# Generate an Objects
%.o: %.c
	@echo "-- Creating Object $@ --"
	$(TOOL_CC) $(CFLAGS) -c $< -o $(DIR_BUILD)$@








