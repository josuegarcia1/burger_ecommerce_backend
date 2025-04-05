class AppException(Exception):
    """Excepción base para la aplicación"""
    pass

class AuthException(AppException):
    """Excepciones relacionadas con autenticación"""
    pass

class DatabaseException(AppException):
    """Excepciones relacionadas con la base de datos"""
    pass

class AWSSyncException(AppException):
    """Excepciones relacionadas con la sincronización con AWS"""
    pass