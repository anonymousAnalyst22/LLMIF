/**
 * Copyright (c) 2020~2022 iotlucker.com, All Rights Reserved.
 *
 * @Official Store: https://shop233815998.taobao.com
 * @Official Website & Online document: http://www.iotlucker.com
 * @WeChat Official Accounts: shanxuefang_iot
 * @Support: 1915912696@qq.com
 */
#ifndef CC2530_IOCTL_H
#define CC2530_IOCTL_H

#include <ioCC2530.h>

#define CC2530_IOCTL_REVISION   1

#ifdef __cplusplus
extern "C" {
#endif

/** @brief  CC2530 GPIO mode. */
#define CC2530_OUTPUT          0 //!< Output.
#define CC2530_INPUT_PULLUP    1 //!< pullup input.
#define CC2530_INPUT_PULLDOWN  2 //!< pulldown input.
#define CC2530_INPUT_TRISTATE  3 //!< 3-state.

/** @brief  Left shift of bit. */
#define CC2530_IOCTL_BV(x)      (1<<(x))
  
/** @brief  Config register: PxSEL. */ 
#define CC2530_REGCFG_PxSEL(port, pin, val) do {        \
    if(val == 0) P##port##SEL &= ~CC2530_IOCTL_BV(pin); \
    else P##port##SEL |= CC2530_IOCTL_BV(pin);          \
} while(0)
 
/** @brief  Config register: PxDIR. */ 
#define CC2530_REGCFG_PxDIR(port, pin, val) do {        \
    if(val == 0) P##port##DIR &= ~CC2530_IOCTL_BV(pin); \
    else P##port##DIR |= CC2530_IOCTL_BV(pin);          \
} while(0)

/** @brief  Config register: PxINP. */
#define CC2530_REGCFG_PxINP(port, pin, val) do {        \
    if(val == 0) P##port##INP &= ~CC2530_IOCTL_BV(pin); \
    else P##port##INP |= CC2530_IOCTL_BV(pin);          \
} while(0)

/** @brief  Config GPIO mode as output. */
#define CC2530_IO_OUTPUT(port, pin) do {    \
    CC2530_REGCFG_PxDIR(port , pin , 1);    \
    CC2530_REGCFG_PxSEL(port , pin , 0);    \
} while(0)

/** @brief  Config GPIO mode as input. */
#define CC2530_IO_INPUT(port, pin, mode) do {                                  \
    CC2530_REGCFG_PxDIR(port , pin , 0);                                       \
    CC2530_REGCFG_PxSEL(port , pin , 0);                                       \
                                                                               \
    if (mode == CC2530_INPUT_TRISTATE) CC2530_REGCFG_PxINP(port , pin , 1);    \
    else {                                                                     \
        CC2530_REGCFG_PxINP(port , pin , 0);                                   \
        if (mode == CC2530_INPUT_PULLUP) CC2530_REGCFG_PxINP(2 , (5+port), 0); \
        else CC2530_REGCFG_PxINP(2 , (5+port), 1);                             \
    }                                                                          \
} while(0)


/** @brief    Config gpio mode.
 *  @warning  P1_0, P1_1 can't configed as input mode.
 */
#define CC2530_IOCTL(port, pin, mode) do {                  \
    if (port > 2 || pin > 7) break;                         \
                                                            \
    if (mode == CC2530_OUTPUT) CC2530_IO_OUTPUT(port, pin); \
    else CC2530_IO_INPUT(port, pin, mode);                  \
} while(0)

/** @brief    Set/Clear GPIO state.
 *  @warning  GPIO must in output mode.
 */
#define CC2530_GPIO_SET(port, pin)      P##port##_##pin = 1
#define CC2530_GPIO_CLEAR(port, pin)    P##port##_##pin = 0

/** @brief    Get GPIO state.
 */
#define CC2530_GPIO_GET(port, pin)      P##port##_##pin

/** @brief    Set system clock as 32MHZ.
 */
#define setSystemClk32MHZ() do { \
    CLKCONCMD &= ~0x40;          \
    while(CLKCONSTA & 0x40);     \
    CLKCONCMD &= ~0x47;          \
} while(0)

   
#ifdef __cplusplus
}
#endif

#endif /* #ifndef CC2530_IOCTL_H */
