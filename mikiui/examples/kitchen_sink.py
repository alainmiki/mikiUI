"""Kitchen sink demo showcasing every MikiUI component and widget.

Run with:  mikiui dev --app mikiui.examples.kitchen_sink:app

This demo exercises every interactive widget to verify touch + mouse
compatibility across desktop and mobile viewport sizes.
"""

from __future__ import annotations
from importlib import reload

from mikiui import (
    A,
    Button,
    Div,
    Form,
    H1,
    H2,
    H3,
    IconButton,
    Input,
    Label,
    MikiApp,
    Modal,
    Navbar,
    Option,
    P,
    Radio,
    Select,
    Slider,
    Span,
    SubmitButton,
    Switch,
    Tabs,
    Textarea,
    Thead,
    Tbody,
    Tfoot,
    Tr,
    Th,
    Td,
    TreeView,
)
from mikiui.components.html import Section
from mikiui.components.feedback import ActivityIndicator, Pressable
from mikiui.components.layout_primitives import Divider
from mikiui.components import (
    Accordion,
    Abbr,
    Address,
    Article,
    Aside,
    BottomSheet,
    Audio,
    Br,
    Breadcrumbs,
    Canvas,
    Calendar,
    Caption,
    Chart,
    Checkbox,
    Cite,
    Citation,
    Details,
    Dialog,
    Em,
    Emphasis,
    Figure,
    Figcaption,
    Fieldset,
    FilePicker,
    Header,
    H4,
    H5,
    H6,
    Hr,
    Img,
    Kbd,
    Legend,
    Li,
    ListItem,
    ListView,
    Main,
    Mark,
    Meter,
    Ol,
    Optgroup,
    OrderedList,
    Output,
    Picture,
    Pre,
    Preformatted,
    ProgressBar as HTMLProgress,
    Small,
    Source,
    Strong,
    Summary,
    Table,
    Time,
    Tooltip,
    TreeView,
    Ul,
    UnorderedList,
    Upload,
    Var,
    Variable,
    Video,
    Blockquote,
    Code,
    EditorGroup,
    EditorTab,
    EditorArea,
)
from mikiui.widgets import (
    Avatar,
    Badge,
    Card,
    Carousel,
    ChatUI,
    CollapsiblePanel,
    ColorPicker,
    ContextWindow,
    Dashboard,
    DataGrid,
    DatePicker,
    Dial,
    DockablePanel,
    Drawer,
    Footer,
    FormWizard,
    GroupBox,
    Hero,
    IDEEditor,
    Icon,
    IconSet,
    InspectorPanel,
    KanbanBoard,
    LCDNumber,
    LoginForm,
    LogViewer,
    MediaPlayer,
    MenuBar,
    MessageBox,
    MikiButtonGroup,
    MikiColumnView,
    MikiMenu,
    MikiSizeGrip,
    MdiArea,
    MdiSubWindow,
    NotificationPanel,
    Pagination,
    ProgressDialog,
    ProfilerPanel,
    PropertyGrid,
    Rail,
    ScrollPanel,
    SearchPanel,
    Sidebar,
    SidePanel,
    SignupForm,
    SplashScreen,
    SplitView,
    StackedPanel,
    StatusBar,
    StreamingPanel,
    TabbedPanel,
    TerminalWidget,
    ThemeSwitcher,
    Toolbar,
    ToolboxPanel,
    DrawerToggle,
    Progress,
)

app = MikiApp(title="MikiUI Kitchen Sink")
app.set_theme("dark")
app.set_style_framework("tailwind",daisyui=True)

FLEX_ROW = "display: flex; flex-direction: row; align-items: center; gap: 1rem"
FLEX_COL = "display: flex; flex-direction: column; gap: 1rem"
CARD = "border: 1px solid var(--miki-border); border-radius: 0.5rem; padding: 1rem"
CARD_NO_PAD = "border: 1px solid var(--miki-border); border-radius: 0.5rem; overflow: hidden"
PADDING = "padding: 2rem"


