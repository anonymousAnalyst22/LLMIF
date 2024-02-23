import logging
from collections import defaultdict
from typing import Union
import re
import random
from basic_type import *
from fuzzer_constants import *

def hex_to_int(hexstr):
    answer = int(hexstr, 16)
    return answer


class ZbeeAttribute:

    def __init__(self, attribute_id, attribute_info_dict:Union[None, dict]) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.attribute_id:'int' = hex_to_int(attribute_id) if isinstance(attribute_id, str) else attribute_id
        self.name:'str' = None
        self.type:'str' = None
        self.access:'int' = 0x0
        self.mo:'str' = MO_OPTIONAL
        self.range:'str' = ALL_RANGE
        self.default = ANY_DEFAULT # Read from repo
        self.default_value = None
        if attribute_info_dict is not None:
            self.__parse_attribute_info_dict(attribute_info_dict)
            self.data:'Mutable' = self.create_data_object()
        
        self.enforced_ops = [] # Only used if the attribute is mutated.
    
    def copy(self):
        new_attr = ZbeeAttribute(hex(self.attribute_id), None)
        new_attr.name = self.name
        new_attr.type = self.type
        new_attr.access = self.access
        new_attr.mo = self.mo
        new_attr.range = self.range
        new_attr.default = self.default
        new_attr.data = self.data.copy()
        return new_attr

    def get_byte_number(self):
        return self.data.octets

    def __determine_default_attr_value(self, type_name:'str', default):
        value = None
        assert(type_name.startswith(tuple(DATA_LEGAL_TYPES)))
        if type_name.startswith(tuple(DATA_NUMERIC_TYPES)):
            try:
                value = hex_to_int(default)
            except:
                value = random.randint(0, 255) # For all other values, e.g., '-', 'MS', 'non', we all treat the value as 0.
        elif type_name.startswith(BOOLPREFIX):
            try:
                value = hex_to_int(default)
            except:
                value = 1 # For all other values, e.g., '-', 'MS', 'non', we all treat the value as 1
            value = False if value == 0 else True
        elif type_name.startswith((STRINGPREFIX, OCTSTRINGPREFIX)):
            if default == ANY_DEFAULT:
                value = []
                str_len = random.randint(1, 5)
                value.append(str_len)
                for i in range(str_len):
                    value.append(random.randint(0, 0xff))
            else:
                assert(isinstance(default, list) or isinstance(default, str))
                value = default
        elif type_name.startswith(VARIABLEPREFIX):
            if default == ANY_DEFAULT:
                value = []
                # Randonly generate a bytearray with length in [1,5]
                str_len = random.randint(1, 5)
                for i in range(str_len):
                    value.append(random.randint(0, 0xff))
            else:
                assert(isinstance(default, list) or isinstance(default, str))
                value = default
        elif type_name.startswith(STRUCTPREFIX):
            value = []
            element_str:'str' = re.findall(STRUCT_VALUE_PATTERN, type_name)[0]
            element_types = element_str.split(',')
            for element_type in element_types:
                # For Struct, we do not support complex structures, in particular, struct in struct or array in struct
                assert(element_type.startswith(tuple(DATA_LEGAL_TYPES)) and not element_type.startswith(tuple(EXTENSIBLE_TYPES)))
                element = self.__initialize_basic_data_object(element_type, ANY_DEFAULT)
                value.append(element)
        elif type_name.startswith(ARRAYPREFIX):
            # For Array, we do not support array in array.
            value = []
            element_type:'str' = re.findall(ARRAY_VALUE_PATTERN, type_name)[0]
            assert(element_type.startswith(tuple(DATA_LEGAL_TYPES)) and not element_type.startswith(ARRAYPREFIX))
            element = self.__initialize_data_object(element_type, ANY_DEFAULT)
            value.append(element)
        return value

    def __parse_attribute_info_dict(self, attribute_info_dict):
        """
        Parse and update the following information from the attribute_info_dict (Derived from the repo's command/attribute json file)
        self.name
        self.type
        self.access
        self.mo
        """
        info_keys = list(attribute_info_dict.keys())
        if NAME_KEYWORD in info_keys or DESCRIPTION_KEYWORD in info_keys:
            self.name = attribute_info_dict[NAME_KEYWORD] if NAME_KEYWORD in info_keys \
                    else attribute_info_dict[DESCRIPTION_KEYWORD]
        if TYPE_KEYWORD in info_keys:
            self.type = attribute_info_dict[TYPE_KEYWORD]
            assert(self.type.startswith(tuple(DATA_LEGAL_TYPES)))
        if ACCESS_KEYWORD in info_keys:
            if attribute_info_dict[ACCESS_KEYWORD] == ALL_RANGE:
                self.access = ACCESS_ALL_BITS
            else:
                for access_chr in attribute_info_dict[ACCESS_KEYWORD]:
                    if access_chr in ACCESS_LEGAL_TYPES:
                        self.access |= ACCESS_BIT_DICT[access_chr]
        if MO_KEYWORD in info_keys:
            assert(attribute_info_dict[MO_KEYWORD].lower() in MO_LEGAL_TYPES)
            self.mo = attribute_info_dict[MO_KEYWORD].lower()
        # For Range and Default field, here we only store its string representation. We put its interpretation in later data type construction.
        if RANGE_KEYWORD in info_keys:
            self.range = attribute_info_dict[RANGE_KEYWORD]

        if DEFAULT_KEYWORD in info_keys:
            self.default = attribute_info_dict[DEFAULT_KEYWORD]
            #self.default_value = self.__determine_default_attr_value(self.type, attribute_info_dict[DEFAULT_KEYWORD])
        #else:
        #    self.default_value = self.__determine_default_attr_value(self.type, ANY_DEFAULT)

    def __initialize_data_object(self, type_name:'str', default=ANY_DEFAULT):
        data = None
        if type_name.startswith(tuple(DATA_LEGAL_TYPES)) and not type_name.startswith(tuple(EXTENSIBLE_TYPES)):
            data = self.__initialize_basic_data_object(type_name, default)
        elif type_name.startswith(STRUCTPREFIX):
            default_value = self.__determine_default_attr_value(type_name, ANY_DEFAULT)
            data = ZbeeStruct(value=default_value, type_name=type_name)
        elif type_name.startswith(ARRAYPREFIX):
            default_value = self.__determine_default_attr_value(type_name, ANY_DEFAULT)
            data = ZbeeArray(value=default_value, type_name=type_name)
        else:
            self.logger.error(f"Unknown data type {type_name} for data object initialization.")
            exit(0)
        return data

    def __initialize_basic_data_object(self, type_name:'str', default=ANY_DEFAULT):
        data = None
        assert(type_name.startswith(tuple(DATA_LEGAL_TYPES)) and not type_name.startswith(tuple(EXTENSIBLE_TYPES)))
        default_value = self.__determine_default_attr_value(type_name, default)
        if type_name.startswith(BOOLPREFIX):
            data = ZbeeBool(value=default_value)
        elif type_name.startswith(UINTPREFIX):
            data = ZbeeUInt(value=default_value, type_name=type_name)
        elif type_name.startswith(INTPREFIX):
            data = ZbeeInt(value=default_value, type_name=type_name)
        elif type_name.startswith(EUIPREFIX):
            data = ZbeeEUI(value=default_value)
        elif type_name.startswith(MAPPREFIX):
            data = ZbeeMap(value=default_value, type_name=type_name)
        elif type_name.startswith(ENUMPREFIX):
            data = ZbeeEnum(value=default_value, type_name=type_name)
        elif type_name.startswith(DATAPREFIX):
            data = ZbeeData(value=default_value, type_name=type_name)
        elif type_name.startswith(SINGLEPREFIX):
            data = ZbeeSingle(value=default_value)
        elif type_name.startswith(UTCPREFIX):
            data = ZbeeUTC(value=default_value)
        elif type_name.startswith(KEYPREFIX):
            data = ZbeeKey(value=default_value)
        elif type_name.startswith(STRINGPREFIX):
            data = ZbeeString(value=default_value)
        elif type_name.startswith(OCTSTRINGPREFIX):
            data = ZbeeOctString(value=default_value)
        elif type_name.startswith(VARIABLEPREFIX):
            data = ZbeeVariable(value=default_value)
        else:
            self.logger.error(type_name)
            assert(0)
        return data

    def __parse_range(self):
        """
        This function parses the range object.
        (1) If the range string is not in the format of ['0xa'...'0xb'], we by default regard it [MIN, MAX].
        (2) If the range string is in the format of ['0xa'...'0xb'], we transform it to  [0xa, 0xb].
        (3) If the range string is in the format of ['someName'...'someName'], we automatically transform it to MIN or MAX.
        NOTE: The transformation part loses much semantic information, which can be further investigated.
        """
        range_low = None
        range_high = None
        if self.type.startswith(tuple(DATA_NUMERIC_TYPES)):
            match = re.search(RANGE_VALUE_PATTERN, self.range)
            if match:
                try:
                    range_low = hex_to_int(match.group(1).strip())
                    range_high = hex_to_int(match.group(2).strip())
                except:
                    pass

        return range_low, range_high

    def create_data_object(self):
        """
        This function utilizes the following information to construct a basic data object.
        self.type: Determine the data type.
        self.default: Determine the data's default value
        self.range: Determine the data range.

        (1) Initialize a data object according to self.type
        (2) Set the data object's default value according to self.default
        (3) Update the data object's range property according to self.range
        """
        # (1) Initialize a data object
        data = None
        if self.type is not None:
            data = self.__initialize_data_object(self.type, default=self.default)
            # (3) Set range
            range_low, range_high = self.__parse_range()
            if range_low is not None:
                data.range_low = range_low
            if range_high is not None:
                data.range_high = range_high
        return data

    def __str__(self):
        attr_str = f"ID,name,type,access={hex(self.attribute_id)},{self.name},{self.type},{self.access}\n"
        attr_str += f"              default={self.default}\n"
        attr_str += f"              data={self.data.byte_array}\n"
        return attr_str

