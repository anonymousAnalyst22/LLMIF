# UART configuration parameters
UART_RX_WAIT_PERIOD = 0.001
MAX_RX_WAIT_TIME = 5 # It should equal to SAMPLEAPP_ACT_TIMEOUT defined in zigbee stack.
MAX_TX_RETRY = 2

# Command types
COMMAND_GENETIC = 0x0
COMMAND_ZCL = 0x1
COMMAND_MANU = 0x2
COMMAND_MISSING_ZCL = 0x3 # A customized command supported by devices in a ZCL-standard cluster
COMMAND_STRANGE = 0x4 # A missing ZCL-standard command which is not supported by device

# Some Genetic and ZCL command IDs
GENETIC_READ_REQUEST = 0x00
GENETIC_WRITE_REQUEST = 0x02
GENETIC_CONFIGURE_REPORT = 0x06

# Characters used for pattern matching
SYMBOL_MATCH_ALL = '*'

# ZDO Cluster IDs
ZDO_RESPONSE_BIT_V1_0 = 0x80
ZDO_RESPONSE_BIT = 0x8000

# Transmission Direction
CLIENT_SERVER_DIRECTION = 0
SERVER_CLIENT_DIRECTION = 1

# Coordinator UART command code
CMD_JC_STEER           =            0x0
CMD_JC_LIST            =            0x1
CMD_JC_NODEREQ         =            0x2
CMD_JC_AEPREQ          =            0x3
CMD_JC_CLUREQ          =            0x4
CMD_JC_CMDREQ          =            0x5
CMD_JC_CMDRSP          =            0x6
CMD_JC_ZCLREQ          =            0x7
CMD_JC_LEVREQ          =            0x8
CUS_AF_MSG             =            0xf8

# Coordinator UART Command Execution State Code
ERR_CMD_TIMEOUT        =            0xfc
ERR_CMD_MISMATCH       =            0xfd
ERR_CMD_NOTFOUND       =            0xfe
ERR_CMD_FAIL           =            0xff

# Node Relations
PARENT                 =            0
CHILD_RFD              =            1
CHILD_RFD_RX_IDLE      =            2
CHILD_FFD              =            3
CHILD_FFD_RX_IDLE      =            4
NEIGHBOR               =            5

NWK_addr_req = 0x0000
IEEE_addr_req = 0x0001
Node_Desc_req = 0x0002
Power_Desc_req = 0x0003
Simple_Desc_req = 0x0004
Active_EP_req = 0x0005
Match_Desc_req = 0x0006
NWK_addr_rsp = NWK_addr_req | ZDO_RESPONSE_BIT
IEEE_addr_rsp = IEEE_addr_req | ZDO_RESPONSE_BIT
Node_Desc_rsp = Node_Desc_req | ZDO_RESPONSE_BIT
Power_Desc_rsp = Power_Desc_req | ZDO_RESPONSE_BIT
Simple_Desc_rsp = Simple_Desc_req | ZDO_RESPONSE_BIT
Active_EP_rsp = Active_EP_req | ZDO_RESPONSE_BIT
Match_Desc_rsp = Match_Desc_req | ZDO_RESPONSE_BIT

Complex_Desc_req = 0x0010
User_Desc_req = 0x0011
Discovery_Cache_req = 0x0012
Device_annce = 0x0013
User_Desc_set = 0x0014
Server_Discovery_req = 0x0015
Parent_annce = 0x001F
Complex_Desc_rsp = Complex_Desc_req | ZDO_RESPONSE_BIT
User_Desc_rsp = User_Desc_req | ZDO_RESPONSE_BIT
Discovery_Cache_rsp = Discovery_Cache_req | ZDO_RESPONSE_BIT
User_Desc_conf = User_Desc_set | ZDO_RESPONSE_BIT
Server_Discovery_rsp = Server_Discovery_req | ZDO_RESPONSE_BIT
Parent_annce_rsp = Parent_annce | ZDO_RESPONSE_BIT

End_Device_Bind_req = 0x0020
Bind_req = 0x0021
Unbind_req = 0x0022
Bind_rsp = Bind_req | ZDO_RESPONSE_BIT
End_Device_Bind_rsp = End_Device_Bind_req | ZDO_RESPONSE_BIT
Unbind_rsp = Unbind_req | ZDO_RESPONSE_BIT

