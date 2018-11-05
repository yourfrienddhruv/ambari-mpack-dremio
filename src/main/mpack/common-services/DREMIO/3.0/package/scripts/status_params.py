#!/usr/bin/env python
from resource_management import *

config = Script.get_config()

dremio_pid_dir = config['configurations']['dremio-env']['dremio_pid_dir']
dremio_pid_file = os.path.join(dremio_pid_dir, 'dremio.pid')

