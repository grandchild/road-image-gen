'''
Config file for passing options from the CLI to the blender project subprocess.

>>> write_config('.', {'one': 1, 'two': 2, 'three': 3}, ['one', 'three'], four=4)
>>> read_config('.')
{'four': 4, 'one': 1, 'three': 3}
>>> remove_config()

The config object returned by :py:meth:`read_config` is a special `dict` subclass
that returns `None` on missing keys:

>>> c = Config({'hey': 'ho'})
>>> print(c['other'])
None
'''
import os
import os.path
# import yaml  # Change this and the relevant lines below to use YAML instead.
import json


# config_filename = 'config.yml'
config_filename = 'config.json'


def write_config(options, keys, output_path='.', file=config_filename, **extra_keys):
    '''
    Write the selected 'keys' from 'options' as well as optional 'extra_keys'
    into config.yml.
    '''
    config = {}
    for key in keys:
        key = key.replace('-', '_')
        try:
            config[key] = options[key]
        except TypeError:
            config[key] = getattr(options, key)
    for key, value in extra_keys.items():
        kye = key.replace('-', '_')
        config[key] = value
    with open(os.path.join(output_path, file), 'w') as config_file:
        # yaml.safe_dump(config, config_file, default_flow_style=False)
        json.dump(config, config_file, indent=4)


def read_config(output_path='.', file=config_filename):
    '''
    Read config.yml and return the values as dict, with nonexistent keys
    defaulting to None.
    
    Returns:
        Config: An instance of :py:class:`Config`, basically a `dict` with the \
            configuration values.
        
    '''
    config = {}
    try:
        with open(os.path.join(output_path, file)) as config_file:
            # config = yaml.safe_load(config_file)
            try:
                config = json.load(config_file)
            except Exception:
                raise ValueError('Invalid JSON in config.')
    except FileNotFoundError:
        print('Warning: No config file found ({}).'.format(os.path.join(output_path, file)))
    return Config(config)


def remove_config(file=config_filename):
    '''Remove the default or given config file.'''
    os.remove(file)


class Config(dict):
    '''A dict that returns None for non-existing keys.'''
    def __missing__(self, key):
        return None
