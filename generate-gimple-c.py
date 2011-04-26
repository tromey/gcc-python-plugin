from maketreetypes import iter_gimple_types, iter_gimple_struct_types

from cpybuilder import *

cu = CompilationUnit()
cu.add_include('gcc-python.h')
cu.add_include('gcc-python-wrappers.h')
cu.add_include('gcc-plugin.h')
cu.add_include("gimple.h")

modinit_preinit = ''
modinit_postinit = ''

gimple_struct_types = list(iter_gimple_struct_types())
gimple_types = list(iter_gimple_types())

# gimple.h declares a family of struct gimple_statement_* which internally express an inheritance hierarchy, via enum enum gimple_statement_structure_enum (see gsstruct.def).
# FIXME there's also enum gimple_code, which is used to look up into this hierarchy
#
# From reading gimple.h, the struct hierarchy is:
#
# gimple_statement_base (GSS_BASE)
#   gimple_statement_with_ops_base
#      gimple_statement_with_ops (GSS_WITH_OPS)
#      gimple_statement_with_memory_ops_base (GSS_WITH_MEM_OPS_BASE)
#         gimple_statement_with_memory_ops (GSS_WITH_MEM_OPS)
#         gimple_statement_call (GSS_CALL)
#         gimple_statement_asm (GSS_ASM)
#   gimple_statement_omp (GSS_OMP)
#     gimple_statement_omp_critical (GSS_OMP_CRITICAL)
#     gimple_statement_omp_for (GSS_OMP_FOR)
#     gimple_statement_omp_parallel (GSS_OMP_PARALLEL)
#       gimple_statement_omp_task (GSS_OMP_TASK)
#     gimple_statement_omp_sections (GSS_OMP_SECTIONS)
#     gimple_statement_omp_single (GSS_OMP_SINGLE)
#   gimple_statement_bind (GSS_BIND)
#   gimple_statement_catch (GSS_CATCH)
#   gimple_statement_eh_filter (GSS_EH_FILTER)
#   gimple_statement_eh_mnt (GSS_EH_MNT)
#   gimple_statement_phi (GSS_PHI)
#   gimple_statement_eh_ctrl (GSS_EH_CTRL)
#   gimple_statement_try (GSS_TRY)
#   gimple_statement_wce (GSS_WCE)
#   gimple_statement_omp_continue (GSS_OMP_CONTINUE)   (does not inherit from gimple_statement_omp)
#   gimple_statement_omp_atomic_load (GSS_OMP_ATOMIC_LOAD  (likewise)
#   gimple_statement_omp_atomic_store (GSS_OMP_ATOMIC_STORE)  (ditto)

# The inheritance hierarchy of struct gimple_statement_*,
#  expressed as (structname, parentstructname) pairs:
struct_hier = (('gimple_statement_base', None),
               ('gimple_statement_with_ops_base', 'simple_statement_base'),
               ('gimple_statement_with_ops', 'gimple_statement_with_ops_base'),
               ('gimple_statement_with_memory_ops_base', 'gimple_statement_with_ops_base opbase'),
               ('gimple_statement_with_memory_ops', 'gimple_statement_with_memory_ops_base membase'),
               ('gimple_statement_call', 'gimple_statement_with_memory_ops_base membase'),
               ('gimple_statement_omp', 'gimple_statement_base'),
               ('gimple_statement_bind', 'gimple_statement_base'),
               ('gimple_statement_catch', 'gimple_statement_base'),
               ('gimple_statement_eh_filter', 'gimple_statement_base'),
               ('gimple_statement_eh_mnt', 'gimple_statement_base'),
               ('gimple_statement_phi', 'gimple_statement_base'),
               ('gimple_statement_eh_ct', 'gimple_statement_base'),
               ('gimple_statement_try', 'gimple_statement_base'),
               ('gimple_statement_wce', 'gimple_statement_base'),
               ('gimple_statement_asm', 'gimple_statement_with_memory_ops_base'),
               ('gimple_statement_omp_critical', 'gimple_statement_omp'),
               ('gimple_statement_omp_for', 'gimple_statement_omp'),
               ('gimple_statement_omp_parallel', 'gimple_statement_omp'),
               ('gimple_statement_omp_task', 'gimple_statement_omp_parallel'),
               ('gimple_statement_omp_sections', 'gimple_statement_omp'),
               ('gimple_statement_omp_continue', 'gimple_statement_base'),
               ('gimple_statement_omp_single', 'gimple_statement_omp'),
               ('gimple_statement_omp_atomic_load', 'gimple_statement_base'),
               ('gimple_statement_omp_atomic_store', 'gimple_statement_base'))