class ZbeeCommand:

    def __init__(self, cmd_id, cmd_info_dict:'dict', command_flag) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        # TODO: Parse the cmd_info_dict, and extract info inside to construct the class
        self.cmd_id:'int' = hex_to_int(cmd_id) if isinstance(cmd_id, str) else cmd_id
        self.command_flag = command_flag # See controller_constants.py
        self.clusterSpecific = False if self.command_flag == COMMAND_GENETIC else True

        self.name:'str' = ''
        self.mo:'bool' = False
        self.payloads:'list[ZbeeAttribute]' = []
        self.__parse_cmd_info_dict(cmd_info_dict)
    
    def __str__(self):
        cmd_str = f"cmd_id, cmd_name, command_flag = {hex(self.cmd_id)}, {self.name}, {hex(self.command_flag)}\n"
        for i, payload in enumerate(self.payloads):
            cmd_str += f"    payload {i} info: {payload}\n"
        return cmd_str
    
    def __parse_cmd_info_dict(self, cmd_info_dict:'dict'):
        """
        For format of the cmd_info_dict, please check zcl-cmd.json.
        In particular, this function handles EXPANDING_PARAM_SYMBOL
        TODO: Parse the dict and generate the following field
        (1) self.name
        (2) self.mo
        (3) self.payloads
        """
        if DESCRIPTION_KEYWORD in cmd_info_dict.keys():
            self.name = cmd_info_dict[DESCRIPTION_KEYWORD]
        if MO_KEYWORD in cmd_info_dict.keys():
            self.mo = True if cmd_info_dict[MO_KEYWORD].lower() == MO_MANDATORY else False
        if PAYLOAD_KEYWORD in cmd_info_dict.keys():
            payload_dict = cmd_info_dict[PAYLOAD_KEYWORD]
            expanding_flag = False
            expanding_element_list = []
            param_pos = 0
            for payload_name, payload_info_dict in payload_dict.items():
                if payload_name == EXPANDING_PARAM_SYMBOL:
                    # We assume that when facing "...", its later payloads construct a duplicable, which we can wrap as an array
                    expanding_flag = True
                    continue
                param_default = ANY_DEFAULT if DEFAULT_KEYWORD not in payload_info_dict.keys() else payload_info_dict[DEFAULT_KEYWORD]
                param_info_dict = {
                    NAME_KEYWORD: payload_name,
                    TYPE_KEYWORD: payload_info_dict[TYPE_KEYWORD],
                    MO_KEYWORD: MO_MANDATORY,
                    RANGE_KEYWORD: ALL_RANGE,
                    DEFAULT_KEYWORD: param_default
                }
                param = ZbeeAttribute(hex(param_pos), param_info_dict)
                if not expanding_flag:
                    self.payloads.append(param)
                    param_pos += 1
                else:
                    expanding_element_list.append(param)
            if len(expanding_element_list) > 0:
                # Construct an Array[Struct(...,...,...)] parameter
                expanding_param_type = ''
                if len(expanding_element_list) == 1:
                    expanding_param_type = f"Array[{expanding_element_list[0].type}]"
                else:
                    element_type_names = [x.type for x in expanding_element_list]
                    expanding_param_type = "Array[Struct({})]".format(','.join(element_type_names))
                #print(f"For command {self.name}, the expanding param types are {expanding_param_type}")
                extending_param_info_dict = {
                    NAME_KEYWORD: 'ExpandingParam',
                    TYPE_KEYWORD: expanding_param_type,
                    MO_KEYWORD: MO_OPTIONAL,
                    RANGE_KEYWORD: ALL_RANGE,
                    DEFAULT_KEYWORD: ANY_DEFAULT
                }
                expanding_param = ZbeeAttribute(hex(param_pos), extending_param_info_dict)
                self.payloads.append(expanding_param)
                payload_types = [payload.type for payload in self.payloads]
                #print(f"For command {self.name}, the list of params are {payload_types}")

