# -*- encoding: utf-8 -*-
"""
@File        :client.py
@Desc        :客户端
@Date        :2022-03-03 10:42
"""
import threading
from datetime import datetime
from functools import lru_cache

import zmq
from zmq.auth.thread import ThreadAuthenticator
from zmq.backend.cython.constants import NOBLOCK

from exception import RemoteException
from constant import KEEP_ALIVE_TOPIC,KEEP_ALIVE_TOLERANCE

class RpcClient:

    def __init__(self):
        self.__context = zmq.Context()
        self.__socket_req = self.__context.socket(zmq.REQ)
        self.__socket_req.setsockopt(zmq.LINGER, 0)
        #self.__poller = zmq.Poller()
        #self.__poller.register(self.__socket_req, zmq.POLLIN)        
        self.__socket_sub = self.__context.socket(zmq.SUB)
        self.__active = False
        self.__thread = None
        self.__lock = threading.Lock()
        self.__authenticator = None# Authenticator used to ensure data security
        self._last_received_ping = str(datetime.utcnow())

    @lru_cache(100)
    def __getattr__(self, name):
        def dorpc(*args, **kwargs):
            timeout = kwargs.pop('timeout',0)
            req = [name, args, kwargs]
            rep = None
            with self.__lock:
                self.__socket_req.send_json(req)
                if not timeout or self.__socket_req.poll(timeout):
                    rep = self.__socket_req.recv_json()
 
            if not rep:
                raise TimeoutError('RpcServer no response in {} second(s)'.format(timeout/1000.0))
            elif rep[0]:
                return rep[1]
            else:
                raise RemoteException(rep[1])

        return dorpc

    def start(self, req_address, sub_address="", client_secretkey_path = "", server_publickey_path = ""):
        if self.__active:
            return

        # Start authenticator
        if client_secretkey_path and server_publickey_path:
            self.__authenticator = ThreadAuthenticator(self.__context)
            self.__authenticator.start()
            self.__authenticator.configure_curve(
                domain="*", 
                location=zmq.auth.CURVE_ALLOW_ANY
            )

            publickey, secretkey = zmq.auth.load_certificate(client_secretkey_path)
            serverkey, _ = zmq.auth.load_certificate(server_publickey_path)
            
            self.__socket_sub.curve_secretkey = secretkey
            self.__socket_sub.curve_publickey = publickey
            self.__socket_sub.curve_serverkey = serverkey

            self.__socket_req.curve_secretkey = secretkey
            self.__socket_req.curve_publickey = publickey
            self.__socket_req.curve_serverkey = serverkey

        self.__socket_req.connect(req_address)
        if sub_address:
            self.__active = True
            self.__socket_sub.connect(sub_address)
            self.__thread = threading.Thread(target=self.run)
            self.__thread.start()
            self._last_received_ping = str(datetime.utcnow())
            self.subscribe_topic(KEEP_ALIVE_TOPIC)
        

    def stop(self):
        if not self.__active:
            return

        self.__active = False

    def join(self):
        # Wait for RpcClient thread to exit
        if self.__thread and self.__thread.is_alive():
            self.__thread.join()
        self.__thread = None

    def run(self):
        pull_tolerance = int(KEEP_ALIVE_TOLERANCE.total_seconds() * 1000)

        while self.__active:
            if not self.__socket_sub.poll(pull_tolerance):
                self._on_unexpected_disconnected()
                continue

            # Receive data from subscribe socket
            topic, data = self.__socket_sub.recv_json(flags=NOBLOCK)

            if topic == KEEP_ALIVE_TOPIC:
                #print("{} beat {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), data))
                self._last_received_ping = data
            else:
                # Process data by callable function
                self.callback(topic, data)

        # Close socket
        self.__socket_req.close()
        self.__socket_sub.close()

    @staticmethod
    def _on_unexpected_disconnected():
        print("RpcServer has no response over {tolerance} seconds, please check you connection."
                .format(tolerance=KEEP_ALIVE_TOLERANCE.total_seconds()))

    def callback(self, topic, data):
        raise NotImplementedError

    def subscribe_topic(self, topic):
        self.__socket_sub.setsockopt_string(zmq.SUBSCRIBE, u'["{}"'.format(topic))