# Interleaving with the material from gimple.def:
# gimple_statement_base (GSS_BASE)
#   GIMPLE_ERROR_MARK, "gimple_error_mark", GSS_BASE
#   GIMPLE_NOP, "gimple_nop", GSS_BASE
#   GIMPLE_OMP_RETURN, "gimple_omp_return", GSS_BASE
#   GIMPLE_OMP_SECTIONS_SWITCH, "gimple_omp_sections_switch", GSS_BASE
#   GIMPLE_PREDICT, "gimple_predict", GSS_BASE
#   gimple_statement_with_ops_base
#      gimple_statement_with_ops (GSS_WITH_OPS)
#        GIMPLE_COND, "gimple_cond", GSS_WITH_OPS
#        GIMPLE_DEBUG, "gimple_debug", GSS_WITH_OPS
#        GIMPLE_GOTO, "gimple_goto", GSS_WITH_OPS
#        GIMPLE_LABEL, "gimple_label", GSS_WITH_OPS
#        GIMPLE_SWITCH, "gimple_switch", GSS_WITH_OPS
#      gimple_statement_with_memory_ops_base (GSS_WITH_MEM_OPS_BASE)
#         gimple_statement_with_memory_ops (GSS_WITH_MEM_OPS)
#           GIMPLE_ASSIGN, "gimple_assign", GSS_WITH_MEM_OPS
#           GIMPLE_RETURN, "gimple_return", GSS_WITH_MEM_OPS
#         gimple_statement_call (GSS_CALL)
#           GIMPLE_CALL, "gimple_call", GSS_CALL
#         gimple_statement_asm (GSS_ASM)
#            GIMPLE_ASM, "gimple_asm", GSS_ASM
#   gimple_statement_omp (GSS_OMP)
#     GIMPLE_OMP_MASTER, "gimple_omp_master", GSS_OMP
#     GIMPLE_OMP_ORDERED, "gimple_omp_ordered", GSS_OMP
#     GIMPLE_OMP_SECTION, "gimple_omp_section", GSS_OMP
#     gimple_statement_omp_critical (GSS_OMP_CRITICAL)
#       GIMPLE_OMP_CRITICAL, "gimple_omp_critical", GSS_OMP_CRITICAL
#     gimple_statement_omp_for (GSS_OMP_FOR)
#        GIMPLE_OMP_FOR, "gimple_omp_for", GSS_OMP_FOR
#     gimple_statement_omp_parallel (GSS_OMP_PARALLEL)
#       GIMPLE_OMP_PARALLEL, "gimple_omp_parallel", GSS_OMP_PARALLEL
#       gimple_statement_omp_task (GSS_OMP_TASK)
#       GIMPLE_OMP_TASK, "gimple_omp_task", GSS_OMP_TASK
#     gimple_statement_omp_sections (GSS_OMP_SECTIONS)
#       GIMPLE_OMP_SECTIONS, "gimple_omp_sections", GSS_OMP_SECTIONS
#     gimple_statement_omp_single (GSS_OMP_SINGLE)
#       GIMPLE_OMP_SINGLE, "gimple_omp_single", GSS_OMP_SINGLE
#   gimple_statement_bind (GSS_BIND)
#     GIMPLE_BIND, "gimple_bind", GSS_BIND
#   gimple_statement_catch (GSS_CATCH)
#     GIMPLE_CATCH, "gimple_catch", GSS_CATCH
#   gimple_statement_eh_filter (GSS_EH_FILTER)
#      GIMPLE_EH_FILTER, "gimple_eh_filter", GSS_EH_FILTER
#   gimple_statement_eh_mnt (GSS_EH_MNT)
#      GIMPLE_EH_MUST_NOT_THROW, "gimple_eh_must_not_throw", GSS_EH_MNT
#   gimple_statement_phi (GSS_PHI)
#      GIMPLE_PHI, "gimple_phi", GSS_PHI
#   gimple_statement_eh_ctrl (GSS_EH_CTRL)
#      GIMPLE_RESX, "gimple_resx", GSS_EH_CTRL
#      GIMPLE_EH_DISPATCH, "gimple_eh_dispatch", GSS_EH_CTRL
#   gimple_statement_try (GSS_TRY)
#     GIMPLE_TRY, "gimple_try", GSS_TRY
#   gimple_statement_wce (GSS_WCE)
#     GIMPLE_WITH_CLEANUP_EXPR, "gimple_with_cleanup_expr", GSS_WCE
#   gimple_statement_omp_continue (GSS_OMP_CONTINUE)   (does not inherit from gimple_statement_omp)
#     GIMPLE_OMP_CONTINUE, "gimple_omp_continue", GSS_OMP_CONTINUE
#   gimple_statement_omp_atomic_load (GSS_OMP_ATOMIC_LOAD  (likewise)
#     GIMPLE_OMP_ATOMIC_LOAD, "gimple_omp_atomic_load", GSS_OMP_ATOMIC_LOAD
#   gimple_statement_omp_atomic_store (GSS_OMP_ATOMIC_STORE)  (ditto)
#     GIMPLE_OMP_ATOMIC_STORE, "gimple_omp_atomic_store", GSS_OMP_ATOMIC_STORE


