from llvmlite import ir, binding
from .lang.types import *

class CodeGen():
    def __init__(self):
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()
        self._config_llvm()
        self._create_execution_engine()
        self._declare_functions()

    def _config_llvm(self):
        # Config LLVM
        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()
        self.builder = ir.IRBuilder()

    def _create_execution_engine(self):
        """
        Create an ExecutionEngine suitable for JIT code generation on
        the host CPU.  The engine is reusable for an arbitrary number of
        modules.
        """
        target = self.binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module
        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        self.engine = engine

    def _declare_functions(self):
        self.functions = {}

        # Declare Printf function
        printf_ty = ir.FunctionType(INTEGER_TYPE,
            [CHARACTER_TYPE.as_pointer()], var_arg=True)
        self.functions["printf"] = ir.Function(self.module, printf_ty,
            name="printf")

        # Declare Malloc function
        malloc_ty = ir.FunctionType(CHARACTER_TYPE.as_pointer(),
            [INTEGER_TYPE], var_arg=True)
        self.functions["malloc"] = ir.Function(self.module, malloc_ty,
            name="malloc")

        # Declare Realloc function
        realloc_ty = ir.FunctionType(CHARACTER_TYPE.as_pointer(),
            [CHARACTER_TYPE.as_pointer(), INTEGER_TYPE], var_arg=True)
        self.functions["realloc"] = ir.Function(self.module, realloc_ty,
            name="realloc")

    def _compile_ir(self, debug):
        """
        Compile the LLVM IR string with the given engine.
        The compiled module object is returned.
        """
        # Create a LLVM module object from the IR
        llvm_ir = str(self.module)
        if debug: print(llvm_ir)
        mod = self.binding.parse_assembly(llvm_ir)
        mod.verify()

        # Link modules
        for ref in self.mod_refs:
            with open(ref) as f:
                mod_ref = binding.parse_assembly(f.read())
                if debug: print(mod_ref)
                mod_ref.verify()
                mod.link_in(mod_ref)

        if debug: print("\n\n\n\n\n", dir(mod))
        # Now add the module and make sure it is ready for execution
        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    def create_ir(self, mod_refs, debug=False):
        self.mod_refs = mod_refs
        self.module = self._compile_ir(debug)

    def save_ir(self, filename):
        with open(filename, 'w') as output_file:
            output_file.write(str(self.module))