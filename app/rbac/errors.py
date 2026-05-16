class AppError(Exception): 
    pass 

class RBACError(AppError): 
    pass

class PermissionDenied(RBACError):
    pass 