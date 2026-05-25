# Function Inventory

Static inventory of all symbolised (named) functions in the firmware,
plus all periodic-task scheduler entries.

Source: `dump.txt` (Ghidra disassembly of `swfl_00000fef.bin.129_160_001`).

## Note on what's *not* in the firmware

This firmware partition (`swfl_00000fef`) contains the **ASW (Application
Software)** only. BMW DMEs typically split flash into:

- **BTLD** — bootloader
- **ASW** (this file) — application code + small const data
- **CAFD** — calibration & data (maps, lookup tables, CAN signal
  definitions, scaling factors, periods, etc.)

The CAFD lives in a *separate* flash partition. At boot, the ASW code
maps CAFD into a known flash address (or copies parts to RAM). Many of
the runtime pointer chains in this firmware end at addresses that we
cannot statically resolve — those almost certainly point into the CAFD
region.

**Practical implication:** per-frame CAN signal bit positions, scaling
factors, periods, and similar configuration are most likely in the CAFD,
not in this firmware. The encoder code reads them at runtime. If you have
the matching `cafd_*` file or another `swfl_*` partition for this DME,
the byte-level signal layout for 0xA5/0xA6/0xA7/etc. is almost certainly
a static table in there.

Named function inventory (symbolised in Ghidra)
======================================================================
  0x800c5c02  CAN::CAN_AccumulateMeasurementError
  0x800c71b8  CAN::CAN_AckRxMessage
  0x800c6794  CAN::CAN_AdvanceProtocolSlot
  0x800c671c  CAN::CAN_AgePriorities
  0x800c65a8  CAN::CAN_BroadcastErrCallback
  0x800c5d06  CAN::CAN_BroadcastSignalGroupA
  0x800c6032  CAN::CAN_BroadcastSignalGroupB
  0x800c653a  CAN::CAN_BroadcastTxCallback
  0x800c67e8  CAN::CAN_BuildTxPacketRegister
  0x800c7db0  CAN::CAN_ClearBusOff
  0x800c6b2c  CAN::CAN_ComputeRate
  0x800c77a4  CAN::CAN_ConfigureMessageObjects_800c77a6
  0x800c5e4e  CAN::CAN_DecodeSignalGroupA
  0x800c6126  CAN::CAN_DecodeSignalGroupB
  0x800c6302  CAN::CAN_DecodeSignalGroupC
  0x800c6572  CAN::CAN_DispatchErrCallback
  0x800c650c  CAN::CAN_DispatchTxCallback
  0x800c6f58  CAN::CAN_EmergencyShutdown
  0x800c70ac  CAN::CAN_ErrorISR_PollNodes
  0x800c9642  CAN::CAN_FUN_800c9644
  0x800f411c  CAN::CAN_FUN_800f411e
  0x800f9e10  CAN::CAN_FUN_800f9e12
  0x800f9e7e  CAN::CAN_FUN_800f9e80
  0x802ee49c  CAN::CAN_FUN_802ee49e
  0x802ee69c  CAN::CAN_FUN_802ee69e
  0x802f4aae  CAN::CAN_FUN_802f4ab0
  0x802f5be8  CAN::CAN_FUN_802f5bea
  0x800c7a7a  CAN::CAN_FinalizeMessageObjectLists
  0x800c7776  CAN::CAN_FindHighestPendingMO
  0x800c814c  CAN::CAN_FindListAndWrite
  0x800c7c14  CAN::CAN_FlushList
  0x800c779c  CAN::CAN_GetRAMTestResult
  0x800c65dc  CAN::CAN_HandleProtocolError
  0x800c738c  CAN::CAN_Init
  0x800e1250  CAN::CAN_InitCallback_RegisterChannels
  0x800c8ae0  CAN::CAN_InitDMASystem
  0x800c72b0  CAN::CAN_MORegisterRAMTest
  0x800c6b54  CAN::CAN_ManagementTask
  0x800c7788  CAN::CAN_MarkMOConfigured
  0x800c7e26  CAN::CAN_MessagePending_ISR
  0x800c6f8a  CAN::CAN_ModuleRegistration
  0x800c6afe  CAN::CAN_Node0HeartbeatTx
  0x800c635a  CAN::CAN_OpenChannel
  0x800c665a  CAN::CAN_PacketFormatDispatch
  0x800c6f16  CAN::CAN_PreTaskProbe
  0x800c5a26  CAN::CAN_ProcessMeasurementFrameA
  0x800c5b1e  CAN::CAN_ProcessMeasurementFrameB
  0x800c6a08  CAN::CAN_ProtocolHandshakeStateMachine
  0x800c6492  CAN::CAN_ProtocolSchedulerTick
  0x800c68f8  CAN::CAN_QueueTx
  0x8006f300  CAN::CAN_RecordTxEvent
  0x800c786e  CAN::CAN_ReinitNode
  0x800c642e  CAN::CAN_ReleaseMatchingSlots
  0x800eb3be  CAN::CAN_ReportDiagnosticEvent
  0x800c6980  CAN::CAN_ResetProtocolStack
  0x800c633e  CAN::CAN_ResetProtocolTimer
  0x800c7c80  CAN::CAN_Rx_ISR
  0x800c6888  CAN::CAN_SelectHighestPrioritySlot
  0x800e16e2  CAN::CAN_SetChannelDescPtr
  0x800c716e  CAN::CAN_SetRxPending
  0x800c859c  CAN::CAN_SetupDMATransfer
  0x800c5fde  CAN::CAN_SignalA_RxInit
  0x800c5c96  CAN::CAN_SignalA_RxInit2
  0x800c5fb0  CAN::CAN_SignalA_TimeoutHandler
  0x800c62d4  CAN::CAN_SignalB_TimeoutHandler
  0x800c7004  CAN::CAN_StartupInit
  0x800c6fc0  CAN::CAN_TimerTick
  0x800c7fa0  CAN::CAN_Transmit
  0x800c6398  CAN::CAN_TransmitExtended
  0x800c63e2  CAN::CAN_TransmitStandard
  0x800c8190  CAN::CAN_TxComplete_DequeueNext
  0x8006f01a  CAN::CAN_UpdateFrameCounterAndSync
  0x800c6f08  CAN::CAN_UpdateHwStateCache
  0x800c71f6  CAN::CAN_UpdateNodeStatus
  0x8006f322  CAN::CAN_UpdateRollingCounter
  0x800c674c  CAN::CAN_UpdateSlotCredit
  0x800c7eec  CAN::CAN_WriteMessageObject
  0x800c7ff6  CAN::CAN_WriteToList
  0x800a9266  CAN::Init_CAN_SRC12_NetworkSync
  0x800a930c  CAN::Init_CAN_SRC13_FrameSync
  0x8007c132  CAN::Init_InterruptPriorityTable
  0x800a98a8  CAN_AccumulateCounter
  0x800c8312  CAN_ChannelMaintenanceTask
  0x800c892e  CAN_DMATransferComplete
  0x800c8594  CAN_Dispatch
  0x800c855c  CAN_FindChannelByParam1
  0x800a9484  CAN_InitProtocolTable
  0x8006f280  CAN_InitRollingCounterSeed
  0x800c852e  CAN_LinkExtCfg
  0x800a929c  CAN_MeasureMOTiming
  0x800a9372  CAN_ProtocolCallbackA
  0x800a93d0  CAN_ProtocolCallbackB
  0x800a94ea  CAN_ProtocolEngineTick
  0x800a9456  CAN_ProtocolNotifyCallback
  0x800a9428  CAN_ProtocolSimpleCallback
  0x800a9336  CAN_ProtocolStateDispatch
  0x800c890c  CAN_RegisterDMADescriptors
  0x800c887c  CAN_ResetDMAState
  0x800ed7da  CAN_RxFrameDispatch
  0x800aee72  CAN_RxHandler_MsgType4
  0x800c5624  CAN_RxHandler_MsgType6
  0x800c5710  CAN_RxHandler_MsgType7
  0x800c8900  CAN_SetDMAParam
  0x8006f292  CAN_StepRollingCounter
  0x800a9858  CAN_TranslateGearMode
  0x800c8968  CAN_TriggerDMACycle
  0x800c854a  CAN_TxDispatch
  0x800c8bb8  CAN_VerifyHardwareConfig
  0x800ae5ae  DEM_ReportFatalError
  0x800a98fc  GPTA_SetMeasurementPeriod
  0x8007c120  Init_InterruptLevel
  0x8007c0c2  STM::STM_Init_SRC0
  0x8007c0f2  STM::STM_Init_SRC1
  0x80057b0d  SUB_80057b0e

