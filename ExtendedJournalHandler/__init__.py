from systemd.journal import JournalHandler, send

JOURNAL_KEY_PREFIX = "JOURNAL_"


class ExtendedJournalHandler(JournalHandler):
    def __init__(self, *args, **kwargs):
        """logging.config.fileConfig does not support kwargs

        see https://bugs.python.org/issue31080

        so let's use last args parameter to update kwargs dict
        and we still can use args to pass positional arguments

        [handler_journal]
        class = ExtendedJournalHandler.ExtendedJournalHandler
        args = (INFO, {"SYSLOG_IDENTIFIER":"my-cool-app"})
        """
        if args and isinstance(args[-1], dict):
            kwargs.update(args[-1])
            args = args[:-1]
        super(ExtendedJournalHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        """Write record as journal event.

        MESSAGE is taken from the message provided by the
        user, and PRIORITY, LOGGER, THREAD_NAME,
        CODE_{FILE,LINE,FUNC} fields are appended
        automatically. In addition, record.MESSAGE_ID will be
        used if present.
        """
        try:
                msg = self.format(record)
                pri = self.mapPriority(record.levelno)
                mid = getattr(record, 'MESSAGE_ID', None)
                extra = dict(self._extra)
                for key in record.__dict__:
                    if key.startswith(JOURNAL_KEY_PREFIX):
                        extra[key[len(JOURNAL_KEY_PREFIX):]] = getattr(record, key)
                send(msg,
                     MESSAGE_ID=mid,
                     PRIORITY=format(pri),
                     LOGGER=record.name,
                     THREAD_NAME=record.threadName,
                     CODE_FILE=record.pathname,
                     CODE_LINE=record.lineno,
                     CODE_FUNC=record.funcName,
                     **extra)
        except Exception:
                self.handleError(record)