def generate_gimple_struct_subclasses():
    global modinit_preinit
    global modinit_postinit
    
    for gt in gimple_struct_types:
    #print gimple_types
        cc = gt.camel_cased_string()
        pytype = PyTypeObject(identifier = 'gcc_GimpleStructType%sType' % cc,
                              localname = 'GimpleStructType' + cc,
                              tp_name = 'gcc.GimpleStructType%s' % cc,
                              struct_name = 'struct PyGccGimple',
                              tp_new = 'PyType_GenericNew',
                              tp_base = '&gcc_GimpleType',
                              #tp_getset = getsettable.identifier,
                              #tp_repr = '(reprfunc)gcc_Gimple_repr',
                              #tp_str = '(reprfunc)gcc_Gimple_str',
                              )
        cu.add_defn(pytype.c_defn())
        modinit_preinit += pytype.c_invoke_type_ready()
        modinit_postinit += pytype.c_invoke_add_to_module()

#generate_gimple_struct_subclasses()

# See gcc/gimple-pretty-print.c (e.g. /usr/src/debug/gcc-4.6.0-20110321/gcc/gimple-pretty-print.c )
# for hints on the innards of gimple, in particular, see dump_gimple_stmt

def generate_gimple():
    #
    # Generate the gcc.Gimple class:
    #
    global modinit_preinit
    global modinit_postinit

    cu.add_defn("""
static PyObject *
gcc_Gimple_get_location(struct PyGccGimple *self, void *closure)
{
    return gcc_python_make_wrapper_location(gimple_location(self->stmt));
}

static PyObject *
gcc_Gimple_get_block(struct PyGccGimple *self, void *closure)
{
    return gcc_python_make_wrapper_tree(gimple_block(self->stmt));
}
""")

    getsettable = PyGetSetDefTable('gcc_Gimple_getset_table',
                                   [PyGetSetDef('loc', 'gcc_Gimple_get_location', None, 'Source code location of this statement, as a gcc.Location'),
                                    PyGetSetDef('block', 'gcc_Gimple_get_block', None, 'The lexical block holding this statement, as a gcc.Tree'),
                                    PyGetSetDef('exprtype',
                                                cu.add_simple_getter('gcc_Gimple_get_exprtype',
                                                                     'PyGccGimple',
                                                                     'gcc_python_make_wrapper_tree(gimple_expr_type(self->stmt))'),
                                                None,
                                                'The type of the main expression computed by this statement, as a gcc.Tree (which might be gcc.VoidType)'),
                                    ])
    cu.add_defn(getsettable.c_defn())

    pytype = PyTypeObject(identifier = 'gcc_GimpleType',
                          localname = 'Gimple',
                          tp_name = 'gcc.Gimple',
                          struct_name = 'struct PyGccGimple',
                          tp_new = 'PyType_GenericNew',
                          tp_getset = getsettable.identifier,
                          tp_repr = '(reprfunc)gcc_Gimple_repr',
                          tp_str = '(reprfunc)gcc_Gimple_str',
                          )
    cu.add_defn(pytype.c_defn())
    modinit_preinit += pytype.c_invoke_type_ready()
    modinit_postinit += pytype.c_invoke_add_to_module()

generate_gimple()