Table A — fast (1-5 ms?)
  base = 0x80059800   count = 242
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x8033ee9a
  [  1] 0x8032ac4c
  [  2] 0x8034f410
  [  3] 0x8034f34e
  [  4] 0x8034f852
  [  5] 0x8034fdbe
  [  6] 0x8035015e
  [  7] 0x80351c64
  [  8] 0x803536fe
  [  9] 0x803564c4
  [ 10] 0x803569f8
  [ 11] 0x8038208e
  [ 12] 0x8035837e
  [ 13] 0x80384cf8
  [ 14] 0x80359428
  [ 15] 0x803591ce
  [ 16] 0x80384faa
  [ 17] 0x80359c8c
  [ 18] 0x803851e8
  [ 19] 0x80359f2c
  [ 20] 0x8035b610
  [ 21] 0x80385f9e
  [ 22] 0x803865a2
  [ 23] 0x8035c07c
  [ 24] 0x8035c4d0
  [ 25] 0x8035ccee
  [ 26] 0x8035e0da
  [ 27] 0x8035ae7c
  [ 28] 0x80381dbc
  [ 29] 0x8035043e
  [ 30] 0x803586aa
  [ 31] 0x8034f554
  [ 32] 0x80376312
  [ 33] 0x80358978
  [ 34] 0x8035d31c
  [ 35] 0x8035845c
  [ 36] 0x803811cc
  [ 37] 0x8037e5f0
  [ 38] 0x800eca9e
  [ 39] 0x80383268
  [ 40] 0x8009c9c0
  [ 41] 0x8009c9fe
  [ 42] 0x800ec7ce
  [ 43] 0x8009ca7e
  [ 44] 0x8009cfde
  [ 45] 0x8009cc32
  [ 46] 0x8009d0ec
  [ 47] 0x8009d1bc
  [ 48] 0x8009d884
  [ 49] 0x8009e69a
  [ 50] 0x8009f4aa
  [ 51] 0x8009f2e4
  [ 52] 0x800ecade
  [ 53] 0x8009fd90
  [ 54] 0x800a002c
  [ 55] 0x800a0a52
  [ 56] 0x800a14c6
  [ 57] 0x800a1fe4
  [ 58] 0x800a2210
  [ 59] 0x800ece4e
  [ 60] 0x800ed292
  [ 61] 0x800a29ae
  [ 62] 0x800a2b68
  [ 63] 0x800a2f00
  [ 64] 0x800a0460
  [ 65] 0x8009fc80
  [ 66] 0x8009cac4
  [ 67] 0x800a056c
  [ 68] 0x800ecd6c
  [ 69] 0x8009d31a
  [ 70] 0x800ec8cc
  [ 71] 0x800e4596
  [ 72] 0x80373eec
  [ 73] 0x800b481e
  [ 74] 0x80348754
  [ 75] 0x8034956e
  [ 76] 0x803199da
  [ 77] 0x80314900
  [ 78] 0x80371544
  [ 79] 0x8030f336
  [ 80] 0x8037f4f6
  [ 81] 0x8007c580
  [ 82] 0x800824e6
  [ 83] 0x8009c96c
  [ 84] 0x8030e88e
  [ 85] 0x80081daa
  [ 86] 0x80322f46
  [ 87] 0x8007f93a
  [ 88] 0x80080780
  [ 89] 0x8030e906
  [ 90] 0x8030ee1e
  [ 91] 0x80340376
  [ 92] 0x803096f6
  [ 93] 0x80308924
  [ 94] 0x8030f8d4
  [ 95] 0x80306fde
  [ 96] 0x80386af6
  [ 97] 0x8030df06
  [ 98] 0x80340c5e
  [ 99] 0x8030ffe8
  [100] 0x8030e056
  [101] 0x8030e078
  [102] 0x800a9338
  [103] 0x8030b1ae
  [104] 0x80381ab6
  [105] 0x8030652e
  [106] 0x8031492c
  [107] 0x8008c72e
  [108] 0x80335e12
  [109] 0x803720b0
  [110] 0x803490ec
  [111] 0x8033cea4
  [112] 0x802fd184
  [113] 0x80349e46
  [114] 0x8034ada6
  [115] 0x80319d70
  [116] 0x8031a0b2
  [117] 0x8034ad72
  [118] 0x803703c4
  [119] 0x80332b2e
  [120] 0x800955cc
  [121] 0x80372e32
  [122] 0x80326ab2
  [123] 0x8033981c
  [124] 0x80339984
  [125] 0x80368206
  [126] 0x8034e544
  [127] 0x8032201c
  [128] 0x80319b38
  [129] 0x80379e68
  [130] 0x8036a47c
  [131] 0x8036ac8e
  [132] 0x802fc698
  [133] 0x8032606a
  [134] 0x80324bb4
  [135] 0x80323b02
  [136] 0x8036ba2e
  [137] 0x802f6f5c
  [138] 0x80311176
  [139] 0x8033f15e
  [140] 0x80328594
  [141] 0x8033f4c2
  [142] 0x80328b50
  [143] 0x8033ae0a
  [144] 0x80327e14
  [145] 0x802ff748
  [146] 0x803056f0
  [147] 0x80305b44
  [148] 0x80316ad0
  [149] 0x8033c54e
  [150] 0x80316c52
  [151] 0x8032ba42
  [152] 0x80348a38
  [153] 0x8033f5ee
  [154] 0x80347dbc
  [155] 0x802f8d32
  [156] 0x8036e550
  [157] 0x8033d50a
  [158] 0x803034e6
  [159] 0x80337b2e
  [160] 0x80317bf8
  [161] 0x80317dd8
  [162] 0x80377bd8
  [163] 0x800b6062
  [164] 0x800b67ae
  [165] 0x8007cce4
  [166] 0x800a3f6e
  [167] 0x800a3ef4
  [168] 0x8032f9b4
  [169] 0x8031671a
  [170] 0x80316ef0
  [171] 0x803117ac
  [172] 0x80326c60
  [173] 0x8032b07e
  [174] 0x803018ba
  [175] 0x80082bdc
  [176] 0x803745d0
  [177] 0x8037561e
  [178] 0x80376222
  [179] 0x80374b56
  [180] 0x800b3e86
  [181] 0x803758fa
  [182] 0x80374240
  [183] 0x80375f56
  [184] 0x80092d50
  [185] 0x80310e86
  [186] 0x80311052
  [187] 0x8032e302
  [188] 0x8032e3fc
  [189] 0x8032e2c0
  [190] 0x8032d73e
  [191] 0x8037fb8e
  [192] 0x800b34c2
  [193] 0x80337726
  [194] 0x8037ff52
  [195] 0x8032d5dc
  [196] 0x80337ea0
  [197] 0x8033a49e
  [198] 0x8033b934
  [199] 0x8034d5be
  [200] 0x8031a9aa
  [201] 0x8031a5cc
  [202] 0x802f709c
  [203] 0x8030b7b4
  [204] 0x803645e8
  [205] 0x802f7328
  [206] 0x8036dafa
  [207] 0x8037e172
  [208] 0x8034eb88
  [209] 0x80316176
  [210] 0x802ff178
  [211] 0x8030608e
  [212] 0x8032bed8
  [213] 0x80371d4e
  [214] 0x80321162
  [215] 0x8031d47e
  [216] 0x8031e6a2
  [217] 0x8031e8e2
  [218] 0x8031faa6
  [219] 0x8037f0e2
  [220] 0x802f2862
  [221] 0x802eeebe
  [222] 0x802edf9e
  [223] 0x80387140
  [224] 0x803871b8
  [225] 0x802ee5bc
  [226] 0x80380e86
  [227] 0x80380990
  [228] 0x80334056
  [229] 0x800c2086
  [230] 0x80082494
  [231] 0x800e37ea
  [232] 0x800d9508
  [233] 0x800e36f4
  [234] 0x800a66b4
  [235] 0x800c898e
  [236] 0x8008c40c
  [237] 0x800f26fc
  [238] 0x800aebea
  [239] 0x800fc846
  [240] 0x80059bc4
  [241] 0x80059be0

