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

download_url = 'https://download.dremio.com/community-server/3.0.0-201810262305460004-5c90d75/dremio-community-3.0.0-201810262305460004-5c90d75.tar.gz'

dremio_user = config['configurations']['dremio-env']['dremio_user']
dremio_group = config['configurations']['dremio-env']['dremio_group']
dremio_home_dir = config['configurations']['dremio-env']['dremio_home_dir']
dremio_pid_dir = config['configurations']['dremio-env']['dremio_pid_dir']
dremio_log_dir = config['configurations']['dremio-env']['dremio_log_dir']
dremio_install_dir = config['configurations']['dremio-env']['dremio_install_dir']
dremio_bin_dir = config['configurations']['dremio-env']['dremio_bin_dir']
dremio_pid_file = dremio_pid_dir + 'dremio.pid'

hue_pseudodistributed_content = config['configurations']['pseudo-distributed.ini']['content']