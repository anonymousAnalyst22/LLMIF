/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef HAL_LCD_SPI_H
#define HAL_LCD_SPI_H

#include "sw_spi.h"
#include "hw_spi.h" 

#ifdef __cplusplus
extern "C" {
#endif

/*
 *  HAL_LCD_SPI_SW: SW-SPI Bus
 *  HAL_LCD_SPI_HW: HW-SPI Bus
 */     
#if !defined(HAL_LCD_SPI_SW) && !defined(HAL_LCD_SPI_HW)
  #define HAL_LCD_SPI_SW
#endif
   
/* SPI GPIO: SCK:P1_5, SDA: P1_6, CS: P1_2, DC: P1_4, RST: P2_0. */   
#ifdef HAL_LCD_SPI_SW
    /* SCK */
    #define HAL_LCD_SPI_SCK_PORT  	1
    #define HAL_LCD_SPI_SCK_PIN   	5
    /* SDA */
    #define HAL_LCD_SPI_SDA_PORT  	1
    #define HAL_LCD_SPI_SDA_PIN   	6
#endif
/* CS */
#define HAL_LCD_SPI_CS_PORT   		2
#define HAL_LCD_SPI_CS_PIN    		0 
/* DC */
#define HAL_LCD_SPI_DC_PORT   		1
#define HAL_LCD_SPI_DC_PIN    		4
/* RST */
#define HAL_LCD_SPI_RST_PORT  		1
#define HAL_LCD_SPI_RST_PIN   		0

void halLcdSpiInit(void);
void halLcdSpiTxCmd(uint8 cmd);
void halLcdSpiTxData(uint8 dat);

#ifdef __cplusplus
}
#endif

#endif /* #ifndef HAL_LCD_SPI_H */
