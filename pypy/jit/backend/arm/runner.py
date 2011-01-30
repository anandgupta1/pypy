from pypy.jit.backend.arm.assembler import AssemblerARM
from pypy.jit.backend.arm.arch import WORD
from pypy.jit.backend.arm.registers import all_regs
from pypy.jit.backend.llsupport.llmodel import AbstractLLCPU
from pypy.rpython.llinterp import LLInterpreter
from pypy.rpython.lltypesystem import lltype, rffi, llmemory


class ArmCPU(AbstractLLCPU):

    BOOTSTRAP_TP = lltype.FuncType([], lltype.Signed)
    supports_floats = False

    def __init__(self, rtyper, stats, opts=None, translate_support_code=False,
                 gcdescr=None):
        AbstractLLCPU.__init__(self, rtyper, stats, opts,
                               translate_support_code, gcdescr)
    def setup(self):
        if self.opts is not None:
            failargs_limit = self.opts.failargs_limit
        else:
            failargs_limit = 1000
        self.assembler = AssemblerARM(self)

    def setup_once(self):
        self.assembler.setup_once()

    def finish_once(self):
        pass

    def compile_loop(self, inputargs, operations, looptoken, log=True):
        self.assembler.assemble_loop(inputargs, operations,
                                                    looptoken, log=log)

    def compile_bridge(self, faildescr, inputargs, operations,
                                       original_loop_token, log=True):
        clt = original_loop_token.compiled_loop_token
        clt.compiling_a_bridge()
        self.assembler.assemble_bridge(faildescr, inputargs, operations,
                                       original_loop_token, log=log)

    def set_future_value_int(self, index, intvalue):
        self.assembler.fail_boxes_int.setitem(index, intvalue)

    def set_future_value_ref(self, index, ptrvalue):
        self.assembler.fail_boxes_ptr.setitem(index, ptrvalue)

    def get_latest_value_int(self, index):
        return self.assembler.fail_boxes_int.getitem(index)

    def get_latest_value_ref(self, index):
        return self.assembler.fail_boxes_ptr.getitem(index)

    def get_latest_value_count(self):
        return self.assembler.fail_boxes_count

    def clear_latest_values(self, count):
        setitem = self.assembler.fail_boxes_ptr.setitem
        null = lltype.nullptr(llmemory.GCREF.TO)
        for index in range(count):
            setitem(index, null)

    def execute_token(self, executable_token):
        #i = [self.get_latest_value_int(x) for x in range(10)]
        #print 'Inputargs: %r for token %r' % (i, executable_token)
        addr = executable_token._arm_bootstrap_code
        assert addr % 8 == 0
        func = rffi.cast(lltype.Ptr(self.BOOTSTRAP_TP), addr)
        fail_index = self._execute_call(func)
        return self.get_fail_descr_from_number(fail_index)

    def _execute_call(self, func):
        prev_interpreter = None
        if not self.translate_support_code:
            prev_interpreter = LLInterpreter.current_interpreter
            LLInterpreter.current_interpreter = self.debug_ll_interpreter
        res = 0
        try:
            res = func()
        finally:
            if not self.translate_support_code:
                LLInterpreter.current_interpreter = prev_interpreter
        return res

    @staticmethod
    def cast_ptr_to_int(x):
        adr = llmemory.cast_ptr_to_adr(x)
        return ArmCPU.cast_adr_to_int(adr)

    def force(self, addr_of_force_index):
        TP = rffi.CArrayPtr(lltype.Signed)
        fail_index = rffi.cast(TP, addr_of_force_index)[0]
        assert fail_index >= 0, "already forced!"
        faildescr = self.get_fail_descr_from_number(fail_index)
        rffi.cast(TP, addr_of_force_index)[0] = -1
        # start of "no gc operation!" block
        frame_depth = faildescr._arm_frame_depth
        addr_end_of_frame = (addr_of_force_index -
                            (frame_depth+len(all_regs))*WORD)
        fail_index_2 = self.assembler.failure_recovery_func(
            faildescr._failure_recovery_code,
            addr_of_force_index,
            addr_end_of_frame)
        self.assembler.leave_jitted_hook()
        # end of "no gc operation!" block
        assert fail_index == fail_index_2
        return faildescr

    def redirect_call_assembler(self, oldlooptoken, newlooptoken):
        self.assembler.redirect_call_assembler(oldlooptoken, newlooptoken)
