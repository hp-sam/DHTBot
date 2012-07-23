"""
An XML RPC wrapper around the DHT protocols

@see dhtbot.protocols

"""
from twisted.application import service
from twisted.web import xmlrpc

from dhtbot.protocols.krpc_sender import IKRPC_Sender
from dhtbot.protocols.krpc_responder import IKRPC_Responder
from dhtbot.xml_rpc.client import unpickle_from_str, pickle_to_str

class KRPC_Sender_Server(xmlrpc.XMLRPC):
    """
    Proxy between the XML RPC Server and the running KRPC_Sender Protocol

    sendQuery is the only proxied function from KRPC_Sender

    @see dhtbot.protocols.krpc_sender.KRPC_Sender

    """

    # Allow this XMLRPC server to transmit None
    allowNone = True
    # useDateTime was enabled because otherwise
    # exceptions were triggered in the XML RPC connection
    # process. (This may be able to be removed)
    # TODO investigate
    useDateTime = True

    def __init__(self, node_proto):
        self.node_proto = node_proto

    def xmlrpc_sendQuery(self, pickled_query, address, timeout):
        """@see dhtbot.protocols.krpc_sender.KRPC_Sender.sendQuery"""
        address = tuple(address)
        # The query was pickled so it could be sent over XMLRPC
        query = unpickle_from_str(pickled_query)
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
        address = tuple(address)
        d = self.node_proto.ping(address, timeout)
        d.addCallback(_pickle_result)
        return d

    def xmlrpc_find_node(self, address, packed_node_id, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.find_node"""
        address = tuple(address)
        node_id = long(packed_node_id)
        d = self.node_proto.find_node(address, node_id, timeout)
        d.addCallback(_pickle_result)
        return d

    def xmlrpc_get_peers(self, address, packed_target_id, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.get_peers"""
        address = tuple(address)
        target_id = long(packed_target_id)
        d = self.node_proto.get_peers(address, target_id, timeout)
        d.addCallback(_pickle_result)
        return d

    def xmlrpc_announce_peer(self,
            address, packed_target_id, token, port, timeout):
        """@see dhtbot.protocols.krpc_responder.KRPC_Responder.announce_peer"""
        address = tuple(address)
        target_id = long(packed_target_id)
        d = self.node_proto.announce_peer(address, token, port, timeout)
        d.addCallback(_pickle_result)
        return d

def _pickle_result(result):
    pickled_result = _pickle_to_str(result)
    return pickled_result