Table B — 10 ms candidate
  base = 0x80059be0   count = 116
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a3fa2
  [  2] 0x8008c4c6
  [  3] 0x80333f3c
  [  4] 0x803789e8
  [  5] 0x80365d04
  [  6] 0x802fe7ba
  [  7] 0x80089d5c
  [  8] 0x80364714
  [  9] 0x8033686a
  [ 10] 0x80368902
  [ 11] 0x80340ef0
  [ 12] 0x8031a44e
  [ 13] 0x8031d198
  [ 14] 0x802fc0a2
  [ 15] 0x8037e0a6
  [ 16] 0x8032f846
  [ 17] 0x80363444
  [ 18] 0x8036fbb6
  [ 19] 0x800efebe
  [ 20] 0x8036d582
  [ 21] 0x8034f2ec
  [ 22] 0x8035156c
  [ 23] 0x8035306e
  [ 24] 0x80384cf2
  [ 25] 0x80384e60
  [ 26] 0x80385a9c
  [ 27] 0x8035b37c
  [ 28] 0x80386578
  [ 29] 0x80358912
  [ 30] 0x8035939e
  [ 31] 0x80359e52
  [ 32] 0x8035c41a
  [ 33] 0x803565c6
  [ 34] 0x803851b8
  [ 35] 0x8037e5fc
  [ 36] 0x80383536
  [ 37] 0x8009ca42
  [ 38] 0x8009c9bc
  [ 39] 0x8009d818
  [ 40] 0x8009e5bc
  [ 41] 0x8009f260
  [ 42] 0x8009f446
  [ 43] 0x800ecada
  [ 44] 0x800a0016
  [ 45] 0x800a04fc
  [ 46] 0x800a0a34
  [ 47] 0x800ed19e
  [ 48] 0x800a1ff6
  [ 49] 0x800a297e
  [ 50] 0x800a0ac2
  [ 51] 0x800ecd82
  [ 52] 0x8009cac0
  [ 53] 0x800eca9a
  [ 54] 0x800ecce4
  [ 55] 0x80302074
  [ 56] 0x80302004
  [ 57] 0x8037e0fa
  [ 58] 0x800a8316
  [ 59] 0x8037d47c
  [ 60] 0x8037bc86
  [ 61] 0x803264b8
  [ 62] 0x80308820
  [ 63] 0x80329410
  [ 64] 0x8030f764
  [ 65] 0x8030757e
  [ 66] 0x8030fc4a
  [ 67] 0x8032a3a4
  [ 68] 0x8032a9e0
  [ 69] 0x803804ae
  [ 70] 0x80307f58
  [ 71] 0x8030a944
  [ 72] 0x803645a2
  [ 73] 0x8030a096
  [ 74] 0x80309b54
  [ 75] 0x80309ae2
  [ 76] 0x80316028
  [ 77] 0x80306b4c
  [ 78] 0x80307d9c
  [ 79] 0x8032c0da
  [ 80] 0x80307d90
  [ 81] 0x8037229a
  [ 82] 0x80367fa2
  [ 83] 0x80371dec
  [ 84] 0x802fd696
  [ 85] 0x8037cbd2
  [ 86] 0x8037c38a
  [ 87] 0x802f6ff2
  [ 88] 0x80311770
  [ 89] 0x8032fdfe
  [ 90] 0x80328428
  [ 91] 0x80328ad6
  [ 92] 0x80305640
  [ 93] 0x8036e7c6
  [ 94] 0x800b5f10
  [ 95] 0x80377960
  [ 96] 0x800b5f74
  [ 97] 0x8033b6d0
  [ 98] 0x80315210
  [ 99] 0x80315e30
  [100] 0x803380a0
  [101] 0x8031f01c
  [102] 0x8031dc7e
  [103] 0x8031e7a4
  [104] 0x80387012
  [105] 0x8037f1b8
  [106] 0x80333f74
  [107] 0x800d9472
  [108] 0x8030d7be
  [109] 0x8008c40c
  [110] 0x800f2714
  [111] 0x800a658c
  [112] 0x800aebea
  [113] 0x800fc846
  [114] 0x80059dac
  [115] 0x80059dc8

