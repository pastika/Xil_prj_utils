from uhalXMLProducerBase import UHALXMLProducerBase

import os

cdma_axi_template = """<node>
  <!-- Memory page segmentation based on
    https://www.xilinx.com/support/documentation/ip_documentation/axi_cdma/v4_1/pg034-axi-cdma.pdf
  -->
  <node id="cdmaCtrl" address="0x0" module="file://cdma_ctrl.xml" description="CDMA Control"/>
  <node id="cdmaStat" address="0x1" module="file://cdma_status.xml" description="CDMA Status"/>
  <node id="CurDesc" address="0x2"  description="Current Descriptor pointer"/>
  <node id="TailDesc" address="0x4" description="Tail Descriptor pointer"/>
  <node id="SA" address="0x6" description="Source Address"/>
  <node id="DA" address="0x8" description="Destination Address"/>
  <node id="BTT" address="0xA" description="Bytes To Transfer"/>
</node >
"""

cdma_ctrl_template = """<node>
  <node id="TailPtrEn" mask="0x2" permission="r" description="Indicate whether Tail Pointer Mode is enabled"/>
  <node id="Reset" mask="0x4" permission="rw" description="Soft Reset AXI CDMA"/>
  <node id="SGMode" mask="0x8" permission="rw"  description="Sets scatter/gather mode on 1, simple dma on 0"/>
  <node id="KeyholeRead" mask="0x10" permission="rw"  description="Enable keyhole read"/>
  <node id="KeyholeWrite" mask="0x20" permission="rw" description="Enable keyhole write"/>
  <node id="CyclicBD" mask="0x40" permission="rw" description="Enable cyclic buffer descriptor mode"/>
  <node id="IOC_IrqEn" mask="0x1000" permission="rw" description="Enable interrupt on complete transfer"/>
  <node id="Dly_IrqEn" mask="0x2000" permission="rw" description="Delat interrupt enable"/>
  <node id="Err_IrqEn" mask="0x4000" permission="rw" description="Error interrupt enable"/>
  <node id="IRQThreshold" mask="0xFF0000" permission="rw" description="Interrupt Threshold"/>
  <node id="IRQDelay" mask="0xFF000000" permission="rw" description="Interrupt Delay Timeout"/>
  <node id="Interrupt" address="0xAA" permission="r" description="Interrupt reg (dummy)" tags="interrupt"/>
</node >
"""

cdma_status_template = """<node>
  <node id="Idle" mask="0x2" permission="r" description="Indicates the state of axi CDMA operations"/>
  <node id="SGIncid" mask="0x8" permission="r" description="Indicates if AXI CDMA is implemented with SG support"/>
  <node id="DMAIntErr" mask="0x10" permission="r"  description="Axi internal error"/>
  <node id="DMASlvErr" mask="0x20" permission="r"  description="Axi slave error response recieved"/>
  <node id="DMADecErr" mask="0x40" permission="r"  description="Axi decode error"/>
  <node id="SGIntErr" mask="0x100" permission="r"  description="Internal error in SG mode"/>
  <node id="SGSlvErr" mask="0x200" permission="r"  description="Indicates an Axi slave error in SG mode"/>
  <node id="SGDecErr" mask="0x400" permission="r" description="Scatter Gather Decode error"/>
  <node id="IOC_Irq" mask="0x1000" permission="rw" description="Indicates an interrupt due to a complete transfer"/>
  <node id="Dly_Irq" mask="0x2000" permission="rw" description="Indicates an interrupt due to a delay timeout"/>
  <node id="Err_Irq" mask="0x4000" permission="rw" description="Indicates an interrupt due to an error"/>
  <node id="IRQThreshStat" mask="0xFF0000" permission="r" description="The current interrupt threshold value"/>
  <node id="IRQDelayStat" mask="0xFF000000" permission="r" description="The current interrupt delay setting"/>
</node >
"""

top_level_node_template = '<node id="%(label)s"	    module="file://modules/cdma_axi.xml"	          address="%(addr)s"/>'

# Class MUST be named UHALXMLProducer
class UHALXMLProducer(UHALXMLProducerBase):
    def __init__(self, factory):
        # Class MUST have "name" attribute defined and this must match the dtbo name of the IP it is meant to manage 
        self.name = "dma"

    # CLass MUST define produce_impl which will produce the xml map file(s) and return the top level node for the module 
    def produce_impl(self, fragment, xmlDir, address, label):

        with open(os.path.join(xmlDir, "modules", "cdma_axi.xml"), "w") as f:
            f.write(cdma_axi_template)

        with open(os.path.join(xmlDir, "modules", "cdma_ctrl.xml"), "w") as f:
            f.write(cdma_ctrl_template)

        with open(os.path.join(xmlDir, "modules", "cdma_status.xml"), "w") as f:
            f.write(cdma_status_template)
        
        return top_level_node_template%{"label": label, "addr": address}