Mgmt_NWK_Disc_req = 0x0030
Mgmt_Lqi_req = 0x0031
Mgmt_Rtg_req = 0x0032
Mgmt_Bind_req = 0x0033
Mgmt_Leave_req = 0x0034
Mgmt_Direct_Join_req = 0x0035
Mgmt_Permit_Join_req = 0x0036
Mgmt_NWK_Update_req = 0x0038
Mgmt_NWK_Disc_rsp = Mgmt_NWK_Disc_req | ZDO_RESPONSE_BIT
Mgmt_Lqi_rsp = Mgmt_Lqi_req | ZDO_RESPONSE_BIT
Mgmt_Rtg_rsp = Mgmt_Rtg_req | ZDO_RESPONSE_BIT
Mgmt_Bind_rsp = Mgmt_Bind_req | ZDO_RESPONSE_BIT
Mgmt_Leave_rsp = Mgmt_Leave_req | ZDO_RESPONSE_BIT
Mgmt_Direct_Join_rsp = Mgmt_Direct_Join_req | ZDO_RESPONSE_BIT
Mgmt_Permit_Join_rsp = Mgmt_Permit_Join_req | ZDO_RESPONSE_BIT
Mgmt_NWK_Update_notify = Mgmt_NWK_Update_req | ZDO_RESPONSE_BIT

ZDO_ALL_MSGS_CLUSTERID = 0xFFFF

# Error Status Codes
ZCL_STATUS_SUCCESS = 0x00
ZCL_STATUS_FAILURE = 0x01
# 0x02-0x7D are reserved.
ZCL_STATUS_NOT_AUTHORIZED = 0x7E
ZCL_STATUS_MALFORMED_COMMAND = 0x80
ZCL_STATUS_UNSUP_CLUSTER_COMMAND = 0x81
ZCL_STATUS_UNSUP_GENERAL_COMMAND = 0x82
ZCL_STATUS_UNSUP_MANU_CLUSTER_COMMAND = 0x83
ZCL_STATUS_UNSUP_MANU_GENERAL_COMMAND = 0x84
ZCL_STATUS_INVALID_FIELD = 0x85
ZCL_STATUS_UNSUPPORTED_ATTRIBUTE = 0x86
ZCL_STATUS_INVALID_VALUE = 0x87
ZCL_STATUS_READ_ONLY = 0x88
ZCL_STATUS_INSUFFICIENT_SPACE = 0x89
ZCL_STATUS_DUPLICATE_EXISTS = 0x8a
ZCL_STATUS_NOT_FOUND = 0x8b
ZCL_STATUS_UNREPORTABLE_ATTRIBUTE = 0x8c
ZCL_STATUS_INVALID_DATA_TYPE = 0x8d
ZCL_STATUS_INVALID_SELECTOR = 0x8e
ZCL_STATUS_WRITE_ONLY = 0x8f
ZCL_STATUS_INCONSISTENT_STARTUP_STATE = 0x90
ZCL_STATUS_DEFINED_OUT_OF_BAND = 0x91
ZCL_STATUS_INCONSISTENT = 0x92
ZCL_STATUS_ACTION_DENIED = 0x93
ZCL_STATUS_TIMEOUT = 0x94
ZCL_STATUS_ABORT = 0x95
ZCL_STATUS_INVALID_IMAGE = 0x96
ZCL_STATUS_WAIT_FOR_DATA = 0x97
ZCL_STATUS_NO_IMAGE_AVAILABLE = 0x98
ZCL_STATUS_REQUIRE_MORE_IMAGE = 0x99

# 0xbd-bf are reserved.
ZCL_STATUS_HARDWARE_FAILURE = 0xc0
ZCL_STATUS_SOFTWARE_FAILURE = 0xc1
ZCL_STATUS_CALIBRATION_ERROR = 0xc2

# Generic Status Return Values
SUCCESS = 0x00
FAILURE = 0x01
INVALIDPARAMETER = 0x02
INVALID_TASK = 0x03
MSG_BUFFER_NOT_AVAIL = 0x04
INVALID_MSG_POINTER = 0x05
INVALID_EVENT_ID = 0x06
INVALID_INTERRUPT_ID = 0x07
NO_TIMER_AVAIL = 0x08
NV_ITEM_UNINIT = 0x09
NV_OPER_FAILED = 0x0A
INVALID_MEM_SIZE = 0x0B
NV_BAD_ITEM_LEN = 0x0C
NV_INVALID_DATA = 0x0D
# JC NOTE: Extern the Zigbee command execution status code
JC_EXECUTION_TIMEOUT = 0x0E
JC_RESPONSE_NOT_ALIGNED = 0x0F

