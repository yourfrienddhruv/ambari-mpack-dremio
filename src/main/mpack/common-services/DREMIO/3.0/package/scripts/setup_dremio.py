#!/usr/bin/env python

from resource_management import *


def setup_dremio(env):
    import params
    env.set_params(params)
    Logger.info("Configure Dremio Service")


def dremio_configure(env):
    import params
    env.set_params(params)
    File(format("{hue_conf_dir}/pseudo-distributed.ini"),
         content = InlineTemplate(params.hue_pseudodistributed_content),
         owner = params.dremio_user
         )
