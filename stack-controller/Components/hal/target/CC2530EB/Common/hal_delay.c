/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#include "hal_delay.h"

#pragma optimize=none
void delayUsIn32Mhz(uint16_t nUs)
{
    for(uint16_t i = 0; i < nUs; i++)
    {
        asm("NOP");
        asm("NOP");
        asm("NOP");
        asm("NOP");
        asm("NOP");
        asm("NOP");
        asm("NOP");
    }
}

#pragma optimize=none
void delayMs(halDelaySysClk_t sysClk, uint16_t nMs)
{
  uint16_t i, j;
  uint16_t loop1Ms;
  
  if (sysClk == SYSCLK_16MHZ) loop1Ms = 535;
  else loop1Ms = 1070;

  for(i = 0; i < nMs; i++) for(j = 0; j < loop1Ms; j++);
}
