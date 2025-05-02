import os
import re
import logging.handlers
import openbomConfig

__version__ = '1.1'
__author__ = 'newmancloud inc'

__logFormat__ = '%(asctime)s [%(levelname)s]:%(threadName)s - %(name)s %(funcName)s - %(message)s'
__logDateFormat__ = '%Y-%m-%d %H:%M:%S'
__logFileSize__ = 1000000

# init log folder
_workingFolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_logFolder = os.path.join(os.path.dirname(_workingFolder), 'logs')
if not os.path.exists(_logFolder):
	os.makedirs(_logFolder)

__logFilePath__ = os.path.join(_logFolder, 'openbom.log')
# log levels
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

DEFAULT = logging.INFO

class LogFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, style='%'):
		super().__init__(fmt=fmt, datefmt=datefmt, style=style)

	def format(self, record):
		result = super().format(record)
		if "token" in result:
			result = re.sub(r'token=[\w.-]*', 'token=...', result)
			result = re.sub(r'_token":\s?"[^"]*"', '_token":"..."', result)
		return result


loggers = []
logHandler = logging.handlers.RotatingFileHandler(__logFilePath__, encoding='utf-8', maxBytes=__logFileSize__, backupCount=5)
logHandler.setLevel(DEFAULT)
logHandler.setFormatter(LogFormatter(__logFormat__, datefmt=__logDateFormat__))


def getLogger(name=None):
	if not name:
		name = 'OpenBOM'

	logger = logging.getLogger(name)
	logger.setLevel(logHandler.level)
	logger.addHandler(logHandler)

	loggers.append(logger)
	return logger


def setLogLevel(logLevel=None):
	logHandler.setLevel(logLevel)
	for logger in loggers:
		logger.setLevel(logLevel)


def getLogLevel():
	return logHandler.level


def removeAll():
	while loggers:
		logger = loggers.pop()
		logger.removeHandler(logHandler)
		del logger