class ZbeeCluster:

    def __init__(self, cluster_id:'int', manu_specific=False) -> None:
        self.cluster_id = cluster_id
        self.manu_specific = manu_specific
        self.cluster_name = ''
        self.attribute_list:'list[ZbeeAttribute]' = []
        self.command_list:'list[ZbeeCommand]' = []
    
    def attribute_lookup(self, attr_id:'int') -> Union[ZbeeAttribute, None]:
        attr:'ZbeeAttribute' = None
        for recorded_attr in self.attribute_list:
            if recorded_attr.attribute_id == attr_id:
                attr = recorded_attr
                break
        return attr
    
    def add_command(self, command:'ZbeeCommand') -> None:
        self.command_list.append(command)
    
    def add_attribute(self, attribute:'ZbeeAttribute') -> None:
        self.attribute_list.append(attribute)

class ZbeeEndpoint:

    def __init__(self, ep_id:'int', profile_id) -> None:
        self.ep_id = ep_id
        self.profile_id = profile_id
        self.cluster_dict = {} # key: cluster_id, value: ZbeeCluster
    
    def cluster_lookup(self, cluster_id) -> Union[ZbeeCluster, None]:
        return None if cluster_id not in self.cluster_dict.keys() else self.cluster_dict[cluster_id]
    
    def add_cluster(self, cluster:'ZbeeCluster'):
        cluster_id = cluster.cluster_id
        assert(self.cluster_lookup(cluster_id) is None)
        self.cluster_dict[cluster_id] = cluster

