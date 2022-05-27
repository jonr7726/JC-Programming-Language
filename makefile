CC = gcc
CFLAGS = -Wall -Werror

TARGET = main

# Set source code, and build (object files) folders
SOURCEDIR = src
BUILDDIR = build
LIBS = lib

# Finds all c files in source directory
SRCFILES := $(wildcard $(SOURCEDIR)/*.c)

# Finds all object files, made from changing .c to .o and the \
	source directory to build directory for each source file
OBJFILES := $(subst $(SOURCEDIR),$(BUILDDIR),$(SRCFILES:.c=.o))

# Makes object file with source file, and build directory
$(BUILDDIR)/%.o : $(SOURCEDIR)/%.c $(BUILDDIR)
	$(CC) $(CFLAGS) -I$(LIBS) $< -c -o $@

# Makes excecutable with object files
$(TARGET) : $(OBJFILES)
	$(CC) $(CFLAGS) -I$(LIBS) -o $@ $^

# Creates build directory (if not already present)
$(BUILDDIR):
	mkdir $@

# Removes object files
.PHONY: clean
clean:
	rm -rf ${BUILDDIR}$/*.o