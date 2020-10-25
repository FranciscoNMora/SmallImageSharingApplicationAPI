from rest_framework.response import Response


class ErrorResponse(Response):
    """For use in API views only"""
    def __init__(self, status, message=None, **kwargs):
        super().__init__(status=status, data={} if message is None else {'message': message}, **kwargs)