import logging
import matplotlib.pyplot as plt
import shutil
import subprocess
import sys
import json
import os
from ast import literal_eval
from pprint import pprint, pformat
from collections import defaultdict, Counter
sys.path.insert(0, 'lib')
sys.path.insert(0, 'spec')
sys.path.insert(0, 'simulation')
from lib.fuzzer import *
from functools import reduce
from spec.libs.process_pdf import text_purify
from spec.libs.poe import get_final_poe_response, select_most_frequent_answer
from lib.zigbee_device import ZbeeAttribute
from simulation.coverage import Coverage
from lib.prompts import *
import traceback

import asyncio

INTERESTING_FIELD_VALUE = 0x1
INTERESTING_ATTR_VALUE = 0x2
FLIP_HEADER_BITS = 0x3
MUTATE_MANU_CODE = 0x4
MUTATE_CMD_ID = 0x5
RESPONSE_EXTRACTION = 0x6
FIELD_DUPLICATION = 0x7
FIELD_DELETION = 0x8
MUTATION_EXTREME_VALUE = 0x9

proj_dir = os.getcwd()
result_dir = proj_dir + '\\simulation\\Debug\\Result\\'
coverage_dir = proj_dir + '\\simulation\\Debug\\Coverage\\'
cfg_dir = proj_dir + '\\simulation\\offline_parser\\cfg\\'
CMD = 'C:\\\\Windows\\\\System32\\\\cmd.exe'
CSPY_SCRIPT = proj_dir + '\\simulation\\ZStackExecute.bat'
EXEC_RESULT_FILE = result_dir + 'result.txt'

spec_cmd_repo = json.load(open('spec/analysis_result/zcl-cmd.json', 'r'))

def purify_string(target_str:str):
    return target_str.strip().replace(' ', '').replace('/', '').lower()

class SpecSearcher():

    def __init__(self) -> None:
        self.cluster_index_dict = {}
        self.cmd_index_dict = {}
        self.cmd_description_dict = {}
        self.__load_spec_contents()
        # From scapy get the response status code table: https://github.com/secdev/scapy/blob/master/scapy/layers/zigbee.py#L639-L722
        self.response_status_dict = {
            0x00: "SUCCESS",
            0x01: "FAILURE",
            # 0x02 - 0x7d Reserved
            0x7e: "NOT_AUTHORIZED",
            0x7f: "RESERVED_FIELD_NOT_ZERO",
            0x80: "MALFORMED_COMMAND",
            0x81: "UNSUP_CLUSTER_COMMAND",
            0x82: "UNSUP_GENERAL_COMMAND",
            0x83: "UNSUP_MANUF_CLUSTER_COMMAND",
            0x84: "UNSUP_MANUF_GENERAL_COMMAND",
            0x85: "INVALID_FIELD",
            0x86: "UNSUPPORTED_ATTRIBUTE",
            0x87: "INVALID_VALUE",
            0x88: "READ_ONLY",
            0x89: "INSUFFICIENT_SPACE",
            0x8a: "DUPLICATE_EXISTS",
            0x8b: "NOT_FOUND",
            0x8c: "UNREPORTABLE_ATTRIBUTE",
            0x8d: "INVALID_DATA_TYPE",
            0x8e: "INVALID_SELECTOR",
            0x8f: "WRITE_ONLY",
            0x90: "INCONSISTENT_STARTUP_STATE",
            0x91: "DEFINED_OUT_OF_BAND",
            0x92: "INCONSISTENT",
            0x93: "ACTION_DENIED",
            0x94: "TIMEOUT",
            0x95: "ABORT",
            0x96: "INVALID_IMAGE",
            0x97: "WAIT_FOR_DATA",
            0x98: "NO_IMAGE_AVAILABLE",
            0x99: "REQUIRE_MORE_IMAGE",
            0x9a: "NOTIFICATION_PENDING",
            # 0x9b - 0xbf Reserved
            0xc0: "HARDWARE_FAILURE",
            0xc1: "SOFTWARE_FAILURE",
            0xc2: "CALIBRATION_ERROR",
            0xc3: "UNSUPPORTED_CLUSTER",
            # 0xc4 - 0xff Reserved
        }
    
    def __load_spec_contents(self):
        with open('spec/docs/cluster-index.json', 'r') as fp:
            cluster_index_dict = json.load(fp)
            self.cluster_index_dict = {int(k):v for k, v in cluster_index_dict.items()}
        with open('spec/docs/cmd-index.json', 'r') as fp:
            cmd_index_dict = json.load(fp)
            for clsuter_index, cmd_info in cmd_index_dict.items():
                self.cmd_index_dict[int(clsuter_index)] = {}
                for cmd_index, cmd_name in cmd_info.items():
                    self.cmd_index_dict[int(clsuter_index)][int(cmd_index)] = cmd_name
        with open('spec/docs/cmd-description.json', 'r') as fp:
            cmd_description_dict = json.load(fp)
            for clsuter_index, cmd_info in cmd_description_dict.items():
                self.cmd_description_dict[int(clsuter_index)] = {}
                for cmd_index, cmd_name in cmd_info.items():
                    self.cmd_description_dict[int(clsuter_index)][int(cmd_index)] = cmd_name
    
    def search_cluster_name(self, cid):
        return self.cluster_index_dict[cid] if cid in self.cluster_index_dict.keys() else None

    def search_cmd_name(self, cid, cmd_id):
        return self.cmd_index_dict[cid][cmd_id] if cid in self.cmd_index_dict.keys() and \
                                        cmd_id in self.cmd_index_dict[cid].keys() else None
    
    def search_cmd_description(self, cid, cmd_id):
        return self.cmd_description_dict[cid][cmd_id] if cid in self.cmd_description_dict.keys() and \
                                        cmd_id in self.cmd_description_dict[cid].keys() else None

