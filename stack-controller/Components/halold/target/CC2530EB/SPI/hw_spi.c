/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#include "hw_spi.h"

static void CC2530_Spi1Init(uint8 alternate, uint8 bitOrder, uint8 CPOL, uint8 CPHA);
static int CC2530_Spi1TxByte(uint8 b);
static uint8 CC2530_Spi1RxByte(void);

void HwSPIInit(HwSPICfg_t *hw)
{
    switch(hw->alternate)
    {
    case HW_SPI1_ALT2:
      CC2530_Spi1Init(HW_SPI1_ALT2, hw->bitOrder, hw->CPOL, hw->CPHA);
    break;
    
    default:
    break;
    }
}

int HwSPITxByte(uint8 alternate, uint8 b)
{
    int ret = -1;
    
    if (alternate == HW_SPI1_ALT2) ret = CC2530_Spi1TxByte(b);
    
    return ret;
}

uint8 HwSPIRxByte(uint8 alternate)
{
    uint8 b = 0x00;

    if (alternate == HW_SPI1_ALT2) b = CC2530_Spi1RxByte();

    return b;
}

/* 
 * @brief	Init CC2530 SPI1
 *
 * @param 	alternate - SPI-1 alternate
 * @param   bitOrder - SPI bit rrder
 * @param   CPOL - lock polarity
 * @param   CPHA - clock phase
 */
static void CC2530_Spi1Init(uint8 alternate, uint8 bitOrder, uint8 CPOL, uint8 CPHA)
{
    /* Mode select UART1 SPI Mode as master. */
    U1CSR = 0; 
  
    /* Setup for baud, sys-clock/8 MHZ */
    U1GCR |= 0x11;
    U1BAUD = 0x00;
  
    if (alternate == HW_SPI1_ALT2) {
      /* Set USART1 I/O to alternate 2 location on P1 pins:
       * SCK:P1_5, MOSI:P1_6, MISO:P1_7
       */
      PERCFG |= 0x02;
      
      /* Select peripheral function on I/O pins but SS is left as GPIO for 
       * separate control: SELP1_[7:4]
       */
      P1SEL |= 0xE0;
    }
    
    /* Set bit order to MSB */
    if (bitOrder == HW_SPI_BITORDER_MSB) U1GCR |= (1 << 5); 
    else U1GCR &= ~(1 << 5); 

    /* Set clock polarity, CPOL */
    if (CPOL == HW_SPI_CPOL_HIGH) U1GCR |= (1<<7);
    else U1GCR &= ~(1<<7);
    
    /* Set clock phase, CPHA */
    if (CPHA == HW_SPI_CPHA_FIRST) U1GCR &= ~(1<<6);
    else U1GCR |= (1<<6);
    
    /* Give USART1 priority over Timer3. */
    P2SEL &= ~0x20;
    
    /* When SPI config is complete, enable it. */
    U1CSR |= 0x40; 
}

/*
 * @brief   Tx a byte by CC2530 HW-SPI-1
 * @param   b - byte
 * @return  SUCCESS: 0, Other: -1
 */
static int CC2530_Spi1TxByte(uint8 b)
{
    uint16 timeout = 6420;  // 32MHZ ~6ms, 16MHZ ~12ms
  
    U1CSR &= ~0x02; 
    U1DBUF = b;
    
    while (!(U1CSR & 0x02)) if (--timeout == 0) break;
    
    return (timeout == 0)? -1 : 0;
}

static uint8 CC2530_Spi1RxByte(void)
{
    uint8 b = U1DBUF;
    return b;
}