Table C — 20 ms?
  base = 0x80059e3c   count = 37
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a576c
  [  2] 0x8008c4ba
  [  3] 0x8030d8b4
  [  4] 0x803386c0
  [  5] 0x800da688
  [  6] 0x803374ce
  [  7] 0x800a985a
  [  8] 0x802f85b2
  [  9] 0x802f5e38
  [ 10] 0x80371c76
  [ 11] 0x802f95f4
  [ 12] 0x8032f902
  [ 13] 0x803374f2
  [ 14] 0x8035db24
  [ 15] 0x8035878e
  [ 16] 0x8037e52a
  [ 17] 0x800ec84a
  [ 18] 0x800a243c
  [ 19] 0x800a2ace
  [ 20] 0x8009f9ba
  [ 21] 0x8009d03a
  [ 22] 0x8009de80
  [ 23] 0x80326774
  [ 24] 0x8030fc44
  [ 25] 0x800a3f18
  [ 26] 0x800b6b4e
  [ 27] 0x800b773c
  [ 28] 0x800b67ee
  [ 29] 0x800ee64c
  [ 30] 0x8008c40c
  [ 31] 0x800f25f0
  [ 32] 0x800a7e2c
  [ 33] 0x800aebea
  [ 34] 0x800fc846
  [ 35] 0x80059ecc
  [ 36] 0x80059ee8

