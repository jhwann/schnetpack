import json
import importlib


class Hyperparameters:


    def __init__(self, config):
        """
        Args:
            config (dict): configuration of __init__
        """
        self.config = {}
        self.default_config = {}
        self.get_configs(config)

    def get_configs(self, config):
        config = config.copy()
        del config['self']
        self.config = config
        defaults = self.__init__.__defaults__
        if defaults is None:
            defaults = ()
        varnames = self.__init__.__code__.co_varnames[1:]
        n_defaults = len(defaults)
        n_vars = len(varnames)
        defaults = (None,) * (n_vars - n_defaults) + defaults
        self.default_config = dict(zip(varnames, defaults))

    # GET
    def get_default_config(self):
        return self.default_config.copy()

    def get_config(self):
        return self.config.copy()

    # DUMP
    def dump_config(self, fp):
        """
        Dump the hyper-parameters to a json file.

        Args:
            fp (str): path to file

        """
        dict_to_dump = self.get_dump_dict()
        with open(fp, 'w') as file:
            json.dump(dict_to_dump, file)

    def dump_default_config(self, fp):
        """
        Dump the hyper-parameters to a json file.

        Args:
            fp (str): path to file

        """
        dict_to_dump = self.get_dump_dict(self.default_config)
        with open(fp, 'w') as file:
            json.dump(dict_to_dump, file)

    def get_dump_dict(self, in_dict=None):
        """
        Prepare hyper-parameters for dumping to json file.

        Args:
            in_dict (dic): hyper-parameters

        """
        if in_dict is None:
            in_dict = self.config
        in_dict = in_dict.copy()
        dump_dict = {}
        for key, value in in_dict.items():
            if isinstance(value, type):
                dump_dict[key] = dict(class_name=value.__name__, module=value.__module__)
            elif isinstance(value, Hyperparameters):
                dump_dict[key] = dict(class_name=value.__class__.__name__, module=value.__class__.__module__,
                params=self.get_dump_dict(value.config))
            else:
                dump_dict[key] = value
        return dump_dict

    # LOAD
    @classmethod
    def from_json(cls, fp):
        """
        Load configuration of a Model from a JSON config file.

        Args:
            fp (str): path to config JSON

        Returns:
            instance of model with loaded configuration

        """
        with open(fp) as file:
            json_config = json.load(file)
        return cls(**cls.from_dict(json_config))

    @classmethod
    def from_dict(cls, config):
        """
        Create self.config from default parameters and config settings.

        Args:
            config (dict): hyper-parameter configuration

        """
        new_config = {}
        for key, value in config.items():
            if type(value) == dict:
                module = importlib.import_module(value['module'])
                module_class = getattr(module, value['class_name'])
                if 'params' in value.keys():
                    new_config[key] = module_class(**cls.from_dict(value['params']))
                else:
                    new_config[key] = module_class
            else:
                new_config[key] = value
        return new_config