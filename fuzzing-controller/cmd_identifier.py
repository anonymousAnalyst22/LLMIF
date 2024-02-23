import logging
logging.basicConfig(
    format='[%(name)s] %(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/fuzzing.log',
    level=logging.INFO,
    filemode='w')
import os
import time
import json
import sys
from collections import OrderedDict, defaultdict
sys.path.insert(0, 'lib')
from lib.controller_constants import *
from lib.basic_type import *
from lib.zigbee_device import ZigbeeDevice, ZbeeEndpoint, ZbeeCluster, ZbeeCommand, ZbeeAttribute
from zbee_controller import ZbeeController
from pprint import pprint, pformat

cmd_scanning_path = 'command-re/command-scanning/'
zcl_cluster_list_path = "command-re/spec/results/cluster-list.txt"

ZCLREPO = 'zcl'
LIBZIGPYREPO = 'zigpy'
LIBHERDSMANREPO = 'herdsman'
APPREPO = 'app'

STATISTIC_ANALYSIS = True

#REPO_NAMES = [ZCLREPO, LIBZIGPYREPO, LIBHERDSMANREPO, APPREPO]
REPO_NAMES = [ZCLREPO]
CMD_JSON_DICT = {
    ZCLREPO: 'command-re/spec/results/zcl-cmd.json', # SPEC
    #LIBZIGPYREPO: 'command-re/library/results/zigpy-cmd.json', # Zigpy
    #LIBHERDSMANREPO: 'command-re/library/results/herdsman-cmd.json', # Herdsman
    #APPREPO: 'command-re/app/results/'
}
ATTR_JSON_DICT = {
    ZCLREPO: 'command-re/spec/results/zcl-attr.json', # SPEC
    #LIBZIGPYREPO: 'command-re/library/results/zigpy-attr.json', # Zigpy
    #LIBHERDSMANREPO: 'command-re/app/results/herdsman-attr.json' # Herdsman
    #APPREPO: ?
}

def hex_to_int(hexstr):
    return int(hexstr, 16)

