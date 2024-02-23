/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#include "hal_lcd_spi.h"
#include <stdarg.h>

static void halLcdSpiTxByte(uint8 b);

void halLcdSpiInit(void)
{
#ifdef HAL_LCD_SPI_SW
    SW_SPI_INIT_CLK(HAL_LCD_SPI_SCK_PORT, HAL_LCD_SPI_SCK_PIN,SPI_CPOL_HIGH);
    SW_SPI_INIT_MOSI(HAL_LCD_SPI_SDA_PORT, HAL_LCD_SPI_SDA_PIN);
#else
    HwSPICfg_t cfg = {
        .alternate = HW_SPI1_ALT2,
        .bitOrder  = HW_SPI_BITORDER_MSB,
        .CPOL      = HW_SPI_CPOL_HIGH,
        .CPHA      = HW_SPI_CPHA_SECOND,
    };
    
    HwSPIInit(&cfg);
#endif
    
    SPI_CS_INIT(HAL_LCD_SPI_CS_PORT, HAL_LCD_SPI_CS_PIN);
    SPI_GPIO_OUTPUT(HAL_LCD_SPI_DC_PORT, HAL_LCD_SPI_DC_PIN);
    SPI_GPIO_OUTPUT(HAL_LCD_SPI_RST_PORT, HAL_LCD_SPI_RST_PIN);
}

void halLcdSpiTxCmd(uint8 cmd)
{
    SPI_CS_SELECT(HAL_LCD_SPI_CS_PORT, HAL_LCD_SPI_CS_PIN);
  
    SPI_GPIO_CLEAR(HAL_LCD_SPI_DC_PORT, HAL_LCD_SPI_DC_PIN);
    halLcdSpiTxByte(cmd);
    
    SPI_CS_RELEASE(HAL_LCD_SPI_CS_PORT, HAL_LCD_SPI_CS_PIN);
}

void halLcdSpiTxData(uint8 dat)
{
    SPI_CS_SELECT(HAL_LCD_SPI_CS_PORT, HAL_LCD_SPI_CS_PIN);
    
    SPI_GPIO_SET(HAL_LCD_SPI_DC_PORT, HAL_LCD_SPI_DC_PIN);
    halLcdSpiTxByte(dat);
    
    SPI_CS_RELEASE(HAL_LCD_SPI_CS_PORT, HAL_LCD_SPI_CS_PIN);
}

static void halLcdSpiTxByte(uint8 b)
{
#ifdef HAL_LCD_SPI_SW
      SwSPITxByte(HAL_LCD_SPI_SCK_PORT, HAL_LCD_SPI_SCK_PIN,
                  HAL_LCD_SPI_SDA_PORT, HAL_LCD_SPI_SDA_PIN,
                  SPI_BITORDER_MSB,
                  SPI_CPOL_HIGH, HW_SPI_CPHA_SECOND,
                  b);
#else
      HwSPITxByte(HW_SPI1_ALT2, b);
#endif 
}