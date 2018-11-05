#!/usr/bin/env python
import os


from resource_management.libraries.functions.default import default
from resource_management.libraries.script.script import Script
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import get_kinit_path, stack_select, conf_select
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources

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

dremio_conf_content = config['configurations']['dremio-env']['dremio_conf']
dremio_env_content = config['configurations']['dremio-env']['dremio_env']
dremio_user = config['configurations']['dremio-env']['dremio_user']
dremio_group = config['configurations']['dremio-env']['dremio_group']
dremio_home_dir = config['configurations']['dremio-env']['dremio_home_dir']
dremio_pid_dir = config['configurations']['dremio-env']['dremio_pid_dir']
dremio_log_dir = config['configurations']['dremio-env']['dremio_log_dir']
dremio_install_dir = config['configurations']['dremio-env']['dremio_install_dir']
dremio_bin_dir = config['configurations']['dremio-env']['dremio_bin_dir']
dremio_pid_file = os.path.join(dremio_pid_dir, 'dremio.pid')


configurations = config['configurations']['dremio-site']

download_url = configurations['dremio_download_url']



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

# configurations of Zookeeper
zookeeper_hosts = default("/clusterHostInfo/zookeeper_hosts", [])
zookeeper_hosts.sort()
zookeeper_client_port = default('/configurations/zoo.cfg/clientPort', None)
zookeeper_host_ports = []
zookeeper_host_port = ''
zookeeper_rest_url = ''
if len(zookeeper_hosts) > 0:
    if zookeeper_client_port is not None:
        for i in range(len(zookeeper_hosts)):
            zookeeper_host_ports.append(format(zookeeper_hosts[i] + ":{{zookeeper_client_port}}"))
    else:
        for i in range(len(zookeeper_hosts)):
            zookeeper_host_ports.append(format(zookeeper_hosts[i] + ":2181"))
    zookeeper_host_port = ",".join(zookeeper_host_ports)



hdfs_user = config['configurations']['hadoop-env']['hdfs_user']

#for create_hdfs_directory
security_enabled = config['configurations']['cluster-env']['security_enabled']
security_param = "true" if security_enabled else "false"
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hdfs_site = config['configurations']['hdfs-site']
default_fs = config['configurations']['core-site']['fs.defaultFS']

dfs_type = default("/commandParams/dfs_type", "")
# node hostname
hostname = config["hostname"]
hdfs_principal_name = default('/configurations/hadoop-env/hdfs_principal_name', 'missing_principal').replace("_HOST", hostname)

import functools
#create partial functions with common arguments for every HdfsResource call
#to create hdfs directory we need to call params.HdfsResource in code
HdfsResource = functools.partial(
    HdfsResource,
    user=hdfs_user,
    hdfs_resource_ignore_file="/var/lib/ambari-agent/data/.hdfs_resource_ignore",
    security_enabled=security_enabled,
    keytab=hdfs_user_keytab,
    kinit_path_local=kinit_path_local,
    hadoop_bin_dir=hadoop_bin_dir,
    hadoop_conf_dir=hadoop_conf_dir,
    principal_name=hdfs_principal_name,
    hdfs_site=hdfs_site,
    default_fs=default_fs,
    immutable_paths=get_not_managed_resources(),
    dfs_type=dfs_type
)