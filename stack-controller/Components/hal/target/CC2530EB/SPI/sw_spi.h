/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef SW_SPI_H
#define SW_SPI_H

#include "spi_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/** @brief  SPI Options.
 */
#define SW_SPI_TX   0 //!< TX.
#define SW_SPI_RX   1 //!< RX.
  
/** @brief  Delay after SPI Clock changed.
 */  
#define SW_SPI_SCK_DELAY()  do{}while(0)
  
/* 
 *  @brief  TX a bit by SW-SPI bus:
 *	@param  SDA_Port, SDA_Pin - SDA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  b - byte.
 */
#define SW_SPI_TX_BIT( SDA_Port, SDA_Pin, bitOrder, b ) do {        \
        if ((bitOrder) == SPI_BITORDER_MSB) {                       \
        if (((b) & 0x80) == 0) SPI_GPIO_CLEAR(SDA_Port, SDA_Pin);   \
        else SPI_GPIO_SET(SDA_Port, SDA_Pin);                       \
        (b) <<= 1;                                                  \
    }                                                               \
    else{                                                           \
        if(((b) & 0x01) == 0) SPI_GPIO_CLEAR(SDA_Port, SDA_Pin);    \
        else SPI_GPIO_SET(SDA_Port, SDA_Pin);                       \
        (b) >>= 1;                                                  \
    }                                                               \
} while(0)

/** @brief  RX a bit From SW-SPI bus:
 *	@param  SDA_Port, SDA_Pin - SDA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  b - byte.
 */
#define SW_SPI_RX_BIT( SDA_Port, SDA_Pin, bitOrder, b ) do {    \
    if ((bitOrder) == SPI_BITORDER_MSB) {                       \
        (b) <<= 1;                                              \
        if (SPI_GPIO_GET(SDA_Port, SDA_Pin)) (b) |= 0x01;       \
        else (b) &= 0xFE;                                       \
    }                                                           \
    else {                                                      \
        (b) >>= 1;                                              \
        if(SPI_GPIO_GET(SDA_Port, SDA_Pin)) (b) |= 0x80;        \
        else (b) &= ~0x80;                                      \
    }                                                           \
} while(0)

/*  @brief  CPOL = 1, CPHA = 1; TX/RX a byte.
 *	@param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *	@param  SDA_Port, SDA_Pin - SPI DATA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  opt - SW_SPI_TX_BYTE, SW_SPI_RX_BYTE.
 *	@param  b - byte.
 */
#define SW_SPI_MODE4_BYTE(CLK_Port, CLK_Pin, SDA_Port, SDA_Pin, bitOrder, opt, b) do {  \
    for (uint8 __SW_SPI_I = 0; __SW_SPI_I < 8; __SW_SPI_I++) {                          \
        SPI_GPIO_CLEAR(CLK_Port, CLK_Pin);                                              \
        SW_SPI_SCK_DELAY();                                                             \
        if ((opt) == SW_SPI_TX) SW_SPI_TX_BIT(SDA_Port, SDA_Pin, bitOrder, b);          \
        else SW_SPI_RX_BIT(SDA_Port, SDA_Pin, bitOrder, b);                             \
        SPI_GPIO_SET(CLK_Port, CLK_Pin);                                                \
        SW_SPI_SCK_DELAY();                                                             \
    }                                                                                   \
} while(0)

/*  @brief  CPOL = 0, CPHA = 0; TX/RX a byte.
 *	@param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *	@param  SDA_Port, SDA_Pin - SPI DATA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  opt - SW_SPI_TX_BYTE, SW_SPI_RX_BYTE.
 *	@param  b - byte.
 */
#define SW_SPI_MODE1_BYTE(CLK_Port, CLK_Pin, SDA_Port, SDA_Pin, bitOrder, opt, b) do { \
    SW_SPI_MODE4_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin, bitOrder,opt, b );	           \
    SPI_GPIO_CLEAR(CLK_Port, CLK_Pin);                                                 \
} while(0)

/*  @brief  CPOL = 0, CPHA = 1; TX/RX a byte.
 *	@param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *	@param  SDA_Port, SDA_Pin - SPI DATA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  opt - SW_SPI_TX_BYTE, SW_SPI_RX_BYTE.
 *	@param  b - byte.
 */
#define SW_SPI_MODE2_BYTE(CLK_Port, CLK_Pin, SDA_Port, SDA_Pin, bitOrder, opt, b) do { \
    for (uint8 __SW_SPI_I = 0; __SW_SPI_I < 8; __SW_SPI_I++) {                         \
        SPI_GPIO_SET(CLK_Port, CLK_Pin);                                               \
        SW_SPI_SCK_DELAY();                                                            \
        if((opt) == SW_SPI_TX) SW_SPI_TX_BIT(SDA_Port, SDA_Pin, bitOrder, b);          \
        else SW_SPI_RX_BIT(SDA_Port, SDA_Pin, bitOrder, b);                            \
        SPI_GPIO_CLEAR(CLK_Port, CLK_Pin);                                             \
        SW_SPI_SCK_DELAY();                                                            \
    }                                                                                  \
} while(0)