@app.route("/")
def kitchen():
    return Div(
        Navbar(
            brand="MikiUI Kitchen Sink",
            links=[
                ("Components", "#components"),
                ("Interactive", "#interactive"),
                ("Layout", "#layout"),
                ("Data", "#data"),
                ("Surfaces", "#surfaces"),
                ("Navigation", "#navigation"),
                ("Advanced", "#advanced"),
            ],
            sticky=True,
            dark=True,
        ),
        Hero(
            title="MikiUI Kitchen Sink",
            subtitle="Every component and widget showcased — test on desktop and mobile.",
            action=Button("Get Started", variant="primary", hx_get="/components"),
            class_="text-2xl bg-red-500 "
        ),
        Div(
            # ==================================================================
            # SECTION 1: BASIC COMPONENTS
            # ==================================================================
            Section(id_="components", *[
                H2("Basic Components & Elements", class_="text-green-400 bg-info  text-2xl text-center py-4"),
                Div(
                    Div(
                        Button("Primary", variant="primary"),
                        Button("Secondary", variant="secondary"),
                        Button("Success", variant="success"),
                        Button("Warning", variant="warning"),
                        Button("Error", variant="error"),
                        Button("Outline", variant="outline"),
                        Button("Ghost", variant="ghost"),
                        style=FLEX_ROW + "; flex-wrap: wrap",
                    ),
                    Div(
                        Button("Small", size="sm"),
                        Button("Default", size="md"),
                        Button("Large", size="lg"),
                        style=FLEX_ROW + "; flex-wrap: wrap",
                    ),
                    Div(
                        Button("Icon Left", icon="star"),
                        Button("Icon Right", icon="star"),
                        style=FLEX_ROW,
                    ),
                    style=FLEX_COL,
                ),
                H3("Typography"),
                Div(
                    H1("Heading 1"),
                    H2("Heading 2"),
                    H3("Heading 3"),
                    P(
                        "This is a paragraph with ",
                        A("a link", href="#"),
                        " and ",
                        Strong("bold text"),
                        " and ",
                        Em("italic text"),
                        ".",
                    ),
                    Blockquote("A famous quote goes here."),
                    Div(
                        Code("const x = 42;"),
                        Kbd("Ctrl"),
                        Span(" + "),
                        Kbd("C"),
                    ),
                    Cite("MikiUI Documentation", cite="https://mikiui.dev"),
                    Time("Last updated August 24, 2026", datetime="2026-08-24"),
                    H4("Heading 4"),
                    H5("Heading 5"),
                    H6("Heading 6"),
                    Var("x"),
                    Small("Registered trademark"),
                    Mark("Marked text"),
                    Address("contact@mikiui.dev"),
                    style=FLEX_COL,
                ),
                H3("Forms"),
                Div(
                    Form(
                        GroupBox(
                            "User Registration",
                            Form(
                                Div(
                                    Label("Username"),
                                    Input(type="text", name="username", placeholder="Enter username"),
                                    style=FLEX_COL,
                                ),
                                Div(
                                    Label("Email"),
                                    Input(type="email", name="email", placeholder="you@example.com"),
                                    style=FLEX_COL,
                                ),
                                Div(
                                    Label("Password"),
                                    Input(type="password", name="password"),
                                    style=FLEX_COL,
                                ),
                                Div(
                                    Label("Bio"),
                                    Textarea(name="bio", placeholder="Tell us about yourself...", rows=3),
                                    style=FLEX_COL,
                                ),
                                Div(
                                    Label("Role"),
                                    Radio("Admin", name="role", value="admin", checked=True),
                                    Radio("Editor", name="role", value="editor"),
                                    Radio("Viewer", name="role", value="viewer"),
                                    style=FLEX_ROW,
                                ),
                                Div(
                                    Label("Newsletter"),
                                    Checkbox(name="newsletter", value="true"),
                                ),
                                Div(
                                    Label("Push notifications"),
                                    Switch(name="notifications", value="true"),
                                ),
                                Div(
                                    Label("Brightness"),
                                    Slider(name="brightness", min=0, max=100, value=50, show_value=True),
                                    style="width: 200px",
                                ),
                                Div(
                                    Label("Favorite color"),
                                    ColorPicker(name="color", value="#3b82f6"),
                                    style=FLEX_ROW + "; align-items: center",
                                ),
                                Div(
                                    Label("Birth date"),
                                    DatePicker(name="birth", value="2000-01-15"),
                                ),
                                Div(
                                    Label("Country"),
                                    Select(
                                        Option("Select country", value="", selected=True),
                                        Option("USA", value="usa"),
                                        Option("UK", value="uk"),
                                        Option("Canada", value="ca"),
                                        Option("Germany", value="de"),
                                        Option("Japan", value="jp"),
                                    ),
                                ),
                                Div(
                                    Label("File upload"),
                                    Upload(name="avatar", accept="image/*", label="Upload avatar"),
                                    style=FLEX_ROW + "; align-items: center",
                                ),
                                Div(
                                Label("HTML progress bar"),
                                HTMLProgress(value=45, max=100),
                            ),
                            Div(
                                Label("Output"),
                                Output("42"),
                            ),
                            Div(
                                Label("Meter"),
                                Meter(value=0.6, min=0, max=1, optlabel="60%"),
                            ),
                                SubmitButton("Submit"),
                                style=FLEX_COL,
                            ),
                        ),
                        style=FLEX_COL,
                    ),
                    style=CARD,
                ),
                H3("Cards & Avatars"),
                Div(
                    Div(
                        Card("Simple card with content."),
                        Card(
                            "Featured content",
                            title="Card Title",
                            footer=Button("Action", variant="primary"),
                        ),
                        Div(
                            Avatar(src="/static/mikiui-avatar.png", alt="User avatar", status="online"),
                            Avatar(src="/static/mikiui-avatar2.png", alt="Team member", status="away", size="lg"),
                            style=FLEX_ROW,
                        ),
                        style=FLEX_ROW,
                    ),
                ),
                H3("Badges"),
                Div(
                    Badge("Default", variant="default"),
                    Badge("Primary", variant="primary"),
                    Badge("Success", variant="success"),
                    Badge("Warning", variant="warning"),
                    Badge("Error", variant="error"),
                    style=FLEX_ROW,
                ),
                H3("Semantic HTML Elements"),
                Div(
                    Article(
                        P(Abbr("HTML", title="HyperText Markup Language"), " is the standard markup language."),
                        Address("Contact: mikiui@example.com"),
                        Mark("Highlighted important text"),
                        Small("Fine print and legal text."),
                        Time("August 24, 2026", datetime="2026-08-24"),
                        Br(),
                        Hr(),
                        Figcaption(Figure(Img(src="/static/mikiui-avatar.png", alt="Demo")), "Figure with caption."),
                        style=FLEX_COL,
                    ),
                    Aside(
                        P("This is an aside — supplementary content."),
                        style="font-size: 0.875rem; color: var(--miki-text-secondary)",
                    ),
                    style=CARD,
                ),
                H3("Lists & Definition"),
                Div(
                    UnorderedList(
                        ListItem("Unordered item 1"),
                        ListItem("Unordered item 2"),
                        ListItem("Unordered item 3"),
                    ),
                    OrderedList(
                        ListItem("Ordered step 1"),
                        ListItem("Ordered step 2"),
                        ListItem("Ordered step 3"),
                    ),
                    style=FLEX_COL,
                ),
                H3("Preformatted & Code"),
                Div(
                    Pre(Code("def hello_world():\n    print('Hello, MikiUI!')\n\nhello_world()")),
                    Preformatted("Monospaced\npreformatted\ntext block"),
                    style=FLEX_COL,
                ),
                H3("Table Sub-Elements"),
                Div(
                    Table(
                        Caption("User data"),
                        Thead(
                            Tr(Th("Name"), Th("Email"), Th("Role")),
                        ),
                        Tbody(
                            Tr(Td("Alice"), Td("alice@ex.com"), Td("Admin")),
                            Tr(Td("Bob"), Td("bob@ex.com"), Td("User")),
                        ),
                        Tfoot(
                            Tr(Td(Strong("Total: 2 users")), Td(""), Td("")),
                        ),
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Fieldset & Legend"),
                Div(
                    Fieldset(
                        Legend("Shipping Address"),
                        Div(
                            Label("Street"), Input(type="text", name="street"),
                            Label("City"), Input(type="text", name="city"),
                            Label("ZIP"), Input(type="text", name="zip"),
                            style=FLEX_COL,
                        ),
                    ),
                    style=CARD,
                ),
                H3("Optgroup in Select"),
                Div(
                    Select(
                        Optgroup("North America",
                            Option("USA", value="usa"),
                            Option("Canada", value="ca"),
                        ),
                        Optgroup("Europe",
                            Option("UK", value="uk"),
                            Option("Germany", value="de"),
                            Option("France", value="fr"),
                        ),
                        name="region",
                    ),
                    style=CARD,
                ),
                H3("Audio & Video"),
                Div(
                    Audio(
                        Source(src="/static/sample.mp3", type_="audio/mpeg"),
                        "Your browser does not support the audio element.",
                        controls=True,
                    ),
                    Video(
                        Source(src="/static/sample.mp4", type_="video/mp4"),
                        "Your browser does not support the video element.",
                        controls=True,
                    ),
                    Canvas(width=300, height=150, id_="demo-canvas"),
                    style=FLEX_COL,
                ),
                H3("Icon Set"),
                Div(
                    Div(
                        Icon("home"),
                        Icon("settings"),
                        Icon("user"),
                        Icon("search"),
                        Icon("star"),
                        Icon("plus"),
                        Icon("check"),
                        Icon("menu"),
                        Icon("alert"),
                        Icon("copy"),
                        Icon("download"),
                        Icon("edit"),
                        style=FLEX_ROW + "; flex-wrap: wrap",
                    ),
                    style=CARD,
                ),
            ]),
            # ==================================================================
            # SECTION 2: INTERACTIVE WIDGETS
            # ==================================================================
            Section(id_="interactive", *[
                H2("Interactive Widgets"),
                H3("Tabs (click / tap / keyboard / swipe)"),
                Div(
                    Tabs(
                        tabs=[
                            ("Overview", Div(P("Project overview and statistics."))),
                            ("Activity", Div(P("Recent activity feed."))),
                            ("Documents", Div(P("Document library and resources."))),
                        ],
                        closable=True,
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Collapsible & Accordion"),
                Div(
                    CollapsiblePanel(
                        "Frequently Asked Questions",
                        Div(
                            P("Q: What is MikiUI?"),
                            P("A: A Python-first UI framework."),
                            P("Q: How to get started?"),
                            P("A: Run mikiui new myapp and start coding."),
                            style=FLEX_COL,
                        ),
                        open=True,
                    ),
                    Accordion(
                        items=[
                            ("Installation", P("Run: pip install mikiui")),
                            ("Usage", P("Create a MikiApp and define routes.")),
                            ("Deployment", P("Use mikiui build for production.")),
                        ],
                    ),
                    style=FLEX_COL,
                ),
                H3("Details & Disclosure"),
                Div(
                    Details(
                        Summary("Click to expand — native details element"),
                        P("This content is wrapped in a native HTML <details> element."),
                        open=False,
                    ),
                    Details(
                        Summary("Another expandable section"),
                        P("Native HTML disclosure widget with keyboard support."),
                        open=True,
                    ),
                    style=FLEX_COL,
                ),
                H3("Split View (touch + mouse drag)"),
                Div(
                    SplitView(
                        Div("Left pane — drag the splitter to resize."),
                        Div("Right pane — works on both touch and mouse."),
                        orientation="horizontal",
                        min_size=150,
                        resize_mode="both",
                    ),
                    style=CARD_NO_PAD + "; height: 12rem",
                ),
                H3("Slider with Touch Feedback"),
                Div(
                    Div(
                        Slider(name="volume", min=0, max=100, value=75, label="Volume", show_value=True),
                        Slider(name="brightness", min=0, max=100, value=30, label="Brightness", show_value=True),
                        style=FLEX_COL + "; width: 200px",
                    ),
                    style=CARD,
                ),
                H3("Pressable Feedback (touch + mouse)"),
                Div(
                    Pressable(
                        Div("Opacity feedback on press", style="padding: 1rem"),
                        feedback="opacity",
                    ),
                    Pressable(
                        Div("Scale feedback on press", style="padding: 1rem"),
                        feedback="scale",
                    ),
                    style=FLEX_ROW,
                ),
                H3("Progress & Activity"),
                Div(
                    Progress(value=75, label="75% complete"),
                    Progress(value=40, label="40% — warning", variant="warning"),
                    ActivityIndicator(size="md", label="Loading data..."),
                    ActivityIndicator(size="lg", label="Processing..."),
                    style=FLEX_COL,
                ),
                H3("Tooltip & Badges"),
                Div(
                    Div(
                        Button("Hover me", variant="secondary"),
                        Tooltip("Hover me", tip="This is a tooltip description for the button."),
                        style="margin-right: 2rem",
                    ),
                    Badge("Touch-ready", variant="success"),
                    Badge("Mouse-ready", variant="info"),
                    style=FLEX_ROW,
                ),
                H3("Breadcrumb Navigation"),
                Div(
                    Breadcrumbs(
                        [("Home", "/"), ("Library", "/library"), ("Documents", None)],
                    ),
                    style=CARD,
                ),
            ]),
            # ==================================================================
            # SECTION 3: LAYOUT WIDGETS
            # ==================================================================
            Section(id_="layout", *[
                H2("Layout Widgets"),
                H3("Dockable Panel (drag & drop on touch/mouse)"),
                Div(
                    DockablePanel(
                        "Properties Panel",
                        Div(
                            P("Drag this panel's header to move it."),
                            P("Release near a screen edge to snap-dock."),
                            P("Click the detach button to float, or double-click to toggle."),
                            style=FLEX_COL,
                        ),
                        dock="right",
                        closeable=True,
                        collapsible=True,
                        detachable=True,
                        open=False,
                        minimal=True,
                        snap_threshold=100,
                    ),
                    style=CARD_NO_PAD + "; height: 16rem",
                ),
                H3("Stacked Panel"),
                Div(
                    StackedPanel(
                        pages=[
                            ("Overview", Div("Project overview metrics and KPIs.")),
                            ("Analytics", Div("Traffic and engagement data.")),
                            ("Reports", Div("Generated reports and exports.")),
                        ],
                        open=True,
                    ),
                    style=CARD_NO_PAD + "; height: 10rem",
                ),
                H3("Tabbed Panel"),
                Div(
                    TabbedPanel(
                        tabs=[
                            ("Tab 1", "Content for tab 1 — settings and configuration."),
                            ("Tab 2", "Content for tab 2 — user preferences."),
                            ("Tab 3", "Content for tab 3 — system information."),
                        ],
                        closable=True,
                    ),
                    style=CARD_NO_PAD + "; height: 8rem",
                ),
                H3("MdiArea (Multiple Document Interface)"),
                Div(
                    MdiArea(
                        MdiSubWindow("main.py",
                            Div(
                                P("# /app.py"),
                                P("def hello():"),
                                P("&nbsp;&nbsp;&nbsp;print('Hello, MikiUI!')"),
                                style="font-family: ui-monospace, monospace",
                            ),
                        ),
                        MdiSubWindow("readme.md",
                            Div(
                                P("# MikiUI"),
                                P("Python-first UI framework with touch support."),
                                style="font-family: ui-monospace, monospace",
                            ),
                        ),
                    ),
                    style=CARD_NO_PAD + "; height: 12rem",
                ),
                H3("Toolbox Panel"),
                Div(
                    ToolboxPanel(
                        groups={
                            "Components": Div(
                                P("Button"), P("Card"), P("Dialog"), P("Tabs"), P("Slider"),
                            ),
                            "Widgets": Div(
                                P("DataGrid"), P("Carousel"), P("Kanban"), P("Chat"),
                            ),
                            "Surfaces": Div(
                                P("Modal"), P("Drawer"), P("MessageBox"),
                            ),
                        },
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Toolbar & StatusBar"),
                Div(
                    Toolbar(
                        Button("New", variant="ghost", type="button"),
                        Button("Open", variant="ghost", type="button"),
                        Button("Save", variant="ghost", type="button"),
                        MikiButtonGroup(["🔍", "⚙", "💡"]),
                        style="flex: 1",
                    ),
                    StatusBar(
                        Div("Ln 1, Col 1"),
                        Div("UTF-8"),
                        Div("Python"),
                        style="justify-content: space-between",
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Side Panel"),
                Div(
                    SidePanel(
                        side="right",
                        header="Side Panel",
                        collapsible=True,
                        children=Div(
                            P("This is a side panel that can be collapsed."),
                            P("It stays fixed on the right side."),
                        ),
                    ),
                     style=CARD_NO_PAD + "; height: 12rem",
                 ),
                H3("Size Grip"),
                Div(
                    MikiSizeGrip(),
                    style=CARD,
                ),
                H3("Scroll Panel"),
                Div(
                    ScrollPanel(
                        "This is scrollable content. ",
                        "Lorem ipsum dolor sit amet, consectetur ",
                        "adipiscing elit. Sed do eiusmod tempor ",
                        "incididunt ut labore et dolore magna aliqua.",
                    ),
                    style=CARD_NO_PAD + "; height: 8rem",
                ),
            ]),
            # ==================================================================
            # SECTION 4: DATA DISPLAY
            # ==================================================================
            Section(id_="data", *[
                H2("Data Display"),
                H3("DataGrid (sortable, filterable, paginated)"),
                Div(
                    DataGrid(
                        columns=["Name", "Email", "Role", "Status"],
                        rows=[
                            ["Alice Chen", "alice@example.com", "Admin", "Active"],
                            ["Bob Smith", "bob@example.com", "User", "Inactive"],
                            ["Carol Wong", "carol@example.com", "User", "Active"],
                            ["David Kim", "david@example.com", "Admin", "Active"],
                            ["Eve Brown", "eve@example.com", "User", "Pending"],
                        ],
                        sortable=True,
                        filterable=True,
                        pagination=True,
                        page_size=3,
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Chart"),
                Div(
                    Chart(
                        series=[30, 45, 28, 60],
                        kind="bar",
                        height=200,
                    ),
                    style=CARD,
                ),
                H3("Calendar"),
                Div(
                    Calendar(),
                    style=CARD_NO_PAD,
                ),
                H3("File Picker (drag & drop)"),
                Div(
                    FilePicker(name="upload", label="Drop files here or click to browse", accept="image/*"),
                    style=CARD,
                ),
                H3("Tree View"),
                Div(
                    TreeView(
                        nodes=[
                            ("📁 src", [
                                ("📄 __init__.py", None),
                                ("📁 components", [
                                    ("📄 button.py", None),
                                    ("📄 dialog.py", None),
                                ]),
                                ("📁 widgets", [
                                    ("📄 kanban.py", None),
                                    ("📄 chat.py", None),
                                ]),
                            ]),
                            ("📁 tests", [
                                ("📄 test_components.py", None),
                                ("📄 test_widgets.py", None),
                            ]),
                        ],
                    ),
                    style=CARD,
                ),
                H3("List View"),
                Div(
                    ListView(
                        items=["First item", "Second item", "Third item", "Fourth item"],
                        selected=0,
                    ),
                    style=CARD,
                ),
                H3("Table"),
                Div(
                    Table(
                        headers=["Product", "SKU", "Price", "Stock"],
                        rows=[
                            ["Widget A", "WID-001", "$12.99", "In Stock"],
                            ["Widget B", "WID-002", "$24.50", "Low Stock"],
                            ["Widget C", "WID-003", "$8.75", "In Stock"],
                            ["Widget D", "WID-004", "$45.00", "Out of Stock"],
                        ],
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Pagination"),
                Div(
                    Pagination(current=1, total=5, base_url="/page"),
                    style=CARD,
                ),
                H3("Property Grid"),
                Div(
                    PropertyGrid({
                        "Application": "MikiUI Kitchen Sink",
                        "Version": "1.0.0",
                        "Author": "MikiUI Team",
                        "License": "MIT",
                        "Python": "3.14+",
                        "Status": "Production",
                    }),
                    style=CARD_NO_PAD,
                ),
            ]),
            # ==================================================================
            # SECTION 5: SURFACES
            # ==================================================================
            Section(id_="surfaces", *[
                H2("Surfaces & Overlays"),
                H3("Dialog (native <dialog>)"),
                Div(
                    Div(
                        Button("Open Dialog", variant="primary"),
                        Div(
                            Div(
                                Button("Close", **{"data-miki-dialog-close": "true"}),
                                style="margin-bottom: 0.5rem",
                            ),
                            P("This is a native HTML dialog element."),
                            P("Click the backdrop or the close button to dismiss."),
                            style=FLEX_COL,
                        ),
                        Dialog(
                            title="Native Dialog",
                            close_on_overlay=True,
                            close_on_escape=True,
                        ),
                        style=FLEX_ROW + "; gap: 2rem",
                    ),
                    style=CARD,
                ),
                H3("Modal"),
                Div(
                    Modal(
                        "This is a modal dialog with focus trap and ESC support.",
                        title="Modal Title",
                        open=False,
                    ),
                    style=CARD,
                ),
                H3("MessageBox (all types)"),
                Div(
                    Div(
                        MessageBox("Success!", "Your changes have been saved successfully.", kind="success", style="display: none;"),
                        MessageBox("Information", "Please review the settings before proceeding.", kind="info", style="display: none;"),
                        MessageBox("Warning", "Your session will expire in 5 minutes.", kind="warning", style="display: none;"),
                        MessageBox("Error", "Database connection failed. Retrying...", kind="error", style="display: none;"),
                        MessageBox("Question", "Are you sure you want to delete this file?", kind="question", style="display: none;"),
                        style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem",
                    ),
                    Div(
                        Button("Show Success", variant="primary", hx_get="#", style="margin-right: 0.5rem"),
                        Button("Show Error", variant="error"),
                        style=FLEX_ROW,
                    ),
                ),
                H3("Drawer"),
                Div(
                    Div(
                        Button("Open Left", onclick="mikiDrawer.open('.ks-drawer-left')", class_="mr-2"),
                        Button("Open Right", onclick="mikiDrawer.open('.ks-drawer-right')", class_="mr-2"),
                        Button("Open Top", onclick="mikiDrawer.open('.ks-drawer-top')", class_="mr-2"),
                        Button("Open Bottom", onclick="mikiDrawer.open('.ks-drawer-bottom')", class_="mr-2"),
                        Button("Open Override", onclick="mikiDrawer.open('.ks-drawer-override')"),
                        class_="flex gap-2 mb-2",
                    ),
                    Drawer(
                        Div(
                            H4("Left Drawer"),
                            P("Slides in from the left edge. Supports ESC, overlay click, close button."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-left')", class_="mt-2"),
                            P("Try the buttons above to open different drawer sides.", class_="mt-3 text-sm"),
                        ),
                        title="Left Drawer",
                        side="left",
                        size="md",
                        open=False,
                        class_="ks-drawer-left",
                    ),
                    Drawer(
                        Div(
                            H4("Right Drawer"),
                            P("Slides in from the right edge."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-right')", class_="mt-2"),
                        ),
                        title="Right Drawer",
                        side="right",
                        size="lg",
                        open=False,
                        class_="ks-drawer-right",
                    ),
                    Drawer(
                        Div(
                            H4("Top Drawer"),
                            P("Slides down from the top edge."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-top')", class_="mt-2"),
                        ),
                        title="Top Drawer",
                        side="top",
                        open=False,
                        class_="ks-drawer-top",
                    ),
                    Drawer(
                        Div(
                            H4("Bottom Drawer"),
                            P("Slides up from the bottom edge."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-bottom')", class_="mt-2"),
                        ),
                        title="Bottom Drawer",
                        side="bottom",
                        open=False,
                        class_="ks-drawer-bottom",
                    ),
                    Drawer(
                        Div(
                            H4("Open-side Override"),
                            P("This drawer uses side=left but opens from the right via open_side=right."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-override')", class_="mt-2"),
                        ),
                        title="Override Drawer",
                        side="left",
                        open_side="right",
                        open=False,
                        class_="ks-drawer-override",
                    ),
                    Drawer(
                        Div(
                            H4("Bottom Drawer"),
                            P("Slides up from the bottom edge."),
                            Button("Close", onclick="mikiDrawer.close('.ks-drawer-bottom')", class_="mt-2"),
                        ),
                        title="Bottom Drawer",
                        side="bottom",
                        open=False,
                        class_="ks-drawer-bottom",
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Bottom Sheet"),
                Div(
                    Div(
                        Button("Open Sheet (md)", onclick="mikiBottomSheet.open('.ks-bottomsheet')", class_="mr-2"),
                        Button("Open Sheet (full)", onclick="mikiBottomSheet.open('.ks-bottomsheet-full')", class_="mr-2"),
                    ),
                    BottomSheet(
                        Div(
                            H4("Bottom Sheet (md)"),
                            P("This sheet slides up from the bottom."),
                            P("Drag the handle down to dismiss, or click the backdrop.", class_="text-sm"),
                            Button("Close", onclick="mikiBottomSheet.close('.ks-bottomsheet')", class_="mt-2"),
                        ),
                        title="Bottom Sheet",
                        size="md",
                        on_close="console.log('sheet closed')",
                        class_="ks-bottomsheet",
                    ),
                    BottomSheet(
                        Div(
                            H4("Full-screen Sheet"),
                            P("This sheet takes up the full screen — ideal for mobile forms or detail views."),
                            Button("Close", onclick="mikiBottomSheet.close('.ks-bottomsheet-full')", class_="mt-2"),
                        ),
                        title="Full Sheet",
                        size="full",
                        class_="ks-bottomsheet-full",
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Progress Dialog"),
                Div(
                    ProgressDialog(title="Installing updates", message="Downloading package 23 of 47...", value=49, style="display: none;"),
                    style=CARD_NO_PAD,
                ),
                H3("Splash Screen"),
                Div(
                    SplashScreen(title="MikiUI", subtitle="Loading...", style="display: none;"),
                    style=CARD_NO_PAD,
                ),
            ]),
            # ==================================================================
            # SECTION 6: NAVIGATION
            # ==================================================================
            Section(id_="navigation", *[
                H2("Navigation Widgets"),
                H3("Navbar (shows hamburger on mobile)"),
                Div(
                    Navbar(
                        brand="My App",
                        links=[("Home", "/"), ("Products", "/products"), ("About", "/about"), ("Contact", "/contact")],
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Sidebar"),
                Div(
                    Div(
                        Sidebar(
                            ("Dashboard", "/"),
                            ("Analytics", "/analytics"),
                            ("Reports", "/reports"),
                            ("Settings", "/settings"),
                            title="Navigation",
                        ),
                        style="width: 16rem; height: 20rem",
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Rail"),
                Div(
                    Div(
                        Rail(
                            ("Home", "/", "home"),
                            ("Settings", "/settings", "settings"),
                            ("Profile", "/profile", "user"),
                            side="left",
                        ),
                        style="height: 16rem",
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Menu Bar"),
                Div(
                    MenuBar(
                        items=[
                            ("File", [("New", "/new"), ("Open", "/open"), ("Save", "/save")]),
                            ("Edit", [("Cut", "/cut"), ("Copy", "/copy"), ("Paste", "/paste")]),
                            ("View", [("Zoom In", "/zoom-in"), ("Zoom Out", "/zoom-out")]),
                        ],
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Context Window"),
                Div(
                    ContextWindow(
                        Div(P("Context menu action 1"), P("Context menu action 2")),
                        trigger=Button("Right-click me"),
                        position="bottom",
                    ),
                    style=CARD,
                ),
                H3("Column View"),
                Div(
                    MikiColumnView(
                        [["Documents", "Photos"], ["Report.pdf", "Vacation.png", "Work.jpg"], ["Details"]],
                    ),
                    style=CARD_NO_PAD,
                ),
            ]),
            # ==================================================================
            # SECTION 7: ADVANCED WIDGETS
            # ==================================================================
            Section(id_="advanced", *[
                H2("Advanced Widgets"),
                H3("Carousel (swipe / tap dots / autoplay)"),
                Div(
                    Carousel(
                        Div(
                            Div(
                                H3("Slide 1: Welcome"),
                                P("Discover the power of MikiUI."),
                                style="background: #e0f2fe; padding: 2rem; text-align: center",
                            ),
                        ),
                        Div(
                            Div(
                                H3("Slide 2: Components"),
                                P("20+ components, all touch-ready."),
                                style="background: #dcfce7; padding: 2rem; text-align: center",
                            ),
                        ),
                        Div(
                            Div(
                                H3("Slide 3: Widgets"),
                                P("Drag-and-drop, sort, and more."),
                                style="background: #fef3c7; padding: 2rem; text-align: center",
                            ),
                        ),
                        autoplay=True,
                        interval=5000,
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Kanban Board (drag & drop on touch/mouse)"),
                Div(
                    KanbanBoard({
                        "Todo": ["Write project specs", "Design component API", "Setup CI/CD pipeline"],
                        "In Progress": ["Implement DragAndDrop", "Add unit tests", "Write documentation"],
                        "Code Review": ["Slider widget", "Tabs widget"],
                        "Done": ["Project scaffold", "CLI tooling", "Theme registry"],
                    }),
                    style=CARD_NO_PAD + "; height: 24rem",
                ),
                H3("Chat UI"),
                Div(
                    ChatUI(
                        messages=[
                            {"role": "user", "text": "Hello there!"},
                            {"role": "bot", "text": "Hi! How's the MikiUI project going?"},
                            {"role": "user", "text": "It's going great! The kitchen sink demo is almost ready."},
                            {"role": "bot", "text": "Want to try the new carousel on mobile? Just swipe left!"},
                        ],
                    ),
                    style=CARD_NO_PAD + "; height: 18rem",
                ),
                H3("Log Viewer"),
                Div(
                    LogViewer(
                        lines=[
                            "info: Application started on port 8000",
                            ("info", "Server listening on http://127.0.0.1:8000"),
                            ("warning", "Connection timeout - retrying in 3s"),
                            ("error", "Database connection failed: Connection refused"),
                            ("info", "Reconnected to database"),
                            "debug: Processing batch record 12345",
                            "info: Request completed in 42ms",
                        ],
                    ),
                    style="font-family: ui-monospace, monospace; font-size: 0.875rem",
                ),
                H3("Terminal Widget"),
                Div(
                    TerminalWidget(
                        lines=[
                            "$ mikiui --version",
                            "MikiUI v1.0.0",
                            "$ pip list | grep mikiui",
                            "mikiui          1.0.0",
                            "$ python -m pytest tests/",
                            "..........................................",
                            "636 passed in 2.5s",
                            "$ ",
                        ],
                    ),
                    style=CARD_NO_PAD + "; height: 12rem",
                ),
                H3("IDE Editor"),
                Div(
                    IDEEditor(
                        content="from mikiui import *\n\napp = MikiApp(title='My App')\n\n@app.route('/')\ndef home():\n    return Div(H1('Hello MikiUI'))\n",
                        language="python",
                    ),
                    style=CARD_NO_PAD + "; height: 18rem",
                ),
                H3("Media Player"),
                Div(
                    MediaPlayer(
                        source="https://commondatastorage.googleapis.com/gtvideos-bucket/speedguardproj.mp4",
                        kind="video",
                    ),
                    style=CARD_NO_PAD + "; height: 14rem",
                ),
                H3("Dashboard"),
                Div(
                    Dashboard(
                        ("Total Users", "1,234", "+12%"),
                        ("Revenue", "$12.3k", "+5%"),
                        ("Orders", "567", "-3%"),
                        ("Active Now", "89", "+21%"),
                        columns=4,
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Form Wizard (Back/Next on click/tap)"),
                Div(
                    FormWizard(
                        steps=[
                            ("Account", Div(
                                Label("Username"), Input(name="username", placeholder="Pick a username"),
                                Label("Email"), Input(type="email", name="email", placeholder="you@example.com"),
                                style=FLEX_COL,
                            )),
                            ("Profile", Div(
                                Label("Display name"), Input(name="display_name"),
                                Label("Bio"), Textarea(name="bio", rows=2),
                                style=FLEX_COL,
                            )),
                            ("Preferences", Div(
                                Label("Theme"),
                                Select(Option("Light", value="light"), Option("Dark", value="dark")),
                                Label("Notifications"),
                                Switch(name="notify", value="true"),
                                style=FLEX_COL,
                            )),
                            ("Review", P("Review your information and click Finish.")),
                        ],
                    ),
                    style=CARD_NO_PAD + "; height: 20rem",
                ),
                H3("Dial"),
                Div(
                    Div(
                        Dial(value=50, min=0, max=100, step=2, size=140),
                        style=CARD_NO_PAD + "; height: 200px",
                    ),
                    style=CARD,
                ),
                H3("Inspector Panel"),
                Div(
                    InspectorPanel(
                        obj={"name": "MikiUI", "version": "1.0.0", "active": True},
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Profiler Panel"),
                Div(
                    ProfilerPanel(
                        metrics=[
                            ("render", 12.5),
                            ("diff", 3.2),
                            ("network", 45.1),
                            ("total", 60.8),
                        ],
                    ),
                    style=CARD_NO_PAD,
                ),
                H3("Search Panel"),
                Div(
                    SearchPanel(placeholder="Search components..."),
                    style=CARD_NO_PAD,
                ),
                H3("Streaming Panel"),
                Div(
                    StreamingPanel(title="Live Events"),
                    style=CARD_NO_PAD + "; height: 10rem",
                ),
                H3("Notification Panel"),
                Div(
                    NotificationPanel(),
                    style=CARD_NO_PAD,
                ),
                H3("Icon Set"),
                Div(
                    Div(
                        Icon("home", aria_label="Home"),
                        Icon("settings", aria_label="Settings"),
                        Icon("user", aria_label="User"),
                        Icon("star", aria_label="Star"),
                        Icon("search", aria_label="Search"),
                        style=FLEX_ROW,
                    ),
                    style=CARD,
                ),
                H3("Theme Switcher"),
                Div(
                    ThemeSwitcher(
                        app=app,
                        label="Choose theme:",
                    ),
                    style=CARD,
                ),
            ]),
            # ==================================================================
            # SECTION 8: FORMS & AUTH
            # ==================================================================
            Section(id_="forms", *[
                H2("Authentication & Form Widgets"),
                H3("Login Form"),
                Div(
                    LoginForm(action="/login", signup_url="/signup"),
                    style=CARD,
                ),
                H3("Signup Form"),
                Div(
                    SignupForm(action="/signup", login_url="/login"),
                    style=CARD,
                ),
                H3("Editor Group (IDE-style tabs)"),
                Div(
                    EditorArea(
                        EditorGroup(
                            tabs=[
                                EditorTab("main.py", "from mikiui import *\n\napp = MikiApp()"),
                                EditorTab("styles.css", "body { margin: 0; }"),
                                EditorTab("README.md", "# My App"),
                            ],
                        ),
                        EditorGroup(
                            tabs=[
                                EditorTab("console", "$ Starting server...\n$ Ready."),
                            ],
                        ),
                        orientation="vertical",
                    ),
                    style=CARD_NO_PAD + "; height: 16rem",
                ),
                H3("Drawer Toggle"),
                Div(
                    DrawerToggle(label="Open Drawer", target="sidebar-drawer"),
                    style=CARD,
                ),
            ]),
            # ==================================================================
            # Responsive test info
            # ==================================================================
            Div(
                H3("Responsive Test Info"),
                Div(
                    P("Viewport width:"),
                    Span("Check on mobile!", class_="miki-badge miki-badge-error"),
                    style=FLEX_ROW,
                ),
                Badge("Touch-ready", variant="success"),
                Badge("Mouse-ready", variant="info"),
                style=FLEX_COL,
            ),
            Divider(),
            Footer(
                P("MikiUI Kitchen Sink &middot; Python-first UI framework &middot; Touch & Mouse Compatible"),
                style="text-align: center",
            ),
            style=PADDING + f"; {FLEX_COL}; gap: 2rem",
        ),
    )


@app.route("/components")
def components_page():
    return Div(
        Navbar(brand="Components", links=[("Home", "/")]),
        Div(
            H1("All Components"),
            P("MikiUI provides 20+ components and 30+ widgets."),
            style=PADDING,
        ),
    )


if __name__ == "__main__":
    # app.run(desktop=False,browser=True, reload=True)
    app.run(desktop=False,browser=True,reload=True)
