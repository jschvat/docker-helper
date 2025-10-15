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
        """Filter containers based on search text"""
        search_text = self.container_search_entry.get_text().lower()
        if not search_text:
            return True

        # Search in ID, Name, Status, Image columns
        container_id = model.get_value(iter, 0).lower()
        container_name = model.get_value(iter, 1).lower()
        status = model.get_value(iter, 2).lower()
        image = model.get_value(iter, 3).lower()

        return (search_text in container_id or
                search_text in container_name or
                search_text in status or
                search_text in image)

    def on_container_search_changed(self, entry):
        """Handle container search text changes"""
        self.running_container_filter.refilter()

    def create_running_container_view(self, container):
        # Create container box with header
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Add section header with consistent height and combobox
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.get_style_context().add_class('section-header')
        header_box.set_size_request(-1, 40)  # Fixed height for alignment

        header_label = Gtk.Label()
        header_label.set_markup('<b>Docker Resources</b>')
        header_label.set_xalign(0)
        header_label.set_margin_start(12)
        header_box.pack_start(header_label, False, False, 0)

        # View selector combobox
        self.view_combo = Gtk.ComboBoxText()
        self.view_combo.append_text("Containers")
        self.view_combo.append_text("Networks")
        self.view_combo.append_text("Volumes")
        self.view_combo.append_text("Images")
        self.view_combo.append_text("Stacks")
        self.view_combo.set_active(0)  # Default to Containers
        self.view_combo.connect("changed", self.on_view_changed)
        self.view_combo.set_margin_start(8)
        header_box.pack_start(self.view_combo, False, False, 0)

        # Add count badge
        self.resource_count_label = Gtk.Label()
        self.resource_count_label.set_markup('<span size="small">0</span>')
        self.resource_count_label.set_margin_end(12)
        header_box.pack_start(self.resource_count_label, False, False, 0)

        vbox.pack_start(header_box, False, False, 0)

        # Create search box with consistent alignment
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(8)

        self.resource_search_entry = Gtk.SearchEntry()
        self.resource_search_entry.set_placeholder_text("Search...")
        self.resource_search_entry.connect("search-changed", self.on_resource_search_changed)
        search_box.pack_start(self.resource_search_entry, True, True, 0)
        vbox.pack_start(search_box, False, False, 0)

        # Create Gtk.Stack to hold different views
        self.view_stack = Gtk.Stack()
        self.view_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.view_stack.set_transition_duration(150)

        # Create scrolled window for the stack
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_bottom(8)

        # 1. Containers View
        self.container_store = Gtk.ListStore(str, str, str, str, str, str, str)
        self.container_filter = self.container_store.filter_new()
        self.container_filter.set_visible_func(self.resource_filter_func, "container")

        self.container_treeview = Gtk.TreeView(model=self.container_filter)
        self.container_treeview.connect("row-activated", self.on_container_activated)
        self.container_treeview.set_tooltip_text("Double-click a container to view details")

        # Define columns with their properties
        column_configs = [
            ("ID", 0, 70, False),
            ("Name", 1, 120, False),
            ("Status", 2, 70, False),
            ("Image", 3, 120, False),  # Reduced from 180
            ("Uptime", 4, 80, False),
            ("Ports", 5, 100, False),
            ("Network", 6, 100, False),
        ]

        for col_title, col_index, fixed_width, expand in column_configs:
            renderer = Gtk.CellRendererText()

            # Enable wrapping for longer text fields
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

            treeview.append_column(column)

        # Add Actions column with clickable text buttons (6 buttons)
        actions_column = Gtk.TreeViewColumn("Actions")
        actions_column.set_fixed_width(84)  # Expanded to fit 6 buttons
        actions_column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)

        # Use six separate text renderers for the buttons
        start_renderer = Gtk.CellRendererText()
        start_renderer.set_property('text', '▶')
        start_renderer.set_property('xalign', 0.5)
        start_renderer.set_property('foreground', '#10b981')  # Green
        start_renderer.set_property('weight', 700)
        start_renderer.set_property('size-points', 12)
        actions_column.pack_start(start_renderer, True)

        restart_renderer = Gtk.CellRendererText()
        restart_renderer.set_property('text', '↻')
        restart_renderer.set_property('xalign', 0.5)
        restart_renderer.set_property('foreground', '#667eea')  # Blue
        restart_renderer.set_property('weight', 700)
        restart_renderer.set_property('size-points', 12)
        actions_column.pack_start(restart_renderer, True)

        stop_renderer = Gtk.CellRendererText()
        stop_renderer.set_property('text', '⏹')
        stop_renderer.set_property('xalign', 0.5)
        stop_renderer.set_property('foreground', '#f59e0b')  # Orange
        stop_renderer.set_property('weight', 700)
        stop_renderer.set_property('size-points', 12)
        actions_column.pack_start(stop_renderer, True)

        logs_renderer = Gtk.CellRendererText()
        logs_renderer.set_property('text', '📋')
        logs_renderer.set_property('xalign', 0.5)
        logs_renderer.set_property('foreground', '#06b6d4')  # Cyan
        logs_renderer.set_property('weight', 700)
        logs_renderer.set_property('size-points', 11)
        actions_column.pack_start(logs_renderer, True)

        backup_renderer = Gtk.CellRendererText()
        backup_renderer.set_property('text', '💾')
        backup_renderer.set_property('xalign', 0.5)
        backup_renderer.set_property('foreground', '#8b5cf6')  # Purple
        backup_renderer.set_property('weight', 700)
        backup_renderer.set_property('size-points', 11)
        actions_column.pack_start(backup_renderer, True)

        remove_renderer = Gtk.CellRendererText()
        remove_renderer.set_property('text', '🗑')
        remove_renderer.set_property('xalign', 0.5)
        remove_renderer.set_property('foreground', '#ef4444')  # Red
        remove_renderer.set_property('weight', 700)
        remove_renderer.set_property('size-points', 11)
        actions_column.pack_start(remove_renderer, True)

        treeview.append_column(actions_column)

        # Enable tooltips for the treeview
        treeview.set_has_tooltip(True)
        treeview.connect("query-tooltip", self.on_container_query_tooltip)

        # Add button press event handler for action buttons
        treeview.connect("button-press-event", self.on_container_button_press)

        # Store the treeview for button callbacks
        self.container_treeview = treeview

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(treeview)
        scrolled_window.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolled_window.set_margin_start(12)
        scrolled_window.set_margin_end(12)
        scrolled_window.set_margin_bottom(8)

        vbox.pack_start(scrolled_window, True, True, 0)
        container.add2(vbox)
        self.update_running_container_view()

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

        # Update count badge
        count = len(running_containers)
        self.container_count_label.set_markup(f'<span size="small">{count} running</span>')

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

        widgets = {"variables": {}, "ports": {}}
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
            elif var_type == 'number':
                adj = Gtk.Adjustment(value=var.get('default', 0), lower=0, upper=65535, step_incr=1)
                input_widget = Gtk.SpinButton.new(adj, 1, 0)
            else: # Default to string/path
                input_widget = Gtk.Entry()
                input_widget.set_text(str(var.get('default', '')))

            grid.attach(label, 0, current_row, 1, 1)
            grid.attach(input_widget, 1, current_row, 1, 1)
            widgets["variables"][var['name']] = input_widget
            current_row += 1

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

        dialog.show_all()

        # Dialog loop to handle Preview button
        while True:
            response = dialog.run()

            # Collect config values
            config_values = {"variables": {}, "ports": {}}
            for name, widget in widgets["variables"].items():
                if isinstance(widget, Gtk.CheckButton):
                    config_values["variables"][name] = widget.get_active()
                elif isinstance(widget, Gtk.SpinButton):
                    config_values["variables"][name] = widget.get_value_as_int()
                else:
                    config_values["variables"][name] = widget.get_text()

            for name, widget in widgets["ports"].items():
                config_values["ports"][name] = widget.get_value_as_int()

            if response == Gtk.ResponseType.HELP:
                # Preview Command button clicked
                command = core.install_service(service_config, config_values)
                self.show_command_preview_dialog(command)
                # Continue loop to keep dialog open
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
