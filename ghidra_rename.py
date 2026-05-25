# ghidra_rename.py — paste into Ghidra Script Manager, language: Jython
# Renames functions / labels at known addresses for the N55 DME firmware
# (swfl_00000fef, MEVD17.2.6 ASW).

from ghidra.program.model.symbol import SourceType

symbols = [
    (0x80032580, "Com_SignalDispatchTable_16"),
    (0x80042908, "BaudCfgEntry_ARRAY"),
    (0x80042938, "MsgCfgEntry_ARRAY"),
    (0x80043f90, "CAN_TxChannel_Cfg_Array"),
    (0x8004d4e4, "Com_RxContext_Base"),
    (0x8004d4f8, "Com_RxContext_SubCtx"),
    (0x8004d560, "Com_RxBufferDescriptor_Table"),
    (0x800500e0, "Com_SignalSubField_DescTable"),
    (0x80050c70, "SubSignal_RangeTable"),
    (0x80051d3e, "Com_SignalTimeout_LUT"),
    (0x80052e7c, "Com_SignalDescriptor_Table"),
    (0x80053188, "Com_LengthMask_LUT"),
    (0x80053214, "Com_PDU_RegTable"),
    (0x80059800, "Sched_Table_A_Fast"),
    (0x80059be0, "Sched_Table_B_10ms"),
    (0x80059e3c, "Sched_Table_C"),
    (0x80059f7c, "Sched_Table_D"),
    (0x8005a0bc, "Sched_Table_E"),
    (0x8005a210, "Sched_Table_F"),
    (0x8005a354, "Sched_Table_G"),
    (0x8007acb6, "Tick_BroadcastA_Call_Slot1"),
    (0x8007b48e, "Tick_BroadcastA_Call_Slot2"),
    (0x8007baba, "Tick_BroadcastA_Call_Slot3"),
    (0x80082c10, "Com_WriteSignal"),
    (0x80082c9c, "Com_SignalDispatch_0_AgeTimeout"),
    (0x80082f04, "Com_SignalDispatch_6"),
    (0x80082f0a, "Com_SignalDispatch_2"),
    (0x80083272, "Com_SignalDispatch_4"),
    (0x80083e12, "Com_SubSignalCommit"),
    (0x800848de, "Com_SubSignalByteWriter"),
    (0x80084e64, "Com_SignalStatusGet"),
    (0x80084f12, "Com_SignalStatusSet"),
    (0x80084fb0, "Com_SignalMultiByteSet"),
    (0x800853a6, "Com_SignalDispatch_9"),
    (0x8008542a, "Com_SignalDispatch_B"),
    (0x8008544e, "Com_SignalDispatch_D"),
    (0x80085468, "Com_SignalDispatch_C"),
    (0x800854ca, "Com_SignalDispatch_A"),
    (0x80085558, "Com_SignalDispatch_E"),
    (0x8008567e, "Com_SignalDispatch_F"),
    (0x800859f0, "Com_PublishTxTablePointers"),
    (0x80085a02, "Com_IsSubscriberActive"),
    (0x80085a74, "Com_SubSignalFlagUpdate"),
    (0x80085caa, "Com_SignalUpdate_Variant"),
    (0x80085cee, "Com_SignalUpdate_Variant2"),
    (0x800866d6, "Com_SignalWritePreamble"),
    (0x800866e4, "Com_SignalStatusLookup"),
    (0x8009ab7c, "FUN_8009ab7c_Trampoline"),
    (0x800aeb3c, "scheduler_tick_sentinel"),
    (0x800b006a, "memcpy_b"),
    (0x800b00ac, "memset_b"),
    (0x800b0b9a, "lookup_helper"),
    (0x800b133e, "math_helper_2"),
    (0x800b13a6, "math_helper_1"),
    (0x800c1732, "App_Query_0x8F_State"),
    (0x800c5d06, "CAN_BroadcastSignalGroupA"),
    (0x800c5e4e, "LAB_CAN_BroadcastA_Return"),
    (0x800c6032, "CAN_BroadcastSignalGroupB"),
    (0x800c8a28, "CAN_AssignChannelMOArray"),
    (0x800c97dc, "CAN_DataBlockLookup"),
    (0x800cae28, "Com_SignalDispatch_1"),
    (0x800cb06e, "Com_SignalDispatch_7"),
    (0x800cb296, "Com_SignalDispatch_3"),
    (0x800cb29c, "Com_SignalDispatch_5"),
    (0x800cb2a2, "Com_SignalStateUpdate2"),
    (0x800cb690, "Com_SignalDispatch_8"),
    (0x800cb6e6, "Com_SignalStateCommit"),
    (0x800cb816, "Com_SignalTimeoutPath"),
    (0x800eb3f0, "Com_ContextSwitch_Helper"),
    (0x800ed734, "Com_WriteSignal_Wrapper"),
    (0x800ed78a, "CAN_RxSubDispatcher"),
    (0x800ed846, "CAN_TimeoutDispatcher"),
    (0x800eda2c, "CAN_RxHandler_MsgType4_Inner"),
    (0x800edb84, "CAN_StoreResponseHelper"),
    (0x800edb9a, "CAN_TransmitRequestHelper"),
    (0x800ee312, "Com_PublishRxCtxBase"),
    (0x800ee3fe, "CAN_RxBitfieldExtract_Variant1"),
    (0x800ee4b6, "CAN_RxBitfieldExtract_8bit"),
    (0x800ee51a, "CAN_RxBitfieldExtract_16bit"),
    (0x800eeb24, "Diag_HandleService_580"),
    (0x800eeecc, "CAN_RxBitfieldExtract_Variant3"),
    (0x800ef1da, "CAN_RxBitfieldHelper_v5"),
    (0x800ef240, "CAN_RxBitfieldHelper_v6"),
    (0x800ef548, "CAN_RxBitfieldExtract_Variant4"),
    (0x800fc0be, "stack_unwind_helper"),
    (0x800fc846, "task_terminator"),
    (0x802ff724, "App_Query_0x8F_Use1"),
    (0x80305906, "App_Query_0x8F_Use2"),
    (0x8030f764, "App_UpdateSignal_0xAF"),
    (0x8030fc4a, "App_UpdateSignalGroup_0xA1_0xA9"),
    (0x8032855e, "App_UpdateSignal_0x8F_State"),
    (0x80329090, "App_Query_0x8F_Use3"),
    (0xd0001bdc, "DAT_TxBitPosTable_Ptr"),
    (0xd0001be0, "DAT_TxByteOffsetTable_Ptr"),
    (0xd0002584, "DAT_MsgCfgEntry_Base"),
    (0xd0002588, "DAT_BaudConstant_Ptr"),
    (0xd000258c, "DAT_BaudCfgEntry_Base"),
    (0xd00027f0, "DAT_ComCtx_RxBase_Ptr"),
    (0xd00043a7, "Broadcast_SignalMaskByte"),
    (0xd000bf18, "perMo_bufferPtr_table"),
    (0xd000ed90, "TxChannelDesc_Table"),
    (0xd000eddc, "PerSignal_State_Table"),
    (0xd00114ee, "moHw_to_msgCfgIdx_table"),
    (0xd001187a, "SubSignal_DirtyBitmap"),
    (0xd00119c6, "GlobalSignal_StatusBitmap"),
    (0xd0011d4e, "SubSignal_BitfieldB"),
    (0xd0012024, "SubSignal_BitfieldA"),
    (0xd0012c9d, "channelTypeTab"),
    (0xd0019170, "DAT_TaskContextTable_Ptr"),
    (0xd001a8c2, "SubSignal_StatusBuffer"),
]

fm = currentProgram.getFunctionManager()
st = currentProgram.getSymbolTable()
addrFactory = currentProgram.getAddressFactory()

renamed = 0
labeled = 0
skipped = 0

for addr_int, name in symbols:
    addr = addrFactory.getAddress("0x%x" % addr_int)
    fn = fm.getFunctionAt(addr)
    if fn is not None:
        try:
            fn.setName(name, SourceType.USER_DEFINED)
            renamed += 1
        except Exception as e:
            print("rename failed @ 0x%x: %s" % (addr_int, e))
            skipped += 1
    else:
        try:
            st.createLabel(addr, name, SourceType.USER_DEFINED)
            labeled += 1
        except Exception as e:
            print("label failed @ 0x%x: %s" % (addr_int, e))
            skipped += 1

print("Renamed %d functions, created %d data labels, skipped %d" % (renamed, labeled, skipped))
