'''
for local debug only
'''
import socket
import socks
SOCKS5_PROXY_HOST = '127.0.0.1'
SOCKS5_PROXY_PORT = 1086
default_socket = socket.socket
socks.set_default_proxy(socks.SOCKS5, SOCKS5_PROXY_HOST, SOCKS5_PROXY_PORT)
socket.socket = socks.socksocket

import json
import time
import traceback

import zmq


class ZProc():
    """
    # ZProc workflow:
        REQ: p0() -> REP: p1()
        REP: p2() -> REQ: p3()
        REQ: p4() -> REP: p5()
        REP: p6() -> REQ: p7()
    """
    context = zmq.Context()


class ZProc_REP(ZProc):

    def __init__(self, config):

        self.socket_REP = self.context.socket(zmq.REP)
        self.socket_REP.bind(config.PORT)

    def REP(self):
        # (REQ -> REP)[1]: handshake
        handshake = self.socket_REP.recv_string()                          # p1
        send_p4 = handshake.split('.')[0]
        recv_p7 = handshake.split('.')[1]
        func = handshake.split('.')[2]
        arg_type = handshake.split('.')[3]
        # (REP -> REQ)[0]: handshake back
        self.socket_REP.send(b'')                                          # p2

        # (REQ -> REP)[1]: get the request
        if send_p4 != 'json':
            query = eval('self.socket_REP.recv_' + send_p4)()              # p5
        else:
            query = json.loads(eval('self.socket_REP.recv_' + send_p4)())  # p5

        # get the shits done
        if send_p4 != 'json':
            result = eval('lib.' + func)(query)
        elif arg_type == 'pd':
            result = eval('lib.' + func)(query['p'], **query['d'])
        else:
            result = eval('lib.' + func)(**query)
        if result is None:
            result = 'None'

        # (REP -> REQ)[0]: deliver
        if recv_p7 != 'json':
            eval('self.socket_REP.send_' + recv_p7)(result)                # p6
        else:
            eval('self.socket_REP.send_' + recv_p7)(json.dumps(result))


class ZProc_REQ(ZProc):
    def __init__(self, config):
        self.socket_REQ = self.context.socket(zmq.REQ)
        self.socket_REQ.connect(config.HOST)

    def REQ(self, params, send_p4, recv_p7, arg_type='normal'):
        '''
            arg_type = ('normal', 'pd')
        '''
        caller = traceback.extract_stack()[-2][2]
        handshake = '{}.{}.{}.{}'.format(send_p4, recv_p7, caller, arg_type)

        # (REQ -> REP)[0]: handshake
        self.socket_REQ.send_string(handshake)                             # p0
        # (REP -> REQ)[1]: handshake back
        self.socket_REQ.recv()                                             # p3
        # (REQ -> REP)[0]: make the request
        eval('self.socket_REQ.send_' + send_p4)(params)                    # p4
        # (REP -> REQ)[1]: get hte delivery
        recv = eval('self.socket_REQ.recv_' + recv_p7)()                   # p7
        return recv


def main():
    from config import Config, lib
    z = ZProc_REP(Config)
    while True:
        z.REP()


if __name__ == '__main__':
    main()
