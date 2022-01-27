from nni.tools.nnictl.nnictl_utils import trial_ls
from nni.tools.nnictl.config_utils import Experiments
from nni.tools.nnictl.launcher import launch_experiment
from nni.experiment import LegacyExperiment
from nni.tools.nnictl.nnictl_utils import stop_experiment
from nni.tools.nnictl.launcher import manage_stopped_experiment
from nni.tools.nnictl.nnictl import parse_args

import os
import sys
import json
import time
import random
import select
import socket
import string
from argparse import Namespace
from socket import AF_INET, SOCK_STREAM, SOMAXCONN

if __name__ == '__main__':
    # argvs = ['/home/geminit/.conda/envs/nni/bin/nnictl', 'create', '--config', '/home/geminit/work/nni/deamo/config.yml']
    # sys.argv = argvs
    # parse_args()
    args = Namespace()
    setattr(args, "debug", False)
    setattr(args, "foreground", False)
    setattr(args, "port", 8888)

    experiment_config = {
        'authorName': 'HTSC',
        'experimentName': 'nni_trainning',
        'trialConcurrency': 1,
        'maxExecDuration': 31536000,
        'maxTrialNum': 100,
        'trainingServicePlatform': 'local',
        'searchSpacePath': '/home/geminit/work/nni/deamo/search_space.json',
        'useAnnotation': False,
        'tuner': {
            'builtinTunerName': 'TPE',
            'classArgs': {
                'optimize_mode': 'minimize'
            }
        },
        'trial': {
            'command': 'python3 mnist.py',
            'codeDir': '/home/geminit/work/nni/deamo/.',
            'gpuNum': 0
        }
    }

    experiment_config2 = {
        "authorName": "HTSC",
        "experimentName": "nni_trainning",
        "trialConcurrency": 1,
        "maxExecDuration": 604800,
        "maxTrialNum": 10,
        "trainingServicePlatform": "local",
        "searchSpacePath": '/home/geminit/work/svn/HTSC/trunk/HTSC-4.0/hydrator2.4.0/annotation-train-plugins/src/main/resources/nni/1/search_space.json',
         "useAnnotation": False,
         "tuner": {
             "builtinTunerName": "TPE",
             "classArgs": {
                 "optimize_mode": "maximize"
             }
         },
        "trial": {
            "command": 'python3 runner.py',
            "codeDir": '/home/geminit/work/svn/HTSC/trunk/HTSC-4.0/hydrator2.4.0/annotation-train-plugins/src/main/resources/nni/1',
            "gpuNum": 0
        }
    }


    experiment_id = ''.join(random.sample(string.ascii_letters + string.digits, 8))

    launch_experiment(args, experiment_config, 'new', experiment_id)
