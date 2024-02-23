import sys
sys.path.insert(0, 'lib')
import random
import time
import math
from typing import Union
import statistics
from zigbee_device import ZigbeeDevice, ZbeeAttribute
from pprint import pprint
from statistics import mean 
from plot import plot_distribution_pie, plot_distribution_hist, plot_rspdistribution_stacked_hist
from zigbee_device import *
from basic_type import *
from controller_constants import *
from fuzzer_constants import *
from collections import defaultdict, Counter
from zbee_controller import ZbeeController

def BIT_FLIP(target:'bytearray', pos:'int'):
    """
    Only used by Mutator
    """
    target[pos >> 3] ^= (128 >> (pos&7))

def BYTE_FLIP(target:'bytearray', pos:'int'):
    target[pos] ^= 0xff

def uint8_normalization(target_val:'int') -> 'int':
    result_val = 0
    if target_val < 0:
        result_val = 0
    elif target_val > 255:
        result_val = 255
    else:
        result_val = target_val
    return result_val

class Mutator():

    """
    This class is responsible for:
      (1) providing mutation operators, and
      (2) selecting appropriate fuzzing strategies.
    NOTE: Each fuzzing operator should record the operation detail into the seed
    """

    def __init__(self):
        pass

    def genetic_function_mutation(self, seed:'Seed', attr_id:int=0, attr_value=None, copy=True):
        """
        This function is used for genetic functions.
        The function updates the "AttributeID" field in these genetic functions with the param attr_id.
        """
        target_seed = seed.copy() if copy else seed # Initialize the fuzzing seed
        selected_attr:list[ZbeeAttribute] = [attr for attr in seed.cluster_attributes if attr.attribute_id == attr_id]
        id_index, original_payload = seed.identify_payload_by_name('AttributeIDi')
        if original_payload is None or len(selected_attr) == 0:
            return target_seed
        # 1. Update the attreibute ID
        selected_attr:ZbeeAttribute = selected_attr[0]
        fuzzing_param_info = {
            DESCRIPTION_KEYWORD: original_payload.name,
            TYPE_KEYWORD: original_payload.type,
            MO_KEYWORD: original_payload.mo,
            RANGE_KEYWORD: original_payload.range,
            DEFAULT_KEYWORD: hex(attr_id)
        }
        fuzzing_attr_payload = ZbeeAttribute(original_payload.attribute_id, fuzzing_param_info)
        target_seed.replace_payload(id_index, fuzzing_attr_payload)
        # 2. Update the Attribute type
        type_index, original_type_payload = seed.identify_payload_by_name('AttrDataTypei')
        if original_type_payload is not None:
            fuzzing_param_info = {
                DESCRIPTION_KEYWORD: original_type_payload.name,
                TYPE_KEYWORD: original_type_payload.type,
                DEFAULT_KEYWORD: hex(selected_attr.data.typecode)
            }
            fuzzing_type_payload = ZbeeAttribute(original_type_payload.attribute_id, fuzzing_param_info)
            target_seed.replace_payload(type_index, fuzzing_type_payload)
        # 3. Update the Attribute Value
        value_index, original_value_payload = seed.identify_payload_by_name('AttrbuteValuei')
        value = attr_value if attr_value is not None else ANY_DEFAULT
        if original_value_payload is not None:
            fuzzing_value_info = {
                DESCRIPTION_KEYWORD: original_value_payload.name,
                TYPE_KEYWORD: CODE_TYPE_TABLE[selected_attr.data.typecode],
                DEFAULT_KEYWORD: value
            }
            fuzzing_value_paylaod = ZbeeAttribute(original_value_payload.attribute_id, fuzzing_value_info)
            target_seed.replace_payload(value_index, fuzzing_value_paylaod)
        return target_seed

    def mutation(self, seed:'Seed'):
        """
        The mutation interface
        """
        pass

    def identify_insensitive_positions(self, payload:'ZbeeAttribute'):
        """
        Given a payload, this function identifies the byte positions which are insensitive to format errors.
        The following cases are format-sensitive.
        (1) String length.
        (2) AttrDataType (Commonly used in genetic functions)
        """
        suitable_positions = [x for x in range(payload.data.octets)]

        if payload.name is not None and 'DataType' in payload.name:
            return []

        if payload.data.type_prefix in STRING_TYPES:
            suitable_positions.remove(0)
        elif payload.data.type_prefix in [STRUCTPREFIX, ARRAYPREFIX]:
            sensitive_poses:'list[int]' = payload.data.identify_sensitive_positions()
            for pos in sensitive_poses:
                suitable_positions.remove(pos)
        
        return suitable_positions

