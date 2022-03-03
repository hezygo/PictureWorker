# -*- encoding: utf-8 -*-
"""
@File        :certificate.py
@Desc        :证书生成
@Date        :2022-03-03 10:20
"""
import os

import zmq
from pathlib import Path

def generate_certificates(name):
    """
    Generate CURVE certificate files for zmq authenticator.
    """
    keys_path = Path.cwd().joinpath("certificates")
    if not keys_path.exists():
        os.mkdir(keys_path)

    zmq.auth.create_certificates(keys_path, name)