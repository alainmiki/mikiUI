"""MikiUI widgets.

High-level composite UI built from :mod:`mikiui.components`. Each widget is a
thin Python class wrapping a component tree, keeping the beginner-friendly API
described in ``context/components.md``.
"""

from __future__ import annotations

from .advanced import FormWizard, NotificationPanel, SearchPanel, StreamingPanel
from .advanced_widgets import Avatar, Badge, Card, Carousel, Pagination, Progress
from .auth import LoginForm, SignupForm
from .chatui import ChatUI
from .dashboard import Dashboard
from .datagrid import DataGrid
from .dockable_panel import DockablePanel
from .icon import Icon, IconSet
from .ide_editor import IDEEditor
from .inspector_panel import InspectorPanel
from .kanbanboard import KanbanBoard
from .layout_widgets import Footer, Hero, Sidebar
from .mediaplayer import MediaPlayer
from .navigation_widgets import ContextWindow, Drawer, DrawerToggle, Rail
from .panels import (
    CollapsiblePanel,
    ColorPicker,
    DatePicker,
    Dial,
    FilePicker,
    GroupBox,
    LCDNumber,
    LogViewer,
    MdiArea,
    MdiSubWindow,
    MenuBar,
    MessageBox,
    MikiButtonGroup,
    MikiColumnView,
    MikiMenu,
    MikiSizeGrip,
    ProfilerPanel,
    ProgressDialog,
    ScrollPanel,
    SidePanel,
    SplashScreen,
    StackedPanel,
    StatusBar,
    TabbedPanel,
    Toolbar,
    ToolboxPanel,
)
from .property_grid import PropertyGrid
from .splitview import SplitView
from .terminal_widget import TerminalWidget
from .theme_switcher import ThemeSwitcher

__all__ = [
    "Avatar",
    "Badge",
    "Card",
    "Carousel",
    "ChatUI",
    "ColorPicker",
    "CollapsiblePanel",
    "ContextWindow",
    "Dashboard",
    "DataGrid",
    "DatePicker",
    "Dial",
    "DockablePanel",
    "Drawer",
    "DrawerToggle",
    "FilePicker",
    "Footer",
    "FormWizard",
    "GroupBox",
    "Hero",
    "IDEEditor",
    "Icon",
    "IconSet",
    "InspectorPanel",
    "KanbanBoard",
    "LCDNumber",
    "LoginForm",
    "LogViewer",
    "MediaPlayer",
    "MenuBar",
    "MessageBox",
    "MikiButtonGroup",
    "MikiColumnView",
    "MikiMenu",
    "MikiSizeGrip",
    "MdiArea",
    "MdiSubWindow",
    "NotificationPanel",
    "Pagination",
    "Progress",
    "ProgressDialog",
    "ProfilerPanel",
    "PropertyGrid",
    "Rail",
    "ScrollPanel",
    "SearchPanel",
    "Sidebar",
    "SidePanel",
    "SignupForm",
    "SplashScreen",
    "SplitView",
    "StackedPanel",
    "StatusBar",
    "StreamingPanel",
    "TabbedPanel",
    "TerminalWidget",
    "ThemeSwitcher",
    "Toolbar",
    "ToolboxPanel",
]