class Seed():

    """
    Semantic meaning of seed: Each seed represents a command template, which includes:
    (1) Endpoint, cluster, and profile information
    (2) Command information, e.g., cmd_id, and
    (3) Detailed payload information, i.e., a list of attributes
    Seed requirement:
    (1) Support copy.
    (2) Support a set of mutation operators.
    """

    def __init__(self, trans_flag, ep, cid, pid, cmd_flag, cmd_id, clusterSpecific, payloads:'list[ZbeeAttribute]', cluster_attributes:'list[ZbeeAttribute]', evolutions:'list[Seed]'=[]) -> None:
        self.trans_flag = trans_flag
        self.ep = ep
        self.cid = cid
        self.pid = pid
        self.cmd_flag = cmd_flag
        self.cmd_id = cmd_id
        self.id = f"{self.ep}:{self.cid}:{self.cmd_id}"
        self.clusterSpecific = clusterSpecific
        self.direction = CLIENT_SERVER_DIRECTION
        self.manuSpecific = False
        self.manuCode = 0x0000
        # NOTE: Since the mutator will mutate the payload_bytearrays not the payloads, eventually payloads will not equal to payload_bytearrays.
        self.payloads:'list[ZbeeAttribute]' = payloads
        self.payload_bytearrays = bytearray()
        self.refresh_byte_array()
        # Some command parameters are attributeIDs, and the cluster_attributes can be used to set interesting values for these params
        # Note that the cluster_attribute is immuatable!
        self.cluster_attributes:'list[ZbeeAttribute]' = cluster_attributes

        # Seed evolutions: Record the list of its ancestor seeds from which it was mutated.
        self.evolutions = evolutions

        # Record the list of mutations ops enforced on the seed
        self.fuzzed = 0
        self.enforced_ops = []

        # Execution metric for seed
        self.execution_time = 1
        self.execStat = 0
        self.rspStat = 0

        # Used to remember the tried attribute IDs for avoiding duplicated int_value_mutation()
        # For used attribute IDs, the dict value is 1; Otherwise 0
        self.tried_attrs = defaultdict(int) # Key - value == AttributeName - ATTR_UNSELECTED/ATTR_SELECTED
    
    def refresh_byte_array(self):
        self.payload_bytearrays = bytearray()
        for payload in self.payloads:
            self.payload_bytearrays += payload.data.byte_array
    
    def payload_alignment_checking(self):
        """
        This function checks the alignment between self.payloads and self.payload_bytearrays.
        (1) Traverse each field, and count whether this field has corresponding payload values which match its length.
        (2) If not matching, count the number of bytes needed for filling the current and the remaining fields.
        (3) Return (1) if every field has been properly filled, and (2) the number of needed bytes.
        """
        SATISFIED = True
        n_payload_bytes = len(self.payload_bytearrays)
        n_consumed_bytes = 0
        n_checked_payloads = 0

        # TODO: For each basic data type, (1) calculate n_minimum_bytes, and (2) assign_bytearray()

        n_needed_bytes = 0
        # For each field, allocate the required number of bytes to it.
        # If the number of remaining bytes is not enough, SATISFIED is set to FALSE.
        for payload in self.payloads:
            n_checked_payloads += 1
            n_required_bytes = payload.data.n_minimum_bytes
            if SATISFIED == False:
                n_needed_bytes += n_required_bytes
            elif payload.data.type_prefix not in [STRINGPREFIX, OCTSTRINGPREFIX]:
                if n_consumed_bytes + n_required_bytes > n_payload_bytes: # IF the remaining byte can satisfy the required number of bytes
                    SATISFIED = False
                    n_needed_bytes += (n_consumed_bytes + n_required_bytes) - n_payload_bytes # It cannot satisfy the requirement.
                else:
                    n_consumed_bytes += n_required_bytes
            else:
                # If all bytes are consumed, just return
                if n_consumed_bytes == n_payload_bytes:
                    SATISFIED = False
                    n_needed_bytes += n_required_bytes
                else:
                    # If there are remaining bytes, first check if the randomly generated array is ok.
                    # If not, allocate a small-length array
                    n_required_bytes = self.payload_bytearrays[n_consumed_bytes] # The first byte of the string specified the number of required bytes
                    if (n_consumed_bytes + 1 + n_required_bytes) > n_payload_bytes:
                        n_remaining_bytes = n_payload_bytes - n_consumed_bytes
                        if n_remaining_bytes == 1:
                            self.payload_bytearrays[-1] = b'\x00'
                            n_consumed_bytes += 1
                        elif n_remaining_bytes > 1:
                            random_array_length = random.randint(1, n_remaining_bytes-1)
                            self.payload_bytearrays[n_consumed_bytes] = random_array_length # Update the random string length
                            n_consumed_bytes = n_consumed_bytes + 1 + random_array_length
                    else:
                        n_consumed_bytes = n_consumed_bytes + 1 + n_required_bytes
            # If the final field is a struct/array, make sure that all the remaining bytes should be dividied by its n_minimum_bytes,
            # and all remaining bytes should be allocated to it.
            if n_checked_payloads == len(self.payloads) and payload.type_prefix in [ARRAYPREFIX, STRUCTPREFIX] and SATISFIED == True:
                n_remaining_bytes = n_payload_bytes - n_consumed_bytes
                if n_remaining_bytes % n_required_bytes == 0:
                    pass
                else:
                    SATISFIED = False
                    n_needed_bytes = n_required_bytes - (n_remaining_bytes%n_required_bytes)

        return SATISFIED, n_needed_bytes
    
    def copy(self):
        # Copy payloads
        new_payloads = [x.copy() for x in self.payloads]
        new_seed = Seed(self.trans_flag, self.ep, self.cid, self.pid,
                    self.cmd_flag, self.cmd_id, self.clusterSpecific,
                    new_payloads, self.cluster_attributes, [x for x in self.evolutions])
        new_seed.manuSpecific = self.manuSpecific
        new_seed.manuCode = self.manuCode
        for enforced_op in self.enforced_ops:
            new_seed.enforced_ops.append(enforced_op)
        return new_seed
    
    def identify_payload_by_name(self, payload_name) -> tuple:
        identified_index:'int' = None
        identified_payload:'ZbeeAttribute' = None
        for index, payload in enumerate(self.payloads):
            if payload.name == payload_name:
                identified_index = index
                identified_payload = payload
                break
        return (None, None) if identified_payload is None else (identified_index, identified_payload)
    
    def replace_payload(self, index, new_payload):
        self.payloads[index] = new_payload
        payload_bytearray = bytearray()
        for payload in self.payloads:
            payload_bytearray += payload.data.byte_array
        self.payload_bytearrays = payload_bytearray

    def __str__(self):
        seed_str = f"(1) ep,pid,cid,cmd_id,cmd_flag,clusterSpecific={hex(self.ep)},{hex(self.pid)},{hex(self.cid)},{hex(self.cmd_id)},{hex(self.cmd_flag)},{self.clusterSpecific}\n"
        seed_str += f"(2) Payload array: {self.payload_bytearrays}\n"
        for i, payload in enumerate(self.payloads):
            seed_str += f"  The {i}th payload: {payload.name}, {payload.type}, {payload.data.octets}, {payload.data.byte_array}\n"
        seed_str += f"(3) Enforced ops: {self.enforced_ops}\n"
        seed_str += f"(4) Direction: {self.direction}, clusterSpecific:{self.clusterSpecific}, manuSpecific: {self.manuSpecific}, manuCode: {self.manuCode}\n"
        seed_str += f"(5) Execution info: execStat={hex(self.execStat)}, rspStat={hex(self.rspStat)}, execTime={self.execution_time}\n"
        return seed_str

    def identify_sensitive_positions(self):
        """
        Report the byte positions which represents string lengths
        """
        sensitive_pos = []
        cur_pos = 0
        for payload in self.payloads:
            if payload.data.type_prefix in [ARRAYPREFIX, STRUCTPREFIX, OCTSTRINGPREFIX, STRINGPREFIX]:
                sensitive_pos += [cur_pos + x for x in payload.data.identify_sensitive_positions()]
            cur_pos += payload.data.octets
        return sensitive_pos