def generate_gimple_subclasses():
    global modinit_preinit
    global modinit_postinit
    
    exprcode_getter = PyGetSetDef('exprcode',
                                  cu.add_simple_getter('gcc_Gimple_get_exprcode',
                                                       'PyGccGimple',
                                                       '(PyObject*)gcc_python_autogenerated_tree_type_for_tree_code(gimple_expr_code(self->stmt), 0)'),
                                  None,
                                  'The kind of the expression, as an gcc.Tree subclass (the type itself, not an instance)')

    rhs_getter = PyGetSetDef('rhs',
                             'gcc_Gimple_get_rhs',
                             None,
                             'The operands on the right-hand-side of the expression, as a list of gcc.Tree instances')

    def make_getset_Assign():
        return PyGetSetDefTable('gcc_%s_getset_table' % cc,
                                [PyGetSetDef('lhs',
                                             cu.add_simple_getter('gcc_GimpleAssign_get_lhs',
                                                                  'PyGccGimple',
                                                                  'gcc_python_make_wrapper_tree(gimple_assign_lhs(self->stmt))'),
                                             None,
                                             'Left-hand-side of the assignment, as a gcc.Tree'),
                                 exprcode_getter,
                                 rhs_getter,
                                 ])
    def make_getset_Call():
        return PyGetSetDefTable('gcc_%s_getset_table' % cc,
                                [PyGetSetDef('lhs',
                                             cu.add_simple_getter('gcc_GimpleCall_get_lhs',
                                                                  'PyGccGimple',
                                                                  'gcc_python_make_wrapper_tree(gimple_call_lhs(self->stmt))'),
                                             None,
                                             'Left-hand-side of the call, as a gcc.Tree'),
                                 rhs_getter,
                                 PyGetSetDef('fn',
                                             cu.add_simple_getter('gcc_GimpleCall_get_fn',
                                                                  'PyGccGimple',
                                                                  'gcc_python_make_wrapper_tree(gimple_call_fn(self->stmt))'),
                                             None,
                                             'The function being called, as a gcc.Tree'),
                                 exprcode_getter,
                                 ])
    def make_getset_Return():
        return PyGetSetDefTable('gcc_%s_getset_table' % cc,
                                [PyGetSetDef('retval',
                                             cu.add_simple_getter('gcc_GimpleReturn_get_retval',
                                                                  'PyGccGimple',
                                                                  'gcc_python_make_wrapper_tree(gimple_return_retval(self->stmt))'),
                                             None,
                                             'The return value, as a gcc.Tree'),
                                 ])


    def make_getset_Cond():
        return PyGetSetDefTable('gcc_%s_getset_table' % cc,
                                [exprcode_getter])

    for gt in gimple_types:
        cc = gt.camel_cased_string()

        getsettable = None
        if cc == 'GimpleAssign':
            getsettable = make_getset_Assign()
        elif cc == 'GimpleCall':
            getsettable = make_getset_Call()
        elif cc == 'GimpleCond':
            getsettable = make_getset_Cond()
        elif cc == 'GimpleReturn':
            getsettable = make_getset_Return()

        if getsettable:
            cu.add_defn(getsettable.c_defn())

            
        pytype = PyTypeObject(identifier = 'gcc_%sType' % cc,
                              localname = cc,
                              tp_name = 'gcc.%s' % cc,
                              struct_name = 'struct PyGccGimple',
                              tp_new = 'PyType_GenericNew',
                              tp_base = '&gcc_GimpleType',
                              tp_getset = getsettable.identifier if getsettable else None,
                              #tp_repr = '(reprfunc)gcc_Gimple_repr',
                              #tp_str = '(reprfunc)gcc_Gimple_str',
                              )
        cu.add_defn(pytype.c_defn())
        modinit_preinit += pytype.c_invoke_type_ready()
        modinit_postinit += pytype.c_invoke_add_to_module()

generate_gimple_subclasses()

def generate_gimple_code_map():
    cu.add_defn('\n/* Map from GCC gimple codes to PyTypeObject* */\n')
    cu.add_defn('PyTypeObject *pytype_for_gimple_code[] = {\n')
    for gt in gimple_types:
        cc = gt.camel_cased_string()
        cu.add_defn('    &gcc_%sType, /* %s */\n' % (cc, gt.gimple_symbol))
    cu.add_defn('};\n\n')

    cu.add_defn("""
PyTypeObject*
gcc_python_autogenerated_gimple_type_for_stmt(gimple g)
{
    enum gimple_code code = gimple_code(g);

    /* printf("code:%i\\n", code); */
    assert(code >= 0);
    assert(code < LAST_AND_UNUSED_GIMPLE_CODE);
    return pytype_for_gimple_code[code];
}
""")

generate_gimple_code_map()


cu.add_defn("""
int autogenerated_gimple_init_types(void)
{
""" + modinit_preinit + """
    return 1;

error:
    return 0;
}
""")

cu.add_defn("""
void autogenerated_gimple_add_types(PyObject *m)
{
""" + modinit_postinit + """
}
""")


print(cu.as_str())
