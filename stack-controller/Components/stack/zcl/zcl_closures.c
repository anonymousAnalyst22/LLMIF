/**************************************************************************************************
  Filename:       zcl_closures.c
  Revised:        $Date: 2013-10-16 16:38:58 -0700 (Wed, 16 Oct 2013) $
  Revision:       $Revision: 35701 $

  Description:    Zigbee Cluster Library - Closures.


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


/*********************************************************************
 * INCLUDES
 */
#include "zcl.h"
#include "zcl_general.h"
#include "zcl_closures.h"

#if defined ( INTER_PAN )
  #include "stub_aps.h"
#endif

/*********************************************************************
 * MACROS
 */

/*********************************************************************
 * CONSTANTS
 */

/*********************************************************************
 * TYPEDEFS
 */
typedef struct zclClosuresDoorLockCBRec
{
  struct zclClosuresDoorLockCBRec     *next;
  uint8                                endpoint; // Used to link it into the endpoint descriptor
  zclClosures_DoorLockAppCallbacks_t  *CBs;     // Pointer to Callback function
} zclClosuresDoorLockCBRec_t;


/*********************************************************************
 * GLOBAL VARIABLES
 */

/*********************************************************************
 * GLOBAL FUNCTIONS
 */

/*********************************************************************
 * LOCAL VARIABLES
 */
static zclClosuresDoorLockCBRec_t *zclClosuresDoorLockCBs = (zclClosuresDoorLockCBRec_t *)NULL;

static uint8 zclDoorLockPluginRegisted = FALSE;


/*********************************************************************
 * LOCAL FUNCTIONS
 */
static ZStatus_t zclClosures_HdlIncoming( zclIncoming_t *pInMsg );
static ZStatus_t zclClosures_HdlInSpecificCommands( zclIncoming_t *pInMsg );

static zclClosures_DoorLockAppCallbacks_t *zclClosures_FindDoorLockCallbacks( uint8 endpoint );
static ZStatus_t zclClosures_ProcessInDoorLockCmds( zclIncoming_t *pInMsg,
                                                    zclClosures_DoorLockAppCallbacks_t *pCBs );
static ZStatus_t zclClosures_ProcessInDoorLock( zclIncoming_t *pInMsg,
                                                zclClosures_DoorLockAppCallbacks_t *pCBs );


/*********************************************************************
 * @fn      zclClosures_RegisterDoorLockCmdCallbacks
 *
 * @brief   Register an applications DoorLock command callbacks
 *
 * @param   endpoint - application's endpoint
 * @param   callbacks - pointer to the callback record.
 *
 * @return  ZMemError if not able to allocate
 */
ZStatus_t zclClosures_RegisterDoorLockCmdCallbacks( uint8 endpoint, zclClosures_DoorLockAppCallbacks_t *callbacks )
{
  zclClosuresDoorLockCBRec_t *pNewItem;
  zclClosuresDoorLockCBRec_t *pLoop;

  // Register as a ZCL Plugin
  if ( !zclDoorLockPluginRegisted )
  {
    zcl_registerPlugin( ZCL_CLUSTER_ID_CLOSURES_DOOR_LOCK,
                        ZCL_CLUSTER_ID_CLOSURES_DOOR_LOCK,
                        zclClosures_HdlIncoming );
    zclDoorLockPluginRegisted = TRUE;
  }

  // Fill in the new profile list
  pNewItem = zcl_mem_alloc( sizeof( zclClosuresDoorLockCBRec_t ) );
  if ( pNewItem == NULL )
  {
    return ( ZMemError );
  }

  pNewItem->next = (zclClosuresDoorLockCBRec_t *)NULL;
  pNewItem->endpoint = endpoint;
  pNewItem->CBs = callbacks;

  // Find spot in list
  if ( zclClosuresDoorLockCBs == NULL )
  {
    zclClosuresDoorLockCBs = pNewItem;
  }
  else
  {
    // Look for end of list
    pLoop = zclClosuresDoorLockCBs;
    while ( pLoop->next != NULL )
    {
      pLoop = pLoop->next;
    }

    // Put new item at end of list
    pLoop->next = pNewItem;
  }
  return ( ZSuccess );
}

/*********************************************************************
 * @fn      zclClosures_FindDoorLockCallbacks
 *
 * @brief   Find the DoorLock callbacks for an endpoint
 *
 * @param   endpoint
 *
 * @return  pointer to the callbacks
 */
static zclClosures_DoorLockAppCallbacks_t *zclClosures_FindDoorLockCallbacks( uint8 endpoint )
{
  zclClosuresDoorLockCBRec_t *pCBs;

  pCBs = zclClosuresDoorLockCBs;
  while ( pCBs )
  {
    if ( pCBs->endpoint == endpoint )
    {
      return ( pCBs->CBs );
    }
    pCBs = pCBs->next;
  }
  return ( (zclClosures_DoorLockAppCallbacks_t *)NULL );
}