class SeedPool():

    def __init__(self, target_device:'ZigbeeDevice', flag=''):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.flag = flag
        self.pool:'list[Seed]' = self.__initialize_seed_pool(target_device)
        self.n_seeds = len(self.pool)

    def __initialize_seed_pool(self, target_device:'ZigbeeDevice'):
        """
        Each seed is derived from a Zigbee command.
        However, the seed should satisfy the following goals.
        (1) The selected Zigbee command should satisfy the pool domain (specified by pool name)
        (2) The seed structure should be asily mapped to inject_zcl_cmd API.

        Extract genetic seed info for command injection: flag, ep_id, cluster_id, profile_id
        """
        pool = []
        for ep_id, endpoint in target_device.endpoint_dict.items():
            profile_id = endpoint.profile_id
            for cluster_id, cluster in endpoint.cluster_dict.items():
                # Only select commands which satisfy self.flag (command type)
                command_list:'list[ZbeeCommand]' = [cmd for cmd in cluster.command_list if cmd.command_flag == self.flag]
                for cmd in command_list:
                    copied_payloads:'list[ZbeeAttribute]' = []
                    for payload in cmd.payloads:
                        copied_payload = payload.copy()
                        copied_payloads.append(copied_payload)
                    cmd_seed = Seed(SAMPLEAPP_UNICAST, ep_id, cluster_id, profile_id, cmd.command_flag, cmd.cmd_id, cmd.clusterSpecific, copied_payloads, cluster.attribute_list)
                    cmd_seed.manuSpecific = True if cmd.command_flag == COMMAND_MANU else False
                    cmd_seed.manuCode = target_device.manufacturerCode if cmd.command_flag == COMMAND_MANU else NO_MANUCODE
                    if VERBOSE:
                        self.logger.info(f"Initialize seed: \n{cmd_seed}")
                    pool.append(cmd_seed)
        return pool

    def add_seed(self, seed:'Seed'):
        self.pool.append(seed)

    def del_seed(self, cid=None, cmd_id=None):
        self.pool = [seed for seed in self.pool if seed.cid != cid and seed.cmd_id != cmd_id]

    def prioritize_seeds(self):
        pass

    def lookup_seed(self, cid, cmd_id):
        target_seed = None
        try:
            target_seed = [seed for seed in self.pool if seed.cid == cid and seed.cmd_id == cmd_id][0]
        except:
            pass
        return target_seed

    def lookup_seed_by_cid(self, cid):
        target_seeds = [seed for seed in self.pool if seed.cid == cid]
        return target_seeds

    def filter_seeds(self, untested_cluster_ids=[]):
        self.pool = [seed for seed in self.pool if seed.cid not in untested_cluster_ids]

