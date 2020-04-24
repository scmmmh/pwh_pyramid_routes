import json

from base64 import urlsafe_b64encode, urlsafe_b64decode
from pyramid_jinja2.filters import route_url_filter, static_url_filter


def encode_route(request):
    """Jinja2 filter that returns the current route as a JSON object, which is then URL-safe base64 encoded."""
    if request.matched_route:
        data = {'route': request.matched_route.name,
                'params': request.matchdict,
                'query': list(request.params.items())}
        return urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode()
    return None


def decode_route(request, default_route='root', default_route_params=None, default_route_query=None):
    """Jinja2 filter that decodes and returns the route URL encoded with :func:`~toja.routes.encode_route`."""
    if 'redirect' in request.params and request.params['redirect']:
        try:
            data = json.loads(urlsafe_b64decode(request.params['redirect'].encode()).decode('utf-8'))
            return request.route_url(data['route'], **data['params'], _query=data['query'])
        except Exception:
            pass
    if not default_route_params:
        default_route_params = {}
    return request.route_url(default_route, **default_route_params, _query=default_route_query)


def update_current_route(request, params=None, query=None):
    """Update the current route with new parameters or query."""
    if query:
        tmp = []
        for key in request.params.keys():
            if key in query:
                tmp.append((key, query[key]))
            else:
                for val in request.params.getall(key):
                    tmp.append((key, val))
        for key, value in query.items():
            tmp.append((key, value))
        query = tmp
    if params and query:
        return request.current_route_url(**params, _query=query)
    elif params:
        return request.current_route_url(**params)
    elif query:
        return request.current_route_url(_query=query)
    else:
        return request.current_route_url()


def includeme(config):
    config.get_jinja2_environment().filters['static_url'] = static_url_filter
    config.get_jinja2_environment().filters['route_url'] = route_url_filter
    config.get_jinja2_environment().filters['encode_route'] = encode_route
    config.get_jinja2_environment().filters['decode_route'] = decode_route
    config.get_jinja2_environment().filters['update_current_route'] = update_current_route
