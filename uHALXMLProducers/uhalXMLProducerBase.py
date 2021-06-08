import os 

#Base class for UHALXMLProducer classes
class UHALXMLProducerBase:
    def __init__(self, factory):
        self.name = "NONE"

        self.factory = factory

    def getModule(self, target_label):
        #Messy ... find the target module with "label" target_lable
        targetFragment = None
        for key, frag in self.factory._fullFragment.items():
            try:
                if self.getProperty(frag, "instance_id") == target_label:
                    targetFragment = frag
                    break
            except(KeyError, TypeError):
                pass

        return targetFragment

    def getProperty(self, fragment, name, index = 1):
        try:
            return fragment[name][index]
        except(KeyError, IndexError):
            raise KeyError(f"Required IP property '{name}' index '{index}' not found")
        
    def _getNameAndLabel(self, fragment):
        address = self.getProperty(fragment, 'reg', 2)

        try:
            label = self.getProperty(fragment, 'label')
        except(KeyError):
            label = self.getProperty(fragment, 'instance_id')

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
