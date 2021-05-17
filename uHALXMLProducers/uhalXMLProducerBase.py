import os 

#Base class for UHALXMLProducer classes
class UHALXMLProducerBase:
    def __init__(self, factory):
        self.name = "NONE"

        self.factory = factory

    def getProperty(self, fragment, name, index = 1):
        try:
            return fragment[name][index]
        except(KeyError, IndexError):
            raise KeyError(f"Required IP property '{name}' index '{index}' not found")
        
    def _getNameAndLabel(self, fragment):
        address = self.getProperty(fragment, 'reg', 2)

        label = self.getProperty(fragment, 'label')

        # Some prints to identify which IP is found
        print("Creating %s entry at address %s"%(label, address))

        return address, label
    
    def produce(self, fragment, xmlDir):
        address, label = self._getNameAndLabel(fragment)

        if not os.path.exists(os.path.join(xmlDir, "modules")):
            os.makedirs(os.path.join(xmlDir, "modules"))
        

        return self.produce_impl(fragment, xmlDir, address, label)

    def produce_impl(self, fragment, xmlDir, address, label):
        pass
