class ZbeeCluster:
    def __init__(self, cluster_id) -> None:
        self.id = cluster_id
        self.cmd_dict = {} # key: cmdID, value: ZbeeCommand