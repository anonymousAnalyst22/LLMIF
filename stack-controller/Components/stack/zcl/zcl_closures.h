/**************************************************************************************************
  Filename:       zcl_closures.h
  Revised:        $Date: 2014-02-04 16:43:21 -0800 (Tue, 04 Feb 2014) $
  Revision:       $Revision: 37119 $

  Description:    This file contains the ZCL Closures definitions.


  Copyright 2006-2013 Texas Instruments Incorporated. All rights reserved.

  IMPORTANT: Your use of this Software is limited to those specific rights
  granted under the terms of a software license agreement between the user
  who downloaded the software, his/her employer (which must be your employer)
  and Texas Instruments Incorporated (the "License").  You may not use this
  Software unless you agree to abide by the terms of the License. The License
  limits your use, and you acknowledge, that the Software may not be modified,
  copied or distributed unless embedded on a Texas Instruments microcontroller
  or used solely and exclusively in conjunction with a Texas Instruments radio
  frequency transceiver, which is integrated into your product.  Other than for
  the foregoing purpose, you may not use, reproduce, copy, prepare derivative
  works of, modify, distribute, perform, display or sell this Software and/or
  its documentation for any purpose.

  YOU FURTHER ACKNOWLEDGE AND AGREE THAT THE SOFTWARE AND DOCUMENTATION ARE
  PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED,
  INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, TITLE,
  NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL
  TEXAS INSTRUMENTS OR ITS LICENSORS BE LIABLE OR OBLIGATED UNDER CONTRACT,
  NEGLIGENCE, STRICT LIABILITY, CONTRIBUTION, BREACH OF WARRANTY, OR OTHER
  LEGAL EQUITABLE THEORY ANY DIRECT OR INDIRECT DAMAGES OR EXPENSES
  INCLUDING BUT NOT LIMITED TO ANY INCIDENTAL, SPECIAL, INDIRECT, PUNITIVE
  OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA, COST OF PROCUREMENT
  OF SUBSTITUTE GOODS, TECHNOLOGY, SERVICES, OR ANY CLAIMS BY THIRD PARTIES
  (INCLUDING BUT NOT LIMITED TO ANY DEFENSE THEREOF), OR OTHER SIMILAR COSTS.

  Should you have any questions regarding your right to use this Software,
  contact Texas Instruments Incorporated at www.TI.com.
**************************************************************************************************/

#ifndef ZCL_CLOSURES_H
#define ZCL_CLOSURES_H

