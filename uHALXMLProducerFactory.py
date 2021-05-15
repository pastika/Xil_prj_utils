import importlib
import inspect
import os
import sys

class UHALXMLProducerFactory:
    def __init__(self, ip_repos:list):
        self._uhalXMLProducers = {}

        # discover possible IP locations 
        if ip_repos != []:
            for ip_repo in ip_repos:
                # try to load ip_repo as a module directly
                try:
                    spec = importlib.util.spec_from_file_location(ip_repo[0], os.path.join(ip_repo[1], ip_repo[0], "__init__.py"))
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module 
                    spec.loader.exec_module(module)
                except(FileNotFoundError):
                    pass
                #load any sub directories as modules as well
                newBase = os.path.join(ip_repo[1], ip_repo[0])
                dirs = [d for d in next(os.walk(newBase))[1] if not d.startswith(".") and not d == "__pycache__"]
                for nmod in dirs:
                    try:
                        spec = importlib.util.spec_from_file_location(nmod, os.path.join(newBase, nmod, "__init__.py"))
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[spec.name] = module 
                        spec.loader.exec_module(module)
                    except(ModuleNotFoundError, FileNotFoundError):
                        pass

        for name, mod in sys.modules.items():
            # fill dict of producer "plugins"
            if 'UHALXMLProducer' in dict(inspect.getmembers(mod)):
                instance = mod.UHALXMLProducer(self)
                self._uhalXMLProducers[instance.name] = instance
            
    def __getitem__(self, key):
        cleanKey = key.split("@")[0]
        if cleanKey in self._uhalXMLProducers:
            return self._uhalXMLProducers[cleanKey].produce
        else:
            raise KeyError(f"No key \"{cleanKey}\" in UHALXMLProducerFactory")
