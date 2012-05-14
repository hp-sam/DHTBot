"""
An XML RPC wrapper around the DHT protocols

@see dhtbot.protocols

"""
from twisted.application import service
from twisted.web import xmlrpc

from dhtbot.protocols.krpc_sender import IKRPC_Sender
from dhtbot.protocols.krpc_responder import IKRPC_Responder
# TODO refactor these functions into a common module
from dhtbot.xml_rpc_client import _pickle_load_string, _pickle_dump_string

class KRPC_Sender_Server(xmlrpc.XMLRPC):
    """
    Proxy between the XML RPC Server and the running KRPC_Sender Protocol

    sendQuery is the only proxied function from KRPC_Sender

    @see dhtbot.protocols.krpc_sender.KRPC_Sender

    """
    def __init__(self, node_proto):
        self.node_proto = node_proto

    def xmlrpc_sendQuery(self, pickled_query, address, timeout):
        """@see dhtbot.protocols.krpc_sender.KRPC_Sender.sendQuery"""
        # The query was pickled so it could be sent over XMLRPC
        query = _pickle_load_string(pickled_query)
        deferred = self.node_proto.sendQuery(query, address, timeout)
        # Pickle the result so that it can be sent over XMLRPC
        deferred.addCallback(_pickle_result)
        return deferred

class KRPC_Responder_Server(KRPC_Sender_Server):
    """
    Proxy between the XML RPC Server and the running KRPC_Responder Protocol

    The following methods are available:
        ping
        find_node
        get_peers
        announce_peer

    @see dhtbot.protocols.krpc_responder.KRPC_Responder

    """
    def xmlrpc_ping(self, address, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.ping"""
        if timeout is None:
            return self.node_proto.ping(address)
        else:
            return self.node_proto.ping(address, timeout)

    def xmlrpc_find_node(self, address, node_id, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.find_node"""
        if timeout is None:
            return self.node_proto.find_node(address, node_id)
        else:
            return self.node_proto.ping(address, node_id, timeout)

    def xmlrpc_get_peers(self, address, target_id, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.get_peers"""
        if timeout is None:
            return self.node_proto.get_peers(address, target_id)
        else:
            return self.node_proto.get_peers(address, target_id, timeout)

    def xmlrpc_announce_peer(self, address, token, port, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.announce_peer"""
        if timeout is None:
            return self.node_proto.announce_peer(address, token, port)
        else:
            return self.node_proto.announce_peer(address, token, port, timeout)

def _pickle_result(result):
    pickled_result = _pickle_dump_string(result)
    return pickled_result