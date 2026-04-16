class S3ServiceError(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class RDSServiceError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