Table D — 50 ms?
  base = 0x80059f7c   count = 28
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a4a70
  [  2] 0x800d4b4a
  [  3] 0x800c9aa8
  [  4] 0x800d85dc
  [  5] 0x800b5a06
  [  6] 0x800d3776
  [  7] 0x800d20a2
  [  8] 0x800cf51e
  [  9] 0x800cf934
  [ 10] 0x800cf390
  [ 11] 0x800cc1e6
  [ 12] 0x800cbf44
  [ 13] 0x800d520c
  [ 14] 0x800d1f50
  [ 15] 0x800d4c0e
  [ 16] 0x80086a80
  [ 17] 0x800af1b0
  [ 18] 0x800ba1e6
  [ 19] 0x800e9216
  [ 20] 0x800b1d04
  [ 21] 0x8033607c
  [ 22] 0x8037e634
  [ 23] 0x800f23be
  [ 24] 0x800aebea
  [ 25] 0x800fc846
  [ 26] 0x80059fe8
  [ 27] 0x8005a004

Table E — 100 ms?
  base = 0x8005a0bc   count = 70
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a579e
  [  2] 0x8008c49e
  [  3] 0x800d4a8e
  [  4] 0x800ae4c2
  [  5] 0x800ae09e
  [  6] 0x800e37b4
  [  7] 0x800e36c6
  [  8] 0x803811ca
  [  9] 0x8008f90a
  [ 10] 0x80367972
  [ 11] 0x80366b76
  [ 12] 0x8030db6e
  [ 13] 0x8033903e
  [ 14] 0x8030d6f8
  [ 15] 0x802f6032
  [ 16] 0x8031991e
  [ 17] 0x80302a3c
  [ 18] 0x8034de3c
  [ 19] 0x800cb892
  [ 20] 0x80386d7a
  [ 21] 0x803646e4
  [ 22] 0x800e5798
  [ 23] 0x80371b5c
  [ 24] 0x803397ce
  [ 25] 0x800a32de
  [ 26] 0x8034f126
  [ 27] 0x803556aa
  [ 28] 0x8035739a
  [ 29] 0x803597b4
  [ 30] 0x8035a0f6
  [ 31] 0x8038577a
  [ 32] 0x8035e042
  [ 33] 0x80381fb4
  [ 34] 0x8037e522
  [ 35] 0x8009ee12
  [ 36] 0x800a05aa
  [ 37] 0x800ed004
  [ 38] 0x8034e96e
  [ 39] 0x800efe28
  [ 40] 0x80316c12
  [ 41] 0x80369fd0
  [ 42] 0x8033a8be
  [ 43] 0x80342b26
  [ 44] 0x802f72e8
  [ 45] 0x80376c24
  [ 46] 0x800b65c4
  [ 47] 0x800b5d5c
  [ 48] 0x800b715c
  [ 49] 0x800b792e
  [ 50] 0x80375734
  [ 51] 0x8008c4e2
  [ 52] 0x8007cd00
  [ 53] 0x800a3f26
  [ 54] 0x800dd7cc
  [ 55] 0x80380ff2
  [ 56] 0x8033429e
  [ 57] 0x800d94b8
  [ 58] 0x8034cc5c
  [ 59] 0x8034b9e2
  [ 60] 0x8034c0ca
  [ 61] 0x800e37dc
  [ 62] 0x800e36ea
  [ 63] 0x8008c40c
  [ 64] 0x800f25cc
  [ 65] 0x800a7e52
  [ 66] 0x800aebea
  [ 67] 0x800fc846
  [ 68] 0x8005a1d0
  [ 69] 0x8005a1ec

