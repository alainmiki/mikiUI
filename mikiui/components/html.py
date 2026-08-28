"""Document, text, layout, media, list and navigation components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Html(Component):
    tag = "html"


class Head(Component):
    tag = "head"


class Title(Component):
    tag = "title"


class Meta(Component):
    tag = "meta"


class Link(Component):
    tag = "link"


class Script(Component):
    tag = "script"


class Style(Component):
    tag = "style"


class Body(Component):
    tag = "body"


class H1(Component):
    tag = "h1"


class H2(Component):
    tag = "h2"


class H3(Component):
    tag = "h3"


class H4(Component):
    tag = "h4"


class H5(Component):
    tag = "h5"


class H6(Component):
    tag = "h6"


class Heading(Component):
    """Configurable heading; ``level`` selects h1..h6 (default 1)."""

    def __init__(self, *children: Any, level: int = 1, **attrs: Any) -> None:
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        self.tag = f"h{level}"
        super().__init__(*children, **attrs)


class P(Component):
    tag = "p"


Paragraph = P


class Span(Component):
    tag = "span"


class Div(Component):
    tag = "div"


class Section(Component):
    tag = "section"


class Article(Component):
    tag = "article"


class Aside(Component):
    tag = "aside"


class Header(Component):
    tag = "header"


class Footer(Component):
    tag = "footer"


class Main(Component):
    tag = "main"


class Nav(Component):
    tag = "nav"


class Br(Component):
    tag = "br"


class Hr(Component):
    tag = "hr"


class Code(Component):
    tag = "code"


class Pre(Component):
    tag = "pre"


Preformatted = Pre


class Blockquote(Component):
    tag = "blockquote"


class Small(Component):
    tag = "small"


class Strong(Component):
    tag = "strong"


class Em(Component):
    tag = "em"


Emphasis = Em


class Mark(Component):
    tag = "mark"


class Abbr(Component):
    tag = "abbr"


Abbreviation = Abbr


class Address(Component):
    tag = "address"


class Time(Component):
    tag = "time"


class Kbd(Component):
    tag = "kbd"


Keyboard = Kbd


class A(Component):
    """Anchor / hyperlink. Add ``hx_get`` for SPA-style partial navigation."""

    tag = "a"


Anchor = A


class Ul(Component):
    tag = "ul"


class Ol(Component):
    tag = "ol"


class Li(Component):
    tag = "li"


UnorderedList = Ul
OrderedList = Ol
ListItem = Li


class Dl(Component):
    tag = "dl"


class Dt(Component):
    tag = "dt"


class Dd(Component):
    tag = "dd"


DescriptionList = Dl
DescriptionTerm = Dt
DescriptionDetail = Dd


class Menu(Component):
    tag = "menu"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("role", "menu")
        attrs.setdefault("aria-label", "Menu")
        super().__init__(*children, **attrs)


class Img(Component):
    tag = "img"


Image = Img


class Video(Component):
    tag = "video"


class Audio(Component):
    tag = "audio"


class Source(Component):
    tag = "source"


class Canvas(Component):
    tag = "canvas"


class Svg(Component):
    tag = "svg"


SVG = Svg


class Figure(Component):
    tag = "figure"


class Figcaption(Component):
    tag = "figcaption"


class Cite(Component):
    tag = "cite"


Citation = Cite


class Var(Component):
    tag = "var"


Variable = Var


class Samp(Component):
    tag = "samp"


Sample = Samp