# Redefined Generic Status Return Values for code backwards compatibility
ZSuccess = SUCCESS
ZFailure = FAILURE
ZInvalidParameter = INVALIDPARAMETER

ZMemError = 0x10
ZBufferFull = 0x11
ZUnsupportedMode = 0x12
ZMacMemError = 0x13

ZSapiInProgress = 0x20
ZSapiTimeout = 0x21
ZSapiInit = 0x22

ZNotAuthorized = 0x7E

ZMalformedCmd = 0x80
ZUnsupClusterCmd = 0x81

ZOtaAbort = 0x95
ZOtaImageInvalid = 0x96
ZOtaWaitForData = 0x97
ZOtaNoImageAvailable = 0x98
ZOtaRequireMoreImage = 0x99

ZApsFail = 0xb1
ZApsTableFull = 0xb2
ZApsIllegalRequest = 0xb3
ZApsInvalidBinding = 0xb4
ZApsUnsupportedAttrib = 0xb5
ZApsNotSupported = 0xb6
ZApsNoAck = 0xb7
ZApsDuplicateEntry = 0xb8
ZApsNoBoundDevice = 0xb9
ZApsNotAllowed = 0xba
ZApsNotAuthenticated = 0xbb

ZSecNoKey = 0xa1
ZSecOldFrmCount = 0xa2
ZSecMaxFrmCount = 0xa3
ZSecCcmFail = 0xa4
ZSecFailure = 0xad

ZNwkInvalidParam = 0xc1
ZNwkInvalidRequest = 0xc2
ZNwkNotPermitted = 0xc3
ZNwkStartupFailure = 0xc4
ZNwkAlreadyPresent = 0xc5
ZNwkSyncFailure = 0xc6
ZNwkTableFull = 0xc7
ZNwkUnknownDevice = 0xc8
ZNwkUnsupportedAttribute = 0xc9
ZNwkNoNetworks = 0xca
ZNwkLeaveUnconfirmed = 0xcb
ZNwkNoAck = 0xcc # not in spec
ZNwkNoRoute = 0xcd

ZMacSuccess = 0x00
ZMacBeaconLoss = 0xe0
ZMacChannelAccessFailure = 0xe1
ZMacDenied = 0xe2
ZMacDisableTrxFailure = 0xe3
ZMacFailedSecurityCheck = 0xe4
ZMacFrameTooLong = 0xe5
ZMacInvalidGTS = 0xe6
ZMacInvalidHandle = 0xe7
ZMacInvalidParameter = 0xe8
ZMacNoACK = 0xe9
ZMacNoBeacon = 0xea
ZMacNoData = 0xeb
ZMacNoShortAddr = 0xec
ZMacOutOfCap = 0xed
ZMacPANIDConflict = 0xee
ZMacRealignment = 0xef
ZMacTransactionExpired = 0xf0
ZMacTransactionOverFlow = 0xf1
ZMacTxActive = 0xf2
ZMacUnAvailableKey = 0xf3
ZMacUnsupportedAttribute = 0xf4
ZMacUnsupported = 0xf5
ZMacSrcMatchInvalidIndex = 0xff


# Message address mode
SAMPLEAPP_BROADCAST        =         0x00
SAMPLEAPP_GROUPCAST        =         0x01
SAMPLEAPP_UNICAST          =         0x10

# Profile ID
ZCL_HA_PROFILE_ID          =         0x0104
ZCL_ZLL_PROFILE_ID         =         0xc05e
ZCL_GP_PROFILE_ID          =         0xa1e0


# NOTE: Skipped testing commands in the format of (clusterID, cmdID)
# Command specified here will not be scanned, conformance-checked, and fuzzed.
#GLOBAL_SKIPPED_CMDS = [(0x0, 0x0), (0x20, 0x1), (0x20, 0x2), (0x20, 0x3)]
GLOBAL_SKIPPED_CMDS = []

STACK_ADDR = '/dev/ttyUSB0'