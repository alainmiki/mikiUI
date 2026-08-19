"""Advanced high-level widgets: Carousel, Pagination, Card, Avatar, Badge, Progress.

Each widget is a composite Component with accessibility attributes, i18n hooks,
and sensible defaults. All are lightweight (no heavy JS dependencies).
"""

from __future__ import annotations

from typing import Any

from ..components import A, Button, Div, Img, Li, P, Span, Ul
from ..components import Progress as ProgressBar
from ..components.base import Component


class Card(Component):
    """A flexible card container with optional header and footer.

    :param content:   Card body content.
    :param title:     Optional card title (rendered in a header).
    :param footer:    Optional footer content.
    :param image:     Optional image URL (top of the card).
    :param variant:   ``"default"``, ``"outlined"``, or ``"filled"``.
    :param attrs:     Extra HTML attributes.

    Example::

        Card("Content here", title="My Card", image="/pic.jpg",
             footer=Button("Action"))
    """

    tag = "div"

    def __init__(
        self,
        *content: Any,
        title: str | None = None,
        footer: Any = None,
        image: str | None = None,
        variant: str = "default",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-card miki-card-{variant}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "region")

        children: list[Any] = []

        if image:
            children.append(Img(src=image, class_="miki-card-image", alt=""))

        if title:
            from ..components import H3
            children.append(
                Div(H3(title), class_="miki-card-header")
            )

        if content:
            children.append(
                Div(*content, class_="miki-card-body")
            )

        if footer:
            children.append(
                Div(footer, class_="miki-card-footer")
            )

        super().__init__(*children, **attrs)


class Carousel(Component):
    """A lightweight image/content carousel with navigation arrows and dots.

    :param items:     List of (content, alt) tuples or Component instances.
    :param autoplay:  If ``True``, auto-advance every ``interval`` ms.
    :param interval:  Auto-advance interval in milliseconds (default 4000).
    :param attrs:     Extra HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        *items: Any,
        autoplay: bool = False,
        interval: int = 4000,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = "miki-carousel"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_label", "Image carousel")
        attrs.setdefault("data-miki-carousel", "true")
        attrs.setdefault("data-autoplay", str(autoplay).lower())
        attrs.setdefault("data-interval", str(interval))

        children: list[Any] = []

        slides: list[Any] = []
        for i, item in enumerate(items):
            if isinstance(item, tuple) and len(item) == 2:
                content, alt = item
            else:
                content, alt = item, None

            slide_class = "miki-carousel-slide"
            if i != 0:
                slide_class += " miki-carousel-slide-hidden"

            if isinstance(content, str) and (content.startswith("http") or content.startswith("/")):
                slide_content = Img(src=content, alt=alt or "", class_="miki-carousel-image")
            else:
                slide_content = content

            slides.append(Div(slide_content, class_=slide_class))

        children.append(Div(*slides, class_="miki-carousel-container"))

        # Navigation arrows
        children.append(
            Button(
                "‹",
                class_="miki-carousel-prev",
                aria_label="Previous slide",
                type="button",
                **{"data-miki-carousel-prev": "true"}
            )
        )
        children.append(
            Button(
                "›",
                class_="miki-carousel-next",
                aria_label="Next slide",
                type="button",
                **{"data-miki-carousel-next": "true"}
            )
        )

        # Dots navigation
        dots = [
            Span(class_="miki-carousel-dot", data_index=str(i))
            for i in range(len(items))
        ]
        children.append(
            Div(*dots, class_="miki-carousel-dots")
        )

        super().__init__(*children, **attrs)


class Pagination(Component):
    """A pagination control with previous/next buttons and page numbers.

    :param current:  Current page number (1-based).
    :param total:    Total number of pages.
    :param base_url: Base URL for pagination links (page number appended as ``/{n}``).
    :param attrs:    Extra HTML attributes.
    """

    tag = "nav"

    def __init__(
        self,
        current: int = 1,
        total: int = 1,
        *,
        base_url: str = "",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = "miki-pagination"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "navigation")
        attrs.setdefault("aria_label", "Pagination")

        if total <= 1:
            super().__init__(Ul(class_="miki-pagination-list"), **attrs)
            return

        items: list[Any] = []

        # Previous button
        if current > 1:
            items.append(
                Li(
                    A("«", href=f"{base_url}/{current - 1}",
                      class_="miki-pagination-link", aria_label="Previous page"),
                    class_="miki-pagination-item",
                )
            )
        else:
            items.append(
                Li(
                    Span("«", class_="miki-pagination-link", aria_hidden="true",
                         aria_label="Previous page"),
                    class_="miki-pagination-item miki-pagination-item-disabled",
                )
            )

        # Page numbers (show first 2, last 2, current±2)
        page_range = set()
        for p in range(1, total + 1):
            if p <= 2 or p >= total - 1 or abs(p - current) <= 2:
                page_range.add(p)

        prev_p = 0
        for p in sorted(page_range):
            if p - prev_p > 1:
                items.append(
                    Li(
                        Span("…", class_="miki-pagination-ellipsis"),
                        class_="miki-pagination-item",
                    )
                )
            if p == current:
                items.append(
                    Li(
                        Span(str(p), class_="miki-pagination-link",
                             aria_current="page"),
                        class_="miki-pagination-item miki-pagination-item-active",
                    )
                )
            else:
                items.append(
                    Li(
                        A(str(p), href=f"{base_url}/{p}", class_="miki-pagination-link"),
                        class_="miki-pagination-item",
                    )
                )
            prev_p = p

        # Next button
        if current < total:
            items.append(
                Li(
                    A("»", href=f"{base_url}/{current + 1}",
                      class_="miki-pagination-link", aria_label="Next page"),
                    class_="miki-pagination-item",
                )
            )
        else:
            items.append(
                Li(
                    Span("»", class_="miki-pagination-link", aria_hidden="true",
                         aria_label="Next page"),
                    class_="miki-pagination-item miki-pagination-item-disabled",
                )
            )

        super().__init__(Ul(*items, class_="miki-pagination-list"), **attrs)


class Avatar(Component):
    """A user avatar / profile picture.

    :param src:     Image source URL.
    :param alt:     Alt text (defaults to name or "User").
    :param size:    ``"sm"``, ``"md"`` (default), or ``"lg"``.
    :param status:  Optional status indicator: ``"online"``, ``"offline"``, ``"away"``.
    :param attrs:   Extra HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        src: str,
        *,
        alt: str | None = None,
        size: str = "md",
        status: str | None = None,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-avatar miki-avatar-{size}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)

        children: list[Any] = [
            Img(src=src, alt=alt or "User", class_="miki-avatar-image")
        ]

        if status:
            children.append(
                Span(
                    class_=f"miki-avatar-status miki-avatar-status-{status}",
                    aria_label=status,
                )
            )

        super().__init__(*children, **attrs)


