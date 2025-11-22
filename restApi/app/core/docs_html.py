"""
Custom HTML templates for API documentation
"""

def get_redoc_html(openapi_url: str, title: str) -> str:
    """
    Generate custom ReDoc HTML with proper configuration.
    
    Args:
        openapi_url: URL to the OpenAPI JSON schema
        title: Title for the page
        
    Returns:
        HTML string for ReDoc page
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title} - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url='{openapi_url}'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """


def get_swagger_html(openapi_url: str, title: str) -> str:
    """
    Generate custom Swagger UI HTML.
    
    Args:
        openapi_url: URL to the OpenAPI JSON schema
        title: Title for the page
        
    Returns:
        HTML string for Swagger UI page
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title} - Swagger UI</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@latest/swagger-ui.css" />
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@latest/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@latest/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    url: '{openapi_url}',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                }})
                window.ui = ui
            }}
        </script>
    </body>
    </html>
    """
