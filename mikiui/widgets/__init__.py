"""MikiUI widgets.

High-level composite UI built from :mod:`mikiui.components`. Each widget is a
thin Python class wrapping a component tree, keeping the beginner-friendly API
described in ``context/components.md``.
"""

from __future__ import annotations

from .advanced import FormWizard, SearchPanel, StreamingPanel, NotificationPanel
from .auth import LoginForm, SignupForm
from .chatui import ChatUI
from .dashboard import Dashboard
from .datagrid import DataGrid
from .dockable_panel import DockablePanel
from .ide_editor import IDEEditor
from .inspector_panel import InspectorPanel
from .kanbanboard import KanbanBoard
from .mediaplayer import MediaPlayer
from .panels import (
    ColorPicker,
    CollapsiblePanel,
    DatePicker,
    Dial,
    GroupBox,
    LCDNumber,
    LogViewer,
    MdiArea,
    MdiSubWindow,
    MenuBar,
    MessageBox,
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

__all__ = [
    "ChatUI",
    "ColorPicker",
    "CollapsiblePanel",
    "Dashboard",
    "DataGrid",
    "DatePicker",
    "Dial",
    "DockablePanel",
    "FormWizard",
    "GroupBox",
    "IDEEditor",
    "InspectorPanel",
    "KanbanBoard",
    "LCDNumber",
    "LoginForm",
    "LogViewer",
    "MediaPlayer",
    "MenuBar",
    "MessageBox",
    "MdiArea",
    "MdiSubWindow",
    "NotificationPanel",
    "ProgressDialog",
    "PropertyGrid",
    "ScrollPanel",
    "SearchPanel",
    "SidePanel",
    "SignupForm",
    "SplashScreen",
    "SplitView",
    "StackedPanel",
    "StatusBar",
    "StreamingPanel",
    "TabbedPanel",
    "TerminalWidget",
    "Toolbar",
    "ToolboxPanel",
]
