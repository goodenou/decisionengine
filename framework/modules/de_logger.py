"""
Logger to use in all modules
"""
import os
import logging
import logging.handlers
import logging.config
import structlog
import decisionengine.framework.modules.de_logger_configDict as configDict

MB = 1000000

myloggers = {"pylogger" : logging.getLogger("decision_engine"),
             "structlogger" : structlog.getLogger("struct_de")}

logger = myloggers["pylogger"]
slogger = myloggers["structlogger"]


def set_logging(log_level,
                file_rotate_by,
                rotation_time_unit,
                rotation_interval,
                max_backup_count,
                max_file_size=200 * MB,
                log_file_name='/tmp/decision_engine_logs/decision_engine_log'):
    """

    :type log_level: :obj:`str`
    :arg log_level: log level
    :type file_rotate_by: :obj: `str`
    :arg file_rotate_by: files rotation by size or by time
    :type rotation_time_unit: :obj:`str`
    :arg rotation_time_unit: unit of time for file rotation
    :type rotation_interval: :obj:`int`
    :arg rotation_interval: time in rotation_time_units between file rotations
    :type log_file_name: :obj:`str`
    :arg log_file_name: log file name
    :type  max_file_size: :obj:`int`
    :arg  max_file_size: maximal size of log file. If reached save and start new log.
    :type  max_backup_count: :obj:`int`
    :arg  max_backup_count: start rotaion after this number is reached
    :rtype: :class:`logging.Logger` - rotating file logger
    """
    dirname = os.path.dirname(log_file_name)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    
    logger.setLevel(getattr(logging, log_level.upper()))
    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s")

    configDict.pylogconfig["handlers"]["file_all_debug"].update({"filename": "{}_all_debug".format(log_file_name)})
    configDict.pylogconfig["handlers"]["file_all_info"].update({"filename": "{}_all_info".format(log_file_name)})
    configDict.pylogconfig["handlers"]["file_structlog_debug"].update({"filename": "{}_structlog_debug".format(log_file_name)})

    if file_rotate_by == "size":
        file_handler = logging.handlers.RotatingFileHandler(log_file_name,
                                                            maxBytes=max_file_size,
                                                            backupCount=max_backup_count)
        configDict.pylogconfig["handlers"]["file_all_debug"].update({"class": "logging.handlers.RotatingFileHandler",
                                                                     "maxBytes": max_file_size,
                                                                     "backupCount": max_backup_count})
        configDict.pylogconfig["handlers"]["file_all_info"].update({"class": "logging.handlers.RotatingFileHandler",
                                                                    "maxBytes": max_file_size,
                                                                    "backupCount": max_backup_count})
        configDict.pylogconfig["handlers"]["file_structlog_debug"].update({"class": "logging.handlers.RotatingFileHandler",
                                                                           "maxBytes": max_file_size,
                                                                           "backupCount": max_backup_count})

    else:
        file_handler = logging.handlers.TimedRotatingFileHandler(log_file_name,
                                                                 when=rotation_time_unit,
                                                                 interval=rotation_interval)
        configDict.pylogconfig["handlers"]["file_all_debug"].update({"class": "logging.handlers.TimedRotatingFileHandler",
                                                                     "when": rotation_time_unit,
                                                                     "interval": rotation_interval})
        configDict.pylogconfig["handlers"]["file_all_info"].update({"class": "logging.handlers.TimedRotatingFileHandler",
                                                                    "when": rotation_time_unit,
                                                                    "interval": rotation_interval})
        configDict.pylogconfig["handlers"]["file_structlog_debug"].update({"class": "logging.handlers.TimedRotatingFileHandler",
                                                                           "when": rotation_time_unit,
                                                                           "interval": rotation_interval})


    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    if log_file_name != '/dev/null':
        if file_rotate_by == "size":
            debug_handler = logging.handlers.RotatingFileHandler("{}_debug".format(log_file_name),
                                                                 maxBytes=max_file_size,
                                                                 backupCount=max_backup_count)
        else:
            debug_handler = logging.handlers.TimedRotatingFileHandler("{}_debug".format(log_file_name),
                                                                      when=rotation_time_unit,
                                                                      interval=rotation_interval)

        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        logger.addHandler(debug_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)
    logger.addHandler(console_handler)


    logging.config.dictConfig(configDict.pylogconfig)

    logger.info("!!!testing!!!") #THIS IS A decision_engine logger log
    log("DEBUG","DEBUG event","message goes here")
    log("INFO","INFO event","message goes here")


def log(level,
        event_to_log='',
        msg_to_log='',
        #module=''
        ):
    """
    This is the logging call for our loggers
    """
    log_level = getattr(logging, level.upper())
    #logger.log(log_level, msg_to_log)creates log in decision_engine_log with name 'de' : will become logger 
    slogger.log(log_level, msg=msg_to_log, event=event_to_log)


def get_logger():
    """
    get default logger - "decision_engine"
    :rtype: :class:`logging.Logger` - rotating file logger
    """
    return myloggers


def set_stream_logging(logger_name=''):
    """
    This is for debugging.
    Set stream logging for logger.

    :type logger_name: :obj:`str`
    :arg logger_name: logger name
    :rtype: :class:`logging.Logger`
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


if __name__ == '__main__':
    set_logging("DEBUG",
                "size",
                'D',
                1,
                max_backup_count=5,
                max_file_size=100000,
                log_file_name='%s/de_log/decision_engine_log0' % (os.environ.get('HOME')))
    logger.error("THIS IS ERROR")
    logger.info("THIS IS INFO")
    logger.debug("THIS IS DEBUG")
    
    slogger.error(msg="THIS IS atructlog ERROR", event="error")
