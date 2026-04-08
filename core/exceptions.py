class BacklinkBaseError(Exception):
    pass

class ConfigError(BacklinkBaseError):
    pass

class SubmissionError(BacklinkBaseError):
    pass

class DuplicateSkippedError(BacklinkBaseError):
    pass

class CaptchaSolveError(BacklinkBaseError):
    pass
