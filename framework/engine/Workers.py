import logging
import structlog
import multiprocessing
import os
import threading

import decisionengine.framework.taskmanager.ProcessingState as ProcessingState
import decisionengine.framework.modules.de_logger_configDict as configDict

FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(module)s - %(process)d - %(threadName)s - %(levelname)s - %(message)s")


class Worker(multiprocessing.Process):
    '''
    Class that encapsulates a channel's task manager as a separate process.

    This class' run function is called whenever the process is
    started.  If the process is abruptly terminated--e.g. the run
    method is pre-empted by a signal or an os._exit(n) call--the
    Worker object will still exist even if the operating-system
    process no longer does.

    To determine the exit code of this process, use the
    Worker.exitcode value, provided by the multiprocessing.Process
    base class.
    '''

    def __init__(self, task_manager, logger_config):
        super().__init__()
        self.task_manager = task_manager
        self.task_manager_id = task_manager.id
        self.logger_config = logger_config

    def wait_until(self, state):
        return self.task_manager.state.wait_until(state)

    def wait_while(self, state):
        return self.task_manager.state.wait_while(state)

    def get_state_name(self):
        return self.task_manager.get_state_name()

    def run(self):
      
        myname = self.task_manager.name
        configDict.pylogconfig["handlers"].update({f"{myname}": {
                                                           "level": "DEBUG",
                                                           "filename": "/var/log/decisionengine/channel_debug.log",
                                                           "formatter": "plain",
                                                           "class": "logging.handlers.RotatingFileHandler",
                                                           "maxBytes": 200 * 1000000,
                                                           "backupCount": self.logger_config.get("max_backup_count", 6)
                                                          }
                                                  })
        
        configDict.pylogconfig["loggers"].update({f"{myname}":{
                                                             "handlers": [f"{myname}"],
                                                             "level": "DEBUG",
                                                             "propagate": True,
                                                             }
                                                  })
        
        logging.config.dictConfig(configDict.pylogconfig)

        structlog.getLogger("struct_de").debug("test1 from Workers", msg="msg")
        structlog.getLogger(f"{myname}").debug(msg="", event="testing from Workers.py")
        #logging.getLogger("testing").debug(msg="", event="testing from Workers.py")FAILED
        logging.getLogger(f"{myname}").debug("testing from Workers.py")

        
        #logger = logging.getLogger()
        logger = logging.getLogger(f"{myname}")
        

      
        logger.setLevel(logging.WARNING)
        channel_log_level = self.logger_config.get("global_channel_log_level", "WARNING")
        self.task_manager.set_loglevel(channel_log_level)
        self.task_manager.run()


class Workers:
    '''
    This class manages and provides access to the task-manager workers.

    The intention is that the decision engine never directly interacts with the
    workers but refers to them via a context manager:

      with workers.access() as ws:
          # Access to ws now protected
          ws['new_channel'] = Worker(...)

    In cases where the decision engine's block_while or block_until
    methods must be called (e.g. during tests), one should used the
    unguarded access:

      with workers.unguarded_access() as ws:
          # Access to ws is unprotected
          ws['new_channel'].wait_until(...)

    Calling a blocking method while using the protected context
    manager (i.e. workers.access()) will likely result in a deadlock.
    '''

    def __init__(self):
        self._workers = {}
        self._lock = threading.Lock()

    def _update_channel_states(self):
        with self._lock:
            for channel, process in self._workers.items():
                if process.is_alive():
                    continue
                if process.task_manager.state.inactive():
                    continue
                process.task_manager.state.set(ProcessingState.State.ERROR)

    class Access:
        def __init__(self, workers, lock):
            self._workers = workers
            self._lock = lock

        def __enter__(self):
            if self._lock:
                self._lock.acquire()
            return self._workers

        def __exit__(self, error, type, bt):
            if self._lock:
                self._lock.release()

    def access(self):
        self._update_channel_states()
        return self.Access(self._workers, self._lock)

    def unguarded_access(self):
        self._update_channel_states()
        return self.Access(self._workers, None)
