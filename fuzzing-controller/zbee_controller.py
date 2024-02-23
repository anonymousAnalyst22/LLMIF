import logging
controller_logger = logging.getLogger("ZbeeController")
import sys
from scapy.all import *
from scapy.layers.zigbee import ZigbeeAppDataPayload, ZigbeeClusterLibrary
from pprint import pprint
sys.path.insert(0, 'lib')
import time
import serial
import json
import time
import hashlib
from collections import defaultdict
from lib.controller_constants import *
from lib.zigbee_device import ZigbeeDevice
from lib.basic_type import DEFAULT_ENDIAN

class ZbeeController:
    
    def __init__(self, port:'str'=None, baud_rate:'int'=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._port = port # "/dev/ttyUSB0"  # replace with your UART port
        self._baud_rate = baud_rate # 115200  # replace with your desired baud rate
        self.uart = self.initialize_uart()
        self.target_device:'ZigbeeDevice' = None
    
    def initialize_uart(self):
        if self._port is None or self._baud_rate is None:
            return None
        uart_port = self._port
        baud_rate = self._baud_rate
        uart = serial.Serial(port=uart_port, baudrate=baud_rate, parity=serial.PARITY_NONE,\
                             stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=6)
        time.sleep(1)
        return uart

    def uart_send_and_listen(self, payload:'bytes'):
        '''
        Send a message to Coordinator through UART, and wait for the response.
        Note: If (1) a command is sent repeatly for 5 times, and
                 (2) there is always timeout (no reply in 2 seconds),
              then a timeout signal is generated.
        '''
        
        if len(payload) > 256:
            self.logger.warning(f"The message length to be transmitted is larger than UART_BUFFER_SIZE ({len(payload)}>256), reject!")
            exit()
        response = None
        timeout = True
        # The UART transmission and command execution may fail, such that no response is collected.
        # Therefore, we set MAX_TX_RETRY to retry the commandTransmission-responseWaiting process.
        for i in range(0, MAX_TX_RETRY):
            sent_length = self.uart.write(payload)
            r_len = 0
            rx_wait_time = 0
            while True: # Check if a complete response within MAX_RX_WAIT_TIME is received.
                time.sleep(UART_RX_WAIT_PERIOD)
                rx_wait_time += UART_RX_WAIT_PERIOD
                if rx_wait_time > MAX_RX_WAIT_TIME:
                    self.uart.reset_input_buffer()
                    self.uart.reset_output_buffer()
                    break
                n_len = self.uart.in_waiting
                if r_len == 0 or r_len != n_len:
                    r_len = n_len
                    continue
                else:
                    timeout = False
                    response = self.uart.read_all()
                    break
            # A complete response is received.
            if timeout == False:
                break
        self.uart.reset_input_buffer()
        self.uart.reset_output_buffer()
        if timeout:
            self.logger.error("Command {} has been transmitted for {} times. The coordinator firmware seems to be crashed.".format(payload, MAX_TX_RETRY))
        return response
    
    def simple_uart_send(self, payload:'bytes'):
        self.uart.write(payload)
        time.sleep(0.005)
        #self.uart.reset_input_buffer()
        #self.uart.reset_output_buffer()

    '''
    Zigbee Network functionalities.
    '''
    def network_steering(self, period):
        if period >= 255 or period <= 0:
            period = 0
        cmd = CMD_JC_STEER.to_bytes(1, 'little') + period.to_bytes(1, 'little')
        rsps = self.uart_send_and_listen(cmd)

        rsp_id = int.from_bytes(rsps[0:2], 'little')
        stat = int.from_bytes(rsps[2:4], 'little')
        assert(rsp_id == CMD_JC_STEER)
        controller_logger.info("Start device discovery with period {}......".format(period, hex(stat)))
        return stat
    
    def get_device_list(self):
        cmd = CMD_JC_LIST.to_bytes(1, 'little')
        rsps = self.uart_send_and_listen(cmd)

        rsp_id = int.from_bytes(rsps[0:2], 'little')
        stat = int.from_bytes(rsps[2:4], 'little')
        assert(rsp_id == CMD_JC_LIST) 
        shortAddrs = []; nodeRels = []
        for i in range(0, int((len(rsps)-4)/4)):
            shortAddrs.append(int.from_bytes(rsps[4+4*i:6+4*i], 'little'))
            nodeRels.append(int.from_bytes(rsps[6+4*i:8+4*i], 'little'))
        # By default we only select the first device
        if len(shortAddrs) > 0:
            self.target_device = ZigbeeDevice(shortAddrs[0], nodeRels[0])
            controller_logger.info("Identified device: {} with nodeRelation {}.".format(hex(shortAddrs[0]), nodeRels[0]))
        return stat
    
    def reset_device(self, nwkAddr, vendorSpecific=False):
        stat = 0
        if vendorSpecific:
            nID = "01"
            n_id = int(nID, base=16)
            dev_str = ("8392bf" + "00")*n_id
            assert(len(dev_str)/2 == 4*n_id)
            # 
            stat, frame, elapsed_time = self.inject_zcl_cmd(nwkAddr, SAMPLEAPP_UNICAST, 11, 0x0000, 0xc05e, 0x00, True, CLIENT_SERVER_DIRECTION, 0x100b, bytearray.fromhex("00f8ff07"+"18c155a104952c31"+nID+dev_str), monitor_response=False)     # Reset command for Philips Hue
        else: # ZDO Network Leave
            cmd_elements = [
                CMD_JC_LEVREQ.to_bytes(1, 'little'),
                nwkAddr.to_bytes(2, 'little')
            ]
            cmd = b''.join(cmd_elements)
            rsps = self.uart_send_and_listen(cmd)
            rsp_id = int.from_bytes(rsps[0:2], 'little')
            stat = int.from_bytes(rsps[2:4], 'little')
            assert(rsp_id == CMD_JC_LEVREQ)
        if not vendorSpecific:
            self.logger.info("NWKReset executed with result stat {}".format(hex(stat)))
        return stat
    
    '''
    Zigbee ZDO functionalities.
    '''
    def get_node_descriptor(self, nwkAddr):
        cmd_elements = [
            CMD_JC_NODEREQ.to_bytes(1, 'little'),
            nwkAddr.to_bytes(2, 'little')
        ]
        cmd = b''.join(cmd_elements)
        # Node Descriptor response in format: [cmd, nwkAddr, status, LogicalType, CapabilityFlag, ManufactuerCode]
        rsps = self.uart_send_and_listen(cmd)
        rsp_id = int.from_bytes(rsps[0:2], 'little')
        stat = int.from_bytes(rsps[2:4], 'little')
        assert(rsp_id == CMD_JC_NODEREQ)

        retNwkAddr = int.from_bytes(rsps[4:6], 'little')
        nodeStat = int.from_bytes(rsps[6:8], 'little')
        logicalType = int.from_bytes(rsps[8:10], 'little')
        capability = int.from_bytes(rsps[10:12], 'little')
        manufacturerCode = int.from_bytes(rsps[12:14], 'little')
        self.target_device.manufacturerCode = manufacturerCode
        self.logger.info("Identified manufacturerCode {}".format(hex(manufacturerCode)))
        return stat
    
    def get_active_endpoint(self, nwkAddr):
        cmd_elements = [
            CMD_JC_AEPREQ.to_bytes(1, 'little'),
            nwkAddr.to_bytes(2, 'little')
        ]
        cmd = b''.join(cmd_elements)
        # Node Descriptor response in format: [cmd, activeEP1, activeEP2,...]
        rsps = self.uart_send_and_listen(cmd)
        rsp_id = int.from_bytes(rsps[0:2], 'little')
        stat = int.from_bytes(rsps[2:4], 'little')
        assert(rsp_id == CMD_JC_AEPREQ)

        n_eps = (int)((len(rsps)-4)/2)
        self.target_device.n_eps = n_eps
        for i in range(n_eps):
            ep = int.from_bytes(rsps[2*i+4:2*i+6], 'little')
            self.target_device.active_eps.append(ep)
        self.logger.info("Identified active endpoint list: {}".format(self.target_device.active_eps))
        return stat
    
    def get_simple_descriptor(self, nwkAddr:'int', endpoint:'int'):
        cmd_elements = [
            CMD_JC_CLUREQ.to_bytes(1, 'little'),
            nwkAddr.to_bytes(2, 'little'),
            endpoint.to_bytes(1, 'little')
        ]
        cmd = b''.join(cmd_elements)
        rsps = self.uart_send_and_listen(cmd)  # Simple Descriptor response in format: [cmd, stat, nwkAddr, endpoint, status, AppProfId, AppDeviceID, AppDevVer, cluster1, cluster2,...]
        rsp_id = int.from_bytes(rsps[0:2], 'little')
        stat = int.from_bytes(rsps[2:4], 'little')
        assert(rsp_id == CMD_JC_CLUREQ)

        retNwkAddr = int.from_bytes(rsps[4:6], 'little')
        retEndpoint = int.from_bytes(rsps[6:8], 'little')
        nodeStat = int.from_bytes(rsps[8:10], 'little')
        if len(rsps) > 16:
            AppProfId = int.from_bytes(rsps[10:12], 'little')
            AppDeviceId = int.from_bytes(rsps[12:14], 'little')
            AppDevVer = int.from_bytes(rsps[14:16], 'little')
            self.target_device.profile_dict[retEndpoint] = AppProfId
            self.target_device.deviceID_dict[retEndpoint] = AppDeviceId
            for i in range(0, int((len(rsps)-16)/2)):
                clusterId = int.from_bytes(rsps[16+2*i:18+2*i], 'little')
                self.target_device.cluster_dict[retEndpoint].append(clusterId)
            self.target_device.n_clusters += len(self.target_device.cluster_dict[retEndpoint])
            self.logger.info("Endpoint {} runs profile {} with {} clusters.".format(endpoint, hex(AppProfId), len(self.target_device.cluster_dict[retEndpoint])))
            for clusterID in self.target_device.cluster_dict[retEndpoint]:
                self.logger.info(f"  Cluster {hex(clusterID)}")
        return stat

    def inject_zcl_cmd(self, nwkAddr:'int', flag:'int', ep:'int', cid:'int', pid:'int', cmd_id:'int', clusterSpecific:'bool', direction:'int', manuCode:'int', payload:'bytes', monitor_response=True, print_response=False):
        '''
        Zigbee AF/ZCL functionalities.
        Depending on monitor_response flag, the return value of this function varies.
        '''
        # Disable Default Response = False: Whenever the ZCL command succeeds or not, there is always a Default Response returned.
        self.logger.debug(f"Inject zcl command (ep={hex(ep)}, cid={hex(cid)}, cmd_id={hex(cmd_id)})")
        monitor_flag = 1 if monitor_response else 0
        cmd_elements = [
            CMD_JC_ZCLREQ.to_bytes(1, 'little'),
            nwkAddr.to_bytes(2, 'little'),
            flag.to_bytes(1, 'little'),
            ep.to_bytes(1, 'little'),
            cid.to_bytes(2, 'little'),
            pid.to_bytes(2, 'little'),
            cmd_id.to_bytes(1, 'little'),
            clusterSpecific.to_bytes(1, 'little'),
            direction.to_bytes(1, 'little'),
            manuCode.to_bytes(2, 'little'),
            monitor_flag.to_bytes(1, 'little'),
            len(payload).to_bytes(2, 'little'),
            payload
        ]
        cmd = b''.join(cmd_elements)

        frame = None
        zcl_payload = None
        elapsed_time = None
        rspStat = None
        frame_length = 0
        if monitor_response:
            rspID = -1
            elapsed_time = -1
            rsps = self.uart_send_and_listen(cmd) # The response should be a Default Response command
            if print_response:
                self.logger.info(rsps)
            rspID = int.from_bytes(rsps[0:2], byteorder=DEFAULT_ENDIAN)
            rspStat = int.from_bytes(rsps[2:4], byteorder=DEFAULT_ENDIAN)
            #print(' '.join([hex(b) for b in rsps]))
            #print(f"rspID = {hex(rspID)}, rspStat = {hex(rspStat)}")
            if rspID != CMD_JC_ZCLREQ:
                self.logger.error(f"Inject zcl command (ep={hex(ep)}, cid={hex(cid)}, cmd_id={hex(cmd_id)}) faield with non-aligned rspID: {hex(rspID)}")
                time.sleep(5)
                rspStat == ERR_CMD_FAIL
                zcl_payload = b''
                elapsed_time = -1
            elif rspStat == SUCCESS and len(rsps) > 4:
                frame_length = rsps[4]; frame = rsps[5:-4]; elapsed_time = rsps[-4:]
                #print(f"frame_length={frame_length}, frame={frame}, frame_real_length={len(frame)}")
                if frame_length != len(frame)+5:
                    self.logger.error(f"Inject zcl command (ep={hex(ep)}, cid={hex(cid)}, cmd_id={hex(cmd_id)}) faield with incorrect UART response!")
                    self.logger.error(f"    The UART response format is incorrect: frame_length={frame_length}, len(frame)={len(frame)}")
                    self.logger.error(f"{frame}")
                    time.sleep(5)
                    rspStat == ERR_CMD_FAIL
                    zcl_payload = b''
                    elapsed_time = -1
                else:
                    elapsed_time = int.from_bytes(elapsed_time, byteorder=DEFAULT_ENDIAN)
                    zcl_payload = rsps[13+3:-4] # 13 is the length of the APS part. 3 is the ZCL frame header part
            # Construct the APS + ZCL frame
            #app_frame = ZigbeeAppDataPayload(frame)
            #print(app_frame.command_identifier)
            #print(app_frame.payload)
            #print(app_frame.payload.__dir__())
        else:
            self.simple_uart_send(cmd)
            time.sleep(0.1)
        return rspStat, zcl_payload, elapsed_time

    '''
    Customized Zigbee functionality
    '''
    def device_scan(self):
        # Scan the target device, let it join the network, and collect its information
        stat = SUCCESS
        timeout = 60
        sleep_interval = 3
        self.network_steering(timeout)
        while self.target_device is None:
            stat = self.get_device_list()
            time.sleep(sleep_interval)
            timeout -= sleep_interval
            if timeout == 0:
                return JC_EXECUTION_TIMEOUT
        stat = self.get_node_descriptor(self.target_device.nwkAddr)
        stat = self.get_active_endpoint(self.target_device.nwkAddr)
        for active_ep in self.target_device.active_eps:
            stat = self.get_simple_descriptor(self.target_device.nwkAddr, active_ep)
        
        # Currently we use the device's manufactuerCode + [(EndpointId, RunningProfileID, AppDeviceID, RunningClusterID)] as the device signature
        self.target_device.signature = hex(self.target_device.manufacturerCode)
        has_cluster_eps = list(self.target_device.cluster_dict.keys())
        self.target_device.active_eps = has_cluster_eps
        for ep in self.target_device.active_eps:
            self.target_device.signature += '({},{},{},{})'.format(ep, self.target_device.profile_dict[ep], self.target_device.deviceID_dict[ep], self.target_device.cluster_dict[ep])
        self.target_device.hash_sig = hashlib.md5(self.target_device.signature.encode('utf-8')).hexdigest()
        return stat

    def cmd_scan(self, vendorSpecific:'bool'=True, selectedEps:'list'=[SYMBOL_MATCH_ALL], selectedClusters:'list'=[SYMBOL_MATCH_ALL], selectedCmds:'list'=[SYMBOL_MATCH_ALL]):
        self.logger.info("Scan the command on device {} with vendorSpecific {}.".format(hex(self.target_device.nwkAddr), vendorSpecific))
        manuCode = self.target_device.manufacturerCode if vendorSpecific else 0x0000
        for active_ep in self.target_device.active_eps:
            if (active_ep not in list(self.target_device.cluster_dict.keys())) or (SYMBOL_MATCH_ALL not in selectedEps and active_ep not in selectedEps): # If the endpoint has no incoming clusters: Ignore
                continue
            profileId = self.target_device.profile_dict[active_ep]
            for clusterId in self.target_device.cluster_dict[active_ep]:
                if SYMBOL_MATCH_ALL not in selectedClusters and clusterId not in selectedClusters:
                    continue
                #self.logger.info("     ep={}, clusterId={}, profileId={}".format(hex(active_ep), hex(clusterId), hex(profileId)))
                for cmdId in range(0x0, 0xff):
                    if SYMBOL_MATCH_ALL not in selectedCmds and cmdId not in selectedCmds:
                        continue
                    if (clusterId, cmdId) in GLOBAL_SKIPPED_CMDS:
                        continue
                    target_dict = self.target_device.manucmd_dict if vendorSpecific else self.target_device.ZCLcmd_dict
                    payload = b''
                    rspStat, zcl_payload, elapsed_time = self.inject_zcl_cmd(self.target_device.nwkAddr, SAMPLEAPP_UNICAST, active_ep, clusterId, profileId, cmdId, True, CLIENT_SERVER_DIRECTION, manuCode, payload)
                    retry = MAX_TX_RETRY
                    while rspStat == ERR_CMD_TIMEOUT and retry > 0:
                        time.sleep(5)
                        rspStat, zcl_payload, elapsed_time = self.inject_zcl_cmd(self.target_device.nwkAddr, SAMPLEAPP_UNICAST, active_ep, clusterId, profileId, cmdId, True, CLIENT_SERVER_DIRECTION, manuCode, payload)
                        retry -= 1
                    if rspStat == ERR_CMD_TIMEOUT:
                        # This is really strange. It seems that during the probing stage, the target device stops responding to the probing command.
                        self.logger.warning(f"ZCL command (ep:cid:cmd_id = {active_ep}:{clusterId}:{cmdId}) probing failed with timeout. It is really strange.")
                    # Sometimes the target device is too slow to respond. So we here set a maximum probing retry.
                    # By doing so, the timeout response code will not affect our probing result.
                    else:
                        if zcl_payload is None or len(zcl_payload) == 0:
                            statCode = SUCCESS
                            self.logger.warning(f"When scanning commands {hex(active_ep)}:{hex(profileId)}:{hex(clusterId)}:{hex(cmdId)}, receive a response with zero paylaod! Please check it!")
                        else:
                            statCode = int(zcl_payload[1]) if len(zcl_payload) > 1 else int(zcl_payload[0])
                        if statCode in [ZCL_STATUS_UNSUP_CLUSTER_COMMAND, ZCL_STATUS_UNSUP_MANU_CLUSTER_COMMAND]:
                            pass
                        else:
                            k = '{}:{}:{}'.format(hex(active_ep), hex(profileId), hex(clusterId))
                            target_dict[k].append((cmdId, statCode))
                            if vendorSpecific:
                                self.target_device.n_manucmds += 1
                            else:
                                self.target_device.n_ZCLcmds += 1
                #self.logger.info(target_dict)
                self.logger.info(f"Finish scanning cluster {hex(clusterId)}")

    '''
    Helper functions
    '''
    def store_scaning_result(self, fname):
        with open(fname, 'w') as f:
            f.write("nEps={},nClusters={},nZCLcmds={},nManucmds={}\n".format(self.target_device.n_eps, self.target_device.n_clusters, self.target_device.n_ZCLcmds, self.target_device.n_manucmds))
            f.write(json.dumps(self.target_device.ZCLcmd_dict))
            f.write('\n')
            f.write(json.dumps(self.target_device.manucmd_dict))
    
    def load_scanning_result(self, fname):
        f = open(fname, 'r')
        zcl_line_waiting = False
        manu_line_waiting = False
        for line in f.readlines():
            line = line.strip()
            if line.startswith('#'): # This is a comment line
                continue
            if line.startswith('nEps'):
                segs = line.split(',')
                self.target_device.n_eps = int(segs[0].split('=')[1])
                self.target_device.n_clusters = int(segs[1].split('=')[1])
                self.target_device.n_ZCLcmds = int(segs[2].split('=')[1])
                self.target_device.n_manucmds = int(segs[3].split('=')[1])
                zcl_line_waiting = True
            elif zcl_line_waiting:
                self.target_device.ZCLcmd_dict = json.loads(line)
                zcl_line_waiting = False
                manu_line_waiting = True
            elif manu_line_waiting:
                self.target_device.manucmd_dict = json.loads(line)
                manu_line_waiting = False

    def configure_poll(self):
        POLL_CONTROL_CLUSTER_ID = 0x20
        target_ep = None
        for ep in self.target_device.active_eps:
            if self.target_device.cluster_lookup(ep, POLL_CONTROL_CLUSTER_ID):
                target_ep = ep
                break
        if target_ep is None:
            self.logger.info("Trying to configure end device poll mechanism, but it seems that the device does not support Poll Control cluster.")
        else:
            # Configure Check-inInterval using WriteAttributes
            self.inject_zcl_cmd(
                self.target_device.nwkAddr, SAMPLEAPP_UNICAST, target_ep, POLL_CONTROL_CLUSTER_ID, 0x0104, 0x2, False, CLIENT_SERVER_DIRECTION,
                0x0, b'\x00\x00\x23\x40\x38')
            # Configure short poll interval
            self.inject_zcl_cmd(
                self.target_device.nwkAddr, SAMPLEAPP_UNICAST, target_ep, POLL_CONTROL_CLUSTER_ID, 0x0104, 0x3, True, CLIENT_SERVER_DIRECTION,
                0x0, b'\x01\x00')
            # Configure long poll interval
            self.inject_zcl_cmd(
                self.target_device.nwkAddr, SAMPLEAPP_UNICAST, target_ep, POLL_CONTROL_CLUSTER_ID, 0x0104, 0x2, True, CLIENT_SERVER_DIRECTION,
                0x0, b'\x02\x00\x00\x00')

    def turn_off(self):
        ep = 0xb
        cid = 0x0006
        pid = ZCL_ZLL_PROFILE_ID
        cmd_id = 0x02
        stat, frame, elapsed_time = self.inject_zcl_cmd(
            self.target_device.nwkAddr, SAMPLEAPP_UNICAST,
            ep, cid, pid, cmd_id, True, CLIENT_SERVER_DIRECTION, 0x0, b''
        )