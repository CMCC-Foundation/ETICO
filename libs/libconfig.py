import configparser
import json

def read_config_as_dict(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    # Converti in dizionario standard
    config_dict = {section: {key: parse_value(value)
                             for key, value in config.items(section)}
                   for section in config.sections()}
    return config_dict

def parse_value(value):
    # Prova a convertire in int o float se possibile, altrimenti lascia come stringa
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        return value
