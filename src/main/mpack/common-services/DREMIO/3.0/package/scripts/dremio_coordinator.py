#!/usr/bin/env python
import grp, pwd, os

from resource_management import Group, User
from resource_management.core.logger import Logger
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.functions.format import format
from resource_management.libraries.script.script import Script
from resource_management.core.resources.system import Directory, File, Execute
from resource_management.core.source import Template, InlineTemplate, DownloadSource

class DremioCordinator(Script):

    def install(self, env):
        import params
        env.set_params(params)

        # create dremio user
        try:
            grp.getgrnam(params.dremio_group)
        except KeyError:
            Logger.info(format("Creating group '{params.dremio_group}' for dremio Service"))
            Group(
                group_name = params.dremio_group,
                ignore_failures = True
            )
        try:
            pwd.getpwnam(params.dremio_user)
        except KeyError:
            Logger.info(format("Creating user '{params.dremio_user}' for dremio Service"))
            User(
                username = params.dremio_user,
                groups = [params.dremio_group],
                ignore_failures = True
            )

        if not os.path.exists("/home/{0}".format(params.dremio_user)):
            Directory(params.dremio_local_home_dir,
                      mode=0700,
                      cd_access='a',
                      owner=params.dremio_user,
                      group=params.dremio_group,
                      create_parents=True
                      )


        # create the pid and log dir
        Directory([params.dremio_log_dir, params.dremio_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.dremio_user,
                  group=params.dremio_group,
                  create_parents=True
                  )

        File('/tmp/dremio.tar.gz',
             content = DownloadSource(params.download_url),
             mode = 0644
             )

        Execute(
            ('tar', 'zxvf', '/tmp/dremio.tar.gz', '-C', params.dremio_bin_dir),
            sudo=True
        )

        Execute(
            ('ln', '-s', params.dremio_install_dir, params.dremio_bin_dir),
            sudo=True
        )

        Execute(
            ('cp', params.dremio_install_dir + '/share/dremio.service', '/etc/systemd/system/dremio.service'),
            sudo=True
        )

        Execute(
            ('systemctl', 'daemon-reload'),
            sudo=True
        )

        Execute(
            ('systemctl', 'enable ', 'dremio'),
            sudo=True
        )


    def configure(self, env):
        import params
        env.set_params(params)
        setup_dremio()

    def start(self, env):
        '''
        Logger.info("Starting Elasticsearch ... ")
        start_command = format('{elasticsearch_home}/bin/elasticsearch -Des.node.name={node_name} -Des.node.master={isMaster} -Des.node.data={isData} -Des.http.port={port} -Des.path.data={path_data} -d -p {pid_file}')

        Execute(
                start_command,
                environment={
                   'JAVA_HOME': params.java64_home,
                   'ES_HEAP_SIZE': memory
                },
                user=params.elasticsearch_config_user
        )
        '''
        pass


    def stop(self, env):
        '''
        pid_file = config['pid_file']

        Execute(
                format('kill `cat {pid_file}`'),
                user=params.elasticsearch_config_user,
                only_if=format('test -f {pid_file}')
        )

        File(pid_file,
             action="delete"
        )
        '''
        pass

    def status(self, env):
        '''
        check_process_status(pid_file)
        '''
        pass

if __name__ == "__main__":
    ExampleMaster().execute()

