import logging
import sys

sys_log = ''
log_directory = 'logs/'
system_log = 'sys_log'
loggers = {}

def new_log(name, level = logging.INFO):
    name = f'{log_directory}{name}.log'
    #if logger already exists
    global loggers
    if loggers.get(name):
        return loggers.get(name)

    #else logger settings
    log = logging.getLogger(name)
    #options: %(asctime)s:%(levelname)s:%(message)s
    formatter = logging.Formatter('%(asctime)s:%(message)s')
    fileHandler = logging.FileHandler(name)
    fileHandler.setFormatter(formatter)

    #only stdout for systemlog
    if name == system_log:
        streamHandler = logging.StreamHandler(stream=sys.stdout)
        streamHandler.setFormatter(formatter)
        log.addHandler(streamHandler)

    log.setLevel(level)
    log.addHandler(fileHandler)
    loggers[name] = log
    return log

sys_log = new_log(system_log)