#ifdef __cplusplus
extern "C"
{
#endif

/*********************************************************************
 * INCLUDES
 */
#include "zcl.h"

/*********************************************************************
 * CONSTANTS
 */

/**********************************************/
/*** Shade Configuration Cluster Attributes ***/
/**********************************************/
  // Shade information attributes set
#define ATTRID_CLOSURES_PHYSICAL_CLOSED_LIMIT                          0x0000 // O, R, UINT16
#define ATTRID_CLOSURES_MOTOR_STEP_SIZE                                0x0001 // O, R, UINT8
#define ATTRID_CLOSURES_STATUS                                         0x0002 // M, R/W, BITMAP8

/*** Status attribute bit values ***/
#define CLOSURES_STATUS_SHADE_IS_OPERATIONAL                           0x01
#define CLOSURES_STATUS_SHADE_IS_ADJUSTING                             0x02
#define CLOSURES_STATUS_SHADE_DIRECTION                                0x04
#define CLOSURES_STATUS_SHADE_MOTOR_FORWARD_DIRECTION                  0x08

  // Shade settings attributes set
#define ATTRID_CLOSURES_CLOSED_LIMIT                                   0x0010
#define ATTRID_CLOSURES_MODE                                           0x0012

/*** Mode attribute values ***/
#define CLOSURES_MODE_NORMAL_MODE                                      0x00
#define CLOSURES_MODE_CONFIGURE_MODE                                   0x01

// cluster has no specific commands

/**********************************************/
/*** Logical Cluster ID - for mapping only ***/
/***  These are not to be used over-the-air ***/
/**********************************************/
#define ZCL_CLOSURES_LOGICAL_CLUSTER_ID_SHADE_CONFIG                   0x0010



  // Server Commands Generated
#define COMMAND_CLOSURES_LOCK_DOOR_RSP                     0x00 // M  status field
#define COMMAND_CLOSURES_UNLOCK_DOOR_RSP                   0x01 // M  status field
#define COMMAND_CLOSURES_TOGGLE_DOOR_RSP                   0x02 // O  status field
#define COMMAND_CLOSURES_UNLOCK_WITH_TIMEOUT_RSP           0x03 // O  status field
#define COMMAND_CLOSURES_GET_LOG_RECORD_RSP                0x04 // O  zclDoorLockGetLogRecordRsp_t
#define COMMAND_CLOSURES_SET_PIN_CODE_RSP                  0x05 // O  status field
#define COMMAND_CLOSURES_GET_PIN_CODE_RSP                  0x06 // O  zclDoorLockGetPINCodeRsp_t
#define COMMAND_CLOSURES_CLEAR_PIN_CODE_RSP                0x07 // O  status field
#define COMMAND_CLOSURES_CLEAR_ALL_PIN_CODES_RSP           0x08 // O  status field
#define COMMAND_CLOSURES_SET_USER_STATUS_RSP               0x09 // O  status field
#define COMMAND_CLOSURES_GET_USER_STATUS_RSP               0x0A // O  zclDoorLockGetUserStateRsp_t
#define COMMAND_CLOSURES_SET_WEEK_DAY_SCHEDULE_RSP         0x0B // O  status field
#define COMMAND_CLOSURES_GET_WEEK_DAY_SCHEDULE_RSP         0x0C // O  zclDoorLockGetWeekDayScheduleRsp_t
#define COMMAND_CLOSURES_CLEAR_WEEK_DAY_SCHEDULE_RSP       0x0D // O  status field
#define COMMAND_CLOSURES_SET_YEAR_DAY_SCHEDULE_RSP         0x0E // O  status field
#define COMMAND_CLOSURES_GET_YEAR_DAY_SCHEDULE_RSP         0x0F // O  zclDoorLockGetYearDayScheduleRsp_t
#define COMMAND_CLOSURES_CLEAR_YEAR_DAY_SCHEDULE_RSP       0x10 // O  status field
#define COMMAND_CLOSURES_SET_HOLIDAY_SCHEDULE_RSP          0x11 // O  status field
#define COMMAND_CLOSURES_GET_HOLIDAY_SCHEDULE_RSP          0x12 // O  zclDoorLockGetHolidayScheduleRsp_t
#define COMMAND_CLOSURES_CLEAR_HOLIDAY_SCHEDULE_RSP        0x13 // O  status field
#define COMMAND_CLOSURES_SET_USER_TYPE_RSP                 0x14 // O  status field
#define COMMAND_CLOSURES_GET_USER_TYPE_RSP                 0x15 // O  zclDoorLockGetUserTypeRsp_t
#define COMMAND_CLOSURES_SET_RFID_CODE_RSP                 0x16 // O  status field
#define COMMAND_CLOSURES_GET_RFID_CODE_RSP                 0x17 // O  zclDoorLockGetRFIDCodeRsp_t
#define COMMAND_CLOSURES_CLEAR_RFID_CODE_RSP               0x18 // O  status field
#define COMMAND_CLOSURES_CLEAR_ALL_RFID_CODES_RSP          0x19 // O  status field

#ifdef ZCL_WINDOWCOVERING
/**********************************************/
/*** Window Covering Cluster Attribute Sets ***/
/**********************************************/
#define ATTRSET_WINDOW_COVERING_INFO                        0x0000
#define ATTRSET_WINDOW_COVERING_SETTINGS                    0x0010

/******************************************/
/*** Window Covering Cluster Attributes ***/
/******************************************/
//Window Covering Information
#define ATTRID_CLOSURES_WINDOW_COVERING_TYPE                ( ATTRSET_WINDOW_COVERING_INFO + 0x0000 )
#define ATTRID_CLOSURES_PHYSICAL_CLOSE_LIMIT_LIFT_CM        ( ATTRSET_WINDOW_COVERING_INFO + 0x0001 )
#define ATTRID_CLOSURES_PHYSICAL_CLOSE_LIMIT_TILT_DDEGREE   ( ATTRSET_WINDOW_COVERING_INFO + 0x0002 )
#define ATTRID_CLOSURES_CURRENT_POSITION_LIFT_CM            ( ATTRSET_WINDOW_COVERING_INFO + 0x0003 )
#define ATTRID_CLOSURES_CURRENT_POSITION_TILT_DDEGREE       ( ATTRSET_WINDOW_COVERING_INFO + 0x0004 )
#define ATTRID_CLOSURES_NUM_OF_ACTUATION_LIFT               ( ATTRSET_WINDOW_COVERING_INFO + 0x0005 )
#define ATTRID_CLOSURES_NUM_OF_ACTUATION_TILT               ( ATTRSET_WINDOW_COVERING_INFO + 0x0006 )
#define ATTRID_CLOSURES_CONFIG_STATUS                       ( ATTRSET_WINDOW_COVERING_INFO + 0x0007 )
#define ATTRID_CLOSURES_CURRENT_POSITION_LIFT_PERCENTAGE    ( ATTRSET_WINDOW_COVERING_INFO + 0x0008 )
#define ATTRID_CLOSURES_CURRENT_POSITION_TILT_PERCENTAGE    ( ATTRSET_WINDOW_COVERING_INFO + 0x0009 )

//Window Covering Setting
#define ATTRID_CLOSURES_INSTALLED_OPEN_LIMIT_LIFT_CM        ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0000 )
#define ATTRID_CLOSURES_INSTALLED_CLOSED_LIMIT_LIFT_CM      ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0001 )
#define ATTRID_CLOSURES_INSTALLED_OPEN_LIMIT_TILT_DDEGREE   ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0002 )
#define ATTRID_CLOSURES_INSTALLED_CLOSED_LIMIT_TILT_DDEGREE ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0003 )
#define ATTRID_CLOSURES_VELOCITY_LIFT                       ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0004 )
#define ATTRID_CLOSURES_ACCELERATION_TIME_LIFT              ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0005 )
#define ATTRID_CLOSURES_DECELERATION_TIME_LIFT              ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0006 )
#define ATTRID_CLOSURES_WINDOW_COVERING_MODE                ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0007 )
#define ATTRID_CLOSURES_INTERMEDIATE_SETPOINTS_LIFT         ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0008 )
#define ATTRID_CLOSURES_INTERMEDIATE_SETPOINTS_TILT         ( ATTRSET_WINDOW_COVERING_SETTINGS + 0x0009 )

/*** Window Covering Type Attribute types ***/
#define CLOSURES_WINDOW_COVERING_TYPE_ROLLERSHADE                       0x00
#define CLOSURES_WINDOW_COVERING_TYPE_ROLLERSHADE_2_MOTOR               0x01
#define CLOSURES_WINDOW_COVERING_TYPE_ROLLERSHADE_EXTERIOR              0x02
#define CLOSURES_WINDOW_COVERING_TYPE_ROLLERSHADE_EXTERIOR_2_MOTOR      0x03
#define CLOSURES_WINDOW_COVERING_TYPE_DRAPERY                           0x04
#define CLOSURES_WINDOW_COVERING_TYPE_AWNING                            0x05
#define CLOSURES_WINDOW_COVERING_TYPE_SHUTTER                           0x06
#define CLOSURES_WINDOW_COVERING_TYPE_TILT_BLIND_TILT_ONLY              0x07
#define CLOSURES_WINDOW_COVERING_TYPE_TILT_BLIND_LIFT_AND_TILT          0x08
#define CLOSURES_WINDOW_COVERING_TYPE_PROJECTOR_SCREEN                  0x09


/****************************************/
/*** Window Covering Cluster Commands ***/
/****************************************/
#define COMMAND_CLOSURES_UP_OPEN                            ( 0x00 )
#define COMMAND_CLOSURES_DOWN_CLOSE                         ( 0x01 )
#define COMMAND_CLOSURES_STOP                               ( 0x02 )
#define COMMAND_CLOSURES_GO_TO_LIFT_VALUE                   ( 0x04 )
#define COMMAND_CLOSURES_GO_TO_LIFT_PERCENTAGE              ( 0x05 )
#define COMMAND_CLOSURES_GO_TO_TILT_VALUE                   ( 0x07 )
#define COMMAND_CLOSURES_GO_TO_TILT_PERCENTAGE              ( 0x08 )

#define ZCL_WC_GOTOVALUEREQ_PAYLOADLEN                      ( 2 )
#define ZCL_WC_GOTOPERCENTAGEREQ_PAYLOADLEN                 ( 1 )

#endif // ZCL_WINDOWCOVERING

/*********************************************************************
 * TYPEDEFS
 */


/*** Window Covering Cluster - Bits in Config/Status Attribute ***/
typedef struct
{
  uint8 Operational : 1;              // Window Covering is operational or not
  uint8 Online : 1;                   // Window Covering is enabled for transmitting over the Zigbee network or not
  uint8 CommandsReversed : 1;         // Identifies the direction of rotation for the Window Covering
  uint8 LiftControl : 1;              // Identifies, lift control supports open loop or closed loop
  uint8 TiltControl : 1;              // Identifies, tilt control supports open loop or closed loop
  uint8 LiftEncoderControlled : 1;    // Identifies, lift control uses Timer or Encoder
  uint8 TiltEncoderControlled : 1;    // Identifies, tilt control uses Timer or Encoder
  uint8 Reserved : 1;
}zclClosuresWcInfoConfigStatus_t;

/*** Window Covering Cluster - Bits in Mode Attribute ***/
typedef struct
{
  uint8 MotorReverseDirection : 1;    // Defines the direction of the motor rotation
  uint8 RunInCalibrationMode : 1;     // Defines Window Covering is in calibration mode or in normal mode
  uint8 RunInMaintenanceMode : 1;     // Defines motor is running in maintenance mode or in normal mode
  uint8 LEDFeedback : 1;              // Enables or Disables feedback LED
  uint8 Reserved : 4;
}zclClosuresWcSetMode_t;

/*** Window Covering Cluster - Setpoint type ***/
typedef enum
{
  lift = 0,
  tilt = 1,
}setpointType_t;

/*** Window Covering Cluster - Setpoint version ***/
typedef enum
{
  programSetpointVersion1 = 1,
  programSetpointVersion2,
}setpointVersion_t;

/*** Window Covering - Program Setpoint Command payload struct ***/
typedef struct
{
  setpointVersion_t version;        // Version of the Program Setpoint command
  uint8 setpointIndex;              // Index of the Setpoint
  uint16 setpointValue;             // Value of the Setpoint
  setpointType_t setpointType;      // Type of the Setpoint; it should be either lift or tilt
}programSetpointPayload_t;

/*** Window Covering Command - General struct ***/
typedef struct
{
  afAddrType_t            *srcAddr;   // requestor's address
  uint8                   cmdID;      // Command id
  uint8                   seqNum;     // Sequence number received with the message

  union                               // Payload
  {
    uint8 indexOfLiftSetpoint;
    uint8 percentageLiftValue;
    uint16 liftValue;
    uint8 indexOfTiltSetpoint;
    uint8 percentageTiltValue;
    uint16 TiltValue;
    programSetpointPayload_t programSetpoint;
  }un;
}zclWindowCovering_t;

//This callback is called to process an incoming Door Lock Response command
typedef ZStatus_t (*zclClosures_DoorLockRsp_t) ( zclIncoming_t *pInMsg, uint8 status );

//This callback is called to process an incoming Window Covering cluster basic commands
typedef void (*zclClosures_WindowCoveringSimple_t) ( void );

//This callback is called to process an incoming Window Covering cluster goto percentage commands
typedef bool (*zclClosures_WindowCoveringGotoPercentage_t) ( uint8 percentage );

//This callback is called to process an incoming Window Covering cluster goto value commands
typedef bool (*zclClosures_WindowCoveringGotoValue_t) ( uint16 value );

//This callback is called to process an incoming Window Covering cluster goto setpoint commands
typedef uint8 (*zclClosures_WindowCoveringGotoSetpoint_t) ( uint8 index );

//This callback is called to process an incoming Window Covering cluster program setpoint commands
typedef bool (*zclClosures_WindowCoveringProgramSetpoint_t) ( programSetpointPayload_t *setpoint );

// Register Callbacks DoorLock Cluster table entry - enter function pointers for callbacks that
// the application would like to receive
typedef struct
{
  zclClosures_DoorLockRsp_t                                     pfnDoorLockRsp;
} zclClosures_DoorLockAppCallbacks_t;

#ifdef ZCL_WINDOWCOVERING
// Register Callbacks Window Covering Cluster table entry - enter function pointers for callbacks that
// the application would like to receive
typedef struct
{
  zclClosures_WindowCoveringSimple_t                            pfnWindowCoveringUpOpen;
  zclClosures_WindowCoveringSimple_t                            pfnWindowCoveringDownClose;
  zclClosures_WindowCoveringSimple_t                            pfnWindowCoveringStop;
  zclClosures_WindowCoveringGotoValue_t                         pfnWindowCoveringGotoLiftValue;
  zclClosures_WindowCoveringGotoPercentage_t                    pfnWindowCoveringGotoLiftPercentage;
  zclClosures_WindowCoveringGotoValue_t                         pfnWindowCoveringGotoTiltValue;
  zclClosures_WindowCoveringGotoPercentage_t                    pfnWindowCoveringGotoTiltPercentage;
} zclClosures_WindowCoveringAppCallbacks_t;
#endif // ZCL_WINDOWCOVERING

/*********************************************************************
 * VARIABLES
 */


/*********************************************************************
 * FUNCTIONS
 */
 /*
  * Register for callbacks from this cluster library
  */
extern ZStatus_t zclClosures_RegisterDoorLockCmdCallbacks( uint8 endpoint, zclClosures_DoorLockAppCallbacks_t *callbacks );

#ifdef ZCL_WINDOWCOVERING
 /*
  * Register for callbacks from this cluster library
  */
extern ZStatus_t zclClosures_RegisterWindowCoveringCmdCallbacks( uint8 endpoint, zclClosures_WindowCoveringAppCallbacks_t *callbacks );

/*
 * The following functions are used in low-level routines.
 * See Function Macros for app-level send functions
 */
extern ZStatus_t zclClosures_WindowCoveringSimpleReq( uint8 srcEP, afAddrType_t *dstAddr,
                                                      uint8 cmd, uint8 disableDefaultRsp, uint8 seqNum );
extern ZStatus_t zclClosures_WindowCoveringSendGoToValueReq( uint8 srcEP, afAddrType_t *dstAddr,
                                                             uint8 cmd, uint16 value,
                                                             uint8 disableDefaultRsp, uint8 seqNum );
extern ZStatus_t zclClosures_WindowCoveringSendGoToPercentageReq( uint8 srcEP, afAddrType_t *dstAddr,
                                                                  uint8 cmd, uint8 percentageValue,
                                                                  uint8 disableDefaultRsp, uint8 seqNum );
#endif // ZCL_WINDOWCOVERING
/*********************************************************************
 * FUNCTION MACROS
 */

/*
 *  Send a Door Lock Lock Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockLockDoor( uint8 srcEP, afAddrType_t *dstAddr, zclDoorLock_t *pPayload, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockLockDoor(a, b, c, d, e) zclClosures_SendDoorLockRequest( (a), (b), COMMAND_CLOSURES_LOCK_DOOR, (c), (d), (e) )

/*
 *  Send a Door Lock Unlock Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockUnlockDoor( uint8 srcEP, afAddrType_t *dstAddr, zclDoorLock_t *pPayload, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockUnlockDoor(a, b, c, d, e) zclClosures_SendDoorLockRequest( (a), (b), COMMAND_CLOSURES_UNLOCK_DOOR, (c), (d), (e) )

/*
 *  Send a Door Lock Toggle Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockToggleDoor( uint8 srcEP, afAddrType_t *dstAddr, zclDoorLock_t *pPayload, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockToggleDoor(a, b, c, d, e) zclClosures_SendDoorLockRequest( (a), (b), COMMAND_CLOSURES_TOGGLE_DOOR, (c), (d), (e) )

/*
 *  Send a Get PIN Code Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetPINCode( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockGetPINCode(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_GET_PIN_CODE, (c), (d), (e) )

/*
 *  Send a Clear PIN Code Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearPINCode( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearPINCode(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_CLEAR_PIN_CODE, (c), (d), (e) )

/*
 *  Send a Clear All PIN Codes Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearAllPINCodes( uint8 srcEP, afAddrType_t *dstAddr, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearAllPINCodes(a, b, c, d) zclClosures_SendDoorLockClearAllCodesRequest( (a), (b), COMMAND_CLOSURES_CLEAR_ALL_PIN_CODES, (c), (d) )

/*
 *  Send a Get User Status Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetUserStatus( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendDoorLockGetUserStatus(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_GET_USER_STATUS, (c), (d), (e) )

/*
 *  Send a Get Week Day Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetWeekDaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 scheduleID, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum);
 */
#define zclClosures_SendDoorLockGetWeekDaySchedule(a, b, c, d, e, f) zclClosures_SendDoorLockScheduleRequest( (a), (b), COMMAND_CLOSURES_GET_WEEK_DAY_SCHEDULE, (c), (d), (e), (f) )

/*
 *  Send a Clear Week Day Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearWeekDaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 scheduleID, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearWeekDaySchedule(a, b, c, d, e, f) zclClosures_SendDoorLockScheduleRequest( (a), (b), COMMAND_CLOSURES_CLEAR_WEEK_DAY_SCHEDULE, (c), (d), (e), (f) )

/*
 *  Send a Get Year Day Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetYearDaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 scheduleID, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockGetYearDaySchedule(a, b, c, d, e, f) zclClosures_SendDoorLockScheduleRequest( (a), (b), COMMAND_CLOSURES_GET_YEAR_DAY_SCHEDULE, (c), (d), (e), (f) )

/*
 *  Send a Clear Year Day Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearYearDaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 scheduleID, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearYearDaySchedule(a, b, c, d, e, f) zclClosures_SendDoorLockScheduleRequest( (a), (b), COMMAND_CLOSURES_CLEAR_YEAR_DAY_SCHEDULE, (c), (d), (e), (f) )

/*
 *  Send a Get Holiday Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetHolidaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 holidayScheduleID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockGetHolidaySchedule(a, b, c, d, e) zclClosures_SendDoorLockHolidayScheduleRequest( (a), (b), COMMAND_CLOSURES_GET_HOLIDAY_SCHEDULE, (c), (d), (e) )

/*
 *  Send a Clear Holiday Schedule Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearHolidaySchedule( uint8 srcEP, afAddrType_t *dstAddr, uint8 holidayScheduleID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearHolidaySchedule(a, b, c, d, e) zclClosures_SendDoorLockHolidayScheduleRequest( (a), (b), COMMAND_CLOSURES_CLEAR_HOLIDAY_SCHEDULE, (c), (d), (e) )

/*
 *  Send a Get User Type Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetUserType( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockGetUserType(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_GET_USER_TYPE, (c), (d), (e) )

/*
 *  Send a Get RFID Code Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockGetRFIDCode( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockGetRFIDCode(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_GET_RFID_CODE, (c), (d), (e) )

/*
 *  Send a Clear RFID Code Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearRFIDCode( uint8 srcEP, afAddrType_t *dstAddr, uint16 userID, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearRFIDCode(a, b, c, d, e) zclClosures_SendDoorLockUserIDRequest( (a), (b), COMMAND_CLOSURES_CLEAR_RFID_CODE, (c), (d), (e) )

/*
 *  Send a Clear All RFID Codes Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearAllRFIDCodes( uint8 srcEP, afAddrType_t *dstAddr, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendDoorLockClearAllRFIDCodes(a, b, c, d) zclClosures_SendDoorLockClearAllCodesRequest( (a), (b), COMMAND_CLOSURES_CLEAR_ALL_RFID_CODES, (c), (d) )

/*
 *  Send a Door Lock Lock Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockLockDoorRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendDoorLockLockDoorRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_LOCK_DOOR_RSP, (c), (d), (e) )

/*
 *  Send a Door Lock Unlock Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockUnlockDoorRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendDoorLockUnlockDoorRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_UNLOCK_DOOR_RSP, (c), (d), (e) )

/*
 *  Send a Toggle Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockToggleDoorRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockToggleDoorRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_TOGGLE_DOOR_RSP, (c), (d), (e) )

/*
 *  Send a Unlock With Timeout Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockUnlockWithTimeoutRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockUnlockWithTimeoutRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_UNLOCK_WITH_TIMEOUT_RSP, (c), (d), (e) )

/*
 *  Send a Set PIN Code Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetPINCodeRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetPINCodeRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_PIN_CODE_RSP, (c), (d), (e) )

/*
 *  Send a Clear PIN Code Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearPINCodeRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearPINCodeRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_PIN_CODE_RSP, (c), (d), (e) )

/*
 *  Send a Clear All PIN Codes Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearAllPINCodesRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearAllPINCodesRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_ALL_PIN_CODES_RSP, (c), (d), (e) )

/*
 *  Send a Set User Status Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetUserStatusRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetUserStatusRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_USER_STATUS_RSP, (c), (d), (e) )

/*
 *  Send a Set Week Day Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetWeekDayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetWeekDayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_WEEK_DAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Clear Week Day Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearWeekDayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearWeekDayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_WEEK_DAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Set Year Day Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetYearDayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetYearDayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_YEAR_DAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Clear Year Day Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearYearDayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearYearDayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_YEAR_DAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Set Holiday Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetHolidayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetHolidayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_HOLIDAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Clear Holiday Schedule Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearHolidayScheduleRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearHolidayScheduleRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_HOLIDAY_SCHEDULE_RSP, (c), (d), (e) )

/*
 *  Send a Set User Type Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetUserTypeRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetUserTypeRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_USER_TYPE_RSP, (c), (d), (e) )

/*
 *  Send a Set RFID Code Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockSetRFIDCodeRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockSetRFIDCodeRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_SET_RFID_CODE_RSP, (c), (d), (e) )

/*
 *  Send a Clear RFID Code Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearRFIDCodeRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearRFIDCodeRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_RFID_CODE_RSP, (c), (d), (e) )

/*
 *  Send a Clear All RFID Codes Response
 *  Use like:
 *      ZStatus_t zclClosures_SendDoorLockClearAllRFIDCodesRsp( uint8 srcEP, afAddrType_t *dstAddr, uint8 status, uint8 disableDefaultRsp, uint8 seqNum );
 */
#define zclClosures_SendDoorLockClearAllRFIDCodesRsp(a, b, c, d, e) zclClosures_SendDoorLockStatusResponse( (a), (b), COMMAND_CLOSURES_CLEAR_ALL_RFID_CODES_RSP, (c), (d), (e) )

/*
 *  Send a Up/Open Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendUpOpen( uint8 srcEP, afAddrType_t *dstAddr, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendUpOpen(a, b, c, d) zclClosures_WindowCoveringSimpleReq( (a), (b), COMMAND_CLOSURES_UP_OPEN, (c), (d) )
/*
 *  Send a Down/Close Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendDownClose( uint8 srcEP, afAddrType_t *dstAddr, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendDownClose(a, b, c, d) zclClosures_WindowCoveringSimpleReq( (a), (b), COMMAND_CLOSURES_DOWN_CLOSE, (c), (d) )

/*
 *  Send a Stop Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendStop( uint8 srcEP, afAddrType_t *dstAddr, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendStop(a, b, c, d) zclClosures_WindowCoveringSimpleReq( (a), (b), COMMAND_CLOSURES_STOP, (c), (d) )

/*
 *  Send a GoToLiftValue Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendGoToLiftValue( uint8 srcEP, afAddrType_t *dstAddr, uint16 liftValue, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendGoToLiftValue(a, b, c, d, e) zclClosures_WindowCoveringSendGoToValueReq( (a), (b), COMMAND_CLOSURES_GO_TO_LIFT_VALUE, (c), (d), (e))

/*
 *  Send a GoToLiftPercentage Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendGoToLiftPercentage( uint8 srcEP, afAddrType_t *dstAddr, uint8 percentageLiftValue, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendGoToLiftPercentage(a, b, c, d, e) zclClosures_WindowCoveringSendGoToPercentageReq( (a), (b), COMMAND_CLOSURES_GO_TO_LIFT_PERCENTAGE, (c), (d), (e))

/*
 *  Send a GoToTiltValue Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendGoToTiltValue( uint8 srcEP, afAddrType_t *dstAddr, uint16 tiltValue, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendGoToTiltValue(a, b, c, d, e) zclClosures_WindowCoveringSendGoToValueReq( (a), (b), COMMAND_CLOSURES_GO_TO_TILT_VALUE, (c), (d), (e))

/*
 *  Send a GoToTiltPercentage Request Command
 *  Use like:
 *      ZStatus_t zclClosures_SendGoToTiltPercentage( uint8 srcEP, afAddrType_t *dstAddr, uint8 percentageTiltValue, uint8 disableDefaultRsp, uint8 seqNum )
 */
#define zclClosures_SendGoToTiltPercentage(a, b, c, d, e) zclClosures_WindowCoveringSendGoToPercentageReq( (a), (b), COMMAND_CLOSURES_GO_TO_TILT_PERCENTAGE, (c), (d), (e))

#ifdef __cplusplus
}
#endif

#endif /* ZCL_CLOSURES_H */