class CmdIdentifier:

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zcl_cluster_list = self.__load_zcl_cluster_list(zcl_cluster_list_path)
        self.cmd_repo_dict = {}
        self.attr_repo_dict = {}

    '''
    helper functions
    '''
    def file_exist(self, path, fname):
        dir = os.listdir(path)
        for f in dir:
            if fname == f:
                return True
        return False

    def __load_zcl_cluster_list(self, fname):
        """
        General knowledge about defined cluster ids in ZCL specification.
        """
        zcl_cluster_list = []
        with open(fname, 'r') as f:
            for line in f.readlines():
                cluster_id = line.split('+++')[1].strip()
                zcl_cluster_list.append(hex_to_int(cluster_id))
        return zcl_cluster_list

    """
    Statistical analysis function
    """
    def _summarize_cmd_dict(self, source=ZCLREPO, cmd_dict={}):
        """
        In this function, we want to achieve the following goals.
        (1) Analyze the number of clusters and commands in each cluster
        (1) Summarize the different values in the following field, such that we can derive their value range
            * MO
            * Attribute types
            * Octets
        """
        n_clusters = 0
        n_cmds = 0
        if source == ZCLREPO:
            cluster_ncmd_dict = defaultdict(int)
            cmd_mos = set()
            attr_types = set()
            attr_octs = set()
            type_frequency_dict = defaultdict(int)
            oct_frequency_dict = defaultdict(int)
            for cluster_id, cluster_info in cmd_dict.items():
                cluster_name = cluster_info['name']
                cluster_cmds = cluster_info['cmds']
                cluster_intro = f"{cluster_id} {cluster_name}"
                for cmd_id, cmd_info in cluster_cmds.items():
                    cluster_ncmd_dict[cluster_intro] += 1
                    cmd_mos.add(cmd_info['mo'])
                    payloads = cmd_info['payload']
                    for payload_id, payload_info in payloads.items():
                        attr_type = payload_info['type']
                        attr_types.add(attr_type)
                        type_frequency_dict[attr_type] += 1
                        #attr_oct = payload_info['octs']
                        #attr_octs.add(attr_oct)
                        #oct_frequency_dict[attr_oct] += 1
            n_clusters = len(list(cluster_ncmd_dict.keys()))
            n_cmds = sum([cluster_ncmd_dict[i] for i in list(cluster_ncmd_dict.keys())])
            self.logger.info(f"Command statistics from source {source}:\n\
                                        n_clusters={n_clusters}, n_cmds={n_cmds}, n_param_types={len(list(type_frequency_dict.keys()))}")
        elif source in [LIBHERDSMANREPO, LIBZIGPYREPO]:
            n_devices = len(list(cmd_dict.keys()))
            n_clusters = 0
            n_cmds = 0
            for dev, dev_info in cmd_dict.items():
                for cluster_id, cluster_info in dev_info.items():
                    n_clusters += 1
                    cmd_info = cluster_info['cmds']
                    n_cmds += len(list(cmd_info.keys()))
            self.logger.info(f"Command statistics from source {source}:\n\
                                        n_devices={n_devices}, n_clusters={n_clusters}, n_cmds={n_cmds}")

    
    def _summarize_attr_dict(self, source='zcl', attr_dict={}):
        """
        In this function, we want to achieve the following goals.
        (1) Analyze the number of clusters and attributes in each cluster
        (2) Summarize the different values in the following field, such that we can derive their value range
            * Attribute types
            * Value ranges
            * Access control
            * Default
            * MO
        """
        cluster_nattr_dict = defaultdict(int)
        attr_types = set()
        attr_ranges = set()
        attr_acs = set()
        attr_defaults = set()
        attr_mos = set()
        type_frequency_dict = defaultdict(int)
        range_frequency_dict = defaultdict(int)
        ac_frequency_dict = defaultdict(int)
        default_frequency_dict = defaultdict(int)
        mo_frequency_dict = defaultdict(int)
        for cluster_id, cluster_info in attr_dict.items():
            cluster_name = cluster_info['name']
            cluster_attrs = cluster_info['attrs']
            cluster_intro = f"{cluster_id} {cluster_name}"
            for attr_id, attr_info in cluster_attrs.items():
                cluster_nattr_dict[cluster_intro] += 1
                attr_type = attr_info['type']
                attr_range = attr_info['range']
                attr_ac = attr_info['access']
                attr_default = attr_info['default']
                attr_mo = attr_info['mo']
                attr_types.add(attr_type); type_frequency_dict[attr_type] += 1
                attr_ranges.add(attr_range); range_frequency_dict[attr_range] += 1
                attr_acs.add(attr_ac); ac_frequency_dict[attr_ac] += 1
                attr_defaults.add(attr_default); default_frequency_dict[attr_default] += 1
                attr_mos.add(attr_mo.lower()); mo_frequency_dict[attr_mo.lower()] += 1
        n_clusters = len(list(cluster_nattr_dict.keys()))
        n_attrs = sum([cluster_nattr_dict[i] for i in list(cluster_nattr_dict.keys())])

    def __summarize_scanning_results(self, target_device:'ZigbeeDevice'):
        self.logger.info(f"Scanning result statistics:\n\
                                    {target_device.n_eps} endpoints, {target_device.n_clusters} clusters,\n\
                                    {target_device.n_ZCLcmds} ZCL commands, and {target_device.n_manucmds} manufacturer-specific commands.")
        #self.logger.info(f"{pformat(target_device.ZCLcmd_dict)}")

    """
    Repo operation function
    """
    def load_repo(self, device_hash_sig):
        # Load command formats from different sources
        for repo_name in REPO_NAMES:
            self.logger.info(f"Loading Repository {repo_name} ......")
            if repo_name == ZCLREPO:
                self.cmd_repo_dict[ZCLREPO] = json.load(open(CMD_JSON_DICT[ZCLREPO]), object_pairs_hook=OrderedDict)
            elif repo_name == APPREPO:
                if self.file_exist(CMD_JSON_DICT[APPREPO], f"{device_hash_sig}.json"):
                    app_file = CMD_JSON_DICT[APPREPO] + f"{device_hash_sig}.json"
                    self.cmd_repo_dict[APPREPO] = json.load(open(app_file), object_pairs_hook=OrderedDict)
            elif repo_name in [LIBHERDSMANREPO, LIBZIGPYREPO]:
                self.cmd_repo_dict[repo_name] = json.load(open(CMD_JSON_DICT[repo_name]), object_pairs_hook=OrderedDict)
        
        # Load attributes from ZCL repo
        self.attr_repo_dict[ZCLREPO] = json.load(open(ATTR_JSON_DICT[ZCLREPO]), object_pairs_hook=OrderedDict)

        if STATISTIC_ANALYSIS:
            for repo_name in REPO_NAMES:
                self._summarize_cmd_dict(repo_name, self.cmd_repo_dict[repo_name])

        self.logger.info(f"Loading Repository ...... Finished")

    def cmd_scanning(self, zbee_controller:'ZbeeController', target_file=None):
        '''
        All scanning results are stored under the folder 'results/command-scanning/'
        Each file is named with 'sighash.txt'
        This function first searches if there is existing file to avoid duplicated search.
        If not, initiate the search
        '''
        f_scan_file = None
        device_hash_file = cmd_scanning_path + '{}.txt'.format(zbee_controller.target_device.hash_sig)
        # (1) Locate the scanning result file
        if self.file_exist(cmd_scanning_path, target_file):
            f_scan_file = f"{cmd_scanning_path}{target_file}"
        elif self.file_exist(cmd_scanning_path, '{}.txt'.format(zbee_controller.target_device.hash_sig)):
            f_scan_file = device_hash_file

        if f_scan_file is not None:
            # Parse the file f_scanfile
            zbee_controller.load_scanning_result(f_scan_file)
        else:
            # Initiate the ZCL + manu command scanning, and store the result into file
            start_time = time.time()
            zbee_controller.cmd_scan(vendorSpecific=False)
            zbee_controller.cmd_scan(vendorSpecific=True)
            end_time = time.time()
            self.logger.info(f"Elapsed time for scanning devices: {(end_time-start_time)*1.0/60} mins.")
            zbee_controller.store_scaning_result(device_hash_file)

        if STATISTIC_ANALYSIS:
            self.__summarize_scanning_results(zbee_controller.target_device)

        self.logger.info(f"Scanning devices ...... Finished")

    def reverse_engineering(self, zbee_controller:'ZbeeController', skipped_genetic_commands=[]):
        """
        Inside controller.target_device, it stores two dict: ZCLcmd_dict and manucmd_dict
        Match it with self.cmd_repo_dict
        (1) Create the endpoint and cluster accordingly.
        (1) Match ZCLcmd_dict with zcl_repo, and build cluster.command_list
        (3) Match the attribute list in attr_repo, and build cluster.attribute_list.
        """
        target_device = zbee_controller.target_device
        if ZCLREPO in self.cmd_repo_dict.keys(): # Reverse engineer general commands and ZCL commands
            # 0. First parse the command and attributes in the Genetic cluster
            ZCLcmd_dict = target_device.ZCLcmd_dict
            zcl_cmd_repo_dict = self.cmd_repo_dict[ZCLREPO]
            zcl_attr_repo_dict = self.attr_repo_dict[ZCLREPO]
            general_attrs = []
            general_commands = []
            # 1. Handle genetic Zigbee commands and attributes
            for attr_idhex, attr_info_dict in zcl_attr_repo_dict[GENERAL_CLUSTER_ID][ATTRS_KEYWORD].items():
                general_attrs.append(ZbeeAttribute(attr_idhex, attr_info_dict))
            for cmd_idhex, cmd_info_dict in zcl_cmd_repo_dict[GENERAL_CLUSTER_ID][CMDS_KEYWORD].items():
                if int(cmd_idhex, 16) not in skipped_genetic_commands:
                    general_commands.append(ZbeeCommand(cmd_idhex, cmd_info_dict, COMMAND_GENETIC))
            # 2. Handle ZCL commands and attributes
            for ep_desc, device_cmd_list in ZCLcmd_dict.items():
                device_supporoted_cmd_idhexs = [x[0] for x in device_cmd_list]
                device_supporoted_cmd_idints = [int(x) for x in device_supporoted_cmd_idhexs]
                ep_id, profile_id, cluster_id = map(hex_to_int, ep_desc.split(':'))
                # 1. Fetch the corresponding endpoint. If not found, create a new one.
                endpoint = target_device.endpoint_lookup(ep_id)
                if not endpoint:
                    endpoint = ZbeeEndpoint(ep_id, profile_id)
                    target_device.add_endpoint(endpoint)
                # 2. Fetch the corresponding cluster. If not found, create a new one.
                device_cluster = endpoint.cluster_lookup(cluster_id)
                if not device_cluster:
                    cluster_manu_specific = True if cluster_id not in self.zcl_cluster_list else False
                    device_cluster = ZbeeCluster(cluster_id, cluster_manu_specific)
                    endpoint.add_cluster(device_cluster)
                # 3. Match and construct the command list
                for cluster_id, cluster_info in zcl_cmd_repo_dict.items():
                    if hex_to_int(cluster_id) != device_cluster.cluster_id:
                        continue
                    device_cluster.cluster_name = cluster_info[NAME_KEYWORD]
                    cluster_supported_cmd_idhexs = list(cluster_info[CMDS_KEYWORD].keys())
                    cluster_supported_cmd_idints = [hex_to_int(x) for x in cluster_supported_cmd_idhexs]
                    # (1). The command is in device_supporoted_cmds and in cluster_supported_cmds: Perfect match, build the command prototype
                    # (2). The command is in device_supporoted_cmds but not in cluster_supported_cmds: A stange command provided by manufacturers and marked as ZCL standard comamnds
                    # (3). The command is not in device_supporoted_cmds but in cluster_supported_cmds: Might be interested to check the MO property of this command
                    perfect_match_cmds = [x for x in cluster_supported_cmd_idhexs if hex_to_int(x) in device_supporoted_cmd_idints]
                    strange_cmds = [x for x in device_supporoted_cmd_idhexs if int(x) not in cluster_supported_cmd_idints]
                    missing_cmds = [x for x in cluster_supported_cmd_idhexs if hex_to_int(x) not in device_supporoted_cmd_idints]
                    # (1) Handle perfect_match_cmds: Generate ZbeeCommand, and store it inside device's cluster.
                    for perfect_cmd_idhex in perfect_match_cmds:
                        perfect_cmd = ZbeeCommand(hex_to_int(perfect_cmd_idhex), cluster_info[CMDS_KEYWORD][perfect_cmd_idhex], command_flag=COMMAND_ZCL)
                        device_cluster.add_command(perfect_cmd)
                    for stange_cmd_idhex in strange_cmds:
                        strange_cmd_info_dict = {
                            DESCRIPTION_KEYWORD: 'StrangeCommand',
                        }
                        strange_cmd = ZbeeCommand(int(stange_cmd_idhex), strange_cmd_info_dict, command_flag=COMMAND_STRANGE)
                        device_cluster.add_command(strange_cmd)
                    # (3) Handle missing command: Generate ZbeeCommand, mark it as missing, and store it inside device's cluster.
                    for missing_cmd_idhex in missing_cmds:
                        missing_cmd = ZbeeCommand(hex_to_int(missing_cmd_idhex), cluster_info['cmds'][missing_cmd_idhex], command_flag=COMMAND_MISSING_ZCL)
                        device_cluster.add_command(missing_cmd)
                    # (4) Add general commands
                    for general_cmd in general_commands:
                        device_cluster.add_command(general_cmd)
                    self.logger.info(f"For cluster {cluster_id}, # zcl commands, missing_cmds, strange_cmds, general_cmds = \
                                     {len(perfect_match_cmds), len(missing_cmds), len(strange_cmds), len(general_commands)}")
                # 4. Generate the attribute list
                for cluster_id, cluster_info  in zcl_attr_repo_dict.items():
                    if hex_to_int(cluster_id) != device_cluster.cluster_id:
                        continue
                    cluster_supported_attr_idhexs = list(cluster_info[ATTRS_KEYWORD].keys())
                    for attr_idhex in cluster_supported_attr_idhexs:
                        attr_info_dict = cluster_info[ATTRS_KEYWORD][attr_idhex]
                        attribute = ZbeeAttribute(attr_idhex, attr_info_dict)
                        device_cluster.add_attribute(attribute)
                    # Add general commands
                    for general_attr in general_attrs:
                        device_cluster.add_attribute(general_attr)

        manu_cmd_dict = target_device.manucmd_dict
        n_reversed_cmds_from_app = 0
        n_reversed_cmds_from_project = 0
        for ep_desc, device_cmd_list in manu_cmd_dict.items(): # Reverse engineer manu-specific commands
            # (1) Build endpoint and cluster for each scanned manu-specific ep:pid:cid:cmd_id record
            ep_id, profile_id, cluster_id = map(hex_to_int, ep_desc.split(':'))
            endpoint = target_device.endpoint_lookup(ep_id)
            if not endpoint:
                endpoint = ZbeeEndpoint(ep_id, profile_id)
                target_device.add_endpoint(endpoint)
            device_cluster = endpoint.cluster_lookup(cluster_id)
            if not device_cluster:
                cluster_manu_specific = True
                device_cluster = ZbeeCluster(cluster_id, cluster_manu_specific)
                endpoint.add_cluster(device_cluster)
            scanned_cmd_idints = [x[0] for x in device_cmd_list]
            # (2) Identify commands from APP repo
            if APPREPO in self.cmd_repo_dict.keys():
                for repo_cid_hex, repo_cluster in self.cmd_repo_dict[APPREPO].items():
                    repo_pid = hex_to_int(repo_cluster["profile"])
                    # Look for the cid_pid matching between APP repo and scanned result
                    if hex_to_int(repo_cid_hex) == cluster_id and repo_pid == profile_id:
                        repo_cmd_idhexs = list(repo_cluster["cmds"].keys())
                        repo_cmd_idints = list(map(hex_to_int, repo_cmd_idhexs))
                        matched_cmds = [cmd_id for cmd_id in scanned_cmd_idints if cmd_id in repo_cmd_idints]
                        for matched_cmd_id in matched_cmds:
                            hex_id = repo_cmd_idhexs[repo_cmd_idints.index(matched_cmd_id)]
                            cmd_object = ZbeeCommand(matched_cmd_id, repo_cluster["cmds"][hex_id], COMMAND_MANU)
                            device_cluster.add_command(cmd_object)
                            n_reversed_cmds_from_app += 1
            # (3) Identify commands from Project repo
            if LIBZIGPYREPO in self.cmd_repo_dict.keys() and LIBHERDSMANREPO in self.cmd_repo_dict.keys():
                for project_name in [LIBZIGPYREPO, LIBHERDSMANREPO]:
                    project_cmd_dict = self.cmd_repo_dict[project_name]
                    # For each project cmd dict, we traverse all device model and their cluster_id:cmd_id pair
                    # Then we match with each scanned_cluster_id:scanned_cmd_id pair. If there is a match, we construct a command.
                    for dev_name, dev_info in project_cmd_dict.items():
                        for repo_cid_hex, repo_cluster in dev_info.items():
                            if hex_to_int(repo_cid_hex) == cluster_id:
                                #self.logger.info(f"Identified a matching cluster ID {cluster_id} in project {project_name} with dev_name={dev_name}")
                                repo_cmd_idhexes = repo_cluster['cmds'].keys()
                                repo_cmd_idints = list(map(hex_to_int, repo_cmd_idhexes))
                                matched_cmds = [cmd_id for cmd_id in scanned_cmd_idints if cmd_id in repo_cmd_idints]
                                #self.logger.info(f"Matched cmds: {matched_cmds}")
                                for matched_cmd_id in matched_cmds:
                                    hex_id = repo_cmd_idhexs[repo_cmd_idints.index(matched_cmd_id)]
                                    cmd_object = ZbeeCommand(matched_cmd_id, repo_cluster["cmds"][hex_id], COMMAND_MANU)
                                    device_cluster.add_command(cmd_object)
                                    n_reversed_cmds_from_project += 1
        self.logger.info(f"Successfully reverse engineered {n_reversed_cmds_from_app} manu commands from app and {n_reversed_cmds_from_project} from project")
    
    """
    Security checking function
    """
    def function_mo_checking(self, zbeeController:'ZbeeController'):
        self.logger.info(f"Initiate function mo checking ......")
        zcl_m_cmds = []; zcl_o_cmds = []
        strange_cmds = []; missing_cmds = []
        n_cmds = 0
        target_device = zbeeController.target_device
        for ep_id, endpoint in zbeeController.target_device.endpoint_dict.items():
            for cluster_id, cluster in endpoint.cluster_dict.items():
                command_list = cluster.command_list
                zcl_m_cmds += [cmd for cmd in command_list if cmd.command_flag == COMMAND_ZCL and cmd.mo is True]
                zcl_o_cmds += [cmd for cmd in command_list if cmd.command_flag == COMMAND_ZCL and cmd.mo is False]
                strange_cmds += [cmd for cmd in command_list if cmd.command_flag == COMMAND_STRANGE]
                missing_cmds += [cmd for cmd in command_list if cmd.command_flag == COMMAND_MISSING_ZCL]
                n_cmds += len(command_list)
        if STATISTIC_ANALYSIS:
            n_m_cmds = len(zcl_m_cmds); n_o_cmds = len(zcl_o_cmds)
            n_strange_cmds = len(strange_cmds); n_missing_cmds = len(missing_cmds)
            self.logger.info(f"     n_cmds, n_missing_cmds, n_strange_cmds = {n_cmds}, {n_missing_cmds}, {n_strange_cmds}")
            self.logger.info(f"     # supported zcl-m cmds = {n_m_cmds}, # supported zcl-o cmds = {n_o_cmds}")
            # Security check: If the missing command is a mandatory command required by ZCL
            for missing_cmd in missing_cmds:
                if missing_cmd.mo is True:
                    self.logger.warning(f"     ZCL mandatory command {missing_cmd.name} is missing")
        self.logger.info(f"Function mo checking...... Done")
