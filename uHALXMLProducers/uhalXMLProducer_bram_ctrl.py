from uhalXMLProducerBase import UHALXMLProducerBase

import os

top_level_node_template = '<node id="%(label)s"	    mode="block"	          address="%(addr)s" size="%(size)s" permission="rw"/>'

# Class MUST be named UHALXMLProducer
class UHALXMLProducer(UHALXMLProducerBase):
    def __init__(self, factory):
        # Class MUST have "name" attribute defined and this must match the dtbo name of the IP it is meant to manage 
        self.name = "axi_bram_ctrl"

    # CLass MUST define produce_impl which will produce the xml map file(s) and return the top level node for the module 
    def produce_impl(self, fragment, xmlDir, address, label):
        size = self.getProperty(fragment, 'reg', 4)
        
        return top_level_node_template%{"label": label, "addr": address, "size": int(size,0)//4}
