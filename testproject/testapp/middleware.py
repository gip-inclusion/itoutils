class PassThroughMiddleware:
    """Pass the request on to the next middleware, nothing else.

    It lives in APPS_DIR, so its frame is on the stack of every query made by a view and would show up in query
    origins. assertSnapshotQueries leaves it out because the line of the frame calls `get_response(request)`:
    the snapshot tests thus check that skip, which only works if the line number read from the frame is right.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