class Fuzzer():

    def __init__(self, controller:'ZbeeController') -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.controller = controller
        self.target_device = self.controller.target_device
        self.base_mutator = Mutator()

        self.genetic_seed_pool = SeedPool(self.target_device, COMMAND_GENETIC)
        self.zcl_seed_pool = SeedPool(self.target_device, COMMAND_ZCL)
        self.manu_seed_pool = SeedPool(self.target_device, COMMAND_MANU)
        self.missed_attrs = []

    def attribute_mo_checking(self):
        """
        TODO: Since the replace_attr_mutation() function has been changed, this function needs to be updated.
        """
        self.logger.info("Initiate attribute mo checking ......")
        candidate_read_seeds:'list[Seed]' = [seed for seed in self.genetic_seed_pool.pool if seed.cmd_id == GENETIC_READ_REQUEST]
        for template_seed in candidate_read_seeds:
            copied_template_seed = template_seed.copy()
            mutated_seed:'Seed' = self.base_mutator.replace_attrid_mutation(copied_template_seed, True) # Each mutation means to determine a specific attribute for testing
            while mutated_seed is not None:
                _, id_payload = mutated_seed.identify_payload_by_name('AttributeIDi')
                attr_key = (mutated_seed.ep, mutated_seed.cid, hex_to_int(id_payload.default))
                # Inject the command bytearray, and collect the response
                stat, rspStat, elapsed_time = self.execute_seed(mutated_seed)
                if rspStat == ZCL_STATUS_UNSUPPORTED_ATTRIBUTE:
                    self.missed_attrs.append(attr_key)
                mutated_seed:'Seed' = self.base_mutator.replace_attrid_mutation(copied_template_seed, True) # Each mutation means to determine a specific attribute for testing
        for (ep, cid, missing_attr_id) in self.missed_attrs:
            recorded_attr = self.target_device.attribute_lookup(ep, cid, missing_attr_id) # It must exist in the repo
            #self.logger.info(self.target_device.endpoint_lookup(ep).cluster_lookup(cid).attribute_lookup(missing_attr_id))
            #self.logger.info(self.target_device.endpoint_lookup(ep).cluster_lookup(cid).attribute_lookup(hex_to_int(missing_attr_id)))
            if recorded_attr.mo.lower() == MO_MANDATORY:
                self.logger.warning(f"Missing mandatory attribute {hex(missing_attr_id)} for ep={hex(ep)}, cid={hex(cid)}")
        self.logger.info("Attribute mo checking ...... Done")

    def attribute_ac_checking(self, ac_type=ACCESS_READ_BIT):
        """
        TODO: Since the replace_attr_mutation() function has been changed, this function needs to be updated.
        """
        # 1. Generate candidate seeds which can be used for access-control inferrence.
        # Each seed represents a read/write/configure command template for a specific endpoint:cluster
        self.logger.info("Initiate attribute ac checking ......")
        assert(ac_type in [ACCESS_READ_BIT, ACCESS_WRITE_BIT, ACCESS_REPORT_BIT])
        candidate_seed_type = None
        if ac_type == ACCESS_READ_BIT:
            candidate_seed_type = GENETIC_READ_REQUEST
        else:
            candidate_seed_type = GENETIC_WRITE_REQUEST if ac_type == ACCESS_WRITE_BIT else GENETIC_CONFIGURE_REPORT
        candidate_seeds:'list[Seed]' = [seed for seed in self.genetic_seed_pool.pool if seed.cmd_id == candidate_seed_type]
        # 2. Mutate these seeds for probing each attributes, and store the probing access-control result into the dict
        probing_ac_dict = {} # The probing ac dict. Key: tuple (ep, cluster_id, attribute_id). Value: access-control values
        for template_seed in candidate_seeds:
            copied_template_seed = template_seed.copy()
            mutated_seed:'Seed' = self.base_mutator.replace_attrid_mutation(copied_template_seed, True) # Each mutation means to determine a specific attribute for testing
            while mutated_seed is not None:
                # Create the entry in the probing_ac_dict
                _, id_payload = mutated_seed.identify_payload_by_name('AttributeIDi')
                attr_key = (mutated_seed.ep, mutated_seed.cid, hex_to_int(id_payload.default))
                # If the currently probing attr is not supported by devices (identified by attribute_mo_checking()), just the ac probing for it.
                if attr_key in self.missed_attrs:
                    mutated_seed = self.base_mutator.replace_attrid_mutation(copied_template_seed, True) # Each mutation means to determine a specific attribute for testing
                    continue
                probing_ac_dict[attr_key] = 0 if attr_key not in probing_ac_dict.keys() else probing_ac_dict[attr_key]
                # Update the potential DataTypeField, which applies for commands like WriteRequest
                self.base_mutator.set_benign_type_mutation(mutated_seed, False)
                # Inject the command bytearray, and collect the response
                stat, rspStat, elapsed_time = self.execute_seed(mutated_seed)
                # Potential response status codes for Read Attribute Request [SUCCESS, UNSUPPORTED_ATTRIBUTE]
                # Potential response status codes for Write Attribute Request [SUCCESS, UNSUPPORTED_ATTRIBUTE, NOT_AUTHORIZED, READ_ONLY, INVALID_VALUE, INVALID_DATA_TYPE]
                # Potential response status codes for Configure Reporting [SUCCESS, UNSUPPORTED_ATTRIBUTE, UNREPORTABLE_ATTRIBUTE, INVALID_DATA_TYPE, INVALID_VALUE]
                # The probing logic should follow the command processing logic specified in ZCL specification, e.g., Section 2.5.3.3 and Section 2.5.7.3
                if mutated_seed.cmd_id == GENETIC_READ_REQUEST and rspStat == SUCCESS:
                    probing_ac_dict[attr_key] = probing_ac_dict[attr_key] | ACCESS_READ_BIT
                elif mutated_seed.cmd_id == GENETIC_WRITE_REQUEST and rspStat not in [ZCL_STATUS_NOT_AUTHORIZED, ZCL_STATUS_READ_ONLY, ZCL_STATUS_INVALID_DATA_TYPE]:
                    probing_ac_dict[attr_key] = probing_ac_dict[attr_key] | ACCESS_WRITE_BIT
                    if rspStat == ZCL_STATUS_INVALID_DATA_TYPE:
                        self.logger.warning(f"Type mismatch when probing with Write Request: Cluster {mutated_seed.cid} Attribute {id_payload.default}")
                elif mutated_seed.cmd_id == GENETIC_CONFIGURE_REPORT and rspStat not in [ZCL_STATUS_UNSUP_GENERAL_COMMAND, ZCL_STATUS_UNSUPPORTED_ATTRIBUTE, ZCL_STATUS_UNREPORTABLE_ATTRIBUTE]:
                    probing_ac_dict[attr_key] = probing_ac_dict[attr_key] | ACCESS_REPORT_BIT
                if rspStat == ZCL_STATUS_INSUFFICIENT_SPACE:
                    self.logger.warning(f"Attribute AC Checking: Device memory-full detected.")
                mutated_seed:'Seed' = self.base_mutator.replace_attrid_mutation(copied_template_seed, True)
        # 4. Compare probing_ac_dict with each attributes' AC property to see
        # (1) if some access control bits in probing_ac_dict are missing, and
        # (2) if some access control bits are not required by the specification.
        for (ep, cid, attr_id), probing_ac in probing_ac_dict.items():
            recored_attr = self.target_device.attribute_lookup(ep, cid, attr_id)
            diff_ac = probing_ac ^ recored_attr.access
            ac_issue = ""
            if (diff_ac & ACCESS_READ_BIT) > 0 and ac_type == ACCESS_READ_BIT:
                read_issue = "Missing Read Access," if (recored_attr.access & ACCESS_READ_BIT) > 0 else "Unreqirued Read Access,"
                ac_issue += read_issue
            if (diff_ac & ACCESS_WRITE_BIT) > 0 and ac_type == ACCESS_WRITE_BIT:
                write_issue = "Missing Write Access," if (recored_attr.access & ACCESS_WRITE_BIT) > 0 else "Unreqirued Write Access,"
                ac_issue += write_issue
            if (diff_ac & ACCESS_REPORT_BIT) > 0 and ac_type == ACCESS_REPORT_BIT:
                report_issue = "Missing Report Access" if (recored_attr.access & ACCESS_REPORT_BIT) > 0 else "Unreqirued Report Access"
                ac_issue += report_issue
            if ac_issue != "":
                self.logger.warning(f"{ac_issue} for ep={hex(ep)}, cid={hex(cid)}, attribute={hex(attr_id)}")
        self.logger.info("Initiate attribute ac checking ...... Done")

    def command_conformance_checking(self):
        """
        This function is responsible for checking the initial seed usage.
        Since the initial seeds are directly derived from specification/open-source library, any failed execution of these seeds imply that the target device does not follow the specification/library.
        Note that for genetic seeds, we have tested them during the attribute mo/ac checking process. So here we will skip them, and directly focus on ZCL + Manu commands.
        """

        self.logger.info("Initiate function conformance checking ......")
        n_params = []
        n_consistent = 0
        n_inconsistent = 0
        del_seeds = []
        for zcl_seed in self.zcl_seed_pool.pool:
            if (zcl_seed.cid, zcl_seed.cmd_id) in GLOBAL_SKIPPED_CMDS:
                continue
            n_param = len(zcl_seed.payloads)
            self.execute_seed(zcl_seed)
            if zcl_seed.rspStat != SUCCESS:
                self.logger.warning(f"Suspicious inconsistent ZCL comamnd: execStat={hex(zcl_seed.execStat)}, rspStat={hex(zcl_seed.rspStat)}, execTime={hex(zcl_seed.execution_time)}.\n{zcl_seed}")
                n_inconsistent += 1
                del_seeds.append((zcl_seed.cid, zcl_seed.cmd_id))
            else:
                n_consistent += 1
                n_params.append(n_param)
        self.logger.info(f"# consistent commands, # inconsistent commands, average # params for consistent commands: {n_consistent}, {n_inconsistent}, {round(statistics.mean(n_params), 2)}")
        self.logger.info("Function conformance checking ...... Done")

    def execute_seed(self, seed:'Seed', assemble=False, monitor_response=True):
        """
        This function is responsbile for:
        (1) Transform the seed into ZCL commands,
        (2) Use coordinator to inject the command, and
        (3) Update the seed's execution information
        """
        manuCode = seed.manuCode if seed.manuSpecific else NO_MANUCODE
        executed_array = bytearray()
        if assemble is False:
            executed_array = seed.payload_bytearrays
        else:
            for payload in seed.payloads:
                executed_array += payload.data.byte_array
        stat, rsp_frame, elapsed_time = self.controller.inject_zcl_cmd(
            self.target_device.nwkAddr, seed.trans_flag,
            seed.ep, seed.cid,
            seed.pid, seed.cmd_id, seed.clusterSpecific, seed.direction,
            manuCode, bytes(executed_array),
            monitor_response=monitor_response
        )
        seed.execStat = stat
        seed.execution_time = elapsed_time
        if VERBOSE:
            self.logger.info(f"Finish execution of seed with information:\n{seed}")
        return stat, rsp_frame, elapsed_time

    def calculate_distribution(self, measurements: 'dict[list[int]]'):
        result_dist:'dict[list[tuple]]'= {}
        for template_id, rspCodes in measurements.items():
            code_counts = Counter(rspCodes)
            total_codes = len(rspCodes)
            code_dis = [(hex(code), round(code_count*1./total_codes,2)) for code, code_count in code_counts.items()]
            code_dis.sort(key=lambda x:x[1],reverse=True)
            result_dist[template_id] = code_dis
        return result_dist