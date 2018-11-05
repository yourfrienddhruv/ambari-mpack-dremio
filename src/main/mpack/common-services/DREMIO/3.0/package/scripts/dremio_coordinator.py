#!/usr/bin/env python
import grp
import pwd
import os
from resource_management import Group, User
from resource_management.core.logger import Logger
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.libraries.functions.format import format
from resource_management.libraries.script.script import Script
from resource_management.core.resources.system import Directory, File, Execute, Link
from resource_management.core.source import DownloadSource, InlineTemplate


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
                group_name=params.dremio_group,
                ignore_failures=True
            )
        try:
            pwd.getpwnam(params.dremio_user)
        except KeyError:
            Logger.info(format("Creating user '{params.dremio_user}' for dremio Service"))
            User(
                username=params.dremio_user,
                groups=[params.dremio_group],
                ignore_failures=True
            )

        if not os.path.exists("{0}".format(params.dremio_user)):
            Directory(params.dremio_home_dir,
                      mode=0700,
                      cd_access='a',
                      owner=params.dremio_user,
                      group=params.dremio_group,
                      create_parents=True
                      )

        params.HdfsResource('/user/' + params.dremio_user,
                        type="directory",
                        action="create_on_execute",
                        owner=params.dremio_user,
                        mode=0755)


        # create the pid and log dir
        Directory([params.dremio_log_dir, params.dremio_pid_dir, params.dremio_install_dir, params.dremio_bin_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.dremio_user,
                  group=params.dremio_group,
                  create_parents=True
                  )


        File('/tmp/dremio.tar.gz',
             content=DownloadSource(params.download_url),
             mode=0644
             )

        Execute(
            ('tar', 'zxvf', '/tmp/dremio.tar.gz', '-C', params.dremio_install_dir, '--strip-components', '1'),
            sudo=True
        )

        Link(params.dremio_install_dir,
            to=params.dremio_bin_dir,
            hard=True,
            ignore_failures=True
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
            ('systemctl', 'enable', 'dremio'),
            sudo=True
        )

    def configure(self, env):
        import params
        env.set_params(params)

        properties_content = InlineTemplate(params.dremio_conf_content)
        File(format("{dremio_home_dir}/dremio.conf"),
             content=properties_content,
             owner=params.dremio_user)

        properties_content = InlineTemplate(params.dremio_env_content)
        File(format("{dremio_home_dir}/dremio-env"),
             content=properties_content,
             owner=params.dremio_user)

    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        Execute('systemctl', 'start', 'dremio')

    def stop(self, env):
        Execute('systemctl', 'stop', 'dremio')

    def restart(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        Execute('systemctl', 'restart', 'dremio')
        
    def status(self, env):
        import status_params
        env.set_params(status_params)
        # use built-in method to check status using pidfile
        check_process_status(status_params.dremio_pid_file)


if __name__ == "__main__":
    DremioCordinator().execute()