/*  @brief  CPOL = 1, CPHA = 0; TX/RX a byte.
 *	@param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *	@param  SDA_Port, SDA_Pin - SPI DATA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *	@param  opt - SW_SPI_TX_BYTE, SW_SPI_RX_BYTE.
 *	@param  b - byte.
 */
#define SW_SPI_MODE3_BYTE(CLK_Port, CLK_Pin, SDA_Port, SDA_Pin, bitOrder, opt, b ) do { \
    SW_SPI_MODE2_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin, bitOrder,opt,b);               \
    SPI_GPIO_SET(CLK_Port, CLK_Pin);                                                    \
} while(0)

/*  @brief  Send a byte to SPI-Slave.
 *	@param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *	@param  SDA_Port, SDA_Pin - SPI DATA GPIO.
 *	@param  bitOrder - MSB/LSB.
 *  @param  CPOL, CPHA - Clock polarity, Clock phase.
 *	@param  opt - SW_SPI_TX_BYTE, SW_SPI_RX_BYTE.
 *	@param  b - byte.
 */
#define SW_SPI_BYTE(CLK_Port, CLK_Pin, SDA_Port, SDA_Pin, bitOrder, CPOL, CPHA, opt, b) \
    if((CPOL) == SPI_CPOL_LOW && (CPHA) == SPI_CPHA_FIRST)                              \
        SW_SPI_MODE1_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin,bitOrder,opt,b);            \
    else if((CPOL) == SPI_CPOL_LOW && (CPHA) == SPI_CPHA_SECOND)                        \
        SW_SPI_MODE2_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin,bitOrder,opt,b);            \
    else if((CPOL) == SPI_CPOL_HIGH && (CPHA) == SPI_CPHA_FIRST)                        \
        SW_SPI_MODE3_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin,bitOrder,opt,b);            \
    else if((CPOL) == SPI_CPOL_HIGH && (CPHA) == SPI_CPHA_SECOND)                       \
        SW_SPI_MODE4_BYTE(CLK_Port,CLK_Pin,SDA_Port,SDA_Pin,bitOrder,opt,b)


/*  @brief	Initial SW-SPI Clock.
 */
#define SW_SPI_INIT_CLK(CLK_Port, CLK_Pin, CPOL) do {               \
    SPI_GPIO_OUTPUT(CLK_Port, CLK_Pin);                             \
    if((CPOL) == SPI_CPOL_LOW) SPI_GPIO_CLEAR(CLK_Port, CLK_Pin);   \
    else SPI_GPIO_SET(CLK_Port, CLK_Pin);                           \
} while(0)

/*  @brief	Initial SW-SPI mode as MOSI/MISO.
 */
#define SW_SPI_INIT_MOSI(MO_Port, MO_Pin)   SPI_GPIO_OUTPUT(MO_Port, MO_Pin)
#define SW_SPI_INIT_MISO(MI_Port, MI_Pin)   SPI_GPIO_OUTPUT(MI_Port, MI_Pin)

/*  @brief	Init. SW-SPI bus.
 *  @param 	CLK_Port, CLK_Pin - SPI Clock GPIO.
 *  @param 	SDA_Port, SDA_Pin - SPI Data GPIO.
 *  @param 	MO_Port, MO_Pin - SPI MOSI GPIO.
 *  @param 	MI_Port, MI_Pin - SPI MISO GPIO.
 *	@param 	CPOL - Clock polarity.
 */
#define SW_SPI_INIT(CLK_Port, CLK_Pin, MO_Port, MO_Pin, MI_Port, MI_Pin, CPOL ) do { \
    SW_SPI_INIT_CLK(CLK_Port, CLK_Pin, CPOL);                                        \
    SW_SPI_INIT_MOSI(MO_Port, MO_Pin);                                               \
    SW_SPI_INIT_MISO(MI_Port, MI_Pin);                                               \
} while(0)

/*  @brief	Tx a byte by SW-SPI bus.
 *  @param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *  @param  MO_Port, MO_Pin - SPI MOSI GPIO.
 *  @param  bitOrder - MSB/LSB.
 *  @param  CPOL, CPHA - Clock polarity, Clock phase.
 *  @param  b - byte.
 *  @note	CS chosen by user.
 */
#define SwSPITxByte(CLK_Port, CLK_Pin, MO_Port, MO_Pin, bitOrder, CPOL, CPHA, b) \
    SW_SPI_BYTE(CLK_Port, CLK_Pin, MO_Port, MO_Pin, bitOrder, CPOL, CPHA, SW_SPI_TX, b)

/*  @brief	Rx a byte by SW(Software) SPI bus.
 *  @param  CLK_Port, CLK_Pin - SPI CLOCK GPIO.
 *  @param  MI_Port, MI_Pin - SPI MISO GPIO.
 *  @param  bitOrder - MSB/LSB.
 *  @param  CPOL, CPHA - Clock polarity, Clock phase.
 *  @param  b - byte.
 *  @note	CS chosen by user.
 */
#define  SwSPIRxByte(CLK_Port, CLK_Pin, MI_Port, MI_Pin, bitOrder, CPOL, CPHA, b) \
    SW_SPI_BYTE(CLK_Port, CLK_Pin, MI_Port, MI_Pin, bitOrder, CPOL, CPHA, SW_SPI_RX, b)


#ifdef __cplusplus
}
#endif

#endif /* #ifndef SW_SPI_H */
