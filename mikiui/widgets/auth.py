"""Authentication widgets: login and sign-up forms."""

from __future__ import annotations

from typing import Any

from ..components import A, Div, Form, Input, SubmitButton
from ..components.base import Component
from ..engine import _


class LoginForm(Component):
    """A username/password login form.

    Renders a ``Form(method="post")`` with username and password inputs, a login
    submit button, and a link to the sign-up page.

    :param action: form ``action`` URL (defaults to ``"/login"``).
    :param signup_url: URL of the sign-up page linked below the form.
    """

    tag = "form"

    def __init__(
        self, action: str = "/login", signup_url: str = "/signup", **attrs: Any
    ) -> None:
        attrs.setdefault("class", "miki-loginform")
        attrs.setdefault("method", "post")
        attrs.setdefault("action", action)
        attrs.setdefault("hx_post", action)
        children = [
            Input(
                type="text",
                name="username",
                placeholder=_("login_username_ph", "Username"),
                aria_label=_("login_username", "Username"),
                required=True,
            ),
            Input(
                type="password",
                name="password",
                placeholder=_("login_password_ph", "Password"),
                aria_label=_("login_password", "Password"),
                required=True,
            ),
            SubmitButton(_("login_button", "Log in")),
            Div(
                A(
                    _("login_signup_link", "Create an account"),
                    href=signup_url,
                    class_="miki-login-signup",
                ),
                class_="miki-login-links",
            ),
        ]
        super().__init__(*children, **attrs)


class SignupForm(Component):
    """A user registration form.

    Renders a ``Form(method="post")`` with name, email, password and
    password-confirm inputs (all ``required``) and a sign-up submit button.

    :param action: form ``action`` URL (defaults to ``"/signup"``).
    :param login_url: URL of the login page linked below the form.
    """

    tag = "form"

    def __init__(
        self, action: str = "/signup", login_url: str = "/login", **attrs: Any
    ) -> None:
        attrs.setdefault("class", "miki-signupform")
        attrs.setdefault("method", "post")
        attrs.setdefault("action", action)
        attrs.setdefault("hx_post", action)
        children = [
            Input(
                type="text",
                name="name",
                placeholder=_("signup_name_ph", "Full name"),
                aria_label=_("signup_name", "Full name"),
                required=True,
            ),
            Input(
                type="email",
                name="email",
                placeholder=_("signup_email_ph", "you@example.com"),
                aria_label=_("signup_email", "Email"),
                required=True,
            ),
            Input(
                type="password",
                name="password",
                placeholder=_("signup_password_ph", "Password"),
                aria_label=_("signup_password", "Password"),
                required=True,
            ),
            Input(
                type="password",
                name="password_confirm",
                placeholder=_("signup_password_confirm_ph", "Confirm password"),
                aria_label=_("signup_password_confirm", "Confirm password"),
                required=True,
            ),
            SubmitButton(_("signup_button", "Sign up")),
            Div(
                A(
                    _("signup_login_link", "Already have an account? Log in"),
                    href=login_url,
                    class_="miki-signup-login",
                ),
                class_="miki-signup-links",
            ),
        ]
        super().__init__(*children, **attrs)
