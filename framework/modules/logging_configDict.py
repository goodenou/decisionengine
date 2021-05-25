"""
Logger config dictionary
"""
import logging
import logging.handlers
import logging.config
import structlog

timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

pre_chain = [structlog.stdlib.add_logger_name,
             structlog.stdlib.add_log_level,
             timestamper,
            ]


pylogconfig = {
               "version": 1,
               "disable_existing_loggers": False,
               "formatters": {
                              "plain": {
                                  "()": structlog.stdlib.ProcessorFormatter,
                                  "processor": structlog.dev.ConsoleRenderer(colors=False),
                                  "foreign_pre_chain": pre_chain,
                                  "format": "%(message)s [%(module)s]"
                              },
                              "colorful": {
                                  "()": structlog.stdlib.ProcessorFormatter,
                                  "processor": structlog.dev.ConsoleRenderer(colors=True),
                                  "foreign_pre_chain": pre_chain,
                                  "format": "%(message)s [%(module)s]"
                              },
                              "for_JSON": {
                                  "()": structlog.stdlib.ProcessorFormatter,
                                  "processor": structlog.dev.ConsoleRenderer(colors=False),
                                  "format": "%(message)s [%(module)s]"
                                  #"foreign_pre_chain": pre_chain,
                              },
                            },
                "handlers": {
                             "default": {
                                         "level": "DEBUG",
                                         "class": "logging.StreamHandler",
                                         "formatter": "colorful",
                             },
                             "file_all_debug": {
                                                "level": "DEBUG",
                                                "class": "logging.handlers.RotatingFileHandler",
                                                "filename": "/var/log/decisionengine/all_debug.log",
                                                "maxBytes": 200*1000000,
                                                "backupCount": 2,
                                                "formatter": "plain",
                             },
                             "file_debug": {
                                            "level": "DEBUG",
                                            "formatter": "plain",
                                      },
                             "file_info": {
                                           "level": "INFO",
                                           "formatter": "plain",
                               },
                             "file_structlog_debug": {
                                                      "level": "DEBUG",
                                                      #"filename": "/var/log/decisionengine/structlog_debug.log",
                                                      "formatter": "for_JSON",
                             },
                           },
                "loggers": {
                            "default": {
                                        "handlers": ["default"],
                                        "level": "DEBUG",
                                        "propagate": True,
                                        },
                            "struct_de": {#gives 'struct_de' calls at DEBUG+ level into structlog_debug handler
                                          "handlers": ["file_structlog_debug"],
                                          "level": "DEBUG",
                                          "propagate": True,
                            },
                            "decision_engine": {#gives de logger call at handler level into handler file (file and level set in de_logger)
                                                "handlers": ["file_debug","file_info"],
                                                "propagate": True,
                            },
                            "": {#this gives me ALL logging at handler level into handler file
                                 "handlers": ["file_all_debug"],
                                 "propagate": True,
                            },
                           }
}

structlog.configure(
    processors=
        pre_chain+
        [structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
         #structlog.processors.ExceptionPrettyPrinter("/var/log/decisionengine/stackInfo.log"),
        structlog.processors.JSONRenderer(sort_keys=True),
         #structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
                    )
