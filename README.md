# LLMIF

LLMIF is an IoT protocol fuzzer guided by the specifciation-augmented large language model. Currently it supports fuzzing the Zigbee protocol. It is composed of two modules: Fuzzing controller and stack controller.

## Usage Instructions
1. Prepare the hardware radio (CC2530/CC2538), download IAR toolchains, compile and flash the stack-controller to the hardware.
2. Connect the hardware radio to the host machine (e.g., your PC) where the fuzzing controller is going to run.
3. Configure the fuzzing controller: (1) The USB port of the hardware radio, and (2) your LLM credentials.
4. Factory reset the device under testing, and run the fuzzing controller by "python main.py".
Followings are details of the two modules. Users may refer to them for understanding how LLMIF is implemented.

## Fuzzing controller

### Introduction
The fuzzing controller is responsible for managing the fuzzing process (Figure 3 in our paper). The main logic is implemented in python and lies in fuzzing-controller/main.py.

### Configuration
Note that before runing the fuzzer by "python main.py", users need to make the following configurations.
* Replace STACK_ADDR in fuzzing-controller/lib/controller_constants.py with the address of your hardware radio, after you connect the radio to your hosting machine, e.g., "/dev/ttyUSB0".
* Replace API_KEY in fuzzing-controller/spec/libs/constants.py with your API key. Here we use POE as the LLM platform.
* Replace LLM_MODEL in fuzzing-controller/spec/libs/constants.py with the LLM model you want to use. Examples are "GPT-3.5-Turbo".

## Stack Controller

### Introduction
The stack controller is responsible for creating the Zigbee coordinator and managing Zigbee communication channels. It should be compiled with IAR development toolchain and flashed into the specific hardware radio (CC2530/CC2538). The main logic of the driver is implemented in C and lies in zstack/HomeAutomation/SampleSwith/CC2530DB/Source/zcl_samplesw.c.

### Instructions for Compliation and Flashing
Our implementation of the stack controller supports two hardware radio (CC2530 and CC2538). Specifically, the firmware codes should be compiled and flashed with IAR development toolchain. The developement kit depends on the hardware radio. Specifically, for CC2530, the user should download and configure IAR Embedded Workbench IDE for 8051, while for CC2538 users should choose IAR Embedded Workbench IDE for ARM.

* After successfully configuring the IAR toolchain, the user can use the IDE to open our provided workspace configuration file at zstack/HomeAutomation/SampleSwith/CC2530DB/SampleSwitch.eww.
* Then users can compile the firmware by clicking Project/Rebuild All.
* Once the firmware is ready, users can connect their CC2530/CC2538 board, and use Flash Programmer to flash the firmware into the board. Or the users can use the IAR IDE to download the firmware to the board and debug it first by clicking Project/Download and Debug.

To use LLMIF, one should
* download IAR toolchains (for 8051 or for ARM) to compile the stack controller. Logics of the stack controller is in the file of ZMain.c.
* Load the compiled stack firmware on CC2530/CC2538 to build a Zigbee coordinator node for Zigbee communiaiton channel.
* Conenct your CC2530/CC2538 module to your PC/Raspberry Pi with USB. A USB-to-serial conveter may be needed.
* Run the fuzzing controller with python. The main.py is a good start to investigate.