class Badge(Component):
    """A small status badge / label.

    :param text:  Badge text content.
    :param variant: ``"default"``, ``"primary"``, ``"success"``, ``"warning"``,
                    ``"error"``, or ``"ghost"``.
    :param size:  ``"sm"`` or ``"md"`` (default).
    :param attrs: Extra HTML attributes.
    """

    tag = "span"

    def __init__(
        self,
        text: str,
        *,
        variant: str = "default",
        size: str = "md",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-badge miki-badge-{variant} miki-badge-{size}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "status")

        super().__init__(text, **attrs)


class Progress(Component):
    """A progress bar with label, percentage, and color variant.

    :param value:   Current progress (0-100).
    :param max:     Maximum value (default 100).
    :param label:   Optional visible label above the progress bar.
    :param variant: ``"default"``, ``"success"``, ``"warning"``, ``"error"``.
    :param attrs:   Extra HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        value: float,
        *,
        max_val: float = 100,
        label: str | None = None,
        variant: str = "default",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-progress miki-progress-{variant}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)

        pct = max(0, min(100, (value / max_val) * 100)) if max_val > 0 else 0

        children: list[Any] = []
        if label:
            children.append(
                Div(
                    P(label, class_="miki-progress-label"),
                    P(f"{pct:.0f}%", class_="miki-progress-value"),
                    class_="miki-progress-header",
                )
            )
        children.append(
            ProgressBar(
                value=value,
                max=max_val,
                class_=f"miki-progress-bar miki-progress-bar-{variant}",
                **{"aria-valuenow": str(value), "aria-valuemin": "0", "aria-valuemax": str(max_val)},
            )
        )

        super().__init__(*children, **attrs)
