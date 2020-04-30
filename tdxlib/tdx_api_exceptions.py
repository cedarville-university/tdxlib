
class TdxApiHTTPError(Exception):
    pass


class TdxApiHTTPRequestError(Exception):
    pass


class TdxApiTicketValidationError(Exception):
    pass


class TdxApiTicketImportError(Exception):
    pass


class TdxApiObjectNotFoundError(Exception):
    pass


class TdxApiObjectTypeError(Exception):
    pass

class TdxApiDuplicateError(Exception):
    pass