Table F — 200 ms?
  base = 0x8005a210   count = 75
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a49b8
  [  2] 0x8008c4a6
  [  3] 0x803397ca
  [  4] 0x8037fb5a
  [  5] 0x8033eade
  [  6] 0x80371b60
  [  7] 0x803622b8
  [  8] 0x803629ae
  [  9] 0x80370560
  [ 10] 0x8034f174
  [ 11] 0x8034f460
  [ 12] 0x80357894
  [ 13] 0x80359d5c
  [ 14] 0x803861d0
  [ 15] 0x80381fd0
  [ 16] 0x8037e5ec
  [ 17] 0x8009ef46
  [ 18] 0x8009f9f6
  [ 19] 0x800a8402
  [ 20] 0x800b1b08
  [ 21] 0x803374f4
  [ 22] 0x8009c992
  [ 23] 0x8032fe58
  [ 24] 0x80331be8
  [ 25] 0x80307e74
  [ 26] 0x80307c3a
  [ 27] 0x803079e4
  [ 28] 0x8032cf0a
  [ 29] 0x80307892
  [ 30] 0x8037e506
  [ 31] 0x80307d76
  [ 32] 0x802fc868
  [ 33] 0x8036a3da
  [ 34] 0x8031cccc
  [ 35] 0x800b1bae
  [ 36] 0x800aec84
  [ 37] 0x802fd9d8
  [ 38] 0x802fe9f4
  [ 39] 0x8036b7c2
  [ 40] 0x8036ade6
  [ 41] 0x80325f7e
  [ 42] 0x802fc36c
  [ 43] 0x8036cba0
  [ 44] 0x8037cc86
  [ 45] 0x80324f5e
  [ 46] 0x8036c34a
  [ 47] 0x8037c428
  [ 48] 0x80323eac
  [ 49] 0x8032346e
  [ 50] 0x80386a44
  [ 51] 0x80339fc0
  [ 52] 0x80301550
  [ 53] 0x802f6eda
  [ 54] 0x8037e438
  [ 55] 0x80344f6a
  [ 56] 0x80303130
  [ 57] 0x800b62b2
  [ 58] 0x80310a0c
  [ 59] 0x8030b692
  [ 60] 0x80316514
  [ 61] 0x8032149c
  [ 62] 0x80321114
  [ 63] 0x8031ea22
  [ 64] 0x8031fa30
  [ 65] 0x80386e86
  [ 66] 0x802edea2
  [ 67] 0x80334746
  [ 68] 0x8008c40c
  [ 69] 0x800f26f0
  [ 70] 0x800a6fe0
  [ 71] 0x800aebea
  [ 72] 0x800fc846
  [ 73] 0x8005a338
  [ 74] 0x8005a354

