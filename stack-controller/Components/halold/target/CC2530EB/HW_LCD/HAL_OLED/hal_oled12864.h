/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef HAL_OLED12864_H
#define HAL_OLED12864_H

#ifdef __cplusplus
extern "C" {
#endif

/** @brief   OLED12864 parameters.
 */
#define HAL_OLED12864_PAGE      8    //!< Total pages
#define HAL_OLED12864_X         128  //!< Max X
#define HAL_OLED12864_Y         64   //!< Max Y

/** @brief   Font Table Configuretion.
 *  8x16
 */
#define FONT_TABLE_8x16           FontTable_V_8X16                //!< 8x16 ASCII Char.
#define FONT_TABLE_CHINESE_16x16  FontTable_Chinese_V_16X16       //!< 16x16 Chinese Char.
#define FONT_TABLE_CHINESE_SIZE   FONTTABLE_CHINESE_V_16x16_NUM   //!< Length of the table.


/**
 * @fn      halOLED12864Init
 * 
 * @brief	Init. OLED12864.
 */
void halOLED12864Init(void);

/**
 * @fn      halOLED12864ClearScreen
 * 
 * @brief	Clear screen.
 */
void halOLED12864ClearScreen(void);
   
/**
 * @fn      halOLED12864Show
 * 
 * @brief	Show x16(Height: 16) String, Supported Font: 
 *          1. ASCII - 8x16 2. Chinese 16x16 characters
 *
 * @param   line - 0 ~ 3
 * @param   column - 0 ~ 127
 * @param   str - string
 *
 * @warning Chinese 16x16 characters must found in table:
 *          FONT_TABLE_CHINESE_16x16
 */
void halOLED12864ShowX16(unsigned char line, unsigned char column, const unsigned char *str);

/**
 * @fn      halOLED12864ShowPicture
 * 
 * @brief	Show Picture
 *
 * @param   x - 0 ~ 127
 * @param   y - 0 ~ 64
 * @param   picWidth - max: 128
 * @param   picHeight - max: 64
 * @param   pic - picture
 */
void halOLED12864ShowPicture(unsigned char x, unsigned char y, unsigned char picWidth, unsigned char picHeight, const unsigned char *pic);


#ifdef __cplusplus
}
#endif

#endif /* #ifndef HAL_OLED12864_H */
