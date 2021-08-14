import dash_html_components as html

def nav(active):
    def nav_classes(pathName):
        if active == pathName:
            return "active"
        else:
            return ""

    return html.Div(
        className="nav",
        children=[
            html.H3(children="Energy Differential Privacy Explorer", className="brand"),
            html.A("Load Shape Explorer", href="/load-shape", className=nav_classes("/load-shape")),
            html.A(
                "About",
                href="/about",
                className=nav_classes("/about"),
            ),
        ],
    )