class ZigbeeDevice:

    def __init__(self, nwkAddr, nodRelation):
        self.nwkAddr = nwkAddr
        self.nodeRelation = nodRelation
        self.manufacturerCode = 0
        self.active_eps = []
        # Use endpoints as keys
        self.profile_dict = {}
        self.deviceID_dict = {}
        self.cluster_dict = defaultdict(list)
        self.ZCLcmd_dict = defaultdict(list) # key -- '{}:{}:{}'.format(hex(active_ep), hex(profileId), hex(clusterId))  value -- [(cmd_id, stat)]
        self.manucmd_dict = defaultdict(list) # key -- '{}:{}:{}'.format(hex(active_ep), hex(profileId), hex(clusterId))  value -- [(cmd_id, stat)]

        self.endpoint_dict = {} # key: endpoint_id, value: ZbeeEndpoint

        self.signature = None
        self.hash_sig = None

        self.n_eps = 0
        self.n_clusters = 0
        self.n_ZCLcmds = 0
        self.n_manucmds = 0

    def endpoint_lookup(self, ep_id:'int') -> Union[ZbeeEndpoint, None]:
        ep_id = hex_to_int(ep_id) if isinstance(ep_id, str) else ep_id
        return None if ep_id not in self.endpoint_dict.keys() else self.endpoint_dict[ep_id]
    
    def cluster_lookup(self, ep, cid) -> Union[ZbeeCluster, None]:
        ep = hex_to_int(ep) if isinstance(ep, str) else ep
        cid = hex_to_int(cid) if isinstance(cid, str) else cid
        cluster = None
        try:
            cluster = self.endpoint_lookup(ep).cluster_lookup(cid)
        except:
            pass
        return cluster
    
    def attribute_lookup(self, ep:'int', cid:'int', attr_id:'int') -> Union[ZbeeAttribute, None]:
        ep = hex_to_int(ep) if isinstance(ep, str) else ep
        cid = hex_to_int(cid) if isinstance(cid, str) else cid
        attr_id = hex_to_int(attr_id) if isinstance(attr_id, str) else attr_id
        attr = None
        try:
            attr = self.endpoint_lookup(ep).cluster_lookup(cid).attribute_lookup(attr_id)
        except:
            pass
        return attr
    
    def add_endpoint(self, endpoint:ZbeeEndpoint):
        ep_id = endpoint.ep_id
        assert(self.endpoint_lookup(ep_id) is None)
        self.endpoint_dict[ep_id] = endpoint
    
    def list_supported_cmds(self):
        
        cmd_ids = []
        for ep_id, ep_info in self.endpoint_dict.items():
            for cluster_id, cluster_info in ep_info.cluster_dict.items():
                for cmd in cluster_info.command_list:
                    cmd_ids.append((cluster_id, cmd.cmd_id, cmd.cmd_flag))
        return cmd_ids