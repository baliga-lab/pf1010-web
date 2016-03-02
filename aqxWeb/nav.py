from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_bootstrap.nav import BootstrapRenderer
from hashlib import sha1
from dominate import tags

nav = Nav()


class SidedViewImage(View):
    def __init__(self, image_url, text, left, endpoint, *args, **kwargs):
        self.text = tags.img(src=image_url, alt=text)
        self.left = left
        self.endpoint = endpoint
        self.url_for_args = args
        self.url_for_kwargs = kwargs


class SidedView(View):
    def __init__(self, text, left, endpoint, *args, **kwargs):
        self.text = text
        self.left = left
        self.endpoint = endpoint
        self.url_for_args = args
        self.url_for_kwargs = kwargs


class SidedSubgroup(Subgroup):
    def __init__(self, title, left, *items):
        self.title = title
        self.left = left
        self.items = items


class SidedLink(Link):
    def __init__(self, text, dest, left):
        self.text = text
        self.dest = dest
        self.left = left


@nav.navigation('navbar')
def navbar():
    return Navbar(
        SidedViewImage('https://aquaponics.systemsbiology.net/static/images/pflogo2.png', 'Project Feed 1010', True, '.index'),
        SidedLink('Login', '#register-popup', False),
        View('Home', 'frontend.index'),
        View('About', 'frontend.about'),
        View('Explore', 'dav.explore'),
        View('Home', 'frontend.newsfeed'),
        View('Profile', 'frontend.coming'),
        View('Analytics', 'frontend.coming'),
        View('Challenges', 'frontend.coming'),
        View('Documents', 'frontend.coming'),
        SidedSubgroup('Oddish', False,
            View('Friends', 'frontend.coming'),
            View('Systems', 'frontend.coming'),
            View('Groups', 'frontend.coming'),
            Separator(),
            View('Settings', 'frontend.coming'),
            Separator(),
            View('Logout', 'frontend.coming'),
        )
    )


@nav.renderer('nav_renderer')
class NavRenderer(BootstrapRenderer):
    def visit_Navbar(self, node):

        root = tags.div()

        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        top = root.add(tags.nav())
        top['class'] = 'navbar navbar-default'
        top['id'] = 'navbar-top'

        container = top.add(tags.div(_class='container'))

        header = container.add(tags.div(_class='navbar-header'))
        button = header.add(tags.button())
        button['type'] = 'button'
        button['class'] = 'navbar-toggle collapsed'
        button['data-toggle'] = 'collapse'
        button['data-target'] = '#' + node_id
        button['aria-expanded'] = 'false'
        button['aria-controls'] = 'navbar'

        button.add(tags.span('Toggle navigation', _class='sr-only'))
        button.add(tags.span(_class='icon-bar'))
        button.add(tags.span(_class='icon-bar'))
        button.add(tags.span(_class='icon-bar'))

        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand', href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = container.add(tags.div(_class='navbar-collapse collapse', id=node_id))
        bar_left = bar.add(tags.ul(_class='nav navbar-nav navbar-left visible-xs'))
        bar_right = bar.add(tags.ul(_class='nav navbar-nav navbar-right hidden-xs'))

        for item in node.items:
            bar_left.add(self.visit(item))
            if not getattr(item, 'left', True):
                bar_right.add(self.visit(item))

        spacer = root.add(tags.div())
        spacer['id'] = 'navbar-spacer'

        bottom = root.add(tags.nav())
        bottom['class'] = 'navbar navbar-inverse hidden-xs'
        bottom['id'] = 'navbar-bottom'

        container = bottom.add(tags.div(_class='container'))

        bar = container.add(tags.div(_class='navbar-collapse collapse'))
        bar_left = bar.add(tags.ul(_class='nav navbar-nav navbar-left'))

        for item in node.items:
            if getattr(item, 'left', True):
                bar_left.add(self.visit(item))

        return root