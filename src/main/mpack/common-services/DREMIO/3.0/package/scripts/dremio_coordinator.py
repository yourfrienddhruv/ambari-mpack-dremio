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
        import params
        env.set_params(params)
        Execute("service dremio start")
        Execute('ps -ef | grep "dremio" | grep -v grep | awk \'{print $2}\' | tail -n 1 > ' + params.dremio_pid_file,
                user=params.dremio_user
                )


    def stop(self, env):
        import params
        env.set_params(params)
        # Kill the process of Airflow
        Execute("service dremio stop")
        File(params.dremio_pid_file,
             action = "delete",
             owner = params.dremio_user
             )


    def status(self, env):
        import params
        env.set_params(params)
        #use built-in method to check status using pidfile
        check_process_status(params.dremio_pid_file)


if __name__ == "__main__":
    DremioCordinator().execute()

