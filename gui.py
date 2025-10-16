import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk
import core
import yaml
import os

class DockerManagerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Docker Container Manager")
        self.set_default_size(1400, 900)
        self.set_position(Gtk.WindowPosition.CENTER)

        try:
            self.client = core.get_client()
        except ConnectionError as e:
            self.show_error_dialog(str(e))
            return

        # Main vertical box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Add header bar
        self.create_header_bar(main_vbox)

        # Content area with margins
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        main_vbox.pack_start(content_box, True, True, 0)

        # Main vertical pane
        v_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        content_box.pack_start(v_paned, True, True, 0)

        # Top horizontal pane (for the two lists)
        h_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        h_paned.set_wide_handle(True)
        v_paned.add1(h_paned)

        self.create_service_list(h_paned)
        self.create_running_container_view(h_paned)

        # Bottom view for output
        self.create_output_view(v_paned)

        v_paned.set_position(500)
        h_paned.set_position(400)

        self.create_command_buttons(content_box)

        # Apply custom CSS for modern styling
        self.apply_modern_css()

    def create_header_bar(self, container):
        """Create a modern header bar with title and subtitle"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_box.get_style_context().add_class('app-header')

        # Title and subtitle
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_box.set_margin_start(20)
        title_box.set_margin_end(20)
        title_box.set_margin_top(16)
        title_box.set_margin_bottom(16)

        title_label = Gtk.Label()
        title_label.set_markup('<span size="x-large" weight="bold">Docker Container Manager</span>')
        title_label.set_xalign(0)
        title_label.get_style_context().add_class('app-title')

        subtitle_label = Gtk.Label()
        subtitle_label.set_markup('<span size="small">Manage Docker containers and services</span>')
        subtitle_label.set_xalign(0)
        subtitle_label.get_style_context().add_class('app-subtitle')

        title_box.pack_start(title_label, False, False, 0)
        title_box.pack_start(subtitle_label, False, False, 0)

        header_box.pack_start(title_box, False, False, 0)

        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.get_style_context().add_class('header-separator')
        header_box.pack_start(separator, False, False, 0)

        container.pack_start(header_box, False, False, 0)

    def apply_modern_css(self):
        """Apply modern CSS styling to the application"""
        css_provider = Gtk.CssProvider()
        css = b"""
        /* Header Styling */
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .app-title {
            color: white;
        }

        .app-subtitle {
            color: rgba(255, 255, 255, 0.9);
        }

        .header-separator {
            background: rgba(255, 255, 255, 0.3);
            min-height: 1px;
        }

        /* TreeView Headers */
        treeview.view header button {
            background: linear-gradient(to bottom, #4a5568, #2d3748);
            color: #ffffff;
            border: none;
            padding: 8px 12px;
            font-weight: bold;
        }

        treeview.view header button:hover {
            background: linear-gradient(to bottom, #5a6578, #3d4758);
        }

        treeview.view header button label {
            color: #ffffff;
        }

        /* TreeView Rows */
        treeview.view {
            background-color: #ffffff;
            font-size: 11pt;
        }

        treeview.view:selected {
            background-color: #667eea;
            color: white;
        }

        /* Section Headers */
        .section-header {
            background: linear-gradient(to bottom, #f7fafc, #edf2f7);
            border-bottom: 2px solid #667eea;
            padding: 8px 12px;
            font-weight: bold;
            color: #2d3748;
        }

        /* ListBox Styling */
        list {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
        }

        list row {
            border-bottom: 1px solid #f7fafc;
            padding: 4px;
        }

        list row:hover {
            background-color: #f7fafc;
        }

        list row:selected {
            background-color: #ebf4ff;
        }

        /* Button Styling */
        .command-button {
            padding: 10px 16px;
            border-radius: 6px;
            border: 1px solid #cbd5e0;
            background: linear-gradient(to bottom, #ffffff, #f7fafc);
            font-weight: 500;
            min-width: 100px;
        }

        .command-button:hover {
            background: linear-gradient(to bottom, #f7fafc, #edf2f7);
            border-color: #667eea;
        }

        .command-button:active {
            background: #edf2f7;
        }

        /* Output View */
        textview {
            background-color: #1a202c;
            color: #e2e8f0;
            font-family: monospace;
            font-size: 10pt;
            padding: 12px;
        }

        textview text {
            background-color: #1a202c;
            color: #e2e8f0;
        }

        /* Scrolled Windows */
        scrolledwindow {
            border-radius: 6px;
        }

        /* Paned Handle */
        paned separator {
            background-color: #cbd5e0;
            min-width: 4px;
            min-height: 4px;
        }

        paned separator:hover {
            background-color: #667eea;
        }

        /* Dialog Styling */
        dialog {
            border-radius: 8px;
        }

        /* Entry and SearchEntry Styling */
        entry, searchentry {
            border-radius: 6px;
            border: 1px solid #cbd5e0;
            padding: 8px 12px;
            background-color: #ffffff;
        }

        entry:focus, searchentry:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Suggested Action Button */
        .suggested-action {
            background: linear-gradient(to bottom, #667eea, #5568d3);
            color: white;
            border: none;
            padding: 8px 16px;
            font-weight: bold;
        }

        .suggested-action:hover {
            background: linear-gradient(to bottom, #5568d3, #4557c2);
        }

        /* SpinButton Styling */
        spinbutton {
            border-radius: 6px;
        }
        """
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def create_service_list(self, container):
        # Create container box with header
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Add section header with consistent height
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.get_style_context().add_class('section-header')
        header_box.set_size_request(-1, 40)  # Fixed height for alignment

        header_label = Gtk.Label()
        header_label.set_markup('<b>Available Services</b>')
        header_label.set_xalign(0)
        header_label.set_margin_start(12)
        header_box.pack_start(header_label, True, True, 0)

        vbox.pack_start(header_box, False, False, 0)

        # Create search box with consistent alignment
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(8)
        search_box.set_size_request(-1, 48)  # Set fixed height to match tabs

        self.service_search_entry = Gtk.SearchEntry()
        self.service_search_entry.set_placeholder_text("Search services...")
        self.service_search_entry.connect("search-changed", self.on_service_search_changed)
        search_box.pack_start(self.service_search_entry, True, True, 0)
        vbox.pack_start(search_box, False, False, 0)

        self.service_listbox = Gtk.ListBox()
        self.service_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.service_listbox.set_filter_func(self.service_filter_func, None)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.service_listbox)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_bottom(8)

        vbox.pack_start(scrolled_window, True, True, 0)
        container.add1(vbox)
        self.update_service_list()

    def service_filter_func(self, row, data):
        """Filter services based on search text"""
        search_text = self.service_search_entry.get_text().lower()
        if not search_text:
            return True

        hbox = row.get_child()
        label = hbox.get_children()[1]
        service_name = label.get_label().lower()
        return search_text in service_name

    def on_service_search_changed(self, entry):
        """Handle search text changes"""
        self.service_listbox.invalidate_filter()

    def container_filter_func(self, model, iter, data):
        """Filter containers - showing all"""
        return True

    def create_running_container_view(self, container):
        # Create container box with header
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Add section header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.get_style_context().add_class('section-header')
        header_box.set_size_request(-1, 40)

        header_label = Gtk.Label()
        header_label.set_markup('<b>Docker Resources</b>')
        header_label.set_xalign(0)
        header_label.set_margin_start(12)
        header_box.pack_start(header_label, True, True, 0)

        # Add count badge
        self.container_count_label = Gtk.Label()
        self.container_count_label.set_markup('<span size="small">0 running</span>')
        self.container_count_label.set_margin_end(12)
        header_box.pack_start(self.container_count_label, False, False, 0)

        vbox.pack_start(header_box, False, False, 0)

        # Create Gtk.Notebook for tabs
        self.resource_notebook = Gtk.Notebook()
        self.resource_notebook.set_margin_start(12)
        self.resource_notebook.set_margin_end(12)
        self.resource_notebook.set_margin_top(8)
        self.resource_notebook.set_margin_bottom(8)
        self.resource_notebook.connect("switch-page", self.on_resource_tab_switched)

        # Tab 1: Containers
        containers_box = self.create_containers_tab()
        containers_label = Gtk.Label(label="Containers")
        self.resource_notebook.append_page(containers_box, containers_label)

        # Tab 2: Networks
        networks_box = self.create_networks_tab()
        networks_label = Gtk.Label(label="Networks")
        self.resource_notebook.append_page(networks_box, networks_label)

        # Tab 3: Volumes
        volumes_box = self.create_volumes_tab()
        volumes_label = Gtk.Label(label="Volumes")
        self.resource_notebook.append_page(volumes_box, volumes_label)

        # Tab 4: Images
        images_box = self.create_images_tab()
        images_label = Gtk.Label(label="Images")
        self.resource_notebook.append_page(images_box, images_label)

        # Tab 5: Stacks
        stacks_box = self.create_stacks_tab()
        stacks_label = Gtk.Label(label="Stacks")
        self.resource_notebook.append_page(stacks_box, stacks_label)

        vbox.pack_start(self.resource_notebook, True, True, 0)
        container.add2(vbox)
        self.update_running_container_view()

    def create_containers_tab(self):
        """Create the containers tab with treeview"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Containers treeview
        self.running_container_store = Gtk.ListStore(str, str, str, str, str, str, str)
        self.running_container_filter = self.running_container_store.filter_new()
        self.running_container_filter.set_visible_func(self.container_filter_func, None)

        self.container_treeview = Gtk.TreeView(model=self.running_container_filter)
        self.container_treeview.connect("row-activated", self.on_container_activated)
        self.container_treeview.connect("button-press-event", self.on_container_button_press)
        self.container_treeview.set_has_tooltip(True)
        self.container_treeview.connect("query-tooltip", self.on_container_query_tooltip)

        # Define columns
        column_configs = [
            ("ID", 0, 70, False),
            ("Name", 1, 120, False),
            ("Status", 2, 70, False),
            ("Image", 3, 120, False),
            ("Uptime", 4, 80, False),
            ("Ports", 5, 100, False),
            ("Network", 6, 100, False),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()

            if col_title in ["Ports", "Network", "Image"]:
                renderer.set_property('wrap-width', 200)
                renderer.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
                renderer.set_property('ellipsize', Pango.EllipsizeMode.END)

            column = Gtk.TreeViewColumn(col_title, renderer, text=col_index)
            column.set_resizable(True)
            column.set_fixed_width(fixed_width)
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)

            if expand:
                column.set_expand(True)

            self.container_treeview.append_column(column)

        # Add Actions column with 6 buttons
        actions_column = Gtk.TreeViewColumn("Actions")
        actions_column.set_fixed_width(84)
        actions_column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)

        start_renderer = Gtk.CellRendererText()
        start_renderer.set_property('text', '▶')
        start_renderer.set_property('xalign', 0.5)
        start_renderer.set_property('foreground', '#10b981')
        start_renderer.set_property('weight', 700)
        start_renderer.set_property('size-points', 12)
        actions_column.pack_start(start_renderer, True)

        restart_renderer = Gtk.CellRendererText()
        restart_renderer.set_property('text', '↻')
        restart_renderer.set_property('xalign', 0.5)
        restart_renderer.set_property('foreground', '#667eea')
        restart_renderer.set_property('weight', 700)
        restart_renderer.set_property('size-points', 12)
        actions_column.pack_start(restart_renderer, True)

        stop_renderer = Gtk.CellRendererText()
        stop_renderer.set_property('text', '⏹')
        stop_renderer.set_property('xalign', 0.5)
        stop_renderer.set_property('foreground', '#f59e0b')
        stop_renderer.set_property('weight', 700)
        stop_renderer.set_property('size-points', 12)
        actions_column.pack_start(stop_renderer, True)

        logs_renderer = Gtk.CellRendererText()
        logs_renderer.set_property('text', '📋')
        logs_renderer.set_property('xalign', 0.5)
        logs_renderer.set_property('foreground', '#06b6d4')
        logs_renderer.set_property('weight', 700)
        logs_renderer.set_property('size-points', 11)
        actions_column.pack_start(logs_renderer, True)

        backup_renderer = Gtk.CellRendererText()
        backup_renderer.set_property('text', '💾')
        backup_renderer.set_property('xalign', 0.5)
        backup_renderer.set_property('foreground', '#8b5cf6')
        backup_renderer.set_property('weight', 700)
        backup_renderer.set_property('size-points', 11)
        actions_column.pack_start(backup_renderer, True)

        remove_renderer = Gtk.CellRendererText()
        remove_renderer.set_property('text', '🗑')
        remove_renderer.set_property('xalign', 0.5)
        remove_renderer.set_property('foreground', '#ef4444')
        remove_renderer.set_property('weight', 700)
        remove_renderer.set_property('size-points', 11)
        actions_column.pack_start(remove_renderer, True)

        self.container_treeview.append_column(actions_column)

        # Scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.container_treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox.pack_start(scrolled_window, True, True, 0)
        return vbox

    def create_networks_tab(self):
        """Create the networks tab with treeview"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Networks treeview - added 'In Use' column and background color
        self.network_store = Gtk.ListStore(str, str, str, str, str, str, str)  # ID, Name, Driver, Scope, Subnet, In Use, Background Color
        self.network_filter = self.network_store.filter_new()
        self.network_filter.set_visible_func(self.network_filter_func, None)

        self.network_treeview = Gtk.TreeView(model=self.network_filter)
        self.network_treeview.connect("row-activated", self.on_network_activated)

        # Define columns
        column_configs = [
            ("ID", 0, 90, False),
            ("Name", 1, 150, True),
            ("Driver", 2, 80, False),
            ("Scope", 3, 80, False),
            ("Subnet", 4, 120, False),
            ("In Use", 5, 80, False),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()

            # Set background color from model column 6
            column = Gtk.TreeViewColumn(col_title, renderer, text=col_index, background=6)
            column.set_resizable(True)

            if not expand:
                column.set_fixed_width(fixed_width)
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                column.set_expand(True)

            self.network_treeview.append_column(column)

        # Scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.network_treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox.pack_start(scrolled_window, True, True, 0)

        # Add cleanup button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_top(8)
        button_box.set_margin_bottom(8)

        cleanup_button = Gtk.Button()
        cleanup_button.get_style_context().add_class('command-button')
        cleanup_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        cleanup_label = Gtk.Label(label="Remove Unused Networks")
        cleanup_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        cleanup_box.pack_start(cleanup_icon, False, False, 0)
        cleanup_box.pack_start(cleanup_label, False, False, 0)
        cleanup_button.add(cleanup_box)
        cleanup_button.connect("clicked", self.on_cleanup_networks_clicked)
        button_box.pack_start(cleanup_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)
        return vbox

    def create_volumes_tab(self):
        """Create the volumes tab with treeview"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Volumes treeview - added 'In Use' column and background color
        self.volume_store = Gtk.ListStore(str, str, str, str, str)  # Name, Driver, Mountpoint, In Use, Background Color
        self.volume_filter = self.volume_store.filter_new()
        self.volume_filter.set_visible_func(self.volume_filter_func, None)

        self.volume_treeview = Gtk.TreeView(model=self.volume_filter)
        self.volume_treeview.connect("row-activated", self.on_volume_activated)

        # Define columns
        column_configs = [
            ("Name", 0, 250, True),
            ("Driver", 1, 100, False),
            ("Mountpoint", 2, 300, True),
            ("In Use", 3, 80, False),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()
            renderer.set_property('ellipsize', Pango.EllipsizeMode.END)

            # Set background color from model column 4
            column = Gtk.TreeViewColumn(col_title, renderer, text=col_index, background=4)
            column.set_resizable(True)

            if not expand:
                column.set_fixed_width(fixed_width)
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                column.set_expand(True)

            self.volume_treeview.append_column(column)

        # Scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.volume_treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox.pack_start(scrolled_window, True, True, 0)

        # Add cleanup button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_top(8)
        button_box.set_margin_bottom(8)

        cleanup_button = Gtk.Button()
        cleanup_button.get_style_context().add_class('command-button')
        cleanup_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        cleanup_label = Gtk.Label(label="Remove Unused Volumes")
        cleanup_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        cleanup_box.pack_start(cleanup_icon, False, False, 0)
        cleanup_box.pack_start(cleanup_label, False, False, 0)
        cleanup_button.add(cleanup_box)
        cleanup_button.connect("clicked", self.on_cleanup_volumes_clicked)
        button_box.pack_start(cleanup_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)
        return vbox

    def create_images_tab(self):
        """Create the images tab with treeview"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Images treeview - added 'In Use' column and background color
        self.image_store = Gtk.ListStore(str, str, str, str, str, str, str)  # ID, Repository, Tag, Size, Created, In Use, Background Color
        self.image_filter = self.image_store.filter_new()
        self.image_filter.set_visible_func(self.image_filter_func, None)

        self.image_treeview = Gtk.TreeView(model=self.image_filter)
        self.image_treeview.connect("row-activated", self.on_image_activated)

        # Define columns
        column_configs = [
            ("ID", 0, 90, False),
            ("Repository", 1, 200, True),
            ("Tag", 2, 100, False),
            ("Size", 3, 80, False),
            ("Created", 4, 120, False),
            ("In Use", 5, 80, False),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()

            # Set background color from model column 6
            column = Gtk.TreeViewColumn(col_title, renderer, text=col_index, background=6)
            column.set_resizable(True)

            if not expand:
                column.set_fixed_width(fixed_width)
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                column.set_expand(True)

            self.image_treeview.append_column(column)

        # Scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.image_treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox.pack_start(scrolled_window, True, True, 0)

        # Add cleanup buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_top(8)
        button_box.set_margin_bottom(8)

        # Remove unused images button
        cleanup_button = Gtk.Button()
        cleanup_button.get_style_context().add_class('command-button')
        cleanup_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        cleanup_label = Gtk.Label(label="Remove Unused Images")
        cleanup_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        cleanup_box.pack_start(cleanup_icon, False, False, 0)
        cleanup_box.pack_start(cleanup_label, False, False, 0)
        cleanup_button.add(cleanup_box)
        cleanup_button.connect("clicked", self.on_cleanup_images_clicked)
        button_box.pack_start(cleanup_button, False, False, 0)

        # Remove dangling images button
        prune_button = Gtk.Button()
        prune_button.get_style_context().add_class('command-button')
        prune_icon = Gtk.Image.new_from_icon_name("edit-clear-all-symbolic", Gtk.IconSize.BUTTON)
        prune_label = Gtk.Label(label="Remove Dangling Images")
        prune_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        prune_box.pack_start(prune_icon, False, False, 0)
        prune_box.pack_start(prune_label, False, False, 0)
        prune_button.add(prune_box)
        prune_button.connect("clicked", self.on_prune_images_clicked)
        button_box.pack_start(prune_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)
        return vbox

    def create_stacks_tab(self):
        """Create the stacks tab with treeview"""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Stacks treeview (Docker Compose projects)
        self.stack_store = Gtk.ListStore(str, str, str, str)  # Name, Status, Services Count, Config Path
        self.stack_filter = self.stack_store.filter_new()
        self.stack_filter.set_visible_func(self.stack_filter_func, None)

        self.stack_treeview = Gtk.TreeView(model=self.stack_filter)
        self.stack_treeview.connect("row-activated", self.on_stack_activated)

        # Define columns
        column_configs = [
            ("Name", 0, 200, True),
            ("Status", 1, 100, False),
            ("Services", 2, 80, False),
            ("Config Path", 3, 300, True),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()
            renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
            column = Gtk.TreeViewColumn(col_title, renderer, text=col_index)
            column.set_resizable(True)

            if not expand:
                column.set_fixed_width(fixed_width)
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            else:
                column.set_expand(True)

            self.stack_treeview.append_column(column)

        # Scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.stack_treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox.pack_start(scrolled_window, True, True, 0)

        # Add export button for selected stack
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_start(8)
        button_box.set_margin_end(8)
        button_box.set_margin_top(8)
        button_box.set_margin_bottom(8)

        export_button = Gtk.Button()
        export_button.get_style_context().add_class('command-button')
        export_icon = Gtk.Image.new_from_icon_name("document-save-as-symbolic", Gtk.IconSize.BUTTON)
        export_label = Gtk.Label(label="Export Selected Stack to docker-compose.yml")
        export_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        export_box.pack_start(export_icon, False, False, 0)
        export_box.pack_start(export_label, False, False, 0)
        export_button.add(export_box)
        export_button.connect("clicked", self.on_export_stack_clicked)
        button_box.pack_start(export_button, False, False, 0)

        vbox.pack_start(button_box, False, False, 0)
        return vbox

    def on_resource_tab_switched(self, notebook, page, page_num):
        """Handle tab switching to update count label"""
        tab_names = ["Containers", "Networks", "Volumes", "Images", "Stacks"]
        if page_num < len(tab_names):
            # Update count label based on current tab
            if page_num == 0:  # Containers
                count = len(self.running_container_store)
                self.container_count_label.set_markup(f'<span size="small">{count} running</span>')
            elif page_num == 1:  # Networks
                count = len(self.network_store)
                self.container_count_label.set_markup(f'<span size="small">{count} networks</span>')
            elif page_num == 2:  # Volumes
                count = len(self.volume_store)
                self.container_count_label.set_markup(f'<span size="small">{count} volumes</span>')
            elif page_num == 3:  # Images
                count = len(self.image_store)
                self.container_count_label.set_markup(f'<span size="small">{count} images</span>')
            elif page_num == 4:  # Stacks
                count = len(self.stack_store)
                self.container_count_label.set_markup(f'<span size="small">{count} stacks</span>')

    def network_filter_func(self, model, iter, data):
        """Filter networks - showing all"""
        return True

    def volume_filter_func(self, model, iter, data):
        """Filter volumes - showing all"""
        return True

    def image_filter_func(self, model, iter, data):
        """Filter images - showing all"""
        return True

    def stack_filter_func(self, model, iter, data):
        """Filter stacks - showing all"""
        return True

    def on_network_activated(self, treeview, path, column):
        """Handle double-click on network to show details"""
        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        if tree_iter is None:
            return

        network_id = model.get_value(tree_iter, 0)
        network_name = model.get_value(tree_iter, 1)

        try:
            network = self.client.networks.get(network_id)
            details = self.format_network_details(network)

            dialog = Gtk.Dialog(
                title=f"Network Details: {network_name}",
                transient_for=self,
                flags=0
            )
            dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            dialog.set_default_size(600, 500)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.set_margin_start(10)
            scrolled_window.set_margin_end(10)
            scrolled_window.set_margin_top(10)
            scrolled_window.set_margin_bottom(10)

            label = Gtk.Label()
            label.set_markup(details)
            label.set_xalign(0)
            label.set_yalign(0)
            label.set_selectable(True)
            label.set_line_wrap(True)

            scrolled_window.add(label)
            box = dialog.get_content_area()
            box.add(scrolled_window)
            dialog.show_all()

            dialog.run()
            dialog.destroy()

        except Exception as e:
            self.show_error_dialog(f"Error getting network details: {str(e)}")

    def on_volume_activated(self, treeview, path, column):
        """Handle double-click on volume to show details"""
        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        if tree_iter is None:
            return

        volume_name = model.get_value(tree_iter, 0)

        try:
            volume = self.client.volumes.get(volume_name)
            details = self.format_volume_details(volume)

            dialog = Gtk.Dialog(
                title=f"Volume Details: {volume_name}",
                transient_for=self,
                flags=0
            )
            dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            dialog.set_default_size(600, 400)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.set_margin_start(10)
            scrolled_window.set_margin_end(10)
            scrolled_window.set_margin_top(10)
            scrolled_window.set_margin_bottom(10)

            label = Gtk.Label()
            label.set_markup(details)
            label.set_xalign(0)
            label.set_yalign(0)
            label.set_selectable(True)
            label.set_line_wrap(True)

            scrolled_window.add(label)
            box = dialog.get_content_area()
            box.add(scrolled_window)
            dialog.show_all()

            dialog.run()
            dialog.destroy()

        except Exception as e:
            self.show_error_dialog(f"Error getting volume details: {str(e)}")

    def format_network_details(self, network):
        """Format network details for display"""
        attrs = network.attrs
        details = f"<b>Network ID:</b> {network.id}\n"
        details += f"<b>Name:</b> {network.name}\n"
        details += f"<b>Driver:</b> {attrs.get('Driver', 'N/A')}\n"
        details += f"<b>Scope:</b> {attrs.get('Scope', 'N/A')}\n\n"

        ipam = attrs.get('IPAM', {})
        config = ipam.get('Config', [])
        if config:
            details += "<b>IPAM Configuration:</b>\n"
            for cfg in config:
                subnet = cfg.get('Subnet', 'N/A')
                gateway = cfg.get('Gateway', 'N/A')
                details += f"  • Subnet: {subnet}\n"
                details += f"    Gateway: {gateway}\n"

        containers = attrs.get('Containers', {})
        if containers:
            details += f"\n<b>Connected Containers ({len(containers)}):</b>\n"
            for container_id, container_info in containers.items():
                name = container_info.get('Name', 'N/A')
                ipv4 = container_info.get('IPv4Address', 'N/A')
                details += f"  • {name} - {ipv4}\n"

        return details

    def format_volume_details(self, volume):
        """Format volume details for display"""
        attrs = volume.attrs
        details = f"<b>Volume Name:</b> {volume.name}\n"
        details += f"<b>Driver:</b> {attrs.get('Driver', 'N/A')}\n"
        details += f"<b>Mountpoint:</b> {attrs.get('Mountpoint', 'N/A')}\n"
        details += f"<b>Scope:</b> {attrs.get('Scope', 'N/A')}\n"
        details += f"<b>Created:</b> {attrs.get('CreatedAt', 'N/A')}\n\n"

        options = attrs.get('Options', {})
        if options:
            details += "<b>Options:</b>\n"
            for key, value in options.items():
                details += f"  • {key}: {value}\n"

        labels = attrs.get('Labels', {})
        if labels:
            details += "\n<b>Labels:</b>\n"
            for key, value in labels.items():
                details += f"  • {key}: {value}\n"

        return details

    def on_image_activated(self, treeview, path, column):
        """Handle double-click on image to show details"""
        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        if tree_iter is None:
            return

        image_id = model.get_value(tree_iter, 0)
        repository = model.get_value(tree_iter, 1)
        tag = model.get_value(tree_iter, 2)

        try:
            image = self.client.images.get(image_id)
            details = self.format_image_details(image)

            dialog = Gtk.Dialog(
                title=f"Image Details: {repository}:{tag}",
                transient_for=self,
                flags=0
            )
            dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            dialog.set_default_size(700, 600)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.set_margin_start(10)
            scrolled_window.set_margin_end(10)
            scrolled_window.set_margin_top(10)
            scrolled_window.set_margin_bottom(10)

            label = Gtk.Label()
            label.set_markup(details)
            label.set_xalign(0)
            label.set_yalign(0)
            label.set_selectable(True)
            label.set_line_wrap(True)

            scrolled_window.add(label)
            box = dialog.get_content_area()
            box.add(scrolled_window)
            dialog.show_all()

            dialog.run()
            dialog.destroy()

        except Exception as e:
            self.show_error_dialog(f"Error getting image details: {str(e)}")

    def on_stack_activated(self, treeview, path, column):
        """Handle double-click on stack to show details"""
        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        if tree_iter is None:
            return

        stack_name = model.get_value(tree_iter, 0)
        config_path = model.get_value(tree_iter, 3)

        try:
            details = self.format_stack_details(stack_name, config_path)

            dialog = Gtk.Dialog(
                title=f"Stack Details: {stack_name}",
                transient_for=self,
                flags=0
            )
            dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            dialog.set_default_size(700, 600)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.set_margin_start(10)
            scrolled_window.set_margin_end(10)
            scrolled_window.set_margin_top(10)
            scrolled_window.set_margin_bottom(10)

            textview = Gtk.TextView()
            textview.set_editable(False)
            textview.set_cursor_visible(True)
            textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            textview.set_left_margin(8)
            textview.set_right_margin(8)
            textview.set_top_margin(8)
            textview.set_bottom_margin(8)
            textview.override_font(Pango.FontDescription("monospace 9"))

            textbuffer = textview.get_buffer()
            textbuffer.set_text(details)

            scrolled_window.add(textview)
            box = dialog.get_content_area()
            box.add(scrolled_window)
            dialog.show_all()

            dialog.run()
            dialog.destroy()

        except Exception as e:
            self.show_error_dialog(f"Error getting stack details: {str(e)}")

    def format_image_details(self, image):
        """Format image details for display"""
        attrs = image.attrs
        details = f"<b>Image ID:</b> {image.id}\n"

        # Tags
        if image.tags:
            details += f"<b>Tags:</b> {', '.join(image.tags)}\n"
        else:
            details += f"<b>Tags:</b> &lt;none&gt; (dangling image)\n"

        # Size
        size_mb = attrs.get('Size', 0) / (1024 * 1024)
        details += f"<b>Size:</b> {size_mb:.2f} MB\n"

        # Created
        created = attrs.get('Created', 'N/A')
        details += f"<b>Created:</b> {created}\n"

        # Architecture
        arch = attrs.get('Architecture', 'N/A')
        os_name = attrs.get('Os', 'N/A')
        details += f"<b>Platform:</b> {os_name}/{arch}\n\n"

        # Config
        config = attrs.get('Config', {})

        # Exposed ports
        exposed_ports = config.get('ExposedPorts', {})
        if exposed_ports:
            details += f"<b>Exposed Ports:</b> {', '.join(exposed_ports.keys())}\n"

        # Environment
        env = config.get('Env', [])
        if env:
            details += f"\n<b>Environment Variables ({len(env)}):</b>\n"
            for e in env[:10]:  # Show first 10
                details += f"  • {e}\n"
            if len(env) > 10:
                details += f"  ... and {len(env) - 10} more\n"

        # Labels
        labels = config.get('Labels', {})
        if labels:
            details += f"\n<b>Labels ({len(labels)}):</b>\n"
            for key, value in list(labels.items())[:10]:  # Show first 10
                details += f"  • {key}: {value}\n"
            if len(labels) > 10:
                details += f"  ... and {len(labels) - 10} more\n"

        # History (layers)
        history = attrs.get('RootFS', {}).get('Layers', [])
        if history:
            details += f"\n<b>Layers:</b> {len(history)}\n"

        return details

    def format_stack_details(self, stack_name, config_path):
        """Format stack details for display"""
        import os

        details = f"Stack: {stack_name}\n"
        details += f"Config: {config_path}\n"
        details += "=" * 60 + "\n\n"

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    details += f.read()
            except Exception as e:
                details += f"Error reading config file: {str(e)}"
        else:
            details += "Config file not found or not specified."

        return details

    def on_container_query_tooltip(self, treeview, x, y, keyboard_mode, tooltip):
        """Show tooltips for action buttons"""
        path_info = treeview.get_path_at_pos(x, y)
        if path_info is None:
            return False

        path, column, cell_x, cell_y = path_info

        # Only show tooltips for Actions column
        if column.get_title() == "Actions":
            # Determine which button is being hovered based on x position (6 buttons)
            column_width = column.get_width()
            button_width = column_width / 6
            relative_x = cell_x

            if relative_x < button_width:
                tooltip.set_text("Start container")
            elif relative_x < button_width * 2:
                tooltip.set_text("Restart container")
            elif relative_x < button_width * 3:
                tooltip.set_text("Stop container")
            elif relative_x < button_width * 4:
                tooltip.set_text("View container logs")
            elif relative_x < button_width * 5:
                tooltip.set_text("Backup container")
            else:
                tooltip.set_text("Remove container")

            return True

        return False

    def on_container_button_press(self, treeview, event):
        """Handle button clicks in the container treeview"""
        if event.button == 1:  # Left click
            path_info = treeview.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, column, cell_x, cell_y = path_info

                # Check if click was in the Actions column
                if column.get_title() == "Actions":
                    model = treeview.get_model()
                    tree_iter = model.get_iter(path)
                    container_id = model.get_value(tree_iter, 0)
                    container_name = model.get_value(tree_iter, 1)

                    # Determine which button was clicked based on x position (6 buttons)
                    column_width = column.get_width()
                    button_width = column_width / 6
                    relative_x = cell_x

                    if relative_x < button_width:
                        # Start button
                        self.start_container(container_id, container_name)
                    elif relative_x < button_width * 2:
                        # Restart button
                        self.restart_container(container_id, container_name)
                    elif relative_x < button_width * 3:
                        # Stop button
                        self.stop_container(container_id, container_name)
                    elif relative_x < button_width * 4:
                        # Logs button
                        self.view_container_logs(container_id, container_name)
                    elif relative_x < button_width * 5:
                        # Backup button
                        self.backup_container(container_id, container_name)
                    else:
                        # Remove button
                        self.remove_container(container_id, container_name)

                    return True  # Event handled

        elif event.button == 3:  # Right click
            path_info = treeview.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, column, cell_x, cell_y = path_info

                # Get container info
                model = treeview.get_model()
                tree_iter = model.get_iter(path)
                container_id = model.get_value(tree_iter, 0)
                container_name = model.get_value(tree_iter, 1)

                # Show context menu
                self.show_container_context_menu(event, container_id, container_name)
                return True  # Event handled

        return False  # Event not handled

    def on_container_activated(self, treeview, path, column):
        """Handle double-click to show container details"""
        # Don't show details if clicking on Actions column
        if column.get_title() == "Actions":
            return

        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        if tree_iter is None:
            return

        # Get values from the filtered model
        container_id = model.get_value(tree_iter, 0)
        container_name = model.get_value(tree_iter, 1)
        details_str = core.get_full_container_details(self.client, container_id)

        dialog = Gtk.Dialog(
            title=f"Details for {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(600, 500)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_start(10)
        scrolled_window.set_margin_end(10)
        scrolled_window.set_margin_top(10)
        scrolled_window.set_margin_bottom(10)

        label = Gtk.Label()
        label.set_markup(details_str)
        label.set_xalign(0)
        label.set_yalign(0)
        label.set_selectable(True)
        label.set_line_wrap(True)

        scrolled_window.add(label)
        box = dialog.get_content_area()
        box.add(scrolled_window)
        dialog.show_all()

        dialog.run()
        dialog.destroy()


    def create_command_buttons(self, container):
        # Add a separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(12)
        container.pack_end(separator, False, True, 0)

        # Create button box with modern styling
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.CENTER)
        container.pack_end(button_box, False, True, 0)

        commands = [
            ("Install", "list-add-symbolic", self.on_install_clicked, "success"),
            ("Uninstall", "list-remove-symbolic", self.on_uninstall_clicked, "danger"),
            ("Start", "media-playback-start-symbolic", self.on_start_clicked, "success"),
            ("Stop", "media-playback-stop-symbolic", self.on_stop_clicked, "warning"),
            ("Restart", "view-refresh-symbolic", self.on_restart_clicked, "info"),
            ("Status", "dialog-information-symbolic", self.on_status_clicked, "info"),
            ("Update", "software-update-available-symbolic", self.on_update_clicked, "info"),
            ("Test", "applications-system-symbolic", self.on_test_clicked, "neutral"),
            ("Refresh", "view-refresh-symbolic", self.on_refresh_clicked, "neutral")
        ]

        for label, icon_name, callback, style_class in commands:
            # Create button with both icon and label
            button = Gtk.Button()
            button.get_style_context().add_class('command-button')

            # Create box for icon and label
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            btn_box.pack_start(icon, False, False, 0)

            btn_label = Gtk.Label(label=label)
            btn_box.pack_start(btn_label, False, False, 0)

            button.add(btn_box)
            button.connect("clicked", callback)
            button_box.pack_start(button, False, False, 0)

    def create_output_view(self, container):
        # Create container box with header
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Add section header with consistent height
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.get_style_context().add_class('section-header')
        header_box.set_size_request(-1, 40)  # Fixed height for alignment

        header_label = Gtk.Label()
        header_label.set_markup('<b>Command Output</b>')
        header_label.set_xalign(0)
        header_label.set_margin_start(12)
        header_box.pack_start(header_label, True, True, 0)

        # Add clear button
        clear_button = Gtk.Button.new_from_icon_name("edit-clear-symbolic", Gtk.IconSize.BUTTON)
        clear_button.set_tooltip_text("Clear output")
        clear_button.set_relief(Gtk.ReliefStyle.NONE)
        clear_button.connect("clicked", self.on_clear_output)
        clear_button.set_margin_end(8)
        header_box.pack_start(clear_button, False, False, 0)

        vbox.pack_start(header_box, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_start(8)
        scrolled_window.set_margin_end(8)
        scrolled_window.set_margin_bottom(8)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_left_margin(8)
        self.textview.set_right_margin(8)
        self.textview.set_top_margin(8)
        self.textview.set_bottom_margin(8)
        self.textbuffer = self.textview.get_buffer()

        # Set monospace font
        self.textview.override_font(Pango.FontDescription("monospace 10"))

        scrolled_window.add(self.textview)
        vbox.pack_start(scrolled_window, True, True, 0)
        container.add2(vbox)

    def on_clear_output(self, button):
        """Clear the output text view"""
        self.textbuffer.set_text("")

    def update_service_list(self):
        for child in self.service_listbox.get_children():
            self.service_listbox.remove(child)
        available_services = core.get_available_services()
        for service in sorted(available_services, key=lambda s: s['name']):
            row = Gtk.ListBoxRow()
            row.set_margin_top(0)
            row.set_margin_bottom(0)
            row.set_margin_start(0)
            row.set_margin_end(0)

            # Main horizontal box
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_top(8)
            hbox.set_margin_bottom(8)
            hbox.set_margin_start(12)
            hbox.set_margin_end(12)

            check = Gtk.CheckButton()
            hbox.pack_start(check, False, False, 0)

            # Vertical box for service name and description
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

            # Service name
            name_label = Gtk.Label(label=service['name'], xalign=0)
            name_label.set_markup(f"<b>{service['name']}</b>")
            vbox.pack_start(name_label, False, False, 0)

            # Service description (if available)
            if service.get('description'):
                desc_label = Gtk.Label(xalign=0)
                desc = service['description']
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                desc_label.set_markup(f'<span size="small" color="#6b7280">{desc}</span>')
                desc_label.set_line_wrap(True)
                desc_label.set_max_width_chars(50)
                vbox.pack_start(desc_label, False, False, 0)

            hbox.pack_start(vbox, True, True, 0)
            row.add(hbox)
            self.service_listbox.add(row)
        self.service_listbox.show_all()

    def update_running_container_view(self):
        # Update containers
        self.running_container_store.clear()
        running_containers = core.get_running_container_details(self.client)
        for container in running_containers:
            self.running_container_store.append([
                container['id'],
                container['name'],
                container['status'],
                container['image'],
                container['uptime'],
                container['ports'],
                container['network']
            ])

        # Update networks with "In Use" detection
        self.network_store.clear()
        try:
            networks = self.client.networks.list()
            for network in networks:
                network_id = network.short_id
                network_name = network.name
                driver = network.attrs.get('Driver', 'N/A')
                scope = network.attrs.get('Scope', 'N/A')

                # Get subnet info
                ipam = network.attrs.get('IPAM', {})
                config = ipam.get('Config', [])
                subnet = config[0].get('Subnet', 'N/A') if config else 'N/A'

                # Check if network is in use
                containers = network.attrs.get('Containers', {})
                in_use = len(containers) > 0

                # Determine background color
                # System networks (bridge, host, none) should always show as white
                if network_name in ['bridge', 'host', 'none']:
                    bg_color = "#ffffff"  # White for system networks
                elif not in_use:
                    bg_color = "#fff3cd"  # Light yellow for unused
                else:
                    bg_color = "#ffffff"  # White for in use

                self.network_store.append([network_id, network_name, driver, scope, subnet, "Yes" if in_use else "No", bg_color])
        except Exception as e:
            print(f"Error loading networks: {e}")

        # Update volumes with "In Use" detection
        self.volume_store.clear()
        try:
            volumes = self.client.volumes.list()
            # Get all containers (not just running) to check volume usage
            all_containers = self.client.containers.list(all=True)

            for volume in volumes:
                volume_name = volume.name
                driver = volume.attrs.get('Driver', 'N/A')
                mountpoint = volume.attrs.get('Mountpoint', 'N/A')

                # Check if volume is in use by any container
                in_use = False
                for container in all_containers:
                    for mount in container.attrs.get('Mounts', []):
                        if mount.get('Type') == 'volume' and mount.get('Name') == volume_name:
                            in_use = True
                            break
                    if in_use:
                        break

                # Add background color based on usage
                bg_color = "#ffffff" if in_use else "#fff3cd"  # Light yellow for unused

                self.volume_store.append([volume_name, driver, mountpoint, "Yes" if in_use else "No", bg_color])
        except Exception as e:
            print(f"Error loading volumes: {e}")

        # Update images with "In Use" detection
        self.image_store.clear()
        try:
            images = self.client.images.list()
            # Get all containers to check image usage
            all_containers = self.client.containers.list(all=True)
            used_image_ids = set()
            for container in all_containers:
                image_id = container.attrs.get('Image', '')
                if image_id:
                    used_image_ids.add(image_id)

            for image in images:
                image_id = image.short_id

                # Get repository and tag
                if image.tags:
                    # Use first tag
                    tag_parts = image.tags[0].split(':')
                    repository = tag_parts[0] if len(tag_parts) > 0 else '<none>'
                    tag = tag_parts[1] if len(tag_parts) > 1 else 'latest'
                else:
                    repository = '<none>'
                    tag = '<none>'

                # Size in MB
                size_mb = image.attrs.get('Size', 0) / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"

                # Created date
                from datetime import datetime
                created_str = image.attrs.get('Created', 'N/A')
                if created_str != 'N/A':
                    try:
                        created_dt = datetime.strptime(created_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                        created_str = created_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass

                # Check if image is in use
                in_use = image.id in used_image_ids

                # Determine background color
                if not image.tags:  # Dangling image
                    bg_color = "#ffe4e1"  # Light red for dangling
                elif not in_use:
                    bg_color = "#fff3cd"  # Light yellow for unused
                else:
                    bg_color = "#ffffff"  # White for in use

                self.image_store.append([image_id, repository, tag, size_str, created_str, "Yes" if in_use else "No", bg_color])
        except Exception as e:
            print(f"Error loading images: {e}")

        # Update stacks (Docker Compose projects)
        self.stack_store.clear()
        try:
            import os
            import subprocess
            # Try to detect docker compose projects
            # This is a simplified implementation - looks for containers with com.docker.compose.project label
            all_containers = self.client.containers.list(all=True)
            stacks_dict = {}

            for container in all_containers:
                labels = container.attrs.get('Config', {}).get('Labels', {})
                project_name = labels.get('com.docker.compose.project')
                config_file = labels.get('com.docker.compose.project.config_files')

                if project_name:
                    if project_name not in stacks_dict:
                        stacks_dict[project_name] = {
                            'containers': [],
                            'config_path': config_file or 'N/A'
                        }
                    stacks_dict[project_name]['containers'].append(container)

            for stack_name, stack_info in stacks_dict.items():
                containers = stack_info['containers']
                running_count = sum(1 for c in containers if c.status == 'running')
                total_count = len(containers)

                if running_count == total_count:
                    status = "Running"
                elif running_count > 0:
                    status = f"Partial ({running_count}/{total_count})"
                else:
                    status = "Stopped"

                services_count = str(total_count)
                config_path = stack_info['config_path']

                self.stack_store.append([stack_name, status, services_count, config_path])

        except Exception as e:
            print(f"Error loading stacks: {e}")

        # Update count badge based on current tab
        current_page = self.resource_notebook.get_current_page()
        if current_page == 0:  # Containers
            count = len(running_containers)
            self.container_count_label.set_markup(f'<span size="small">{count} running</span>')
        elif current_page == 1:  # Networks
            count = len(self.network_store)
            self.container_count_label.set_markup(f'<span size="small">{count} networks</span>')
        elif current_page == 2:  # Volumes
            count = len(self.volume_store)
            self.container_count_label.set_markup(f'<span size="small">{count} volumes</span>')
        elif current_page == 3:  # Images
            count = len(self.image_store)
            self.container_count_label.set_markup(f'<span size="small">{count} images</span>')
        elif current_page == 4:  # Stacks
            count = len(self.stack_store)
            self.container_count_label.set_markup(f'<span size="small">{count} stacks</span>')

    def get_selected_services(self):
        selected = []
        for row in self.service_listbox.get_children():
            hbox = row.get_child()
            check_button = hbox.get_children()[0]
            if check_button.get_active():
                # Get the vbox which contains the name label
                vbox = hbox.get_children()[1]
                name_label = vbox.get_children()[0]
                # Extract text from markup
                service_name = name_label.get_text()
                selected.append(service_name)
        return selected

    def run_command(self, command_func):
        selected_services = self.get_selected_services()
        if not selected_services:
            self.show_error_dialog("Please select at least one service.")
            return

        output = []
        for service in selected_services:
            output.append(command_func(self.client, service))
        self.textbuffer.set_text("\n".join(output))

    def on_install_clicked(self, widget):
        selected_services = self.get_selected_services()
        if not selected_services:
            self.show_error_dialog("Please select at least one service to install.")
            return

        # Install all selected services, one at a time
        self.install_services_batch(selected_services)

    def install_services_batch(self, service_names):
        """Install multiple services one at a time"""
        for i, service_name in enumerate(service_names):
            result = self.show_install_dialog(service_name, i + 1, len(service_names))
            if result == "cancelled":
                self.textbuffer.set_text(f"Installation cancelled at service {i+1}/{len(service_names)}: {service_name}")
                break

    def show_install_dialog(self, service_name, service_index=1, total_services=1):
        try:
            with open(f'services/{service_name}.yml', 'r') as f:
                service_config = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.show_error_dialog(f"Could not load or parse service file for {service_name}: {e}")
            return "cancelled"

        # Create dialog with progress info
        title = f"Install {service_config.get('name', service_name)}"
        if total_services > 1:
            title += f" ({service_index}/{total_services})"

        dialog = Gtk.Dialog(
            title=title,
            transient_for=self,
            flags=0
        )
        preview_button = dialog.add_button("Preview Command", Gtk.ResponseType.HELP)
        compose_button = dialog.add_button("Save as docker-compose.yml", Gtk.ResponseType.APPLY)
        install_button = dialog.add_button("Install", Gtk.ResponseType.OK)
        install_button.get_style_context().add_class('suggested-action')
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.set_default_size(600, 700)
        dialog.set_border_width(0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_top(10)
        box = dialog.get_content_area()
        box.add(scrolled_window)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(5)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        scrolled_window.add(grid)

        description_label = Gtk.Label()
        description_label.set_markup(f"<i>{service_config.get('description', '')}</i>")
        description_label.set_line_wrap(True)
        description_label.set_xalign(0)
        grid.attach(description_label, 0, 0, 2, 1)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, 1, 2, 1)

        widgets = {"variables": {}, "ports": {}, "volume_mappings": {}}
        current_row = 2

        # Create inputs for variables
        for var in service_config.get('variables', []):
            label = Gtk.Label(label=var['label'], xalign=0)
            label.set_tooltip_text(var.get('description', ''))

            input_widget = None
            var_type = var.get('type', 'string')

            if var_type == 'boolean':
                input_widget = Gtk.CheckButton()
                input_widget.set_active(var.get('default', False))
                grid.attach(label, 0, current_row, 1, 1)
                grid.attach(input_widget, 1, current_row, 1, 1)
                current_row += 1

                # Add description caption if available
                if var.get('description'):
                    desc_label = Gtk.Label(xalign=0)
                    desc_label.set_markup(f"<small><i>{var['description']}</i></small>")
                    desc_label.set_line_wrap(True)
                    desc_label.set_max_width_chars(50)
                    desc_label.get_style_context().add_class('dim-label')
                    grid.attach(desc_label, 0, current_row, 2, 1)
                    current_row += 1

            elif var_type == 'number':
                adj = Gtk.Adjustment(value=var.get('default', 0), lower=0, upper=65535, step_incr=1)
                input_widget = Gtk.SpinButton.new(adj, 1, 0)
                grid.attach(label, 0, current_row, 1, 1)
                grid.attach(input_widget, 1, current_row, 1, 1)
                current_row += 1

                # Add description caption if available
                if var.get('description'):
                    desc_label = Gtk.Label(xalign=0)
                    desc_label.set_markup(f"<small><i>{var['description']}</i></small>")
                    desc_label.set_line_wrap(True)
                    desc_label.set_max_width_chars(50)
                    desc_label.get_style_context().add_class('dim-label')
                    grid.attach(desc_label, 0, current_row, 2, 1)
                    current_row += 1

            elif var_type in ['path', 'directory']: # Path/directory types
                # Create a horizontal box for entry + browse button
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

                input_widget = Gtk.Entry()
                input_widget.set_text(str(var.get('default', '')))
                input_widget.set_hexpand(True)
                hbox.pack_start(input_widget, True, True, 0)

                # Browse button
                browse_button = Gtk.Button()
                browse_icon = Gtk.Image.new_from_icon_name("folder-open-symbolic", Gtk.IconSize.BUTTON)
                browse_button.add(browse_icon)
                browse_button.set_tooltip_text("Browse for directory")
                browse_button.connect("clicked", self.on_browse_directory_clicked, input_widget)
                hbox.pack_start(browse_button, False, False, 0)

                grid.attach(label, 0, current_row, 1, 1)
                grid.attach(hbox, 1, current_row, 1, 1)
                current_row += 1

                # Add description caption if available
                if var.get('description'):
                    desc_label = Gtk.Label(xalign=0)
                    desc_label.set_markup(f"<small><i>{var['description']}</i></small>")
                    desc_label.set_line_wrap(True)
                    desc_label.set_max_width_chars(50)
                    desc_label.get_style_context().add_class('dim-label')
                    grid.attach(desc_label, 0, current_row, 2, 1)
                    current_row += 1

                # Add volume mapping checkbox and container path entry
                volume_check = Gtk.CheckButton(label="Map as volume to container path:")
                volume_check.set_active(False)
                grid.attach(volume_check, 0, current_row, 1, 1)

                container_path_entry = Gtk.Entry()
                container_path_entry.set_text(var.get('container_path', f"/data/{var['name']}"))
                container_path_entry.set_placeholder_text("Container mount path (e.g., /data)")
                container_path_entry.set_sensitive(False)
                grid.attach(container_path_entry, 1, current_row, 1, 1)

                # Enable/disable container path entry based on checkbox
                def on_volume_check_toggled(check, entry):
                    entry.set_sensitive(check.get_active())

                volume_check.connect("toggled", on_volume_check_toggled, container_path_entry)

                # Store volume mapping widgets
                widgets["volume_mappings"][var['name']] = {
                    'enabled': volume_check,
                    'host_path': input_widget,
                    'container_path': container_path_entry
                }
                current_row += 1

            else: # Default to string
                input_widget = Gtk.Entry()
                input_widget.set_text(str(var.get('default', '')))
                grid.attach(label, 0, current_row, 1, 1)
                grid.attach(input_widget, 1, current_row, 1, 1)
                current_row += 1

                # Add description caption if available
                if var.get('description'):
                    desc_label = Gtk.Label(xalign=0)
                    desc_label.set_markup(f"<small><i>{var['description']}</i></small>")
                    desc_label.set_line_wrap(True)
                    desc_label.set_max_width_chars(50)
                    desc_label.get_style_context().add_class('dim-label')
                    grid.attach(desc_label, 0, current_row, 2, 1)
                    current_row += 1

            widgets["variables"][var['name']] = input_widget

        # Create inputs for ports
        for port in service_config.get('ports', []):
            label = Gtk.Label(label=f"{port['name']} ({port['container']}/{port['protocol']})", xalign=0)
            label.set_tooltip_text(port.get('description', ''))

            adj = Gtk.Adjustment(value=port.get('host', 0), lower=0, upper=65535, step_incr=1)
            input_widget = Gtk.SpinButton.new(adj, 1, 0)

            grid.attach(label, 0, current_row, 1, 1)
            grid.attach(input_widget, 1, current_row, 1, 1)
            widgets["ports"][port['name']] = input_widget
            current_row += 1

            # Add description caption if available
            if port.get('description'):
                desc_label = Gtk.Label(xalign=0)
                desc_label.set_markup(f"<small><i>{port['description']}</i></small>")
                desc_label.set_line_wrap(True)
                desc_label.set_max_width_chars(50)
                desc_label.get_style_context().add_class('dim-label')
                grid.attach(desc_label, 0, current_row, 2, 1)
                current_row += 1

        dialog.show_all()

        # Dialog loop to handle Preview button
        while True:
            response = dialog.run()

            # Collect config values
            config_values = {"variables": {}, "ports": {}, "volume_mappings": {}}
            for name, widget in widgets["variables"].items():
                if isinstance(widget, Gtk.CheckButton):
                    config_values["variables"][name] = widget.get_active()
                elif isinstance(widget, Gtk.SpinButton):
                    config_values["variables"][name] = widget.get_value_as_int()
                else:
                    config_values["variables"][name] = widget.get_text()

            for name, widget in widgets["ports"].items():
                config_values["ports"][name] = widget.get_value_as_int()

            # Collect volume mappings
            for var_name, mapping_widgets in widgets["volume_mappings"].items():
                config_values["volume_mappings"][var_name] = {
                    'enabled': mapping_widgets['enabled'].get_active(),
                    'host_path': mapping_widgets['host_path'].get_text(),
                    'container_path': mapping_widgets['container_path'].get_text()
                }

            if response == Gtk.ResponseType.HELP:
                # Preview Command button clicked
                command = core.install_service(service_config, config_values)
                self.show_command_preview_dialog(command)
                # Continue loop to keep dialog open
                continue

            elif response == Gtk.ResponseType.APPLY:
                # Save as docker-compose.yml button clicked
                result = self.save_service_as_compose(service_config, config_values)
                if result == "deployed":
                    # User saved and deployed the compose file
                    dialog.destroy()
                    self.update_running_container_view()
                    return "installed"
                elif result == "saved":
                    # User saved but didn't deploy
                    dialog.destroy()
                    return "saved"
                # If cancelled, continue loop to keep dialog open
                continue

            elif response == Gtk.ResponseType.OK:
                # Install button clicked
                command = core.install_service(service_config, config_values)

                # Show confirmation dialog
                if self.show_install_confirmation_dialog(service_config.get('name', service_name), command):
                    # User confirmed, execute the command
                    success, output = self.execute_docker_command(command)

                    # Update output display
                    status_msg = f"{'✓' if success else '✗'} Installation of {service_name}:\n{output}\n"
                    current_text = self.textbuffer.get_text(
                        self.textbuffer.get_start_iter(),
                        self.textbuffer.get_end_iter(),
                        True
                    )
                    self.textbuffer.set_text(current_text + status_msg if current_text else status_msg)

                    # Refresh container list
                    self.update_running_container_view()

                    dialog.destroy()
                    return "installed" if success else "error"
                else:
                    # User cancelled confirmation, keep config dialog open
                    continue

            else:  # CANCEL
                dialog.destroy()
                return "cancelled"


    def show_command_preview_dialog(self, command):
        """Show a dialog with the Docker command that will be executed"""
        dialog = Gtk.Dialog(
            title="Docker Command Preview",
            transient_for=self,
            flags=0
        )
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(700, 400)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_top(12)
        scrolled_window.set_margin_bottom(12)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(True)
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview.set_left_margin(8)
        textview.set_right_margin(8)
        textview.set_top_margin(8)
        textview.set_bottom_margin(8)
        textview.override_font(Pango.FontDescription("monospace 10"))

        textbuffer = textview.get_buffer()
        textbuffer.set_text(command)

        scrolled_window.add(textview)
        box = dialog.get_content_area()
        box.add(scrolled_window)
        dialog.show_all()

        dialog.run()
        dialog.destroy()

    def show_install_confirmation_dialog(self, service_name, command):
        """Show confirmation dialog before executing the Docker command"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Execute Docker installation for {service_name}?",
        )

        # Format command for display
        formatted_command = command.replace("Generated command:\n", "")
        dialog.format_secondary_text(
            f"The following command will be executed:\n\n{formatted_command}\n\nDo you want to proceed?"
        )

        response = dialog.run()
        dialog.destroy()

        return response == Gtk.ResponseType.YES

    def execute_docker_command(self, command_output):
        """Execute the Docker command and return success status and output"""
        import subprocess

        # Extract the actual command from the output
        command = command_output.replace("Generated command:\n", "").strip()

        try:
            # Execute the docker command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                output = result.stdout if result.stdout else "Container started successfully"
                return True, output
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Error: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Error: Command timed out after 60 seconds"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"

    def start_container(self, container_id, container_name):
        """Start a stopped container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            self.textbuffer.set_text(f"✓ Started container: {container_name} ({container_id})")
            self.update_running_container_view()
        except Exception as e:
            self.textbuffer.set_text(f"✗ Error starting {container_name}: {str(e)}")

    def restart_container(self, container_id, container_name):
        """Restart a container"""
        try:
            container = self.client.containers.get(container_id)
            container.restart()
            self.textbuffer.set_text(f"✓ Restarted container: {container_name} ({container_id})")
            self.update_running_container_view()
        except Exception as e:
            self.textbuffer.set_text(f"✗ Error restarting {container_name}: {str(e)}")

    def stop_container(self, container_id, container_name):
        """Stop a container"""
        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Stop container {container_name}?",
        )
        dialog.format_secondary_text(f"Container ID: {container_id}")

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            try:
                container = self.client.containers.get(container_id)
                container.stop()
                self.textbuffer.set_text(f"✓ Stopped container: {container_name} ({container_id})")
                self.update_running_container_view()
            except Exception as e:
                self.textbuffer.set_text(f"✗ Error stopping {container_name}: {str(e)}")

    def view_container_logs(self, container_id, container_name):
        """View container logs in a dialog"""
        dialog = Gtk.Dialog(
            title=f"Logs: {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button("Refresh", Gtk.ResponseType.APPLY)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(900, 600)

        content_area = dialog.get_content_area()
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)

        # Options bar
        options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        options_box.set_margin_bottom(8)

        # Tail lines option
        tail_label = Gtk.Label(label="Tail lines:")
        options_box.pack_start(tail_label, False, False, 0)

        tail_adj = Gtk.Adjustment(value=100, lower=10, upper=10000, step_incr=10)
        tail_spin = Gtk.SpinButton.new(tail_adj, 1, 0)
        options_box.pack_start(tail_spin, False, False, 0)

        # Follow logs checkbox
        follow_check = Gtk.CheckButton(label="Follow logs (live)")
        options_box.pack_start(follow_check, False, False, 8)

        # Timestamps checkbox
        timestamps_check = Gtk.CheckButton(label="Show timestamps")
        timestamps_check.set_active(True)
        options_box.pack_start(timestamps_check, False, False, 0)

        content_area.pack_start(options_box, False, False, 0)

        # Logs text view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        logs_textview = Gtk.TextView()
        logs_textview.set_editable(False)
        logs_textview.set_cursor_visible(True)
        logs_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        logs_textview.set_left_margin(8)
        logs_textview.set_right_margin(8)
        logs_textview.set_top_margin(8)
        logs_textview.set_bottom_margin(8)
        logs_textview.override_font(Pango.FontDescription("monospace 9"))

        logs_textbuffer = logs_textview.get_buffer()

        scrolled_window.add(logs_textview)
        content_area.pack_start(scrolled_window, True, True, 0)

        # Function to load logs
        def load_logs():
            try:
                container = self.client.containers.get(container_id)
                tail_lines = tail_spin.get_value_as_int()
                show_timestamps = timestamps_check.get_active()

                logs = container.logs(
                    tail=tail_lines,
                    timestamps=show_timestamps
                ).decode('utf-8', errors='replace')

                logs_textbuffer.set_text(logs)

                # Scroll to bottom
                end_iter = logs_textbuffer.get_end_iter()
                logs_textview.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)

            except Exception as e:
                logs_textbuffer.set_text(f"Error retrieving logs: {str(e)}")

        # Initial load
        load_logs()

        dialog.show_all()

        # Dialog loop for refresh button
        while True:
            response = dialog.run()

            if response == Gtk.ResponseType.APPLY:
                # Refresh button clicked
                load_logs()
            else:
                # Close button or dialog closed
                break

        dialog.destroy()

    def show_container_context_menu(self, event, container_id, container_name):
        """Show context menu for container row"""
        menu = Gtk.Menu()

        # Open Terminal menu item
        terminal_item = Gtk.MenuItem(label="🖥 Open Terminal in Container")
        terminal_item.connect("activate", self.on_context_open_terminal, container_id, container_name)
        menu.append(terminal_item)

        # View Details menu item
        details_item = Gtk.MenuItem(label="ℹ View Details")
        details_item.connect("activate", self.on_context_view_details, container_id, container_name)
        menu.append(details_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Export Files menu item
        export_item = Gtk.MenuItem(label="📤 Export Files from Container")
        export_item.connect("activate", self.on_context_export_files, container_id, container_name)
        menu.append(export_item)

        # View Logs menu item
        logs_item = Gtk.MenuItem(label="📋 View Logs")
        logs_item.connect("activate", self.on_context_view_logs, container_id, container_name)
        menu.append(logs_item)

        # Backup menu item
        backup_item = Gtk.MenuItem(label="💾 Backup Container")
        backup_item.connect("activate", self.on_context_backup, container_id, container_name)
        menu.append(backup_item)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def on_context_open_terminal(self, menuitem, container_id, container_name):
        """Handle Open Terminal context menu action"""
        self.open_container_terminal(container_id, container_name)

    def on_context_view_details(self, menuitem, container_id, container_name):
        """Handle View Details context menu action"""
        details_str = core.get_full_container_details(self.client, container_id)

        dialog = Gtk.Dialog(
            title=f"Details for {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(600, 500)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_start(10)
        scrolled_window.set_margin_end(10)
        scrolled_window.set_margin_top(10)
        scrolled_window.set_margin_bottom(10)

        label = Gtk.Label()
        label.set_markup(details_str)
        label.set_xalign(0)
        label.set_yalign(0)
        label.set_selectable(True)
        label.set_line_wrap(True)

        scrolled_window.add(label)
        box = dialog.get_content_area()
        box.add(scrolled_window)
        dialog.show_all()

        dialog.run()
        dialog.destroy()

    def on_context_export_files(self, menuitem, container_id, container_name):
        """Handle Export Files context menu action"""
        self.export_files_from_container(container_id, container_name)

    def on_context_view_logs(self, menuitem, container_id, container_name):
        """Handle View Logs context menu action"""
        self.view_container_logs(container_id, container_name)

    def on_context_backup(self, menuitem, container_id, container_name):
        """Handle Backup context menu action"""
        self.backup_container(container_id, container_name)

    def open_container_terminal(self, container_id, container_name):
        """Open a terminal window with shell access to the container"""
        import subprocess
        import shutil

        # Try to find available terminal emulators
        terminals = [
            ('gnome-terminal', ['gnome-terminal', '--', 'docker', 'exec', '-it', container_id, '/bin/sh']),
            ('xterm', ['xterm', '-e', f'docker exec -it {container_id} /bin/sh']),
            ('konsole', ['konsole', '-e', f'docker exec -it {container_id} /bin/sh']),
            ('xfce4-terminal', ['xfce4-terminal', '-e', f'docker exec -it {container_id} /bin/sh']),
            ('mate-terminal', ['mate-terminal', '-e', f'docker exec -it {container_id} /bin/sh']),
            ('terminator', ['terminator', '-e', f'docker exec -it {container_id} /bin/sh']),
        ]

        # Find the first available terminal
        terminal_found = None
        for term_name, term_cmd in terminals:
            if shutil.which(term_name.split()[0]):
                terminal_found = term_cmd
                break

        if terminal_found is None:
            # No terminal found, show error
            self.show_error_dialog(
                "No supported terminal emulator found.\n\n"
                "Supported terminals: gnome-terminal, xterm, konsole, xfce4-terminal, mate-terminal, terminator\n\n"
                "You can manually run:\n"
                f"docker exec -it {container_id} /bin/sh"
            )
            return

        try:
            # Launch terminal in background
            subprocess.Popen(terminal_found, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.textbuffer.set_text(f"✓ Opened terminal for container: {container_name} ({container_id})")
        except Exception as e:
            self.textbuffer.set_text(f"✗ Error opening terminal for {container_name}: {str(e)}")

    def backup_container(self, container_id, container_name):
        """Comprehensive backup dialog with multiple options"""
        container = self.client.containers.get(container_id)

        dialog = Gtk.Dialog(
            title=f"Backup Options: {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button("Execute Backup", Gtk.ResponseType.OK)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.set_default_size(650, 550)

        content_area = dialog.get_content_area()
        content_area.set_margin_start(16)
        content_area.set_margin_end(16)
        content_area.set_margin_top(16)
        content_area.set_margin_bottom(16)

        # Container info
        info_label = Gtk.Label()
        info_label.set_markup(
            f"<b>Container:</b> {container_name}\n"
            f"<b>ID:</b> {container_id}\n"
            f"<b>Image:</b> {container.image.tags[0] if container.image.tags else container.image.short_id}"
        )
        info_label.set_xalign(0)
        content_area.pack_start(info_label, False, False, 8)

        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.pack_start(separator1, False, False, 8)

        # Backup type selection
        backup_label = Gtk.Label()
        backup_label.set_markup("<b>Select Backup Type:</b>")
        backup_label.set_xalign(0)
        content_area.pack_start(backup_label, False, False, 4)

        # Radio buttons for backup type
        commit_radio = Gtk.RadioButton.new_with_label_from_widget(None,
            "Commit to Image (filesystem snapshot, no volumes)")
        content_area.pack_start(commit_radio, False, False, 2)

        export_radio = Gtk.RadioButton.new_with_label_from_widget(commit_radio,
            "Export to TAR (full container export, no volumes)")
        content_area.pack_start(export_radio, False, False, 2)

        full_radio = Gtk.RadioButton.new_with_label_from_widget(commit_radio,
            "Full Backup (container + volumes + run command)")
        full_radio.set_active(True)  # Default to full backup
        content_area.pack_start(full_radio, False, False, 2)

        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.pack_start(separator2, False, False, 8)

        # Backup location
        location_label = Gtk.Label()
        location_label.set_markup("<b>Backup Location:</b>")
        location_label.set_xalign(0)
        content_area.pack_start(location_label, False, False, 4)

        location_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        location_entry = Gtk.Entry()
        location_entry.set_text(f"/tmp/{container_name}-backup")
        location_box.pack_start(location_entry, True, True, 0)

        browse_button = Gtk.Button(label="Browse...")
        browse_button.connect("clicked", self.on_backup_browse_clicked, location_entry)
        location_box.pack_start(browse_button, False, False, 0)
        content_area.pack_start(location_box, False, False, 4)

        # Options
        separator3 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.pack_start(separator3, False, False, 8)

        options_label = Gtk.Label()
        options_label.set_markup("<b>Options:</b>")
        options_label.set_xalign(0)
        content_area.pack_start(options_label, False, False, 4)

        pause_check = Gtk.CheckButton(label="Pause container during backup (safer)")
        pause_check.set_active(True)
        content_area.pack_start(pause_check, False, False, 2)

        compress_check = Gtk.CheckButton(label="Compress backup files")
        compress_check.set_active(True)
        content_area.pack_start(compress_check, False, False, 2)

        save_config_check = Gtk.CheckButton(label="Save container recreation script")
        save_config_check.set_active(True)
        content_area.pack_start(save_config_check, False, False, 2)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            backup_location = location_entry.get_text().strip()

            if commit_radio.get_active():
                backup_type = "commit"
            elif export_radio.get_active():
                backup_type = "export"
            else:
                backup_type = "full"

            options = {
                "pause": pause_check.get_active(),
                "compress": compress_check.get_active(),
                "save_config": save_config_check.get_active()
            }

            dialog.destroy()

            # Execute the backup
            self.execute_backup(container_id, container_name, backup_type, backup_location, options)
        else:
            dialog.destroy()

    def on_backup_browse_clicked(self, button, entry):
        """Browse for backup directory"""
        dialog = Gtk.FileChooserDialog(
            title="Select Backup Directory",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()

    def on_browse_directory_clicked(self, button, entry):
        """Browse for directory for volume mapping"""
        dialog = Gtk.FileChooserDialog(
            title="Select Directory",
            transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Set current directory if path exists
        current_path = entry.get_text()
        if current_path and os.path.exists(current_path):
            dialog.set_current_folder(current_path)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()

    def execute_backup(self, container_id, container_name, backup_type, backup_location, options):
        """Execute the container backup based on selected type"""
        import os
        import subprocess
        import tarfile
        from datetime import datetime

        try:
            container = self.client.containers.get(container_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create backup directory
            os.makedirs(backup_location, exist_ok=True)

            output_messages = []

            # Pause container if requested
            was_paused = False
            if options["pause"] and container.status == "running":
                container.pause()
                was_paused = True
                output_messages.append("⏸ Container paused for backup")

            try:
                if backup_type == "commit":
                    # Commit to image
                    image_name = f"{container_name}-backup"
                    image = container.commit(repository=image_name, tag=timestamp)
                    output_messages.append(f"✓ Committed to image: {image_name}:{timestamp}")
                    output_messages.append(f"  Image ID: {image.short_id}")

                elif backup_type == "export":
                    # Export container to TAR
                    export_file = os.path.join(backup_location, f"{container_name}_{timestamp}.tar")
                    if options["compress"]:
                        export_file += ".gz"

                    output_messages.append(f"📦 Exporting container to {export_file}...")

                    # Export container
                    bits = container.export()
                    with open(export_file if not options["compress"] else export_file.replace('.gz', ''), 'wb') as f:
                        for chunk in bits:
                            f.write(chunk)

                    # Compress if requested
                    if options["compress"]:
                        import gzip
                        import shutil
                        with open(export_file.replace('.gz', ''), 'rb') as f_in:
                            with gzip.open(export_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(export_file.replace('.gz', ''))

                    output_messages.append(f"✓ Container exported successfully")

                elif backup_type == "full":
                    # Full backup: export + volumes + config
                    backup_dir = os.path.join(backup_location, f"{container_name}_{timestamp}")
                    os.makedirs(backup_dir, exist_ok=True)

                    # 1. Export container
                    export_file = os.path.join(backup_dir, "container.tar")
                    output_messages.append(f"📦 Exporting container...")
                    bits = container.export()
                    with open(export_file, 'wb') as f:
                        for chunk in bits:
                            f.write(chunk)

                    if options["compress"]:
                        subprocess.run(['gzip', export_file], check=True)
                        export_file += ".gz"

                    output_messages.append(f"✓ Container exported")

                    # 2. Backup volumes
                    mounts = container.attrs.get('Mounts', [])
                    if mounts:
                        volumes_dir = os.path.join(backup_dir, "volumes")
                        os.makedirs(volumes_dir, exist_ok=True)
                        output_messages.append(f"💾 Backing up {len(mounts)} volume(s)...")

                        for i, mount in enumerate(mounts):
                            mount_type = mount.get('Type', 'unknown')
                            source = mount.get('Source', '')
                            destination = mount.get('Destination', '')

                            if mount_type in ['volume', 'bind'] and source:
                                volume_backup = os.path.join(volumes_dir, f"volume_{i}_{os.path.basename(destination)}.tar")

                                try:
                                    # Create tar of volume data
                                    with tarfile.open(volume_backup, 'w') as tar:
                                        tar.add(source, arcname=os.path.basename(source))

                                    if options["compress"]:
                                        subprocess.run(['gzip', volume_backup], check=True)

                                    output_messages.append(f"  ✓ Volume: {destination}")
                                except Exception as e:
                                    output_messages.append(f"  ✗ Failed to backup {destination}: {str(e)}")

                        output_messages.append(f"✓ Volumes backed up")

                    # 3. Save recreation script
                    if options["save_config"]:
                        config_file = os.path.join(backup_dir, "recreate.sh")
                        self.generate_recreation_script(container, config_file)
                        output_messages.append(f"✓ Recreation script saved: recreate.sh")

                    output_messages.append(f"\n📁 Full backup location: {backup_dir}")

            finally:
                # Unpause container if it was paused
                if was_paused:
                    container.unpause()
                    output_messages.append("▶ Container resumed")

            self.textbuffer.set_text("\n".join(output_messages))

        except Exception as e:
            self.textbuffer.set_text(f"✗ Backup failed: {str(e)}")

    def generate_recreation_script(self, container, output_file):
        """Generate a shell script to recreate the container"""
        from datetime import datetime

        attrs = container.attrs
        config = attrs['Config']
        host_config = attrs['HostConfig']

        script_lines = [
            "#!/bin/bash",
            "# Container Recreation Script",
            f"# Original container: {container.name}",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "docker run -d \\",
            f"  --name {container.name} \\",
        ]

        # Add environment variables
        for env in config.get('Env', []):
            if not env.startswith(('PATH=', 'HOME=')):  # Skip common defaults
                script_lines.append(f"  -e '{env}' \\")

        # Add port mappings
        port_bindings = host_config.get('PortBindings', {})
        for container_port, host_ports in port_bindings.items():
            if host_ports:
                host_port = host_ports[0]['HostPort']
                script_lines.append(f"  -p {host_port}:{container_port} \\")

        # Add volume mounts
        for mount in attrs.get('Mounts', []):
            source = mount.get('Source', '')
            destination = mount.get('Destination', '')
            if source and destination:
                script_lines.append(f"  -v {source}:{destination} \\")

        # Add network
        networks = attrs.get('NetworkSettings', {}).get('Networks', {})
        for network_name in networks.keys():
            if network_name != 'bridge':
                script_lines.append(f"  --network {network_name} \\")

        # Add restart policy
        restart_policy = host_config.get('RestartPolicy', {}).get('Name', '')
        if restart_policy:
            script_lines.append(f"  --restart {restart_policy} \\")

        # Add image
        image = config.get('Image', '')
        script_lines.append(f"  {image}")

        # Write script
        with open(output_file, 'w') as f:
            f.write('\n'.join(script_lines))
            f.write('\n')

        # Make executable
        os.chmod(output_file, 0o755)

    def remove_container(self, container_id, container_name):
        """Remove a container with option to remove associated volumes"""
        try:
            container = self.client.containers.get(container_id)
            mounts = container.attrs.get('Mounts', [])
        except Exception as e:
            self.show_error_dialog(f"Error accessing container: {str(e)}")
            return

        # Create custom dialog with volume information
        dialog = Gtk.Dialog(
            title=f"Remove Container: {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button("Remove", Gtk.ResponseType.YES)
        dialog.add_button("Cancel", Gtk.ResponseType.NO)
        dialog.set_default_size(600, 400)

        content_area = dialog.get_content_area()
        content_area.set_margin_start(16)
        content_area.set_margin_end(16)
        content_area.set_margin_top(16)
        content_area.set_margin_bottom(16)

        # Warning header
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning", Gtk.IconSize.DIALOG)
        warning_box.pack_start(warning_icon, False, False, 0)

        warning_label = Gtk.Label()
        warning_label.set_markup(
            f"<span size='large' weight='bold'>Remove container {container_name}?</span>\n\n"
            f"<b>Container ID:</b> {container_id}\n\n"
            f"This will permanently remove the container.\n"
            f"The container will be stopped if it is running."
        )
        warning_label.set_xalign(0)
        warning_label.set_line_wrap(True)
        warning_box.pack_start(warning_label, True, True, 0)

        content_area.pack_start(warning_box, False, False, 8)

        # Separator
        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.pack_start(separator1, False, False, 8)

        # Volume information (if any volumes exist)
        if mounts:
            volumes_label = Gtk.Label()
            volumes_label.set_markup(f"<b>Associated Volumes ({len(mounts)}):</b>")
            volumes_label.set_xalign(0)
            content_area.pack_start(volumes_label, False, False, 4)

            # Scrolled window for volume list
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
            scrolled_window.set_min_content_height(120)

            volumes_textview = Gtk.TextView()
            volumes_textview.set_editable(False)
            volumes_textview.set_cursor_visible(False)
            volumes_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            volumes_textview.set_left_margin(8)
            volumes_textview.set_right_margin(8)
            volumes_textview.set_top_margin(8)
            volumes_textview.set_bottom_margin(8)
            volumes_textview.override_font(Pango.FontDescription("monospace 9"))

            volumes_textbuffer = volumes_textview.get_buffer()

            # Build volume information text
            volume_info_lines = []
            for i, mount in enumerate(mounts, 1):
                mount_type = mount.get('Type', 'unknown')
                source = mount.get('Source', 'N/A')
                destination = mount.get('Destination', 'N/A')

                volume_info_lines.append(f"{i}. Type: {mount_type}")
                volume_info_lines.append(f"   Source: {source}")
                volume_info_lines.append(f"   Destination: {destination}")
                volume_info_lines.append("")

            volumes_textbuffer.set_text('\n'.join(volume_info_lines))

            scrolled_window.add(volumes_textview)
            content_area.pack_start(scrolled_window, True, True, 4)

            # Separator
            separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            content_area.pack_start(separator2, False, False, 8)

            # Checkbox for volume removal
            remove_volumes_check = Gtk.CheckButton(label="Also remove associated volumes")
            remove_volumes_check.set_active(False)  # Default to NOT removing volumes
            content_area.pack_start(remove_volumes_check, False, False, 4)

            # Warning about volume removal
            volume_warning = Gtk.Label()
            volume_warning.set_markup(
                '<span size="small" color="#ef4444">'
                '<b>Warning:</b> Removing volumes will permanently delete all data in these volumes!'
                '</span>'
            )
            volume_warning.set_xalign(0)
            volume_warning.set_line_wrap(True)
            content_area.pack_start(volume_warning, False, False, 4)
        else:
            # No volumes
            no_volumes_label = Gtk.Label()
            no_volumes_label.set_markup("<i>This container has no associated volumes.</i>")
            no_volumes_label.set_xalign(0)
            content_area.pack_start(no_volumes_label, False, False, 8)
            remove_volumes_check = None

        dialog.show_all()
        response = dialog.run()

        # Get checkbox state if volumes exist
        remove_volumes = False
        if mounts and remove_volumes_check:
            remove_volumes = remove_volumes_check.get_active()

        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            try:
                container.remove(force=True, v=remove_volumes)

                status_msg = f"✓ Removed container: {container_name} ({container_id})"
                if remove_volumes and mounts:
                    status_msg += f"\n✓ Removed {len(mounts)} associated volume(s)"

                self.textbuffer.set_text(status_msg)
                self.update_running_container_view()
            except Exception as e:
                self.textbuffer.set_text(f"✗ Error removing {container_name}: {str(e)}")

    def on_cleanup_networks_clicked(self, widget):
        """Remove all unused networks (excluding system networks)"""
        # Collect unused networks
        unused_networks = []
        try:
            networks = self.client.networks.list()
            for network in networks:
                network_name = network.name
                # Skip system networks
                if network_name in ['bridge', 'host', 'none']:
                    continue

                # Check if network is in use
                containers = network.attrs.get('Containers', {})
                if len(containers) == 0:
                    unused_networks.append((network.id, network_name))

        except Exception as e:
            self.show_error_dialog(f"Error scanning networks: {str(e)}")
            return

        if not unused_networks:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No Unused Networks",
            )
            dialog.format_secondary_text("All networks are currently in use or are system networks.")
            dialog.run()
            dialog.destroy()
            return

        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Remove {len(unused_networks)} unused network(s)?",
        )

        network_list = "\n".join([f"  • {name}" for _, name in unused_networks])
        dialog.format_secondary_text(
            f"The following unused networks will be removed:\n\n{network_list}\n\n"
            f"This action cannot be undone. Continue?"
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            removed_count = 0
            errors = []

            for network_id, network_name in unused_networks:
                try:
                    network = self.client.networks.get(network_id)
                    network.remove()
                    removed_count += 1
                except Exception as e:
                    errors.append(f"{network_name}: {str(e)}")

            # Update display
            result_msg = f"✓ Removed {removed_count} unused network(s)"
            if errors:
                result_msg += f"\n✗ Failed to remove {len(errors)} network(s):\n"
                result_msg += "\n".join([f"  • {err}" for err in errors])

            self.textbuffer.set_text(result_msg)
            self.update_running_container_view()

    def on_cleanup_volumes_clicked(self, widget):
        """Remove all unused volumes"""
        # Collect unused volumes
        unused_volumes = []
        try:
            volumes = self.client.volumes.list()
            all_containers = self.client.containers.list(all=True)

            for volume in volumes:
                volume_name = volume.name

                # Check if volume is in use by any container
                in_use = False
                for container in all_containers:
                    for mount in container.attrs.get('Mounts', []):
                        if mount.get('Type') == 'volume' and mount.get('Name') == volume_name:
                            in_use = True
                            break
                    if in_use:
                        break

                if not in_use:
                    unused_volumes.append(volume_name)

        except Exception as e:
            self.show_error_dialog(f"Error scanning volumes: {str(e)}")
            return

        if not unused_volumes:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No Unused Volumes",
            )
            dialog.format_secondary_text("All volumes are currently in use by containers.")
            dialog.run()
            dialog.destroy()
            return

        # Show confirmation dialog with warning
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Remove {len(unused_volumes)} unused volume(s)?",
        )

        volume_list = "\n".join([f"  • {name}" for name in unused_volumes])
        dialog.format_secondary_text(
            f"⚠️  WARNING: This will permanently delete all data in these volumes!\n\n"
            f"The following unused volumes will be removed:\n\n{volume_list}\n\n"
            f"This action CANNOT be undone. Continue?"
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            removed_count = 0
            errors = []

            for volume_name in unused_volumes:
                try:
                    volume = self.client.volumes.get(volume_name)
                    volume.remove()
                    removed_count += 1
                except Exception as e:
                    errors.append(f"{volume_name}: {str(e)}")

            # Update display
            result_msg = f"✓ Removed {removed_count} unused volume(s)"
            if errors:
                result_msg += f"\n✗ Failed to remove {len(errors)} volume(s):\n"
                result_msg += "\n".join([f"  • {err}" for err in errors])

            self.textbuffer.set_text(result_msg)
            self.update_running_container_view()

    def on_cleanup_images_clicked(self, widget):
        """Remove all unused images (excluding those in use)"""
        # Collect unused images
        unused_images = []
        try:
            images = self.client.images.list()
            all_containers = self.client.containers.list(all=True)
            used_image_ids = set()

            for container in all_containers:
                image_id = container.attrs.get('Image', '')
                if image_id:
                    used_image_ids.add(image_id)

            for image in images:
                # Skip if image is in use
                if image.id in used_image_ids:
                    continue

                # Get tag info
                if image.tags:
                    tag_name = image.tags[0]
                else:
                    tag_name = f"<none> ({image.short_id})"

                size_mb = image.attrs.get('Size', 0) / (1024 * 1024)
                unused_images.append((image.id, tag_name, size_mb))

        except Exception as e:
            self.show_error_dialog(f"Error scanning images: {str(e)}")
            return

        if not unused_images:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No Unused Images",
            )
            dialog.format_secondary_text("All images are currently in use by containers.")
            dialog.run()
            dialog.destroy()
            return

        # Calculate total size
        total_size_mb = sum([size for _, _, size in unused_images])

        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Remove {len(unused_images)} unused image(s)?",
        )

        image_list = "\n".join([f"  • {tag} ({size:.1f} MB)" for _, tag, size in unused_images[:20]])
        if len(unused_images) > 20:
            image_list += f"\n  ... and {len(unused_images) - 20} more"

        dialog.format_secondary_text(
            f"The following unused images will be removed:\n\n{image_list}\n\n"
            f"Total space to be freed: {total_size_mb:.1f} MB\n\n"
            f"Continue?"
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            removed_count = 0
            freed_space_mb = 0
            errors = []

            for image_id, tag_name, size_mb in unused_images:
                try:
                    self.client.images.remove(image_id, force=False)
                    removed_count += 1
                    freed_space_mb += size_mb
                except Exception as e:
                    errors.append(f"{tag_name}: {str(e)}")

            # Update display
            result_msg = f"✓ Removed {removed_count} unused image(s)\n✓ Freed {freed_space_mb:.1f} MB of disk space"
            if errors:
                result_msg += f"\n✗ Failed to remove {len(errors)} image(s):\n"
                result_msg += "\n".join([f"  • {err}" for err in errors[:10]])
                if len(errors) > 10:
                    result_msg += f"\n  ... and {len(errors) - 10} more errors"

            self.textbuffer.set_text(result_msg)
            self.update_running_container_view()

    def on_prune_images_clicked(self, widget):
        """Remove all dangling images (images with no tags)"""
        # Collect dangling images
        dangling_images = []
        try:
            images = self.client.images.list(filters={'dangling': True})

            for image in images:
                size_mb = image.attrs.get('Size', 0) / (1024 * 1024)
                dangling_images.append((image.id, image.short_id, size_mb))

        except Exception as e:
            self.show_error_dialog(f"Error scanning images: {str(e)}")
            return

        if not dangling_images:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No Dangling Images",
            )
            dialog.format_secondary_text("There are no dangling images to remove.")
            dialog.run()
            dialog.destroy()
            return

        # Calculate total size
        total_size_mb = sum([size for _, _, size in dangling_images])

        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Remove {len(dangling_images)} dangling image(s)?",
        )

        dialog.format_secondary_text(
            f"Dangling images are layers that have no relationship to any tagged images.\n"
            f"They are usually safe to remove.\n\n"
            f"Total space to be freed: {total_size_mb:.1f} MB\n\n"
            f"Continue?"
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            try:
                # Use Docker's prune API for efficiency
                result = self.client.images.prune(filters={'dangling': True})
                deleted_count = len(result.get('ImagesDeleted', []))
                freed_space = result.get('SpaceReclaimed', 0) / (1024 * 1024)

                self.textbuffer.set_text(
                    f"✓ Removed {deleted_count} dangling image(s)\n"
                    f"✓ Freed {freed_space:.1f} MB of disk space"
                )
                self.update_running_container_view()
            except Exception as e:
                self.textbuffer.set_text(f"✗ Error pruning dangling images: {str(e)}")

    def on_export_stack_clicked(self, widget):
        """Export selected stack to docker-compose.yml file"""
        # Get selected stack
        selection = self.stack_treeview.get_selection()
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            self.show_error_dialog("Please select a stack to export.")
            return

        stack_name = model.get_value(tree_iter, 0)

        # Get all containers for this stack
        try:
            all_containers = self.client.containers.list(all=True)
            stack_containers = []

            for container in all_containers:
                labels = container.attrs.get('Config', {}).get('Labels', {})
                project_name = labels.get('com.docker.compose.project')

                if project_name == stack_name:
                    stack_containers.append(container)

            if not stack_containers:
                self.show_error_dialog(f"No containers found for stack '{stack_name}'.")
                return

            # Generate docker-compose content
            compose_content = self.generate_docker_compose(stack_name, stack_containers)

            # Show file save dialog
            dialog = Gtk.FileChooserDialog(
                title=f"Save docker-compose.yml for '{stack_name}'",
                transient_for=self,
                action=Gtk.FileChooserAction.SAVE
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
            dialog.set_current_name(f"{stack_name}-docker-compose.yml")
            dialog.set_do_overwrite_confirmation(True)

            # Add file filter
            filter_yaml = Gtk.FileFilter()
            filter_yaml.set_name("YAML files")
            filter_yaml.add_pattern("*.yml")
            filter_yaml.add_pattern("*.yaml")
            dialog.add_filter(filter_yaml)

            filter_all = Gtk.FileFilter()
            filter_all.set_name("All files")
            filter_all.add_pattern("*")
            dialog.add_filter(filter_all)

            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                filepath = dialog.get_filename()
                dialog.destroy()

                # Write to file
                try:
                    with open(filepath, 'w') as f:
                        f.write(compose_content)

                    self.textbuffer.set_text(
                        f"✓ Exported stack '{stack_name}' to docker-compose.yml\n"
                        f"✓ File saved: {filepath}\n"
                        f"✓ {len(stack_containers)} service(s) exported"
                    )
                except Exception as e:
                    self.show_error_dialog(f"Error writing file: {str(e)}")
            else:
                dialog.destroy()

        except Exception as e:
            self.show_error_dialog(f"Error exporting stack: {str(e)}")

    def generate_docker_compose(self, stack_name, containers):
        """Generate docker-compose.yml content from containers"""
        import yaml

        compose = {
            'version': '3.8',
            'services': {}
        }

        volumes_defined = set()
        networks_defined = set()

        for container in containers:
            attrs = container.attrs
            config = attrs.get('Config', {})
            host_config = attrs.get('HostConfig', {})
            labels = config.get('Labels', {})

            # Get service name from label or container name
            service_name = labels.get('com.docker.compose.service', container.name)

            service = {}

            # Image
            image = config.get('Image', '')
            if image:
                service['image'] = image

            # Container name
            service['container_name'] = container.name

            # Command
            cmd = config.get('Cmd')
            if cmd:
                service['command'] = cmd if isinstance(cmd, str) else ' '.join(cmd)

            # Environment variables
            env = config.get('Env', [])
            if env:
                env_dict = {}
                for e in env:
                    if '=' in e and not e.startswith(('PATH=', 'HOME=', 'HOSTNAME=')):
                        key, value = e.split('=', 1)
                        env_dict[key] = value
                if env_dict:
                    service['environment'] = env_dict

            # Ports
            port_bindings = host_config.get('PortBindings', {})
            if port_bindings:
                ports = []
                for container_port, host_ports in port_bindings.items():
                    if host_ports:
                        host_port = host_ports[0].get('HostPort', '')
                        host_ip = host_ports[0].get('HostIp', '')
                        if host_ip and host_ip != '0.0.0.0':
                            ports.append(f"{host_ip}:{host_port}:{container_port}")
                        else:
                            ports.append(f"{host_port}:{container_port}")
                if ports:
                    service['ports'] = ports

            # Volumes
            mounts = attrs.get('Mounts', [])
            if mounts:
                volumes = []
                for mount in mounts:
                    mount_type = mount.get('Type', '')
                    source = mount.get('Source', '')
                    destination = mount.get('Destination', '')
                    read_only = mount.get('RW', True) == False

                    if mount_type == 'volume':
                        # Named volume
                        volume_name = mount.get('Name', source)
                        volumes_defined.add(volume_name)
                        volume_str = f"{volume_name}:{destination}"
                        if read_only:
                            volume_str += ":ro"
                        volumes.append(volume_str)
                    elif mount_type == 'bind':
                        # Bind mount
                        volume_str = f"{source}:{destination}"
                        if read_only:
                            volume_str += ":ro"
                        volumes.append(volume_str)

                if volumes:
                    service['volumes'] = volumes

            # Networks
            networks = attrs.get('NetworkSettings', {}).get('Networks', {})
            if networks:
                network_list = []
                for network_name in networks.keys():
                    if network_name != 'bridge':
                        network_list.append(network_name)
                        networks_defined.add(network_name)
                if network_list:
                    service['networks'] = network_list

            # Restart policy
            restart_policy = host_config.get('RestartPolicy', {}).get('Name', '')
            if restart_policy and restart_policy != 'no':
                service['restart'] = restart_policy

            # Privileged
            if host_config.get('Privileged', False):
                service['privileged'] = True

            # Cap add/drop
            cap_add = host_config.get('CapAdd')
            if cap_add:
                service['cap_add'] = cap_add

            cap_drop = host_config.get('CapDrop')
            if cap_drop:
                service['cap_drop'] = cap_drop

            # Devices
            devices = host_config.get('Devices', [])
            if devices:
                device_list = []
                for device in devices:
                    path_on_host = device.get('PathOnHost', '')
                    path_in_container = device.get('PathInContainer', '')
                    if path_on_host and path_in_container:
                        device_list.append(f"{path_on_host}:{path_in_container}")
                if device_list:
                    service['devices'] = device_list

            # Depends on
            depends_on_label = labels.get('com.docker.compose.depends_on')
            if depends_on_label:
                service['depends_on'] = depends_on_label.split(',')

            # Labels (keep only non-compose labels)
            custom_labels = {}
            for key, value in labels.items():
                if not key.startswith('com.docker.compose'):
                    custom_labels[key] = value
            if custom_labels:
                service['labels'] = custom_labels

            compose['services'][service_name] = service

        # Add volumes section
        if volumes_defined:
            compose['volumes'] = {vol: {} for vol in volumes_defined}

        # Add networks section
        if networks_defined:
            compose['networks'] = {net: {} for net in networks_defined}

        # Convert to YAML
        yaml_output = yaml.dump(compose, default_flow_style=False, sort_keys=False, indent=2)

        # Add header comment
        header = f"# docker-compose.yml for stack: {stack_name}\n"
        header += f"# Generated by Docker Helper on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# This file was reconstructed from running containers\n\n"

        return header + yaml_output

    def save_service_as_compose(self, service_config, config_values):
        """Save service configuration as docker-compose.yml and optionally deploy"""
        import yaml
        import os
        import subprocess

        service_name = service_config.get('name', 'service')

        # Generate docker-compose content
        compose = {
            'version': '3.8',
            'services': {
                service_name: {}
            }
        }

        service_def = compose['services'][service_name]

        # Image
        image = service_config.get('image')
        if image:
            service_def['image'] = image

        # Container name
        service_def['container_name'] = service_name

        # Environment variables
        env_dict = {}
        for var in service_config.get('variables', []):
            var_name = var['name']
            var_type = var.get('type', 'string')
            user_value = config_values['variables'].get(var_name)

            if user_value is None:
                continue

            # Check if this is a volume mapping
            volume_mappings = config_values.get('volume_mappings', {})
            if var_type in ['path', 'directory'] and var_name in volume_mappings:
                if volume_mappings[var_name]['enabled']:
                    # Skip - will be added as volume
                    continue

            # Add as environment variable
            if var_type not in ['path', 'directory']:
                env_dict[var_name] = user_value

        if env_dict:
            service_def['environment'] = env_dict

        # Ports
        ports = []
        for port in service_config.get('ports', []):
            port_name = port['name']
            host_port = config_values['ports'].get(port_name)
            if host_port is not None and host_port > 0:
                container_port = port['container']
                protocol = port.get('protocol', 'tcp')
                ports.append(f"{host_port}:{container_port}")
        if ports:
            service_def['ports'] = ports

        # Volumes
        volumes = []
        volume_mappings = config_values.get('volume_mappings', {})
        for var_name, mapping in volume_mappings.items():
            if mapping['enabled']:
                host_path = mapping['host_path']
                container_path = mapping['container_path']
                if host_path and container_path:
                    volumes.append(f"{host_path}:{container_path}")
        if volumes:
            service_def['volumes'] = volumes

        # Restart policy
        service_def['restart'] = 'unless-stopped'

        # Convert to YAML
        yaml_output = yaml.dump(compose, default_flow_style=False, sort_keys=False, indent=2)

        # Add header comment
        header = f"# docker-compose.yml for service: {service_name}\n"
        header += f"# Generated by Docker Helper on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        compose_content = header + yaml_output

        # Show file save dialog
        save_dialog = Gtk.FileChooserDialog(
            title=f"Save docker-compose.yml for '{service_name}'",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE
        )
        save_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        save_dialog.set_current_name("docker-compose.yml")
        save_dialog.set_do_overwrite_confirmation(True)

        # Add file filter
        filter_yaml = Gtk.FileFilter()
        filter_yaml.set_name("YAML files")
        filter_yaml.add_pattern("*.yml")
        filter_yaml.add_pattern("*.yaml")
        save_dialog.add_filter(filter_yaml)

        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        save_dialog.add_filter(filter_all)

        response = save_dialog.run()

        if response == Gtk.ResponseType.OK:
            filepath = save_dialog.get_filename()
            compose_dir = os.path.dirname(filepath)
            save_dialog.destroy()

            # Write to file
            try:
                with open(filepath, 'w') as f:
                    f.write(compose_content)

                self.textbuffer.set_text(
                    f"✓ Saved docker-compose.yml for '{service_name}'\n"
                    f"✓ File saved: {filepath}\n"
                )

                # Ask if user wants to deploy
                deploy_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=f"Deploy '{service_name}' now?",
                )
                deploy_dialog.format_secondary_text(
                    f"The docker-compose.yml file has been saved to:\n{filepath}\n\n"
                    f"Would you like to create the container from this compose file now?\n\n"
                    f"This will run: docker-compose -f {os.path.basename(filepath)} up -d"
                )

                deploy_response = deploy_dialog.run()
                deploy_dialog.destroy()

                if deploy_response == Gtk.ResponseType.YES:
                    # Deploy using docker-compose
                    try:
                        result = subprocess.run(
                            ['docker-compose', '-f', filepath, 'up', '-d'],
                            cwd=compose_dir,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )

                        if result.returncode == 0:
                            output = result.stdout if result.stdout else "Container created successfully"
                            self.textbuffer.set_text(
                                f"✓ Saved docker-compose.yml: {filepath}\n"
                                f"✓ Deployed '{service_name}' successfully!\n\n"
                                f"Output:\n{output}"
                            )
                            return "deployed"
                        else:
                            error_msg = result.stderr if result.stderr else result.stdout
                            self.textbuffer.set_text(
                                f"✓ Saved docker-compose.yml: {filepath}\n"
                                f"✗ Error deploying container:\n{error_msg}"
                            )
                            self.show_error_dialog(f"Error deploying container:\n{error_msg}")
                            return "saved"

                    except FileNotFoundError:
                        self.show_error_dialog(
                            "docker-compose command not found.\n\n"
                            "Please install docker-compose:\n"
                            "- Ubuntu/Debian: sudo apt install docker-compose\n"
                            "- Or use Docker Compose V2: docker compose"
                        )
                        return "saved"
                    except subprocess.TimeoutExpired:
                        self.show_error_dialog("docker-compose command timed out after 120 seconds")
                        return "saved"
                    except Exception as e:
                        self.show_error_dialog(f"Error running docker-compose: {str(e)}")
                        return "saved"
                else:
                    # User chose not to deploy
                    return "saved"

            except Exception as e:
                self.show_error_dialog(f"Error writing file: {str(e)}")
                return "cancelled"
        else:
            save_dialog.destroy()
            return "cancelled"

    def on_uninstall_clicked(self, widget):
        self.run_command(core.uninstall_service)

    def on_start_clicked(self, widget):
        self.run_command(core.start_service)

    def on_stop_clicked(self, widget):
        self.run_command(core.stop_service)

    def on_restart_clicked(self, widget):
        self.run_command(core.restart_service)

    def on_status_clicked(self, widget):
        selected_services = self.get_selected_services()
        if not selected_services:
            # If no services are selected, get status for all installed services
            output = core.get_status(self.client, [])
        else:
            output = core.get_status(self.client, selected_services)
        self.textbuffer.set_text(output)

    def on_update_clicked(self, widget):
        self.run_command(core.update_service)

    def on_test_clicked(self, widget):
        output = core.test_container(self.client)
        self.textbuffer.set_text(output)

    def on_refresh_clicked(self, widget):
        self.update_service_list()
        self.update_running_container_view()

    def show_container_file_browser(self, parent_dialog, container_id, container_name):
        """Show a file browser for the container's filesystem"""
        import subprocess

        dialog = Gtk.Dialog(
            title=f"Browse Files in {container_name}",
            transient_for=parent_dialog,
            flags=0
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        select_button = dialog.add_button("Select", Gtk.ResponseType.OK)
        select_button.get_style_context().add_class('suggested-action')
        dialog.set_default_size(700, 500)

        content_area = dialog.get_content_area()
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)

        # Current path display
        path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        path_label = Gtk.Label(label="Current path:", xalign=0)
        path_box.pack_start(path_label, False, False, 0)

        current_path_entry = Gtk.Entry()
        current_path_entry.set_text("/")
        current_path_entry.set_hexpand(True)
        path_box.pack_start(current_path_entry, True, True, 0)

        # Go button to navigate to typed path
        go_button = Gtk.Button(label="Go")
        path_box.pack_start(go_button, False, False, 0)

        path_box.set_margin_bottom(8)
        content_area.pack_start(path_box, False, False, 0)

        # File list
        file_store = Gtk.ListStore(str, str, str)  # name, type, full_path
        file_treeview = Gtk.TreeView(model=file_store)
        file_treeview.set_headers_visible(True)

        # Name column
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn("Name", name_renderer, text=0)
        name_column.set_expand(True)
        file_treeview.append_column(name_column)

        # Type column
        type_renderer = Gtk.CellRendererText()
        type_column = Gtk.TreeViewColumn("Type", type_renderer, text=1)
        type_column.set_fixed_width(100)
        file_treeview.append_column(type_column)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.add(file_treeview)
        content_area.pack_start(scrolled, True, True, 0)

        def list_directory(path):
            """List files in the specified directory"""
            file_store.clear()

            try:
                # Use docker exec to list directory contents
                # Use ls -1Ap to get one file per line, with / for dirs, without . and ..
                cmd = ['docker', 'exec', container_id, 'ls', '-1Ap', path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode != 0:
                    self.show_error_dialog(f"Cannot access path: {path}\n{result.stderr}")
                    return

                lines = result.stdout.strip().split('\n')

                # Add parent directory entry if not at root
                if path != '/':
                    parent_path = os.path.dirname(path.rstrip('/'))
                    if not parent_path:
                        parent_path = '/'
                    file_store.append(['..', 'Directory', parent_path])

                for line in lines:
                    if not line or line == './':
                        continue

                    name = line.rstrip('/')
                    is_dir = line.endswith('/')

                    full_path = os.path.join(path, name)
                    if path.endswith('/'):
                        full_path = path + name

                    file_type = 'Directory' if is_dir else 'File'
                    display_name = name + '/' if is_dir else name

                    file_store.append([display_name, file_type, full_path])

            except subprocess.TimeoutExpired:
                self.show_error_dialog("Listing directory timed out.")
            except Exception as e:
                self.show_error_dialog(f"Error listing directory: {str(e)}")

        def on_row_activated(treeview, path, column):
            """Handle double-click on a file/directory"""
            model = treeview.get_model()
            tree_iter = model.get_iter(path)
            item_type = model.get_value(tree_iter, 1)
            full_path = model.get_value(tree_iter, 2)

            if item_type == 'Directory':
                current_path_entry.set_text(full_path)
                list_directory(full_path)

        def on_go_clicked(button):
            """Navigate to the path in the entry"""
            path = current_path_entry.get_text().strip()
            if not path:
                path = '/'
            list_directory(path)

        file_treeview.connect("row-activated", on_row_activated)
        go_button.connect("clicked", on_go_clicked)

        # Initial directory listing
        list_directory('/')

        dialog.show_all()
        response = dialog.run()

        selected_path = None
        if response == Gtk.ResponseType.OK:
            selection = file_treeview.get_selection()
            model, tree_iter = selection.get_selected()
            if tree_iter:
                selected_path = model.get_value(tree_iter, 2)

        dialog.destroy()
        return selected_path

    def export_files_from_container(self, container_id, container_name):
        """Export files or folders from a container to the host"""
        import subprocess

        # Dialog to get container path
        dialog = Gtk.Dialog(
            title=f"Export Files from {container_name}",
            transient_for=self,
            flags=0
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        export_button = dialog.add_button("Export", Gtk.ResponseType.OK)
        export_button.get_style_context().add_class('suggested-action')
        dialog.set_default_size(550, 200)

        content_area = dialog.get_content_area()
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)

        # Instructions
        instructions = Gtk.Label()
        instructions.set_markup("<b>Export files or folders from container to host</b>")
        instructions.set_xalign(0)
        instructions.set_margin_bottom(8)
        content_area.pack_start(instructions, False, False, 0)

        # Container path input
        container_path_label = Gtk.Label(label="Container path (file or folder):", xalign=0)
        content_area.pack_start(container_path_label, False, False, 0)

        container_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        container_path_entry = Gtk.Entry()
        container_path_entry.set_placeholder_text("e.g., /app/data or /etc/nginx/nginx.conf")
        container_path_entry.set_hexpand(True)
        container_path_box.pack_start(container_path_entry, True, True, 0)

        # Browse container files button
        browse_container_button = Gtk.Button()
        browse_container_icon = Gtk.Image.new_from_icon_name("folder-symbolic", Gtk.IconSize.BUTTON)
        browse_container_button.add(browse_container_icon)
        browse_container_button.set_tooltip_text("Browse container filesystem")

        def on_browse_container_clicked(button):
            selected_path = self.show_container_file_browser(dialog, container_id, container_name)
            if selected_path:
                container_path_entry.set_text(selected_path)

        browse_container_button.connect("clicked", on_browse_container_clicked)
        container_path_box.pack_start(browse_container_button, False, False, 0)

        container_path_box.set_margin_bottom(12)
        content_area.pack_start(container_path_box, False, False, 0)

        # Host destination folder input
        host_path_label = Gtk.Label(label="Save to host folder:", xalign=0)
        content_area.pack_start(host_path_label, False, False, 0)

        host_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        host_path_entry = Gtk.Entry()
        host_path_entry.set_text(os.path.expanduser("~"))
        host_path_entry.set_hexpand(True)
        host_path_box.pack_start(host_path_entry, True, True, 0)

        # Browse button
        browse_button = Gtk.Button()
        browse_icon = Gtk.Image.new_from_icon_name("folder-open-symbolic", Gtk.IconSize.BUTTON)
        browse_button.add(browse_icon)
        browse_button.set_tooltip_text("Browse for destination folder")

        def on_browse_clicked(button):
            browse_dialog = Gtk.FileChooserDialog(
                title="Select Destination Folder",
                transient_for=dialog,
                action=Gtk.FileChooserAction.SELECT_FOLDER
            )
            browse_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            browse_dialog.add_button("Select", Gtk.ResponseType.OK)

            current_path = host_path_entry.get_text()
            if current_path and os.path.exists(current_path):
                browse_dialog.set_current_folder(current_path)

            response = browse_dialog.run()
            if response == Gtk.ResponseType.OK:
                host_path_entry.set_text(browse_dialog.get_filename())
            browse_dialog.destroy()

        browse_button.connect("clicked", on_browse_clicked)
        host_path_box.pack_start(browse_button, False, False, 0)
        content_area.pack_start(host_path_box, False, False, 0)

        # Archive option
        archive_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        archive_box.set_margin_top(12)

        archive_check = Gtk.CheckButton(label="Create archive of exported folder")
        archive_check.set_active(False)
        archive_box.pack_start(archive_check, False, False, 0)

        # Archive format dropdown
        format_label = Gtk.Label(label="Format:", xalign=0)
        archive_box.pack_start(format_label, False, False, 0)

        format_combo = Gtk.ComboBoxText()
        format_combo.append_text("tar.gz")
        format_combo.append_text("zip")
        format_combo.set_active(0)
        format_combo.set_sensitive(False)
        archive_box.pack_start(format_combo, False, False, 0)

        def on_archive_toggled(checkbox):
            format_combo.set_sensitive(checkbox.get_active())

        archive_check.connect("toggled", on_archive_toggled)
        content_area.pack_start(archive_box, False, False, 0)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            container_path = container_path_entry.get_text().strip()
            host_path = host_path_entry.get_text().strip()
            create_archive = archive_check.get_active()
            archive_format = format_combo.get_active_text()

            if not container_path:
                dialog.destroy()
                self.show_error_dialog("Please specify a container path to export.")
                return

            if not host_path or not os.path.exists(host_path):
                dialog.destroy()
                self.show_error_dialog("Please specify a valid host destination folder.")
                return

            dialog.destroy()

            # Execute docker cp command
            try:
                cmd = ['docker', 'cp', f'{container_id}:{container_path}', host_path]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    # Success
                    exported_name = os.path.basename(container_path)
                    final_path = os.path.join(host_path, exported_name)

                    # Check if we need to create an archive
                    archive_path = None
                    if create_archive and os.path.isdir(final_path):
                        import tarfile
                        import zipfile
                        import shutil
                        from datetime import datetime

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                        if archive_format == "tar.gz":
                            archive_path = os.path.join(host_path, f"{exported_name}_{timestamp}.tar.gz")
                            with tarfile.open(archive_path, "w:gz") as tar:
                                tar.add(final_path, arcname=exported_name)
                        elif archive_format == "zip":
                            archive_path = os.path.join(host_path, f"{exported_name}_{timestamp}.zip")
                            shutil.make_archive(archive_path.replace('.zip', ''), 'zip', final_path)

                        # Remove the original exported folder after archiving
                        if archive_path and os.path.exists(archive_path):
                            shutil.rmtree(final_path)
                            final_path = archive_path

                    success_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="Export Successful",
                    )

                    if archive_path:
                        success_dialog.format_secondary_text(
                            f"Exported from container:\n{container_path}\n\n"
                            f"Archived to:\n{final_path}"
                        )
                    else:
                        success_dialog.format_secondary_text(
                            f"Exported from container:\n{container_path}\n\n"
                            f"To host location:\n{final_path}"
                        )

                    success_dialog.run()
                    success_dialog.destroy()

                    if archive_path:
                        self.textbuffer.set_text(f"✓ Exported and archived {container_path} from {container_name} to {final_path}")
                    else:
                        self.textbuffer.set_text(f"✓ Exported {container_path} from {container_name} to {final_path}")
                else:
                    # Error
                    error_msg = result.stderr if result.stderr else result.stdout
                    self.show_error_dialog(f"Export failed:\n{error_msg}")
                    self.textbuffer.set_text(f"✗ Export failed: {error_msg}")

            except subprocess.TimeoutExpired:
                self.show_error_dialog("Export operation timed out after 60 seconds.")
            except Exception as e:
                self.show_error_dialog(f"Export error: {str(e)}")
        else:
            dialog.destroy()

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def main():
    win = DockerManagerWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
