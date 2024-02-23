/**************************************************************************************************
  Filename:       zcl_samplesw.h
  Revised:        $Date: 2015-08-19 17:11:00 -0700 (Wed, 19 Aug 2015) $
  Revision:       $Revision: 44460 $


  Description:    This file contains the Zigbee Cluster Library Home
                  Automation Sample Application.


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
  PROVIDED �AS IS� WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED,
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

#ifndef ZCL_SAMPLESW_H
#define ZCL_SAMPLESW_H

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
#define SAMPLESW_HA_ENDPOINT               8
#define SAMPLESW_ZLL_ENDPOINT              9
#define SAMPLESW_GP_ENDPOINT               10

#define ZCL_ZLL_PROFILE_ID              0xc05e
#define ZCL_GP_PROFILE_ID               0xa1e0

#define LIGHT_OFF                       0x00
#define LIGHT_ON                        0x01

// Events for the sample app
#define SAMPLEAPP_END_DEVICE_REJOIN_EVT   0x0001
  
// Test  
#define SAMPLEAPP_ACT_EVT                  0x0040
#define SAMPLEAPP_LEV_EVT                  0x0400
//#define SAMPLEAPP_UART_RX_EVT               0x0080
#define SAMPLEAPP_BROADCAST                 0x00
#define SAMPLEAPP_GROUPCAST                 0x01
#define SAMPLEAPP_UNICAST                   0x10
  
#ifdef ZDO_COORDINATOR
#else
  // rejoin
  #define SAMPLEAPP_REJOIN_EVT          0x0080
  #define SAMPLEAPP_REJOIN_PERIOD       1000
#endif  


#define CMD_JC_STEER           0x0
#define CMD_JC_LIST            0x1
#define CMD_JC_NODEREQ         0x2
#define CMD_JC_AEPREQ          0x3
#define CMD_JC_CLUREQ          0x4
#define CMD_JC_CMDREQ          0x5
#define CMD_JC_CMDRSP          0x6
#define CMD_JC_ZCLREQ          0x7
#define CMD_JC_LEVREQ          0x8

#define ERR_CMD_TIMEOUT      0xfc
#define ERR_CMD_NOTFOUND    0xfe
#define ERR_CMD_FAIL        0xff
  

#define SAMPLEAPP_END_DEVICE_REJOIN_DELAY 10000

#define SAMPLEAPP_ACT_TIMEOUT 5000

/*********************************************************************
 * MACROS
 */
/*********************************************************************
 * TYPEDEFS
 */

/*********************************************************************
 * VARIABLES
 */
extern SimpleDescriptionFormat_t zclSampleSw_HASimpleDesc;
extern SimpleDescriptionFormat_t zclSampleSw_ZLLSimpleDesc;
extern SimpleDescriptionFormat_t zclSampleSw_GPSimpleDesc;

extern SimpleDescriptionFormat_t zclSampleSw9_SimpleDesc;

extern CONST zclAttrRec_t zclSampleSw_Attrs[];

extern uint8  zclSampleSw_OnOff;

extern uint16 zclSampleSw_IdentifyTime;

extern uint8 zclSampleSw_OnOffSwitchType;

extern uint8 zclSampleSw_OnOffSwitchActions;

extern CONST uint8 zclSampleSw_NumAttributes;

/*********************************************************************
 * FUNCTIONS
 */

 /*
  * Initialization for the task
  */
extern void zclSampleSw_Init( byte task_id );

/*
 *  Event Process for the task
 */
extern UINT16 zclSampleSw_event_loop( byte task_id, UINT16 events );

/*
 *  Reset all writable attributes to their default values.
 */
extern void zclSampleSw_ResetAttributesToDefaultValues(void); //implemented in zcl_samplesw_data.c

/*********************************************************************
*********************************************************************/

#ifdef __cplusplus
}
#endif

#endif /* ZCL_SAMPLEAPP_H */
