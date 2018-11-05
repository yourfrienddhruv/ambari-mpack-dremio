#!/usr/bin/env python
import os

from resource_management.libraries.functions.default import default
from resource_management.libraries.script.script import Script

# a map of the Ambari role to the component name
# for use with <stack-root>/current/<component>
SERVER_ROLE_DIRECTORY_MAP = {
    'DREMIO_COORDINATOR' : 'dremio-coordinator',
}


component_directory = Script.get_component_from_role(SERVER_ROLE_DIRECTORY_MAP, "DREMIO_COORDINATOR")
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()
stack_root = Script.get_stack_root()
# New Cluster Stack Version that is defined during the RESTART of a Rolling Upgrade
version = default("/commandParams/version", None)
stack_name = default("/hostLevelParams/stack_name", None)
#e.g. /var/lib/ambari-agent/cache/stacks/HDP/$VERSION/services/DREMIO/package
service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
cluster_name = str(config['clusterName'])
ambari_server_hostname = config['clusterHostInfo']['ambari_server_host'][0]


dremio_user = config['configurations']['dremio-env']['dremio_user']
dremio_group = config['configurations']['dremio-env']['dremio_group']
dremio_home_dir = config['configurations']['dremio-env']['dremio_home_dir']
dremio_pid_dir = config['configurations']['dremio-env']['dremio_pid_dir']
dremio_log_dir = config['configurations']['dremio-env']['dremio_log_dir']
dremio_install_dir = config['configurations']['dremio-env']['dremio_install_dir']
dremio_bin_dir = config['configurations']['dremio-env']['dremio_bin_dir']
dremio_pid_file = os.path.join(dremio_pid_dir, 'dremio.pid')


configurations = config['configurations']['flink-ambari-config']

download_url = configurations['flink_download_url']
dremio_conf_content = configurations['dremio_conf']
dremio_env_content = configurations['dremio_env']


# configurations of HDFS
namenode_host = default("/clusterHostInfo/namenode_host", [])
namenode_host.sort()
namenode_address = None
if 'dfs.namenode.rpc-address' in config['configurations']['hdfs-site']:
    namenode_rpcaddress = config['configurations']['hdfs-site']['dfs.namenode.rpc-address']
    namenode_address = format("hdfs://{namenode_rpcaddress}")
else:
    namenode_address = config['configurations']['core-site']['fs.defaultFS']
# To judge whether the namenode HA mode
dfs_ha_enabled = False
dfs_ha_nameservices = default("/configurations/hdfs-site/dfs.nameservices", None)
dfs_ha_namenode_ids = default(format("/configurations/hdfs-site/dfs.ha.namenodes.{dfs_ha_nameservices}"), None)
dfs_ha_namemodes_ids_list = []
if dfs_ha_namenode_ids:
    dfs_ha_namemodes_ids_list = dfs_ha_namenode_ids.split(",")
    dfs_ha_namenode_ids_array_len = len(dfs_ha_namemodes_ids_list)
    if dfs_ha_namenode_ids_array_len > 1:
        dfs_ha_enabled = True
if dfs_ha_enabled:
    namenode_address = format('hdfs://{dfs_ha_nameservices}')
    logical_name = dfs_ha_nameservices