/*********************************************************************
 * @fn      zclClosures_HdlIncoming
 *
 * @brief   Callback from ZCL to process incoming Commands specific
 *          to this cluster library or Profile commands for attributes
 *          that aren't in the attribute list
 *
 * @param   pInMsg - pointer to the incoming message
 * @param   logicalClusterID
 *
 * @return  ZStatus_t
 */
static ZStatus_t zclClosures_HdlIncoming( zclIncoming_t *pInMsg )
{
  ZStatus_t stat = ZSuccess;

#if defined ( INTER_PAN )
  if ( StubAPS_InterPan( pInMsg->msg->srcAddr.panId, pInMsg->msg->srcAddr.endPoint ) )
    return ( stat ); // Cluster not supported thru Inter-PAN
#endif
  if ( zcl_ClusterCmd( pInMsg->hdr.fc.type ) )
  {
    // Is this a manufacturer specific command?
    if ( pInMsg->hdr.fc.manuSpecific == 0 )
    {
      stat = zclClosures_HdlInSpecificCommands( pInMsg );
    }
    else
    {
      // We don't support any manufacturer specific command.
      stat = ZFailure;
    }
  }
  else
  {
    // Handle all the normal (Read, Write...) commands -- should never get here
    stat = ZFailure;
  }
  return ( stat );
}

/*********************************************************************
 * @fn      zclClosures_HdlInSpecificCommands
 *
 * @brief   Callback from ZCL to process incoming Commands specific
 *          to this cluster library

 * @param   pInMsg - pointer to the incoming message
 *
 * @return  ZStatus_t
 */
static ZStatus_t zclClosures_HdlInSpecificCommands( zclIncoming_t *pInMsg )
{
  ZStatus_t stat;
  zclClosures_DoorLockAppCallbacks_t *pDLCBs;


  // make sure endpoint exists
  pDLCBs = zclClosures_FindDoorLockCallbacks( pInMsg->msg->endPoint );
  if ( pDLCBs == NULL )
  {
    return ( ZFailure );
  }


  switch ( pInMsg->msg->clusterId )
  {
    case ZCL_CLUSTER_ID_CLOSURES_DOOR_LOCK:
      stat = zclClosures_ProcessInDoorLockCmds( pInMsg, pDLCBs );
      break;

    case ZCL_CLUSTER_ID_CLOSURES_WINDOW_COVERING:
#ifdef ZCL_WINDOWCOVERING
      stat = zclClosures_ProcessInWindowCovering( pInMsg, pWCCBs );
#endif //ZCL_WINDOWCOVERING
      break;

    default:
      stat = ZFailure;
      break;
  }

  return ( stat );
}

/*********************************************************************
 * @fn      zclClosures_ProcessInDoorLockCmds
 *
 * @brief   Process in the received DoorLock Command.
 *
 * @param   pInMsg - pointer to the incoming message
 * @param   pCBs - pointer to the Application callback functions
 *
 * @return  ZStatus_t
 */
