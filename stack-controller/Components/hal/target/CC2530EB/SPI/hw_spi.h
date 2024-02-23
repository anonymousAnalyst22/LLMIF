/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef HW_SPI_H
#define HW_SPI_H

#include "spi_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * HW(Hardware) SPI parameters: alternate, bit order, clock polarity, clock phase
 */   
// alternate
#define HW_SPI1_ALT2        3  // CC2530 - SCK:P1_5, MISO:P1_6, MOSI:P1_7
// bit order
#define HW_SPI_BITORDER_MSB 0  // MSB
#define HW_SPI_BITORDER_LSB 1  // LSB
// clock polarity
#define HW_SPI_CPOL_LOW     0  // low level
#define HW_SPI_CPOL_HIGH    1  // high level
// clock phase
#define HW_SPI_CPHA_FIRST   0  // sample in first edge
#define HW_SPI_CPHA_SECOND  1  // sample in second edge

/** @brief  HW(Hardware) SPI parameters.
 *  alternate - Set SPI I/O to alternate x,
 *	bitOrder - LSB/MSB,
 *	CPOL, CPHA - clock polarity, clock phase
 *
 *  @note See the definition [HW_SPI_xxx] for specific parameters!
 */
typedef struct
{    
    uint8 alternate;
    uint8 bitOrder;
    uint8 CPOL, CPHA;
} HwSPICfg_t;

/**
 * @fn      halHwSPIInit
 * 
 * @brief	Init. SPI bus by HW(Hardware) or SW(Software)
 *
 * @param 	hw - Hardware configuration
 *
 * @return 	none
 */
void HwSPIInit(HwSPICfg_t *hw);

/**
 * @fn      HwSPITxByte
 * 
 * @brief	Tx a byte by HW(Hardware) SPI bus
 *
 * @param 	alternate - SPI alternate
 * @param   b - data
 *
 * @return 	SUCCESS: 0, Other: -1
 *
 * @note	CS chosen by user, or using API: HW_SPI_TX_BYTE
 */
int HwSPITxByte(uint8 alternate, uint8 b);

/**
 * @fn      HwSPIRxByte
 * 
 * @brief	Rx a byte by HW(Hardware) SPI bus
 *
 * @param 	alternate - SPI alternate
 *
 * @return 	Data from HW-SPI
 *
 * @note	CS chosen by user, or using API: HW_SPI_TX_BYTE
 */
uint8 HwSPIRxByte(uint8 alternate);


#ifdef __cplusplus
}
#endif

#endif /* #ifndef HW_SPI_H */
