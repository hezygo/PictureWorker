# -*- encoding: utf-8 -*-
"""
@File        :server.py
@Desc        :服务端
@Date        :2022-03-03 10:41
"""

import threading
import traceback
from datetime import datetime

import zmq
from zmq.auth.thread import ThreadAuthenticator

from constant import KEEP_ALIVE_INTERVAL,KEEP_ALIVE_TOPIC

class RpcServer:
    def __init__(self):
        self.__functions = {}
        self.__context = zmq.Context()
        self.__socket_rep = self.__context.socket(zmq.REP)
        self.__socket_pub = self.__context.socket(zmq.PUB)
        self.__active = False
        self.__thread = None
        self.__authenticator = None
        self._register(KEEP_ALIVE_TOPIC, lambda n: n)

    def is_active(self):
        return self.__active

    def start(self, rep_address, pub_address, server_secretkey_path = ""):
        if self.__active:
            return

        if server_secretkey_path:
            self.__authenticator = ThreadAuthenticator(self.__context)
            self.__authenticator.start()
            self.__authenticator.configure_curve(
                domain="*", 
                location=zmq.auth.CURVE_ALLOW_ANY
            )

            publickey, secretkey = zmq.auth.load_certificate(server_secretkey_path)
            
            self.__socket_pub.curve_secretkey = secretkey
            self.__socket_pub.curve_publickey = publickey
            self.__socket_pub.curve_server = True

            self.__socket_rep.curve_secretkey = secretkey
            self.__socket_rep.curve_publickey = publickey
            self.__socket_rep.curve_server = True

        self.__socket_rep.bind(rep_address)
        self.__socket_pub.bind(pub_address)

        self.__active = True
        
        self.__thread = threading.Thread(target=self.run)
        self.__thread.start()

    def stop(self):
        if not self.__active:
            return
        
        self.__active = False

    def join(self):
        # Wait for RpcServer thread to exit
        if self.__thread and self.__thread.is_alive():
            self.__thread.join()
        self.__thread = None

    def run(self):
        start = datetime.utcnow()
        while self.__active:
            # Use poll to wait event arrival, waiting time is 1 second
            cur = datetime.utcnow()
            delta = cur - start
            if delta >= KEEP_ALIVE_INTERVAL:
                start = cur
                self.publish(KEEP_ALIVE_TOPIC, str(cur))
                
            if not self.__socket_rep.poll(1000):
                continue
            
            req = self.__socket_rep.recv_json()
            name, args, kwargs = req
            try:
                func = self.__functions[name]
                r = func(*args, **kwargs)
                rep = [True, r]
            except Exception as e:
                rep = [False, traceback.format_exc()]
            self.__socket_rep.send_json(rep)
            #start = datetime.utcnow()

        self.__socket_pub.unbind(self.__socket_pub.LAST_ENDPOINT)
        self.__socket_rep.unbind(self.__socket_rep.LAST_ENDPOINT)

    def publish(self, topic, data):
        self.__socket_pub.send_json([topic, data])
        
    def register(self, func):
        return self._register(func.__name__, func)

    def _register(self, name, func):
        self.__functions[name] = func