static ZStatus_t zclClosures_ProcessInDoorLockCmds( zclIncoming_t *pInMsg,
                                                    zclClosures_DoorLockAppCallbacks_t *pCBs )
{
  ZStatus_t stat;

  // Client-to-Server
  if ( zcl_ServerCmd( pInMsg->hdr.fc.direction ) )
  {
    stat = ZFailure;
  }
  // Server-to-Client
  else
  {
    switch(pInMsg->hdr.commandID)
    {
      case COMMAND_CLOSURES_LOCK_DOOR_RSP:
      case COMMAND_CLOSURES_UNLOCK_DOOR_RSP:
      case COMMAND_CLOSURES_TOGGLE_DOOR_RSP:
        if ( pCBs->pfnDoorLockRsp )
        {
          return ( pCBs->pfnDoorLockRsp( pInMsg, pInMsg->pData[0] ) );
        }
      case COMMAND_CLOSURES_UNLOCK_WITH_TIMEOUT_RSP:
      case COMMAND_CLOSURES_GET_LOG_RECORD_RSP:
      case COMMAND_CLOSURES_SET_PIN_CODE_RSP:
      case COMMAND_CLOSURES_GET_PIN_CODE_RSP:
      case COMMAND_CLOSURES_CLEAR_PIN_CODE_RSP:
      case COMMAND_CLOSURES_CLEAR_ALL_PIN_CODES_RSP:
      case COMMAND_CLOSURES_SET_USER_STATUS_RSP:
      case COMMAND_CLOSURES_GET_USER_STATUS_RSP:
      case COMMAND_CLOSURES_SET_WEEK_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_GET_WEEK_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_CLEAR_WEEK_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_SET_YEAR_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_GET_YEAR_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_CLEAR_YEAR_DAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_SET_HOLIDAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_GET_HOLIDAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_CLEAR_HOLIDAY_SCHEDULE_RSP:
      case COMMAND_CLOSURES_SET_USER_TYPE_RSP:
      case COMMAND_CLOSURES_GET_USER_TYPE_RSP:
      case COMMAND_CLOSURES_SET_RFID_CODE_RSP:
      case COMMAND_CLOSURES_GET_RFID_CODE_RSP:
      case COMMAND_CLOSURES_CLEAR_RFID_CODE_RSP:
      case COMMAND_CLOSURES_CLEAR_ALL_RFID_CODES_RSP:
        if ( pCBs->pfnDoorLockRsp )
        {
          return ( pCBs->pfnDoorLockRsp( pInMsg, 0x0 ) );
        }

      return ( ZCL_STATUS_FAILURE );
        
#ifdef ZCL_DOORLOCK_EXT
        
      case COMMAND_CLOSURES_UNLOCK_WITH_TIMEOUT_RSP:
        stat = zclClosures_ProcessInDoorLockUnlockWithTimeoutRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_LOG_RECORD_RSP:
        stat = zclClosures_ProcessInDoorLockGetLogRecordRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_PIN_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockSetPINCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_PIN_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockGetPINCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_PIN_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockClearPINCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_ALL_PIN_CODES_RSP:
        stat = zclClosures_ProcessInDoorLockClearAllPINCodesRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_USER_STATUS_RSP:
        stat = zclClosures_ProcessInDoorLockSetUserStatusRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_USER_STATUS_RSP:
        stat = zclClosures_ProcessInDoorLockGetUserStatusRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_WEEK_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockSetWeekDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_WEEK_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockGetWeekDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_WEEK_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockClearWeekDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_YEAR_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockSetYearDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_YEAR_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockGetYearDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_YEAR_DAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockClearYearDayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_HOLIDAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockSetHolidayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_HOLIDAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockGetHolidayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_HOLIDAY_SCHEDULE_RSP:
        stat = zclClosures_ProcessInDoorLockClearHolidayScheduleRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_USER_TYPE_RSP:
        stat = zclClosures_ProcessInDoorLockSetUserTypeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_USER_TYPE_RSP:
        stat = zclClosures_ProcessInDoorLockGetUserTypeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_SET_RFID_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockSetRFIDCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_GET_RFID_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockGetRFIDCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_RFID_CODE_RSP:
        stat = zclClosures_ProcessInDoorLockClearRFIDCodeRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_CLEAR_ALL_RFID_CODES_RSP:
        stat = zclClosures_ProcessInDoorLockClearAllRFIDCodesRsp( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_OPERATION_EVENT_NOTIFICATION:
        stat = zclClosures_ProcessInDoorLockOperationEventNotification( pInMsg, pCBs );
        break;

      case COMMAND_CLOSURES_PROGRAMMING_EVENT_NOTIFICATION:
        stat = zclClosures_ProcessInDoorLockProgrammingEventNotification( pInMsg, pCBs );
        break;
        
#endif //ZCL_DOORLOCK_EXT

      default:
        // Unknown command
        stat = ZFailure;
        break;
    }
  }

  return ( stat );
}

/*********************************************************************
 * @fn      zclClosures_ProcessInDoorLock
 *
 * @brief   Process in the received Door Lock cmds
 *
 * @param   pInMsg - pointer to the incoming message
 * @param   pCBs - pointer to the application callbacks
 *
 * @return  ZStatus_t
 */
static ZStatus_t zclClosures_ProcessInDoorLock( zclIncoming_t *pInMsg,
                                                zclClosures_DoorLockAppCallbacks_t *pCBs )
{
  ZStatus_t status;

  // Client-to-Server
  if ( zcl_ServerCmd( pInMsg->hdr.fc.direction ) )
  {
    return ( ZFailure );   // Error ignore the command
  }
  // Server-to-Client
  else
  {
    switch(pInMsg->hdr.commandID)
    {
      case COMMAND_CLOSURES_LOCK_DOOR_RSP:
      case COMMAND_CLOSURES_UNLOCK_DOOR_RSP:
      case COMMAND_CLOSURES_TOGGLE_DOOR_RSP:
        if ( pCBs->pfnDoorLockRsp )
        {
          return ( pCBs->pfnDoorLockRsp( pInMsg, pInMsg->pData[0] ) );
        }

        return ( ZCL_STATUS_FAILURE );
        break;

      default:
        return ( ZFailure );   // Error ignore the command
    }
  }
}


/********************************************************************************************
*********************************************************************************************/
