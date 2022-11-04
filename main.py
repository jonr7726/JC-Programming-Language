import sys
import os
import subprocess
import compiler
from compiler.error import JCError

EXTENSION = "jc"

SPACE = 9
def format_space(string):
    return string + (" " * (SPACE - len(string)))

HELP_LINE_START = ": "
def format_help_message(help_message):
    formatted = ""
    help_message = help_message.split("\n")

    formatted += HELP_LINE_START + help_message[0][0].upper() + help_message[0][1:]
    for line in help_message[1:]:
        formatted += "\n" + (" " * (SPACE + len(HELP_LINE_START))) + line

    return formatted

def make_help_line(identifier, help_message):
    return format_space(identifier) + format_help_message(help_message)

class Option:
    def __init__(self, *args, type="bool", val=False, help_message="", help_args=None):
        self.args = []
        for arg in args:
            self.args.append(arg)

        self.val = val
        self.type = type
        self.help_message = help_message
        self.help_args = help_args

    def arg_to_string(self, index):
        if self.help_args != None:
            return "-%s [%s]" % (self.args[index], " | ".join(self.help_args))
        else:
            return "-%s" % self.args[index]

    def help(self):
        string = ""
        for arg in range(len(self.args[:-1])):
            string += "%s\n" % self.arg_to_string(arg)

        string += make_help_line("%s" % self.arg_to_string(-1), self.help_message)

        return string

options = {
    "help": Option(
        "h", "help",
        help_message="Displays this message"
    ),
    "ir": Option(
        "ll", "ir",
        help_message="Does not delete IR file ('.ll' file) after compiling"
    ),
    "lib": Option(
        "lib",
        help_message="Compiles only to IR file (overrides -ir (-ll) and -i options)"
    ),
    "interpret": Option(
        "i",
        help_message="Interprets file rather than compiles\n" +
            "(Runs code then deletes binary files)"
    ),
    "output": Option(
        "o",
        type="string",val=None,
        help_args=["file"],
        help_message="Set output file (Followed by file name argument)\n" +
            "Output file must have no extension"
    ),
    "debug": Option(
        "d",
        help_message="Debug: prints assembly code before compiles"
    ),
}

def is_option(arg):
    return arg[0] == "-"

class UserError(JCError):
    def __init__(self, message):
        super().__init__("%s; use '-%s' for help" %
            (message, options["help"].args[0]))

class ArgError(UserError):
    def __init__(self, arg, after=None, expected=False):
        # Expected arg, or arg where unexpected
        expected = "Expected" if expected else "Unexpected"

        # Arg is option or argument
        type = "option" if is_option(arg) else "argument"

        # Preceeding option / argument
        after = "" if (after == None) else " after '%s'" % after

        super().__init__("%s %s %s%s" % (expected, type, arg, after))

class ExtensionError(UserError):
    def __init__(self, file_type, file, expected=None):
        # Get extension
        if "." not in file:
            extension = None
        else:
            extension = file.split(".")[-1]

        assert(extension != None or expected != None)
        # (Ensures error declared when calling super)

        if extension == None and expected != None:
            error = "%s '%s' does not have extension (expected: '.%s')" % (
                file_type, file, expected)
        elif extension != None and expected == None:
            error = "%s '%s' has unexpected extension (found: '.%s')" % (
                file_type, file, extension)
        elif extension != None and expected != None:
            error = "%s '%s' has invalid extension (expected: '.%s', found: '.%s')" % (
                file_type, file, expected, extension)

        super().__init__(error)

# Get command line arguments and options
source_file = None
skip_next = 0
for arg in range(1, len(sys.argv)):
    if skip_next > 0:
        skip_next = skip_next - 1
        continue
    elif is_option(sys.argv[arg]):
        for option in options:
            if sys.argv[arg][1:] in options[option].args:
                if option == "help":
                    if arg != 1:
                        # Added help after other args
                        raise ArgError(sys.argv[arg])
                    elif len(sys.argv) > 2:
                        # Added args after help
                        raise ArgError(sys.argv[arg+1], after=sys.argv[arg])
                if options[option].type == "bool":
                    options[option].val = True;
                elif options[option].type == "string":
                    # Set value to next argument
                    if arg + 1 >= len(sys.argv):
                        raise ArgError("file name", after=sys.argv[arg], expected=True)
                    elif is_option(sys.argv[arg + 1]):
                        raise ArgError("file name", after=sys.argv[arg], expected=True)
                    else:
                        options[option].val = sys.argv[arg + 1]
                        skip_next = 1
    else:
        if source_file == None:
            # Ensure source file has valid extension
            if (not "." in sys.argv[arg]) or (sys.argv[arg].split(".")[-1] != EXTENSION):
                raise ExtensionError("input file", sys.argv[arg], expected=EXTENSION)
            else:
                source_file = sys.argv[arg]
        else:
             raise ArgError(sys.argv[arg])

# Help
if options["help"].val == True:
    print("usage: %s [option | argument] ..." % sys.argv[0])
    print("Arguments:")
    print(make_help_line("File", "The source code file to compile (or interpret)\n" +
        "Must have the valid extension: '.%s'" % EXTENSION))
    print("Options:")
    for option in options:
        print(options[option].help())
    quit()

# Set input
if source_file == None:
    raise UserError("Please enter file to compile")

# Set output file
if options["output"].val != None:
    if "." in options["output"].val:
        raise ExtensionError("output file", options["output"].val, expected=None)
    else:
        out_file = options["output"].val
else:
    out_file = source_file.split(".")[0]

# Set input directory
directory = os.path.dirname(os.path.realpath(source_file))

# Open source code file
with open(source_file) as f:
    text_input = f.read()

# Run preprocessor
pre = compiler.Preprocessor(directory)
text_input = pre.process(text_input)

# Perform lexical analysis
lexer = compiler.Lexer().get_lexer()
tokens = lexer.lex(text_input)

token_names = [rule.name for rule in lexer.rules]

# Initialise IR code generation
codegen = compiler.CodeGen()

# Parse tokens
pg = compiler.Parser(codegen.module, codegen.builder, codegen.functions, token_names)
pg.parse()
parser = pg.get_parser()

parser.parse(tokens).eval()

# Print parser warnings
if options["debug"].val:
    for warning in parser.lr_table.sr_conflicts:
        print("Shift/reduce conflict: %s" % str(warning))
    for warning in parser.lr_table.rr_conflicts:
        print("Reduce/reduce conflict: %s" % str(warning))

# Compile to IR
codegen.create_ir(pg.state.mod_refs, options["debug"].val)
codegen.save_ir(out_file + ".ll")

if options["lib"].val == False:
    # Compile to object code
    res =  subprocess.call("llc -filetype=obj %s.ll" % out_file, shell = True)
    if res != 0:
        raise JCError("Error compiling IR: %s" % res)

    # Delete IR file
    if options["ir"].val == False:
        subprocess.call("rm %s.ll" % out_file, shell = True)

    # Compile to machine code
    res = subprocess.call("gcc %s.o -o %s -no-pie" % (out_file, out_file), shell = True)
    if res != 0:
        raise JCError("Error compiling IR: %s" % res)

    # Run code and delete output file
    if options["interpret"].val == True:
        subprocess.call("./%s" % out_file, shell = True)
        subprocess.call("rm %s" % out_file, shell = True)