Table G — 1000 ms?
  base = 0x8005a354   count = 57
  -----------------------------------------------------------------
  idx     task fn
  [  0] 0x800aeb3c
  [  1] 0x800a5016
  [  2] 0x8008c4ba
  [  3] 0x8030d8b6
  [  4] 0x803386c4
  [  5] 0x80308178
  [  6] 0x800da688
  [  7] 0x803374ce
  [  8] 0x800a985a
  [  9] 0x802f85de
  [ 10] 0x802f5e38
  [ 11] 0x80381b76
  [ 12] 0x802f95f2
  [ 13] 0x8032f902
  [ 14] 0x803374f2
  [ 15] 0x8034f3ac
  [ 16] 0x803555c6
  [ 17] 0x80384d4a
  [ 18] 0x803583c6
  [ 19] 0x803584a6
  [ 20] 0x8035c7a2
  [ 21] 0x8035db3a
  [ 22] 0x8034fd36
  [ 23] 0x80385b1a
  [ 24] 0x803525be
  [ 25] 0x803587ea
  [ 26] 0x80359676
  [ 27] 0x80381dd4
  [ 28] 0x8037ea20
  [ 29] 0x800ec874
  [ 30] 0x8009d050
  [ 31] 0x8009df4c
  [ 32] 0x8009edec
  [ 33] 0x800eccd0
  [ 34] 0x8009fe1c
  [ 35] 0x800a2452
  [ 36] 0x800a2ae6
  [ 37] 0x800a2f84
  [ 38] 0x8009f9d2
  [ 39] 0x800ed226
  [ 40] 0x80379e52
  [ 41] 0x80326774
  [ 42] 0x8038054a
  [ 43] 0x8033af90
  [ 44] 0x8037423c
  [ 45] 0x8033c016
  [ 46] 0x800a3f18
  [ 47] 0x800b6b4e
  [ 48] 0x800b773c
  [ 49] 0x800b67ee
  [ 50] 0x8008c40c
  [ 51] 0x800f2828
  [ 52] 0x800a7598
  [ 53] 0x800aebea
  [ 54] 0x800fc846
  [ 55] 0x8005a434
  [ 56] 0x8005a450
