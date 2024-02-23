/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef HAL_TFT_H
#define HAL_TFT_H

#include "hal_lcd_spi.h"

#ifdef __cplusplus
extern "C" {
#endif

#define LCD_TFT096        0
#define LCD_IPS096_T1     1

/** @brief   LCD type.
 */
#define LCD_TYPE          LCD_IPS096_T1

/** @brief   TFT pixel color.
 */
#define HAL_TFT_PIXEL_RED       0xF800 //!< Red.
#define HAL_TFT_PIXEL_GREEN     0x07E0 //!< Green.
#define HAL_TFT_PIXEL_BLUE      0x001F //!< Blue.
#define HAL_TFT_PIXEL_BLACK     0x0000 //!< Black.
#define HAL_TFT_PIXEL_WHITE     0xFFFF //!< White.
#define HAL_TFT_PIXEL_YELLOW    0xFFE0 //!< Yellow.
#define HAL_TFT_PIXEL_GRAY      0xEF7D //!< Gray.
   
/** @brief   TFT parameters.
 */
#if (defined LCD_TYPE) && (LCD_TYPE == LCD_TFT096)
#define HAL_TFT_X               128 //!< x(0 ~ 127).
#define HAL_TFT_Y               128 //!< y(64 ~ 127).
#define HAL_TFT_Y_OFFSET        64  //!< Offset.
#elif (defined LCD_TYPE) && (LCD_TYPE == LCD_IPS096_T1)
#define HAL_TFT_X               160
#define HAL_TFT_Y               80
#define HAL_TFT_Y_OFFSET        0
#endif
   
/** @brief   Font Table Configuretion.
 *  8x16
 */
#define HAL_TFT_FONT_TBL_8x16           FontTable_H_8X16                //!< 8x16 ASCII Char.
#define HAL_TFT_FONT_TBL_CHINESE_16x16  FontTable_Chinese_H_16X16       //!< 16x16 Chinese Char.
#define HAL_TFT_FONT_TBL_CHINESE_SIZE   FONTTABLE_CHINESE_H_16x16_NUM   //!< Size of the talbe.

/**
 * @fn      halTFTInit
 * 
 * @brief   Init. TFT
 *
 * @param   screenColor - screen color(HAL_TFT_PIXEL_BLACK ...)
 */
void halTFTInit(uint16 screenColor);

/**
 * @fn      halTFTClearScreen
 * 
 * @brief   Set screen color
 *
 * @param   pixelVal - pixel value
 */
void halTFTSetScreen(uint16 pixelVal);

/**
 * @fn      halTFTShowX16
 * 
 * @brief   Show x16(Height: 16) String, Supported Font: 1. ASCII - 8x16  2. Chinese 16x16 characters.
 *
 * @param   x - 0 ~ 127
 * @param   y - 0 ~ 63
 * @param   fontColor - font color
 * @param   backgroundColor - background color
 * @param   str - string
 *
 * @warning Chinese 16x16 characters must found in table: FONT_TABLE_CHINESE_16x16
 */
void halTFTShowX16(uint16 x, uint16 y, uint16 fontColor, uint16 backgroundColor, const uint8 *str);

/**
 * @fn      halTFTShowPicture
 * 
 * @brief   Show Picture
 *
 * @param   x - 0 ~ 127
 * @param   y - 0 ~ 64
 * @param   picWidth - max: 128
 * @param   picHeight - max: 64
 * @param   pic - picture
 */
void halTFTShowPicture(uint8 x, uint8 y, uint8 picWidth, uint8 picHeight, const uint8 *pic);

#ifdef __cplusplus
}
#endif

#endif /* #ifndef HAL_TFT_H */
