from os import remove
from json import load, dumps

def _configs_exist():
    try:
        open('configs.json','r')
        return True
    except FileNotFoundError:
        return False

def _default_configs():
    configs = {"accounts": {}, "categories":{}}

    if not _configs_exist():
        open('configs.json','x')
    else:
        remove('configs.json')

    open('configs.json','w').write(dumps(configs, sort_keys=True, indent=4))
    return True

def read_configs():
    if not _configs_exist():
            _default_configs()

    configs = load(open('configs.json','r'))

    return configs

# decorator to easily add to configs file
def update_configs(func):
    def wrapper(*args, **kwargs):
        # run function with json file contents passed
        configs = func(read_configs(), *args, **kwargs)

        # opens configs file in "write" mode, therefore empties configs file for overwritting later
        with open('configs.json', 'w') as configs_writer:
            # rewrites configs and prettifies output
            configs_writer.write(dumps(configs, sort_keys=True, indent=4))

        return True

    return wrapper