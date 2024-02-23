/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef HAL_DELAY_H
#define HAL_DELAY_H

#include "hal_types.h"

typedef uint8 uint8_t;
typedef uint16 uint16_t;

#ifdef __cplusplus
extern "C" {
#endif

typedef enum { SYSCLK_16MHZ, SYSCLK_32MHZ } halDelaySysClk_t;

void delayUsIn32Mhz(uint16_t nUs);
void delayMs(halDelaySysClk_t sysClk, uint16_t nMs);


#ifdef __cplusplus
}
#endif

#endif /* #ifndef HAL_DELAY_H */