class SpecMutator(Mutator):
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.spec_analysis_path = 'spec/inter_result/'
        self.name = SPEC
        self.payload_mutation_ops = {
            MUTATION_EXTREME_VALUE: self.extreme_field_value,
            MUTATION_STRING_EXPAND: self.string_expand_mutation,
            MUTATION_VARIABLE_EXPAND: self.variable_expand_mutation,
        }
        self.attribute_mutation_ops = {
            INTERESTING_ATTR_VALUE: self.interesting_attr_value
        }
        self.header_mutation_ops = {
            FLIP_HEADER_BITS: self.flip_header_bits,
            MUTATE_MANU_CODE: self.mutate_manu_code,
            MUTATE_CMD_ID: self.mutate_cmd_id,
        }
        self.disturbing_mutation_ops = {
            DELETE_BYTE_MUTATION: self.delbyte_mutation,
            STRING_INC_MUTATION: self.string_length_inc_mutation,
            STRING_DEC_MUTATION: self.string_length_dec_mutation
        }
        #self.constraint_dict = self.field_constraint_collection()
        self.constraint_dict = self.field_valid_range_collection()
        self.interesting_value_dict = self.field_interesting_value_collection()
        self.n_set_invalid_range_fields = 0
        self.n_set_semantic_fields = 0
    
    """
    Operators for initial seed generation
    """
    def set_field_value_from_invalid_range(self, seed:'Seed', copy=True):
        """
        Replace the seed's field value with interesting valeu identified from the spec.
        """
        target_seed:'Seed' = seed.copy() if copy else seed
        if  target_seed.cmd_flag == COMMAND_ZCL and\
            target_seed.cid in self.constraint_dict.keys() and \
            target_seed.cmd_id in self.constraint_dict[target_seed.cid].keys():
            cmd_constraints:dict = self.constraint_dict[target_seed.cid][target_seed.cmd_id]
            # Given the command, identify the candidate fields which have cosntraints specified in the spec
            candidate_fields = [x for x in cmd_constraints.keys() if \
                                cmd_constraints[x]['isField'] == 1 and len(cmd_constraints[x]['bounds']) > 0]
            if len(candidate_fields) > 0:
                # 1. Randomly select a field
                mutated_field = random.sample(candidate_fields, 1)[0]
                # 2. Search from the seed payload to identify the corresponding payload field
                payload_fields:ZbeeAttribute = [x for x in target_seed.payloads if purify_string(x.name) == purify_string(mutated_field)]
                if len(payload_fields) > 0:
                    payload_field = payload_fields[0]
                    # 3. Identify the domain of the field
                    domain_low = payload_field.data.range_low
                    domain_high = payload_field.data.range_high
                    # 4. Randomly select a value range regulated by the spec
                    selected_range_low, selected_range_high = random.sample(cmd_constraints[mutated_field]['bounds'], 1)[0]
                    # 5. Determine if flipping the range to generate values against the specification: 80% flip
                    mutation_ranges = []
                    flip = random.choices([True, False], k=1, weights=[4, 1])[0]
                    if flip:
                        if selected_range_low >= domain_low:
                            mutation_ranges.append((domain_low, selected_range_low))
                        if domain_high >= selected_range_high:
                            mutation_ranges.append((selected_range_high, domain_high))
                    else:
                        if selected_range_high >= selected_range_low:
                            mutation_ranges.append((selected_range_low, selected_range_high))
                    # 6. Randomly generate a field value
                    selected_mutation_range_low, selected_mutation_range_high = random.choice(mutation_ranges)
                    mutated_field_value = random.randint(selected_mutation_range_low, selected_mutation_range_high)
                    # 7 Update the seed with the selected field value
                    payload_field.data.assign(mutated_field_value)
                    target_seed.enforced_ops.append(('Invalid Field Range', flip, payload_field.name, (selected_mutation_range_low, selected_mutation_range_high), mutated_field_value))
                    payload_field.enforced_ops.append(('Invalid Field Range', flip, payload_field.name, (selected_mutation_range_low, selected_mutation_range_high), mutated_field_value))
                    self.n_set_invalid_range_fields += 1
            target_seed.refresh_byte_array()
        elif target_seed.cmd_flag == COMMAND_GENETIC and len(target_seed.cluster_attributes) > 0:
            # If the command is a genetic command, just set the real attributeID to set attribute ID field. 
            # For the attribute values, we temporally set it as random.
            selected_attr = random.choice(target_seed.cluster_attributes)
            target_seed:'Seed' = self.genetic_function_mutation(target_seed, selected_attr.attribute_id)
        return target_seed
    
    def set_field_value_from_semantic_value(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        if  target_seed.cmd_flag == COMMAND_ZCL and\
            target_seed.cid in self.interesting_value_dict.keys() and \
            target_seed.cmd_id in self.interesting_value_dict[target_seed.cid].keys():
                interesting_fields = self.interesting_value_dict[target_seed.cid][target_seed.cmd_id]
                # Field names recorded in the interesting value file
                candidate_fields = [x for x in interesting_fields.keys() if len(interesting_fields[x]) > 0]
                purified_candidate_field_names = [purify_string(x) for x in candidate_fields]
                # Identified payload fields whose name is in the interesting value file and the data type is numeric
                candidate_payload_fields = [x for x in target_seed.payloads if purify_string(x.name) in purified_candidate_field_names and x.data.type_prefix in DATA_NUMERIC_TYPES]
                if len(candidate_payload_fields) > 0:
                    payload_field = random.choice(candidate_payload_fields)
                    paylaod_field_name = [x for x in candidate_fields if purify_string(x) == purify_string(payload_field.name)][0]
                    # Identify the interesting values for the field
                    interesting_field_value = random.choice(interesting_fields[paylaod_field_name])
                    payload_field.data.assign(interesting_field_value)
                    target_seed.enforced_ops.append(('Semantic Field Value', payload_field.name, hex(interesting_field_value)))
                    payload_field.enforced_ops.append(('Semantic Field Value', payload_field.name, hex(interesting_field_value)))
                    self.n_set_semantic_fields += 1
                    #mutated_field = random.sample(candidate_fields, 1)[0]
                    #payload_fields:ZbeeAttribute = [x for x in target_seed.payloads if purify_string(x.name) == purify_string(mutated_field)]
                    #if len(payload_fields) > 0 and payload_fields[0].data.type_prefix in DATA_NUMERIC_TYPES:
                    #    payload_field = payload_fields[0]
                    #    interesting_field_value = random.choice(interesting_fields[mutated_field])
                    #    payload_field.data.assign(interesting_field_value)
                    #    target_seed.enforced_ops.append(('Semantic Field Value', payload_field.name, hex(interesting_field_value)))
                    #    payload_field.enforced_ops.append(('Semantic Field Value', payload_field.name, hex(interesting_field_value)))
                target_seed.refresh_byte_array()
        elif target_seed.cmd_flag == COMMAND_GENETIC and len(target_seed.cluster_attributes) > 0:
            # If the command is a genetic command, just set the real attributeID to set attribute ID field. 
            # For the attribute values, we temporally set it as random.
            selected_attr = random.choice(target_seed.cluster_attributes)
            target_seed:'Seed' = self.genetic_function_mutation(target_seed, selected_attr.attribute_id)
        return target_seed

    def field_duplication(self, seed:'Seed', last_seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        type_matched_fields = [(seed_field, last_seed_field) 
                        for seed_field in target_seed.payloads for last_seed_field in last_seed.payloads
                        if seed_field.type == last_seed_field.type]
        if len(type_matched_fields) > 0:
            selected_seed_field, selected_last_field = random.sample(type_matched_fields, 1)[0]
            selected_seed_field.data.assign(selected_last_field.data.value)
            target_seed.refresh_byte_array()
            target_seed.enforced_ops.append((FIELD_DUPLICATION, selected_seed_field.name, selected_last_field.name, selected_seed_field.data.byte_array))
        return target_seed

    def response_extraction(self, seed:'Seed', response_bytes:'bytes', copy=True):
        """
        Randomly select a field from the current seed, and use the bytes from the response_bytes as the field value
        """
        target_seed:'Seed' = seed.copy() if copy else seed
        n_response_bytes = len(response_bytes)
        numerical_type_fields = [field for field in seed.payloads if field.type.startswith(tuple(DATA_NUMERIC_TYPES))]
        # This operator only applies for numerical fields, e.g., with type uint16 or map8.
        if len(numerical_type_fields) > 0 and n_response_bytes > 0:
            # If the number of response bytes is large enough to cover the selcted field, randomly sample continous bytes as the field value.
            selected_field = random.sample(numerical_type_fields, 1)[0]
            n_required_bytes = selected_field.data.octets
            if n_response_bytes >= n_required_bytes:
                start_pos = random.sample(list(range(0, n_response_bytes-n_required_bytes+1)), 1)[0]
                cutoff_bytes = response_bytes[start_pos:start_pos+n_required_bytes-1]
                selected_field.data.assign(int.from_bytes(bytes(cutoff_bytes), byteorder=DEFAULT_ENDIAN))
            # Else, use the whole response bytes as the field value
            else:
                selected_field.data.assign(int.from_bytes(bytes(response_bytes), byteorder=DEFAULT_ENDIAN))
            target_seed.refresh_byte_array()
            target_seed.enforced_ops.append(('ResponseExtraction', selected_field.name, selected_field.data.byte_array))
        return target_seed

    """
    Payload mutation operators
    """

    def determine_available_payload_mutation_ops(self, cmd:'Seed'):
        available_ops = list(self.payload_mutation_ops.keys())
        # Check if the cluster command has identified interesting attributes
        string_fields = [field for field in cmd.payloads if field.data.type_prefix in STRING_TYPES]
        if len(string_fields) == 0:
            available_ops.remove(MUTATION_STRING_EXPAND)
        variable_fields = [field for field in cmd.payloads if field.data.type_prefix == VARIABLEPREFIX]
        if len(variable_fields) == 0:
            available_ops.remove(MUTATION_VARIABLE_EXPAND)
        return available_ops

    def field_interesting_value_collection(self):
        value_dict = {}
        value_file = f"spec/analysis_result/field_int_values_summary.json"
        n_constraint_cmds = 0
        n_constraint_fields = 0
        n_constraint_values = 0
        with open(value_file, 'r') as fp:
            summary_dict = json.load(fp)
            for cluster_name, cluster_info in summary_dict.items():
                cluster_id = [(k, int(k, 16)) for k, v in spec_cmd_repo.items() if purify_string(v['name']) == purify_string(cluster_name)]
                if len(cluster_id) == 0:
                    self.logger.warning(f"Miss cluster {cluster_name}")
                    continue
                cluster_id_hex, cluster_id = cluster_id[0][0], cluster_id[0][1]
                value_dict[cluster_id] = {}
                for cmd_name, cmd_info in cluster_info.items():
                    cmd_id = [(k, int(k, 16)) for k, v in spec_cmd_repo[cluster_id_hex]['cmds'].items() if purify_string(v['description']) == purify_string(cmd_name)]
                    if len(cmd_id) == 0:
                        continue
                    cmd_id_hex, cmd_id = cmd_id[0][0], cmd_id[0][1]
                    value_dict[cluster_id][cmd_id] = {}
                    n_constraint_cmd_fields = 0
                    for field_name, field_values in cmd_info.items():
                        if len(field_values) == 0:
                            continue
                        n_constraint_fields += 1
                        n_constraint_cmd_fields += 1
                        value_dict[cluster_id][cmd_id][field_name] = []
                        for field_value in field_values:
                            value_dict[cluster_id][cmd_id][field_name].append(field_value)
                            n_constraint_values += 1
                    if n_constraint_cmd_fields > 0:
                        n_constraint_cmds += 1
        self.logger.info(f"# constraint commands, fields, values = {n_constraint_cmds}, {n_constraint_fields}, {n_constraint_values}")
        return value_dict

    def field_valid_range_collection(self):
        range_dict = {}
        range_file = f"spec/analysis_result/field_range_summary.json"
        n_constraint_cmds = 0
        n_constraint_fields = 0
        with open(range_file, 'r') as fp:
            summary_dict = json.load(fp)
            for cluster_name, cluster_info in summary_dict.items():
                cluster_id = [(k, int(k, 16)) for k, v in spec_cmd_repo.items() if purify_string(v['name']) == purify_string(cluster_name)]
                if len(cluster_id) == 0:
                    continue
                cluster_id_hex, cluster_id = cluster_id[0][0], cluster_id[0][1]
                range_dict[cluster_id] = {}
                for cmd_name, cmd_info in cluster_info.items():
                    cmd_id = [(k, int(k, 16)) for k, v in spec_cmd_repo[cluster_id_hex]['cmds'].items() if purify_string(v['description']) == purify_string(cmd_name)]
                    if len(cmd_id) == 0:
                        continue
                    cmd_id_hex, cmd_id = cmd_id[0][0], cmd_id[0][1]
                    range_dict[cluster_id][cmd_id] = {}
                    n_constraint_cmd_fields = 0
                    for field_name, field_ranges in cmd_info.items():
                        if len(field_ranges) == 0:
                            continue
                        n_constraint_fields += 1
                        n_constraint_cmd_fields += 1
                        range_dict[cluster_id][cmd_id][field_name] = {}
                        range_dict[cluster_id][cmd_id][field_name]['isField'] = 1
                        range_dict[cluster_id][cmd_id][field_name]['bounds'] = []
                        for field_range in field_ranges:
                            range_dict[cluster_id][cmd_id][field_name]['bounds'].append(tuple(field_range))
                    if n_constraint_cmd_fields > 0:
                        n_constraint_cmds += 1
        self.logger.info(f"# constraint commands, fields = {n_constraint_cmds}, {n_constraint_fields}")
        return range_dict

    def field_constraint_collection(self):
        # All field constraints are stored in {cluster_name}-condition-mutation.json files
        # (1) Identify all file names
        # (2) For each file, load its json content.
        # Return value: constraint_dict. The data schema is as follows:
        #       constraint_dict[cluster_id][cmd_id][attr_name]['isField']: 0 or 1
        #       constraint_dict[cluster_id][cmd_id][attr_name]['bounds']: List of tuple, each of which records the lower bound and the upper bound
        n_constraint_cmds = 0; n_constraint_fields = 0
        constraint_dict = {}
        constraint_files = [f for f in os.listdir(self.spec_analysis_path) if 'condition-mutation' in f]
        for constraint_file in constraint_files:
            cluster_name = constraint_file.split('-', 1)[0].strip()
            #cluster_id = [CLUSTER_IDS[x] for x in CLUSTER_IDS.keys() if purify_string(x) == purify_string(cluster_name)][0]
            cluster_id = [(k, int(k, 16)) for k, v in spec_cmd_repo.items() if purify_string(v['name']) == purify_string(cluster_name)]
            if len(cluster_id) == 0:
                continue
            cluster_id_hex, cluster_id = cluster_id[0][0], cluster_id[0][1]
            constraint_dict[cluster_id] = {}
            cmd_json = json.load(open(self.spec_analysis_path + constraint_file, 'r'))
            for cmd_name, constraint_info in cmd_json.items():
                cmd_id = [(k, int(k, 16)) for k, v in spec_cmd_repo[cluster_id_hex]['cmds'].items() if purify_string(v['description']) == purify_string(cmd_name)]
                if len(cmd_id) == 0:
                    continue
                cmd_id_hex, cmd_id = cmd_id[0][0], cmd_id[0][1]
                #cmd_id = [CMD_IDS[x] for x in CMD_IDS.keys() if purify_string(x) == purify_string(cmd_name)][0]
                constraint_dict[cluster_id][cmd_id] = {}
                constrained_attr_names = [x for x in constraint_info.keys() if x not in ['others', 'reception']]
                if len(constrained_attr_names) == 0:
                    continue
                n_constraint_cmds += 1
                for attr_name in constrained_attr_names:
                    n_constraint_fields += 1
                    constraint_dict[cluster_id][cmd_id][attr_name] = {}
                    # (1) Determine whether attr_name refers to an attribute, or command field
                    #cmd_fields = [purify_string(y) for y in CMD_FORMAT_DESCRIPTIONS[cluster_name][cmd_name]['fields']]
                    cmd_fields = [purify_string(k) for k, v in spec_cmd_repo[cluster_id_hex]['cmds'][cmd_id_hex]['payload'].items()]
                    constraint_dict[cluster_id][cmd_id][attr_name]['isField'] = 1 if any([purify_string(attr_name) == x for x in cmd_fields]) else 0
                    # (2) Extract and parse the value range
                    constraint_dict[cluster_id][cmd_id][attr_name]['bounds'] = []
                    assert(isinstance(constraint_info[attr_name], list))
                    for value_range in constraint_info[attr_name]:
                        try:
                            value_range = value_range.replace('true', '1')
                            value_range = value_range.replace('false', '0')
                            bound = literal_eval(value_range)
                            constraint_dict[cluster_id][cmd_id][attr_name]['bounds'].append(tuple(bound))
                        except:
                            self.logger.error(f"[Field Constraint Collection] For cluster {cluster_name}, command {cmd_name}, attribute name {attr_name}: Incorrect format of value_range: {value_range}")
                    # Remove duplicates
                    constraint_dict[cluster_id][cmd_id][attr_name]['bounds'] = list(set(constraint_dict[cluster_id][cmd_id][attr_name]['bounds']))
        self.logger.info(f"# constraint commands, fields = {n_constraint_cmds}, {n_constraint_fields}")
        return constraint_dict

    def extreme_field_value(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        payloads = [payload for payload in target_seed.payloads if payload.data.octets > 0 and payload.data.type_prefix not in NONFIXED_NBYTES_TYPES]
        # Remove fields which previously set interesting value fields or duplicates field values
        uninerested_payloads = [field for field in payloads if len(field.enforced_ops) == 0]
        if len(uninerested_payloads) > 0:
            payload:'ZbeeAttribute' = random.sample(uninerested_payloads, 1)[0]
            starting_index = 1 if payload.data.type_prefix in STRING_TYPES else 0
            end_index = payload.data.octets
            rand_val = random.choice([0x0, 0xff])
            for i in range(starting_index, end_index):
                payload.data.byte_array[i] = rand_val
            payload.data.refresh_value()
            target_seed.refresh_byte_array()
            target_seed.enforced_ops.append(('ExtremeValue', payload.name, rand_val))
        return [target_seed]

    def string_expand_mutation(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        string_fields = [field for field in target_seed.payloads if field.data.type_prefix in STRING_TYPES]
        if len(string_fields) > 0:
            payload = random.sample(string_fields, 1)[0]
            rand_length = random.randint(0x10, 0x20)
            expaned_array = bytearray([])
            for i in range(rand_length):
                expaned_array.append(random.randint(0x0,0xff))
            payload.data.byte_array[0] += rand_length
            payload.data.byte_array = payload.data.byte_array + expaned_array
            payload.data.octets = len(payload.data.byte_array)
            payload.data.refresh_value()
            target_seed.refresh_byte_array()
            target_seed.enforced_ops.append(('STRING_EXPAND', rand_length, expaned_array))
        return [target_seed]

    def variable_expand_mutation(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        variable_fields = [field for field in target_seed.payloads if field.data.type_prefix == VARIABLEPREFIX]
        if len(variable_fields) > 0:
            payload = random.sample(variable_fields, 1)[0]
            rand_length = random.randint(0x10, 0x20)
            expaned_array = bytearray([])
            for i in range(rand_length):
                expaned_array.append(random.randint(0x0,0xff))
            payload.data.byte_array = payload.data.byte_array + expaned_array
            payload.data.octets = len(payload.data.byte_array)
            payload.data.refresh_value()
            target_seed.refresh_byte_array()
            target_seed.enforced_ops.append(('VARIABLE_EXPAND', rand_length, expaned_array))
        return [target_seed]

    """
    Attribute mutation operators
    """

    def interesting_attr_value(self, seed:'Seed', write_attribute_template:'Seed', copy=True):
        """
        Given the target seed, randomly mutate its dependent attribute values.
        If there is no dependent attributes, randomly select one from the cluster.
        """
        assert(seed.cid == write_attribute_template.cid and write_attribute_template.cmd_id == GENETIC_WRITE_REQUEST)
        target_seed:'Seed' = seed.copy() if copy else seed
        write_attribute_seed = None
        # Check if the cluster command has companion interesting attribute values
        candidate_attrs = []; has_intesting_attr = False
        try:
            cmd_constraints:dict = self.constraint_dict[target_seed.cid][target_seed.cmd_id]
            candidate_attrs = [x for x in cmd_constraints.keys() if \
                            cmd_constraints[x]['isField'] == 0 and len(cmd_constraints[x]['bounds']) > 0]
            has_intesting_attr = True if len(candidate_attrs) > 0 else False
        except:
            has_intesting_attr = False
        if has_intesting_attr:
            # 1. Randomly select a field
            mutated_attr = random.sample(candidate_attrs, 1)[0]
            # 2. Search from the seed payload to identify the corresponding payload field
            cluster_attr:ZbeeAttribute = [x for x in target_seed.cluster_attributes if purify_string(x.name) == purify_string(mutated_attr)]
            if len(cluster_attr) > 0:
                # 3. Identify the domain of the attribute
                cluster_attr = cluster_attr[0]
                domain_low = cluster_attr.data.range_low
                domain_high = cluster_attr.data.range_high
                # 4. Randomly select a value range regulated by the spec
                selected_range_low, selected_range_high = random.sample(cmd_constraints[mutated_attr]['bounds'], 1)[0]
                # 5. Determine if flipping the range to generate values against the specification: 75% flip
                mutation_ranges = []
                flip = random.choices([True, False], k=1, weights=[3, 1])[0]
                if flip:
                    mutation_ranges.append((domain_low, selected_range_low))
                    mutation_ranges.append((selected_range_high, domain_high))
                else:
                    mutation_ranges.append((selected_range_low, selected_range_high))
                # 6. Randomly generate a field value
                selected_mutation_range_low, selected_mutation_range_high = random.choice(mutation_ranges)
                mutated_field_value = random.randint(selected_mutation_range_low, selected_mutation_range_high)
                # 7. Generate a Write Attribute Command and set the attribute to specific values
                write_attribute_seed:'Seed' = self.genetic_function_mutation(write_attribute_template, cluster_attr.attribute_id, mutated_field_value)
            else:
                self.logger.warning(f"In cluster {hex(target_seed.cid)}, did not find the attribute for mutation: {purify_string(mutated_attr)}")
        else:
            cluster_attr:ZbeeAttribute = random.sample(target_seed.cluster_attributes, 1)[0]
            write_attribute_seed:'Seed' = self.genetic_function_mutation(write_attribute_template, cluster_attr.attribute_id)
        
        target_seed.refresh_byte_array()
        if write_attribute_seed is not None:
            write_attribute_seed.refresh_byte_array()
            target_seed.enforced_ops.append(('WriteAttr', hex(target_seed.cid),\
                            hex(cluster_attr.attribute_id), write_attribute_seed.identify_payload_by_name('AttrbuteValuei')[1].data.byte_array))
            return [write_attribute_seed, target_seed]
        else:
            return [target_seed]

    """
    Header mutation operators
    """

    def flip_header_bits(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        important_bits = ['FrameType', 'ManuSpecific', 'Direction']
        selected_bits = []
        if random.uniform(0, 1) > .9:
            target_seed.clusterSpecific = False if target_seed.clusterSpecific is True else True
            selected_bits.append(important_bits[0])
        if random.uniform(0, 1) > .9:
            target_seed.manuSpecific = False if seed.cmd_flag == COMMAND_MANU else True
            selected_bits.append(important_bits[1])
        if random.uniform(0, 1) > .5:
            target_seed.direction = SERVER_CLIENT_DIRECTION if target_seed.direction == CLIENT_SERVER_DIRECTION else CLIENT_SERVER_DIRECTION
            selected_bits.append(important_bits[2])
        target_seed.enforced_ops.append(('FlipHeader', ' + '.join(selected_bits)))
        return [target_seed]
    
    def mutate_manu_code(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        if random.uniform(0, 1) > 0.7:
            target_seed.manuCode = random.choice([0x0, 0xffff])
        else:
            target_seed.manuCode = random.randint(0x0, 0xffff)
        target_seed.enforced_ops.append(('UpdateManuCode', hex(target_seed.manuCode)))
        return [target_seed]
    
    def mutate_cmd_id(self, seed:'Seed', copy=True):
        target_seed:'Seed' = seed.copy() if copy else seed
        target_seed.cmd_id = random.randint(0x0, 0xff)
        target_seed.enforced_ops.append(('UpdateCmdID', hex(target_seed.cmd_id)))
        return [target_seed]

    """
    Format disturbing operators here
    """

    def delbyte_mutation(self, seed:'Seed', copy=True):
        """
        This function initiates the following functionality.
        (1) Remove `removed_fields` number of fields from seed.payloads.
        (2) If the number of remaining fields > 0, randomly delete some bytes of the last field (not removing it).
        NOTE: After the mutation is executed, the data in the payload will not be aligned.
        """
        target_seed:'Seed' = seed.copy() if copy else seed
        n_fields = len(target_seed.payloads)
        n_removed_fields = random.choice(list(range(1, n_fields+1))) if n_fields > 0 else 0
        new_payloads = target_seed.payloads if n_removed_fields == 0 else target_seed.payloads[:-n_removed_fields]
        ## Uncommit the following codes if you want to further delete bytes
        #if len(new_payloads) > 0:
        #    n_bytes = len(new_payloads[-1].data.byte_array)
        #    if n_bytes > 1:
        #        n_removed_bytes = random.randint(1, n_bytes-1)
        #        new_payloads[-1].data.set_byte_array(new_payloads[-1].data.byte_array[:-n_removed_bytes], value_refresh=False)
        #    elif n_bytes == 1: # Just remove the field
        #        new_payloads = new_payloads[:-1]
        target_seed.payloads = new_payloads
        target_seed.refresh_byte_array()
        target_seed.enforced_ops.append(('DeleteFields', n_removed_fields))
        return [target_seed]

    def string_length_inc_mutation(self, seed:'Seed', copy=True):
        """
        This function initiates the following functionality.
        (1) Identify the bytes which represent the string fields' lengths.
        (2) Randomly add it with some numbers
        NOTE: After the mutation is executed, the data in the payload will not be aligned.
        """
        target_seed:'Seed' = seed.copy() if copy else seed
        # Fetch all byte positions which represents
        sensitive_pos = target_seed.identify_sensitive_positions()
        if len(sensitive_pos) > 0:
            # Randomly pick one sensitive positions
            picked_pos = random.choice(sensitive_pos)
            random_length = random.sample([0xff, 0xfe, 0xfd], k=1)[0]
            target_seed.payload_bytearrays[picked_pos] = random_length
            target_seed.enforced_ops.append(('STRINGINC', random_length))
        return [target_seed]

    def string_length_dec_mutation(self, seed:'Seed', copy=True):
        """
        This function initiates the following functionality.
        (1) Identify the bytes which represent the string fields' lengths.
        (2) With 50% probability set it to 0, Otherwise 50% randomly decrease it with some numbers
        NOTE: After the mutation is executed, the data in the payload will not be aligned.
        """
        target_seed:'Seed' = seed.copy() if copy else seed
        # Fetch all byte positions which represents
        sensitive_pos = target_seed.identify_sensitive_positions()
        if len(sensitive_pos) > 0:
            # Randomly pick one sensitive positions
            picked_pos = random.choice(sensitive_pos)
            if random.uniform(0, 1) >= 0.5 and target_seed.payload_bytearrays[picked_pos] > 1:
                random_length = random.randint(1, target_seed.payload_bytearrays[picked_pos]-1)
            else:
                random_length = target_seed.payload_bytearrays[picked_pos]
            target_seed.payload_bytearrays[picked_pos] -= random_length
            target_seed.enforced_ops.append(('STRINGDEC', random_length))

        return [target_seed]

    def mutation(self, cmd:'Seed'):
        """
        This function mutates the `cmd`. The applied mutation operator types follow the order.
        (1) payload_mutation_ops
        (2) disturbing_mutation_ops
        (3) header_mutation_ops
        (4) attribute_mutation_ops
        The return value is list[Seed].
        """
        mutation_prob = {
            'disturb': .3,
            'header': .3,
            'mutate_manucode': .05,
            'mutate_cmd_id': .05,
        }
        # 1. Mutate the payload
        available_payload_ops = self.determine_available_payload_mutation_ops(cmd)
        selected_op = random.choice(available_payload_ops)
        mutation_result:list[Seed] = self.payload_mutation_ops[selected_op](cmd)
        # 2. With probability 10%, disturb the seed format.
        if random.uniform(0, 1) > 1. - mutation_prob['disturb']:
            disturbing_op = random.choice(list(self.disturbing_mutation_ops.keys()))
            mutation_result = self.disturbing_mutation_ops[disturbing_op](mutation_result[-1])
        # 3. With probability 50%, mutate the header.
        if random.uniform(0, 1) > 1. - mutation_prob['header']:
            #header_op = random.choice(list(self.header_mutation_ops.keys()))
            mutation_result = self.flip_header_bits(mutation_result[-1])
        if random.uniform(0, 1) > 1. - mutation_prob['mutate_manucode']:
            #header_op = random.choice(list(self.header_mutation_ops.keys()))
            mutation_result = self.mutate_manu_code(mutation_result[-1])
        if random.uniform(0, 1) > 1. - mutation_prob['mutate_cmd_id']:
            #header_op = random.choice(list(self.header_mutation_ops.keys()))
            mutation_result = self.mutate_cmd_id(mutation_result[-1])
        return mutation_result

class SpecPool(SeedPool):

    def __init__(self, target_device: ZigbeeDevice, flag=''):
        super().__init__(target_device, flag)
        # Used for round robin
        self.seed_bitmap = {(cid, cmd_id):0 for (cid, cmd_id) in [(seed.cid, seed.cmd_id) for seed in self.pool]}
    
    def filter_seeds(self, untested_cluster_ids=[], skipped_cmds=[]):
        pool = [seed for seed in self.pool if seed.cid not in untested_cluster_ids]
        pool = [seed for seed in self.pool if (seed.cid, seed.cmd_id) not in skipped_cmds]
        self.pool = pool
        self.seed_bitmap = {(cid, cmd_id):0 for (cid, cmd_id) in [(seed.cid, seed.cmd_id) for seed in self.pool]}

    def prioritize_seeds_by_selection(self):
        """
        Prioritize seeds which are not selected before.
        """
        unselected_seeds = [k for k,v in self.seed_bitmap.items() if v == 0]
        if len(unselected_seeds) > 0:
            selected_seed_cid, selected_seed_cmd_id = random.choice(unselected_seeds)
            selected_seed = self.lookup_seed(selected_seed_cid, selected_seed_cmd_id)
            self.seed_bitmap[(selected_seed_cid,selected_seed_cmd_id)] = 1
            return selected_seed
        else:
            self.seed_bitmap = {k:0 for k in self.seed_bitmap.keys()}
            return self.prioritize_seeds_by_selection()

class SpecFuzzer(Fuzzer):

    def __init__(self, controller:'ZbeeController'):
        self.name = AFL
        self.logger = logging.getLogger(self.__class__.__name__)
        self.spec_analysis_path = 'spec/inter_result/'
        super().__init__(controller)

        self.spec_searcher = SpecSearcher()

        self.genetic_seed_pool = SpecPool(self.target_device, COMMAND_GENETIC)
        self.zcl_seed_pool = SpecPool(self.target_device, COMMAND_ZCL)
        self.manu_seed_pool = SpecPool(self.target_device, COMMAND_MANU)

        self.mutator = SpecMutator()
        self.msg_dependency_graph, self.n_dependencies = self.build_message_dependency_graph()

        self.n_simulation_error_case = 0
        self.coverage_analyzer = Coverage()
        self.coverage_analyzer.init_count_class16()

        self.total_edges = []
        self.total_statements = []
        self.coverage_history = []
        self.stat_coverage_history = []

        self.async_loop = asyncio.get_event_loop()
        
        self.interesting_case_repo = []
        #self.logger.info("Seeds number for genetic, zcl, and manu commands: {} {} {}".format(
        #    self.genetic_seed_pool.n_seeds, self.zcl_seed_pool.n_seeds, self.manu_seed_pool.n_seeds))
        # The un-supported ZCL attributes by devices, which may imply some security issues

    def build_message_dependency_graph(self, dependency_file):
        """
        This function reads the cmd-dependency.json function as inputs, and build a message adjacancy graph
        """
        msg_dependency_graph:dict[list] = defaultdict(list)
        n_dependencies = 0
        unique_cmd_ids = set()
        with open(dependency_file, 'r') as fp:
            content = fp.readline().strip()
            dependency_list = literal_eval(content)
            for dependency in dependency_list:
                preceding_msg_id = (int(dependency[0][0]), int(dependency[0][1]))
                consecutive_msg_id = (int(dependency[1][0]), int(dependency[1][1]))
                msg_dependency_graph[preceding_msg_id].append(consecutive_msg_id)
                unique_cmd_ids.add(preceding_msg_id); unique_cmd_ids.add(consecutive_msg_id)
                n_dependencies += 1
        self.logger.info(f"Successfully built Message Dependency Graph. # cmds and dependencies: {len(unique_cmd_ids)}, {n_dependencies}")
        return msg_dependency_graph, n_dependencies
        
        # Use device supported commands to built the initial list
        for ep_id, ep_info in self.target_device.endpoint_dict.items():
            for cluster_id, cluster_info in ep_info.cluster_dict.items():
                for cmd in cluster_info.command_list:
                    msg_dependency_graph[(cluster_id, cmd.cmd_id)] = []
        
        n_dependencies = 0
        graph_json = json.load(open(self.spec_analysis_path+'cmd-dependency.json', 'r'))
        for msg_pair, pair_info in graph_json.items():
            has_relation = pair_info['relation']
            if has_relation:
                preceding_cmd = msg_pair.split('->')[0].strip(); consecutive_cmd = msg_pair.split('->')[1].strip()
                preceding_cluster_name, preceding_cmd_name = preceding_cmd.split(':', 1)
                consecutive_cluster_name, consecutive_cmd_name = consecutive_cmd.split(':', 1)
                #if 'color' in preceding_cluster_name.strip().lower():
                #    print(f"{preceding_cluster_name}:{preceding_cmd_name} -> {consecutive_cluster_name}{consecutive_cmd_name}")
                preceding_cid_hex, preceding_cid = [(k, int(k, 16)) for k, v in spec_cmd_repo.items() if purify_string(v['name']) == purify_string(preceding_cluster_name)][0]
                #preceding_cid = [CLUSTER_IDS[x] for x in CLUSTER_IDS.keys() if purify_string(x) == purify_string(preceding_cluster_name)][0]
                #consecutive_cid = [CLUSTER_IDS[x] for x in CLUSTER_IDS.keys() if purify_string(x) == purify_string(consecutive_cluster_name)][0]
                #preceding_cmd_id = [CMD_IDS[x] for x in CMD_IDS.keys() if purify_string(x) == purify_string(preceding_cmd_name)][0]
                #consecutive_cmd_id = [CMD_IDS[x] for x in CMD_IDS.keys() if purify_string(x) == purify_string(consecutive_cmd_name)][0]
                consecutive_cid_hex, consecutive_cid = [(k, int(k, 16)) for k, v in spec_cmd_repo.items() if purify_string(v['name']) == purify_string(consecutive_cluster_name)][0]
                preceding_cmd_id = [int(k, 16) for k, v in spec_cmd_repo[preceding_cid_hex]['cmds'].items() if purify_string(v['description']) == purify_string(preceding_cmd_name)]
                consecutive_cmd_id = [int(k, 16) for k, v in spec_cmd_repo[consecutive_cid_hex]['cmds'].items() if purify_string(v['description']) == purify_string(consecutive_cmd_name)]
                if len(preceding_cmd_id) == 0 or len(consecutive_cmd_id) == 0:
                    #print(f"Miss preceding or consecutive cmd in file: {preceding_cmd_name} {consecutive_cmd_name}")
                    continue
                preceding_cmd_id = preceding_cmd_id[0]
                consecutive_cmd_id = consecutive_cmd_id[0]
                # If any cluster is not the device-supported cluster, we dont consider the dependency edge.
                preceding_key = (preceding_cid, preceding_cmd_id)
                consecutive_key = (consecutive_cid, consecutive_cmd_id)
                # If the device does not support the cluster:command in the message depedency graph: Skip the dependency
                if preceding_key not in msg_dependency_graph.keys() or consecutive_key not in msg_dependency_graph.keys():
                    self.logger.info(f"Miss preceding or consecutive keys: {preceding_key} {consecutive_key}")
                    continue
                msg_dependency_graph[preceding_key].append(consecutive_key)
                n_dependencies += 1
        self.logger.info(f"Successfully built Message Dependency Graph. # dependencies: {n_dependencies}")
        return msg_dependency_graph, n_dependencies

    def send_zcl_command(self, cid, cmd_id, field_values):
        seed_pool = self.zcl_seed_pool # TODO: Test other commands
        target_seed:'Seed' = [seed for seed in seed_pool.pool if seed.cid == cid and seed.cmd_id == cmd_id][0]
        for field_name, field_value in field_values.items():
            # Find the matched payload
            for payload in target_seed.payloads:
                if payload.name.replace(' ', '').lower() == field_name.replace(' ', '').lower():
                    payload.data.assign(field_value)
        self.execute_seed(target_seed, True, False)

    def initial_seed_generation(self, round_robin=True):
        """
        (1) Randomly select a command as the start of the seed
        (2) Based on the message dependency graph, extend the seed to the length of `max_length`
        (3) Leverage interesting value to set the field of the seed
        (4) Leverage field duplication to set the consecutive message payloads.
        """
        # 1. Randomly select a command from zcl repo and genetic repo
        zcl_seed_pool = self.zcl_seed_pool
        genetic_seed_pool = self.genetic_seed_pool
        initial_seed = []
        from_zcl = random.uniform(0, 1) >= 0.3
        if round_robin:
            initial_seed = [zcl_seed_pool.prioritize_seeds_by_selection()] if from_zcl else [genetic_seed_pool.prioritize_seeds_by_selection()]
        else:
            initial_seed = [random.choice(zcl_seed_pool.pool)] if from_zcl else [random.choice(genetic_seed_pool.pool)]
        return initial_seed
    
    def generate_msg_with_interesting_value(self, seed_msg:'Seed', last_msg:'Seed', copy=True):
        if seed_msg.cmd_flag == COMMAND_ZCL:
            new_cmd = self.mutator.set_field_value_from_invalid_range(seed_msg, copy) if random.uniform(0, 1) > .5\
                            else self.mutator.set_field_value_from_semantic_value(seed_msg, copy)
        else:
            assert(seed_msg.cmd_flag == COMMAND_GENETIC)
            new_cmd = self.mutator.set_field_value_from_invalid_range(seed_msg, copy)
        
        # Randomly duplicate the field value based on the last message
        if last_msg is not None and random.uniform(0, 1) >= 0.3:
            new_cmd = self.mutator.field_duplication(seed_msg, last_msg, True)
        
        return new_cmd

    def interesting_case_enrichment(self, intcase:'list[Seed]'):
        """
            Enrich the seed with ZCL comamnds.
            Note that here we only use ZCL commands. We do not extend the seed with genetic commands
        """
        assert(len(intcase) > 0 and intcase[-1].cmd_flag == COMMAND_ZCL)
        
        
        enrich_flag = False
        last_msg = intcase[-1]
        preceding_cmd = (last_msg.cid, last_msg.cmd_id)
        candidate_next_cmds = self.msg_dependency_graph[preceding_cmd] # Check all dependent comamnds from msg_dependency_graph
        candidate_next_msg_templates = [self.zcl_seed_pool.lookup_seed(x[0], x[1]) for x in candidate_next_cmds]
        candidate_next_msg_templates = [x for x in candidate_next_msg_templates if x is not None]
        
        
        if len(candidate_next_msg_templates) > 0:
            target_msg_template = random.choice(candidate_next_msg_templates)
            intcase.append(target_msg_template.copy())
            enrich_flag = True
        else:
            self.logger.warning(f"Cannot find any dependency record for the command {preceding_cmd}, is it normal?")
        
        DEBUGGING = False
        if DEBUGGING:
            print(f"The last message in the current interesting case: {self.spec_searcher.search_cmd_name(preceding_cmd[0], preceding_cmd[1])}")
            dependent_msg_names = [self.spec_searcher.search_cmd_name(msg_template.cid, msg_template.cmd_id) for msg_template in candidate_next_msg_templates]
            print(f"    Candidate dependent commands: {dependent_msg_names}")
            print(f"    Enrich decision: {enrich_flag} with command {self.spec_searcher.search_cmd_name(intcase[-1].cid, intcase[-1].cmd_id)}")
            input()
        return enrich_flag

    async def is_interesting_case(self, testing_case:'list[Seed]', responses, n_times=5):
        is_interesting = False
        assert(len(testing_case) > 0 and len(testing_case) == len(responses))
        last_msg = testing_case[-1]
        cmd_name = self.spec_searcher.search_cmd_name(last_msg.cid, last_msg.cmd_id)
        if last_msg.cmd_flag != COMMAND_ZCL or cmd_name is None:
            return is_interesting
        # 1. Build the message detail
        cmd_payload_info = []
        for field in last_msg.payloads:
            hex_field_value = '0x' + ''.join(['{:02x}'.format(b) for b in field.data.byte_array[:6]])
            cmd_payload_info.append((field.name, hex_field_value))
        msg_str = f"""Transmited "{cmd_name}" command with payload values: """ + ','.join(['='.join(x) for x in cmd_payload_info])

        # 2. Build the response detail. We by default use the first byte in the response zcl payload as the status code
        last_response = responses[-1]
        if last_response is None or len(last_response) == 0:
            return is_interesting
        response_status_code = int(last_response[1]) if len(last_response) > 1 else int(last_response[0])
        response_status_name = self.spec_searcher.response_status_dict[response_status_code] \
                                if response_status_code in self.spec_searcher.response_status_dict.keys() else 'SUCCESS'
        response_str = f"""Received response: "{response_status_name}" Execution Status"""

        # 3. Join to get the conversation
        conversation_history = '\n'.join([msg_str, response_str])

        # 4. Fetch the command description
        cmd_description = self.spec_searcher.search_cmd_description(last_msg.cid, last_msg.cmd_id)

        # 5. Construct the final prompt
        prompt = DETERMINE_INTERESTING_CASE_PROMPT.format(cmd_name, cmd_description, conversation_history)
        prompts = [prompt] * n_times
        tasks = [get_final_poe_response(prompt, 0) for prompt in prompts]
        llm_answers = await asyncio.gather(*tasks)
        misalignment_decision = select_most_frequent_answer([text_purify(MISALIGNMENT_KEYWORD) in text_purify(answer) for answer in llm_answers])
        state_changed_decision = select_most_frequent_answer([text_purify(STATE_UNCHANGE_KEYWORD) not in text_purify(answer) for answer in llm_answers])
        if misalignment_decision is True or state_changed_decision is True:
            is_interesting = True
        if is_interesting:
            int_case = {
                "Conversation": conversation_history,
                "Answer": llm_answers[0],
                "Misalignment": misalignment_decision,
                "State changed": state_changed_decision
            }
            self.interesting_case_repo.append(int_case)
        return is_interesting

    async def select_interesting_cases(self, testing_cases:'list[list[Seed]]', responses, max_case_length):
        case_response_pairs = list(zip(testing_cases, responses))
        candidate_cases = []
        candidate_prompts = []
        candidate_conversation_histories = []
        for testing_case, response in case_response_pairs:
            # Build the prompt for each testing case
            assert(len(testing_case) > 0 and len(testing_case) == len(response))
            if len(testing_case) >= max_case_length:
                continue
            last_msg = testing_case[-1]
            cmd_name = self.spec_searcher.search_cmd_name(last_msg.cid, last_msg.cmd_id)
            if last_msg.cmd_flag != COMMAND_ZCL or cmd_name is None:
                continue
            # 1. Build the message detail
            cmd_payload_info = []
            for field in last_msg.payloads:
                hex_field_value = '0x' + ''.join(['{:02x}'.format(b) for b in field.data.byte_array[:6]])
                cmd_payload_info.append((field.name, hex_field_value))
            payload_value_str = ','.join(['='.join(x) for x in cmd_payload_info])
            if len(payload_value_str) > 0:
                msg_str = f"""Transmited "{cmd_name}" command with payload values: """ + ','.join(['='.join(x) for x in cmd_payload_info])
            else:
                msg_str = f"""Transmited "{cmd_name}" command with payload values: Empty payload"""
            # 2. Build the response detail. We by default use the second byte in the response zcl payload as the status code.
            #       Check the payload of Default Response for reasons.
            last_response = response[-1]
            if last_response is None or len(last_response) == 0:
                continue
            response_status_code = int(last_response[1]) if len(last_response) > 1 else int(last_response[0])
            response_status_name = self.spec_searcher.response_status_dict[response_status_code] \
                                    if response_status_code in self.spec_searcher.response_status_dict.keys() else 'SUCCESS'
            response_str = f"""Response: "{response_status_name}" Execution Status"""
            # 3. Join to get the conversation
            conversation_history = '\n'.join([msg_str, response_str])
            # 4. Fetch the command description
            cmd_description = self.spec_searcher.search_cmd_description(last_msg.cid, last_msg.cmd_id)
            # 5. Construct the final prompt
            prompt = DETERMINE_INTERESTING_CASE_PROMPT.format(cmd_name, cmd_description, conversation_history)
            candidate_cases.append(testing_case)
            candidate_conversation_histories.append(conversation_history)
            candidate_prompts.append(prompt)
        assert(len(candidate_cases) == len(candidate_prompts) == len(candidate_conversation_histories))
        tasks = [get_final_poe_response(prompt, 0) for prompt in candidate_prompts]
        llm_answers = await asyncio.gather(*tasks)
        
        interesting_cases = []
        misalignment_flags = [text_purify(MISALIGNMENT_KEYWORD) in text_purify(answer) for answer in llm_answers]
        state_changed_flags = [text_purify(STATE_UNCHANGE_KEYWORD) not in text_purify(answer) for answer in llm_answers]
        assert(len(llm_answers) == len(misalignment_flags) == len(state_changed_flags))
        is_interesting_flags = []
        for i, misalignment_flag in enumerate(misalignment_flags):
            is_interesting_flags.append(misalignment_flag or state_changed_flags[i])
        assert(len(is_interesting_flags) == len(candidate_cases) == len(candidate_conversation_histories))
        for i, is_interesting_flag in enumerate(is_interesting_flags):
            if is_interesting_flag:
                int_case_description = {
                    "Conversation": candidate_conversation_histories[i],
                    "Answer": llm_answers[i],
                    "Misalignment": misalignment_flags[i],
                    "State changed": state_changed_flags[i]
                }
                interesting_cases.append(candidate_cases[i])
                self.interesting_case_repo.append(int_case_description)
        return interesting_cases

    def fuzzing_with_feedback(self,
                              skipped_clusters=[],
                              skipped_cmds=[],
                              max_retry=3,
                              max_case_length=3,
                              n_cases_per_round=10):
        crashing_cases = []
        # 1. Prepare the message format repository
        self.zcl_seed_pool.filter_seeds(skipped_clusters, skipped_cmds)

        intcases = []
        timeout = 36000 # Here we set the timeout as 24 hours
        start_time = time.time()
        n_round = 0
        try:
            while (time.time() - start_time) < timeout:
                # 0. Determine the seed s in the current fuzzing round
                s = []
                if len(intcases) == 0:
                    s = self.initial_seed_generation(round_robin=True)
                else:
                    s = random.choice(intcases)
                    # Remove the interesting case from the list
                    intcases.remove(s)
                    enrich_flag = self.interesting_case_enrichment(s)
                    if not enrich_flag:
                        # TODO: These are interesing cases but with no enrichment potentials. How to handle them?
                        # Currently we choose to continue and skip the case
                        continue
                
                # Using the current seed, we generate n_trail testing cases for testing
                testing_cases = []
                responses = []
                for n_trail in range(n_cases_per_round):
                    # 1. Assign interesting value to the newly generated message
                    last_msg = s[-2] if len(s) > 1 else None
                    msg_with_interesting_value = self.generate_msg_with_interesting_value(s[-1], last_msg)
                    assert(msg_with_interesting_value is not None)
                    s = s[:-1] + [msg_with_interesting_value]
                    # 2. Mutate the selected seed and generate the testing case c. We only mutate the last message in the current seed
                    mutation_result:'list[Seed]' = self.mutator.mutation(s[-1])
                    testing_case = s[:-1] + mutation_result
                    # 3. Execute the testing case, montior crashes, and collect the response from the device
                    response_seq = []
                    crash_detected = False
                    for msg in testing_case:
                        retry = 0
                        stat, rsp_zcl_payload, elpased_time = self.execute_seed(msg)
                        while (msg.execStat == ERR_CMD_TIMEOUT) and (retry < max_retry):
                            stat, rsp_zcl_payload, elpased_time = self.execute_seed(msg)
                            retry += 1
                        if msg.execStat == ERR_CMD_TIMEOUT:
                            # Crash detected!
                            crash_detected = True
                            break
                        else:
                            response_seq.append(rsp_zcl_payload)
                    # 4. If any crash is detected, record it.
                    if crash_detected:
                        self.logger.warning("A device crash is detected!")
                        crashing_cases.append(testing_case)
                        time.sleep(10)
                    #elif self.async_loop.run_until_complete(self.is_interesting_case(testing_case, responses)) and len(testing_case) < max_case_length:
                    #    intcases.append(testing_case)
                    #    self.logger.info(f"Interesting testing case {len(self.interesting_case_repo)}: {self.interesting_case_repo[-1]}")
                    else:
                        testing_cases.append(testing_case)
                        responses.append(response_seq)
                        
                # 5. For testing cases which do not cause crash, further check if they are interesting cases
                interesting_cases = self.async_loop.run_until_complete(self.select_interesting_cases(testing_cases, responses, max_case_length))
                intcases += interesting_cases
                n_round += 1
                self.logger.info(f"Round {n_round} finished with case_length={len(testing_case)}")
                print(f"Identified # interesting cases in round {n_round}: {len(interesting_cases)}")
                if len(self.interesting_case_repo) > 0:
                    self.logger.info(f"Interesting testing case {len(self.interesting_case_repo)}: {self.interesting_case_repo[-1]}")
        except Exception as e:
            print(f"Fuzzing faced with exception: {e}")
            traceback.print_exc()
        finally:
            # Store the identified crashing cases and interesting cases
            with open('results/crashing.log', 'w') as fp:
                for i, crashing_case in enumerate(crashing_cases):
                    fp.write(f"\n********** Case {i+1} **********\n")
                    for msg in crashing_case:
                        fp.write(f"\n{msg}\n")
            with open('results/interesting-case.log', 'w') as fp:
                for i, interesting_case in enumerate(self.interesting_case_repo):
                    fp.write(f"\n********** Case {i+1} **********\n")
                    fp.write(json.dumps(interesting_case))
    
    def reproduce_testing_cases(self, crashing_log='', one_by_one=True, n_trails_each_msg=1):
        """
        Example descriptions.
            (1) ep,pid,cid,cmd_id,cmd_flag,clusterSpecific=0x1,0x104,0x300,0x5,0x0,False
            (2) Payload array: bytearray(b'\xff\xff!\x14\x00\xe4\x007a\t\xd6\xf5')
              The 0th payload: AttributeIDi, uint16, 2, bytearray(b'\xff\xff')
              The 1th payload: AttrDataTypei, uint8, 1, bytearray(b'!')
              The 2th payload: AttrbuteValuei, uint16, 2, bytearray(b'\x14\x00')
              The 3th payload: ExpandingParam, Array[Struct(uint16,uint8,Variable)], 7, bytearray(b'\xe4\x007a\t\xd6\xf5')
            (3) Enforced ops: [('ExtremeValue', 'AttributeIDi', 255)]
            (4) Direction: 0, clusterSpecific:False, manuSpecific: False, manuCode: 0
            (5) Execution info: execStat=0xfc, rspStat=0x0, execTime=-1
        """
        with open(crashing_log, 'r') as fp:
            case_description = []
            case_id = 0
            nwkAddr = None; flag = SAMPLEAPP_UNICAST
            ep = None; cid = None; pid = None; cmd_id = None
            clusterSpecific = None; direction = None; manuCode = None
            payload = None
            for line in fp.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith('*****'):
                    print(f"Varify case {case_id} finsihed. Continue?")
                    if one_by_one:
                        input()
                    case_id += 1
                    nwkAddr = None; flag = SAMPLEAPP_UNICAST
                    ep = None; cid = None; pid = None; cmd_id = None
                    clusterSpecific = None; direction = None; manuCode = None
                    payload = None
                if line.startswith('(1)'):
                    segs = line.split(',')
                    clusterSpecific = literal_eval(segs[-1])
                    cmd_id = literal_eval(segs[-3])
                    cid = literal_eval(segs[-4])
                    pid = literal_eval(segs[-5])
                    ep = literal_eval(segs[-6].split('=')[1])
                if line.startswith('(2)'):
                    byte_string = line.split("""bytearray(""")[1][:-1]
                    print(byte_string)
                    payload = eval(byte_string)
                if line.startswith('(4)'):
                    segs = line.split(',')
                    direction = literal_eval(segs[0].split(':')[1])
                    clusterSpecific = literal_eval(segs[1].split(':')[1])
                    manuCode = literal_eval(segs[3].split(':')[1])
                    print(" Inject msg:")
                    print(f"        {hex(self.controller.target_device.nwkAddr)} {hex(flag)}")
                    print(f"        {hex(ep)} {hex(cid)} {hex(pid)} {hex(cmd_id)} {clusterSpecific} {direction} {hex(manuCode)}")
                    print(f"        {payload}")
                    for i in range(n_trails_each_msg):
                        self.controller.inject_zcl_cmd(
                            self.controller.target_device.nwkAddr, flag, ep, cid, pid, cmd_id, clusterSpecific, direction, manuCode, payload,
                            monitor_response = False
                        )
                        time.sleep(0.05)
                if line.startswith('(5)'):
                    nwkAddr = None; flag = SAMPLEAPP_UNICAST
                    ep = None; cid = None; pid = None; cmd_id = None
                    clusterSpecific = None; direction = None; manuCode = None
                    payload = None
    
    def fuzzing_simulation_device(self, skipped_clusters=[],
                                  seedfile:str='simulation/seedfile',
                                  target_zcl_cfgs:list[str]=[],
                                  max_length=1,
                                  round_robin=True,
                                  set_interesting_value=True):
        zcl_seed_pool = self.zcl_seed_pool
        genetic_seed_pool = self.genetic_seed_pool
        zcl_seed_pool.filter_seeds(skipped_clusters)

        #initial_seed = self.zcl_seed_pool.lookup_seed(0x0101, 0x18)
        #print(f"Seed.cid={hex(initial_seed.cid)}, Seed.cmd_id={hex(initial_seed.cmd_id)}")
        #self.simulation_execution_seed([initial_seed], seedfile, target_zcl_cfgs)
        #exit()

        n_cases = 0
        start_time = time.time()
        try:
            start_time = time.time()
            for i in range(N_EXPLORE_FUZZING_ROUND):
                finally_execution_sequences = []
                # 1. Generate the initial seed
                initial_seed = self.initial_seed_generation(skipped_clusters, max_length, round_robin, set_interesting_value)
                # 2. Sequentially mutate the commands in initial_seeds
                print(f"Round {i}: Seed.cid={hex(initial_seed[0].cid)}, Seed.cmd_id={hex(initial_seed[0].cmd_id)}")
                for cmd in initial_seed:
                    # Mutate the current commands.
                    write_attr_cmd = genetic_seed_pool.lookup_seed(cmd.cid, GENETIC_WRITE_REQUEST) if max_length > 1 else None
                    # In simulation, we cannot get the response. So we remove the response extraction operator by setting preceding_response to be None
                    mutation_result:list[Seed] = self.mutator.mutation(cmd, write_attr_cmd)
                    # 3.2 Execute the current commands, and collect the response
                    finally_execution_sequences += mutation_result
                #print(finally_execution_sequences[-1])
                self.simulation_execution_seed(finally_execution_sequences, seedfile, target_zcl_cfgs)
                if i % 100 == 0:
                    self.logger.info(f"Until msg {i}, n_edge_coverage={self.coverage_analyzer.calculate_explored_edges()}, n_stat_coverage={self.coverage_analyzer.calculate_explored_statements()}")
                n_cases += 1
                print(f"n_edge_coverage={self.coverage_analyzer.calculate_explored_edges()}, n_stat_coverage={self.coverage_analyzer.calculate_explored_statements()}")
                #print(f"Uncoved edges:\n{pformat(self.coverage_analyzer.cumu_uncovered_edges)}")
                #input()
        except Exception as e:
            print(f"Faced with exception: {e}")
            traceback.print_exc()
            pass
        finally:
            end_time = time.time()
            self.logger.info(f"# analyzed modules: {len(target_zcl_cfgs)}")
            self.logger.info(f"# total edges, total statements: {sum(self.total_edges)}, {sum(self.total_statements)}")
            self.logger.info(f"     Module edges: {self.total_edges}")
            self.logger.info(f"     Module statements: {self.total_statements}")
            module_edge_coverage_frequency = {k:len(v) for k, v in self.coverage_analyzer.module_cumu_covered_edges.items()}
            self.logger.info(f"Module edge coverage:\n{pformat(module_edge_coverage_frequency)}")
            #uncovered_edges = [x for x in self.coverage_analyzer.cumu_uncovered_edge_frequency.keys() if abs(self.coverage_analyzer.cumu_uncovered_edge_frequency[x]-n_cases)<=1]
            #for uncovered_edge in uncovered_edges:
            #    self.logger.info(uncovered_edge)
            self.logger.info(f"Edge coverage list:\n{self.coverage_history[-1]}")
            self.logger.info(f"Statement coverage list:\n{self.stat_coverage_history[-1]}")
            self.logger.info(f"Consumed time: {round((end_time-start_time)*1./60 ,2)}")

            self.logger.info(f"# set invalid range fields, # set semantic value fields = {self.mutator.n_set_invalid_range_fields}, {self.mutator.n_set_semantic_fields}")

            x_list = list(range(N_EXPLORE_FUZZING_ROUND+1))
            edge_coverage_list = [0] + self.coverage_history
            stats_coverage_list = [0] + self.stat_coverage_history
            edge_coverage_list = [round(edge_coverage_list[i]*1./sum(self.total_edges), 2) for i in range(len(edge_coverage_list))]
            stats_coverage_list = [round(stats_coverage_list[i]*1./sum(self.total_statements), 2) for i in range(len(stats_coverage_list))]
            plt.plot(x_list, edge_coverage_list, marker='o', linestyle='-', color='b', label='GPTFuzzer')
            plt.title('Edge coverage analysis')
            plt.xlabel('# testing cases')
            plt.ylabel('Covered edges')
            plt.savefig('figure/edge-coverage.png')
            plt.clf()
            plt.plot(x_list, stats_coverage_list, marker='o', linestyle='-', color='b', label='GPTFuzzer')
            plt.title('Statements coverage analysis')
            plt.xlabel('# testing cases')
            plt.ylabel('Covered statements')
            plt.savefig('figure/statement-coverage.png')

    def simulation_execution_seed(self, execution_sequences:list[Seed], seedfile, target_zcl_cfgs:list[str]):
        """
        In this function, we need to store the raw byte message into the seedfile
        The separator is "\xff\x40\x50\x60\x70\xff"
        Final commandBytes = {2 bytes `n_cmd_bytes`}{2 bytes `clusterID` + n bytes `zclFrame`}{6 bytes `separator`}{...}
        """
        final_str = ''
        final_str += "**************** Seed Generation **************\n"
        separator = b'\xff\x40\x50\x60\x70\xff'
        messages:list[bytes] = []
        n_msg = 0
        for cmd in execution_sequences:
            cmd_bytes = bytearray()
            # Build clusterID
            clusterId = cmd.cid.to_bytes(2, DEFAULT_ENDIAN)
            cmd_bytes += clusterId
            # Build header
            fc = 0; seq_num = 0xff
            fc |= 0x1 if cmd.clusterSpecific else fc # Set Frame type
            fc |= 0x4 if cmd.manuSpecific else fc # Set Manuspecific
            fc |= 0x8 if cmd.direction else fc # Set Direction
            fc &= 0xef # Set Disable Default Response
            cmd_bytes += bytearray(b''.join([
                fc.to_bytes(1, DEFAULT_ENDIAN),
                cmd.manuCode.to_bytes(2, DEFAULT_ENDIAN) if cmd.manuSpecific else b'',
                seq_num.to_bytes(1, DEFAULT_ENDIAN),
                cmd.cmd_id.to_bytes(1, DEFAULT_ENDIAN),
            ]))
            # Build paylaods
            for payload in cmd.payloads:
                cmd_bytes += payload.data.byte_array
            #self.logger.info(cmd_bytes)
            messages.append(cmd_bytes)
            n_msg += 1
            #print(f"msg cid={hex(cmd.cid)}, cmd_id={cmd.cmd_id}")
            #print(cmd.enforced_ops)
        final_bytes = separator.join(messages)
        msg_len = len(final_bytes) + 2
        final_bytes = msg_len.to_bytes(2, DEFAULT_ENDIAN) + final_bytes
        #final_str += f"# msg = {n_msg}, total_bytes = {msg_len}\n"
        for i in range(n_msg):
            final_str += f"Msg {i}: {messages[i].hex()}\n"
        with open(seedfile, 'wb') as sfp:
            sfp.write(final_bytes)
        #print(f"[SpecFuzzer] Send bytes: {final_bytes}")
        final_str += "**************** Seed Generation End**************\n"
        # Call cspy to execute the seedfile.
        command =  [CMD, '/C', CSPY_SCRIPT]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e)
            pass
        # If there is any execution error, store the result file for further analysis.
        # At the same time, calculate the code coverage
        finally:
            print(output.decode())
            output = str(output.decode("utf-8"))
            final_str += "\n************Execution result*********\n"
            final_str += output
            final_str += "************END*********\n"
            if "ERROR" in output or "CSpyBat terminating." in output:
                self.n_simulation_error_case += 1
                with open(f"{result_dir}error{self.n_simulation_error_case}.txt", 'w', encoding='utf-8') as result_fop:
                    result_fop.write(final_str)
            # Determine cfg files
            cfg_files = []
            if len(target_zcl_cfgs) == 0:
                cfg_files = os.listdir(cfg_dir)
            else:
                cfg_files = [x for x in os.listdir(cfg_dir) if x in target_zcl_cfgs]
            # Calculate the total edges and total statements in these cfg files
            n_edges = []; n_stats = []
            for cfg_file in cfg_files:
                module_coverage = self.coverage_analyzer.parse_coverage_result(cfg_file=f"{cfg_dir}{cfg_file}",
                                                             coverage_file=f"{coverage_dir}coverage.txt")
                n_edges.append(self.coverage_analyzer.total_edge)
                n_stats.append(self.coverage_analyzer.total_statement)
            self.total_edges = n_edges
            self.total_statements = n_stats

            n_after_edges = self.coverage_analyzer.calculate_explored_edges()
            n_after_statements = self.coverage_analyzer.calculate_explored_statements()
            self.coverage_history.append(n_after_edges)
            self.stat_coverage_history.append(n_after_statements)
            #self.logger.info(f"Code coverage result: # stats, # edges = {n_after_statements} {n_after_edges}")
        # Finally, calculate the code coverage

    def spec_fuzzing_no_feedback(self, skipped_clusters=[], monitor_response=True):
        """
        The algorithm runs n_round.
        In each round, it initiates the following procedure.
        (1) Generate a random number `length` between 1-10, which determines the length of the initial seed.
        (2) Follow the message dependency graph, and randomly generate a command sequence whose len(seq) < length.
        (3) Sequentially mutate and execute the command.
        """

        zcl_seed_pool = self.zcl_seed_pool
        genetic_seed_pool = self.genetic_seed_pool
        zcl_seed_pool.filter_seeds(skipped_clusters)

        template_rspcode_dis:'dict[list]' = defaultdict(list)

        for i in range(N_EXPLORE_FUZZING_ROUND):
            finally_executed_sequences = []
            # 1. Determine the length of the initial seed.
            n_cmds = random.choice([i for i in range(1, 11)])
            # 2. Follow the message dependency graph and generate the initial seed.
            initial_seeds = [random.choice(zcl_seed_pool.pool)]
            for i in range(n_cmds-1):
                preceding_cmd = (initial_seeds[-1].cid, initial_seeds[-1].cmd_id)
                candidate_next_cmds = self.msg_dependency_graph[preceding_cmd]
                if len(candidate_next_cmds) == 0:
                    self.logger.warning(f"Cannot find any dependency record for the command {preceding_cmd}, is it normal?")
                    break
                initial_seeds.append(random.choice(candidate_next_cmds))
            # 3. Sequentially mutate and execute the commands in initial_seeds
            preceding_cmd = None
            preceding_response = None
            for cmd in initial_seeds:
                # 3.1 Mutate the current commands.
                write_attr_cmd = genetic_seed_pool.lookup_seed(cmd.cid, GENETIC_WRITE_REQUEST)
                mutation_result:list[Seed] = self.mutator.mutation(cmd, preceding_cmd, preceding_response, write_attr_cmd)
                responses:list[bytes] = []
                # 3.2 Execute the current commands, and collect the response
                for mutated_cmd in mutation_result:
                    stat, rsp_frame, elapsed_time = self.execute_seed(mutated_cmd)
                    responses.append(rsp_frame)
                preceding_cmd = mutation_result[-1]
                preceding_response = responses[-1]
                finally_executed_sequences += mutation_result

    def test_bug(self, msgs:list[bytes], seedfile:'str'):
        separator = b'\xff\x40\x50\x60\x70\xff'
        final_bytes = separator.join(msgs)
        msg_len = len(final_bytes) + 2
        final_bytes = msg_len.to_bytes(2, DEFAULT_ENDIAN) + final_bytes
        with open(seedfile, 'wb') as sfp:
            sfp.write(final_bytes)
        command =  [CMD, '/C', CSPY_SCRIPT]
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e)
        finally:
            print(output.decode())