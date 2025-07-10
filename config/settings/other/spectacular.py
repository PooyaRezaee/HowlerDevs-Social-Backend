def preprocessing_filter_spec(endpoints):
    filtered = []
    from django.shortcuts import resolve_url

    exclude_views_name = [
        # Endpoint names
        # "app_name:view_name",
    ]
    exclude_urls = [resolve_url(view) for view in exclude_views_name]

    for path, path_regex, method, callback in endpoints:
        if path in exclude_urls:
            continue
        filtered.append((path, path_regex, method, callback))

    return filtered


SPECTACULAR_SETTINGS = {
    "TITLE": "django-social",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "PREPROCESSING_HOOKS": [
        "config.settings.other.spectacular.preprocessing_filter_spec"
    ],
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
