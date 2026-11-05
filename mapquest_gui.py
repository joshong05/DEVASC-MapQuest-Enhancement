"""Desktop route planner with an interactive map. Run with: python mapquest_gui.py"""

import queue
import threading
from datetime import datetime, timedelta

import customtkinter as ctk
import tkintermapview
from PIL import Image, ImageTk

import routing_service as service
from routing_service import (
    Location, RoutingError, format_distance, format_duration, format_trip,
    get_route_details, reverse_geocode, search_locations,
)


APP_TITLE = "Quatro Kantos Route Planner"
DEFAULT_CENTER = (14.5995, 120.9842)  # Manila
DEFAULT_ZOOM = 11

FONT_FAMILY = "Segoe UI"

# (light, dark) colour pairs, used by every customtkinter widget.
BG = ("#F4F6FA", "#0F141B")
SURFACE = ("#FFFFFF", "#171E28")
SURFACE_ALT = ("#EEF1F6", "#1F2833")
BORDER = ("#DDE2EA", "#2A3441")
TEXT = ("#111827", "#E8ECF2")
MUTED = ("#6B7280", "#8B95A5")
PRIMARY = ("#2563EB", "#3B82F6")
PRIMARY_HOVER = ("#1D4ED8", "#2563EB")
HOVER = ("#E8EEFB", "#223047")
SELECTED = ("#DBE6FE", "#1E3A66")
DANGER = ("#DC2626", "#F87171")
SUCCESS = ("#15803D", "#4ADE80")

START_COLOR = ("#16A34A", "#14532D")   # marker outside, inner circle
END_COLOR = ("#DC2626", "#7F1D1D")
CANDIDATE_COLOR = ("#64748B", "#1E293B")
ROUTE_CASING = "#1E3A8A"
ROUTE_LINE = "#3B82F6"
ROUTE_HIGHLIGHT = "#F59E0B"

MODES = {"Car": "car", "Bike": "bike", "Walk": "foot"}
UNITS = {"Miles": "miles", "Kilometers": "kilometers"}

ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/{}/MapServer/tile/{{z}}/{{y}}/{{x}}"
BASEMAPS = {  # name: (tile URL, max zoom, attribution); all free to use without a key
    "Streets": (ESRI.format("World_Street_Map"), 19, "Tiles © Esri"),
    "Light": (ESRI.format("Canvas/World_Light_Gray_Base"), 16, "Tiles © Esri"),
    "Dark": (ESRI.format("Canvas/World_Dark_Gray_Base"), 16, "Tiles © Esri"),
    "Satellite": (ESRI.format("World_Imagery"), 19, "Imagery © Esri"),
    "Terrain": (ESRI.format("World_Topo_Map"), 19, "Tiles © Esri"),
}

# GraphHopper instruction "sign" values mapped to arrow glyphs.
TURN_GLYPHS = {
    -98: "↶", -8: "↶", -7: "↖", -3: "↙", -2: "←", -1: "↖",
    0: "↑", 1: "↗", 2: "→", 3: "↘", 4: "◉", 5: "•",
    6: "↻", 7: "↗", 8: "↷",
}


def font(size=13, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def padded_bounds(points, padding=0.18, minimum_span=0.008):
    """Bounding box for fit_bounding_box: ((north, west), (south, east)), never zero-sized."""
    lats = [lat for lat, _ in points]
    lngs = [lng for _, lng in points]
    lat_span = max(max(lats) - min(lats), minimum_span)
    lng_span = max(max(lngs) - min(lngs), minimum_span)
    mid_lat, mid_lng = (max(lats) + min(lats)) / 2, (max(lngs) + min(lngs)) / 2
    half_lat, half_lng = lat_span * (0.5 + padding), lng_span * (0.5 + padding)
    north, south = min(mid_lat + half_lat, 85), max(mid_lat - half_lat, -85)
    west, east = max(mid_lng - half_lng, -180), min(mid_lng + half_lng, 180)
    return (north, west), (south, east)


class TaskRunner:
    """Runs blocking API calls off the UI thread and delivers results back on it."""

    def __init__(self, widget):
        self.widget = widget
        self.results = queue.Queue()
        self.widget.after(60, self._poll)

    def run(self, work, on_success, on_error):
        def target():
            try:
                outcome = (on_success, work())
            except RoutingError as error:
                outcome = (on_error, str(error))
            except Exception as error:  # keep the window alive on unexpected failures
                outcome = (on_error, f"Unexpected error: {error}")
            self.results.put(outcome)

        threading.Thread(target=target, daemon=True).start()

    def _poll(self):
        try:
            while True:
                callback, value = self.results.get_nowait()
                callback(value)
        except queue.Empty:
            pass
        if self.widget.winfo_exists():
            self.widget.after(60, self._poll)


class LocationField(ctk.CTkFrame):
    """A search box that lists geocoding matches and keeps the confirmed choice."""

    def __init__(self, master, app, label, placeholder, colour):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.label = label
        self.selected = None
        self.matches = []
        self._request = 0

        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="●", text_color=colour[0], font=font(16), width=18).grid(
            row=0, column=0, padx=(0, 8))
        self.entry = ctk.CTkEntry(
            self, placeholder_text=placeholder, height=40, corner_radius=8, border_width=1,
            border_color=BORDER, fg_color=SURFACE, text_color=TEXT, font=font(13))
        self.entry.grid(row=0, column=1, sticky="ew")
        self.entry.bind("<Return>", lambda _event: self.search())
        self.entry.bind("<KeyRelease>", self._on_edit)

        self.search_button = ctk.CTkButton(
            self, text="Search", width=70, height=40, corner_radius=8, font=font(12, "bold"),
            fg_color=SURFACE_ALT, hover_color=HOVER, text_color=TEXT, command=self.search)
        self.search_button.grid(row=0, column=2, padx=(6, 0))

        self.note = ctk.CTkLabel(self, text="", text_color=MUTED, font=font(11), anchor="w", height=16,
                                 justify="left", wraplength=300)
        self.note.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(2, 0))

        self.suggestions = ctk.CTkFrame(self, fg_color=SURFACE, border_color=BORDER, border_width=1,
                                        corner_radius=8)

    # --- searching -------------------------------------------------------
    def search(self):
        query = self.entry.get().strip()
        if not query:
            self.set_note(f"Type a {self.label.lower()} to search.", DANGER)
            self.entry.focus_set()
            return
        self._request += 1
        request = self._request
        self.search_button.configure(state="disabled", text="...")
        self.set_note("Searching...", MUTED)
        self.app.set_busy(True, f"Searching for “{query}”")
        near = self.app.map.get_position()  # rank places near the visible map area first
        self.app.tasks.run(
            lambda: search_locations(query, near),
            lambda matches: self._show_matches(request, query, matches),
            lambda message: self._search_failed(request, message))

    def _search_failed(self, request, message):
        if request != self._request:
            return
        self.search_button.configure(state="normal", text="Search")
        self.app.set_busy(False)
        self.set_note(message, DANGER)
        self.app.show_error(message)

    def _show_matches(self, request, query, matches):
        if request != self._request:
            return
        self.search_button.configure(state="normal", text="Search")
        self.app.set_busy(False)
        self.app._update_attribution()
        self.matches = matches
        self._clear_suggestions()
        if not matches:
            self.set_note("No matches. Check spelling or add a city or country.", DANGER)
            self.app.show_error(f"Location not found: {query}")
            return
        self.set_note(f"{len(matches)} match{'es' if len(matches) > 1 else ''} — choose one below or on the map.",
                      MUTED)
        for number, match in enumerate(matches, 1):
            button = ctk.CTkButton(
                self.suggestions, text=f"{number}.  {match.name}\n      {match.lat:.5f}, {match.lng:.5f}",
                anchor="w", height=46, corner_radius=6, font=font(12), fg_color="transparent",
                hover_color=HOVER, text_color=TEXT, command=lambda m=match: self.select(m))
            button.pack(fill="x", padx=4, pady=(4 if number == 1 else 0, 4 if number == len(matches) else 0))
        self.suggestions.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(4, 0))
        self.app.show_candidates(self, matches)
        self.app.set_status(f"Pick the correct {self.label.lower()} from the list.")

    def _clear_suggestions(self):
        for child in self.suggestions.winfo_children():
            child.destroy()
        self.suggestions.grid_remove()

    # --- selection -------------------------------------------------------
    def select(self, location):
        self._request += 1  # ignore any search still in flight
        self.search_button.configure(state="normal", text="Search")
        self.selected = location
        self.matches = []
        self._clear_suggestions()
        self.entry.delete(0, "end")
        self.entry.insert(0, location.name)
        self.entry.configure(border_color=BORDER)
        self.set_note(f"✓  {location.lat:.5f}, {location.lng:.5f}", SUCCESS)
        self.app.location_changed()

    def clear(self):
        self._request += 1
        self.search_button.configure(state="normal", text="Search")
        self.selected = None
        self.matches = []
        self._clear_suggestions()
        self.entry.delete(0, "end")
        self.set_note("")

    def _on_edit(self, event):
        if event.keysym in ("Return", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
        if self.selected and self.entry.get().strip() != self.selected.name:
            self.selected = None
            self.set_note("Press Enter to search.", MUTED)
            self.app.location_changed()

    def set_note(self, text, colour=MUTED):
        self.note.configure(text=text, text_color=colour)


class DirectionsList(ctk.CTkScrollableFrame):
    def __init__(self, master, on_select):
        super().__init__(master, fg_color="transparent", corner_radius=0,
                         scrollbar_button_color=BORDER, scrollbar_button_hover_color=MUTED)
        self.on_select = on_select
        self.rows = []
        self.active = None
        self.grid_columnconfigure(0, weight=1)

    def show(self, route, unit):
        for row in self.rows:
            row.destroy()
        self.rows = []
        self.active = None
        for index, step in enumerate(route.steps):
            row = ctk.CTkFrame(self, fg_color="transparent", corner_radius=8, cursor="hand2")
            row.grid(row=index, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(2, weight=1)
            badge = ctk.CTkLabel(row, text=TURN_GLYPHS.get(step.sign, "↑"), width=30, height=30,
                                 corner_radius=15, fg_color=SURFACE_ALT, text_color=PRIMARY,
                                 font=ctk.CTkFont(family="Segoe UI Symbol", size=15, weight="bold"))
            badge.grid(row=0, column=0, rowspan=2, padx=(6, 10), pady=8)
            text = ctk.CTkLabel(row, text=step.text, anchor="w", justify="left", wraplength=230,
                                text_color=TEXT, font=font(12))
            text.grid(row=0, column=2, sticky="ew", pady=(8, 0))
            detail = format_distance(step.distance, unit) if step.distance else "Arrive"
            meta = ctk.CTkLabel(row, text=f"Step {index + 1}  ·  {detail}", anchor="w",
                                text_color=MUTED, font=font(11))
            meta.grid(row=1, column=2, sticky="ew", pady=(0, 8))
            for widget in (row, badge, text, meta):
                widget.bind("<Button-1>", lambda _e, i=index: self.activate(i))
                widget.bind("<Enter>", lambda _e, r=row: self._hover(r, True))
                widget.bind("<Leave>", lambda _e, r=row: self._hover(r, False))
            self.rows.append(row)
        self._parent_canvas.yview_moveto(0)

    def clear(self):
        for row in self.rows:
            row.destroy()
        self.rows = []
        self.active = None

    def activate(self, index):
        if self.active is not None and self.active < len(self.rows):
            self.rows[self.active].configure(fg_color="transparent")
        self.active = index
        self.rows[index].configure(fg_color=SELECTED)
        self.on_select(index)

    def _hover(self, row, inside):
        if self.active is not None and self.rows[self.active] is row:
            return
        row.configure(fg_color=HOVER if inside else "transparent")


class Segmented(ctk.CTkSegmentedButton):
    """Segmented control with white text on the selected segment."""

    def _select_button_by_value(self, value):
        super()._select_button_by_value(value)
        self._buttons_dict[value].configure(text_color="#FFFFFF")

    def _unselect_button_by_value(self, value):
        super()._unselect_button_by_value(value)
        if value in self._buttons_dict:
            self._buttons_dict[value].configure(text_color=TEXT)


class StatTile(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color=SURFACE_ALT, corner_radius=10)
        ctk.CTkLabel(self, text=title.upper(), text_color=MUTED, font=font(10, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(10, 0))
        self.value = ctk.CTkLabel(self, text="—", text_color=TEXT, font=font(18, "bold"), anchor="w")
        self.value.pack(fill="x", padx=12, pady=(0, 10))

    def set(self, text):
        self.value.configure(text=text)


class RoutePlannerApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title(APP_TITLE)
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{min(1360, screen_w - 60)}x{min(860, screen_h - 100)}+20+20")
        self.minsize(min(1000, screen_w - 60), min(620, screen_h - 100))
        if screen_h < 900 and self._windowingsystem == "win32":
            self.after(0, lambda: self.state("zoomed"))  # use the whole screen on laptops

        self.tasks = TaskRunner(self)
        self.route = None
        self.route_endpoints = None
        self.route_paths = []
        self.highlight_path = None
        self.markers = {}
        self.candidate_markers = []
        self._route_request = 0

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_map()

        self.bind("<Control-Return>", lambda _e: self.find_route())
        self.bind("<Escape>", lambda _e: self.fit_view())
        self.theme_button.configure(text="☀" if ctk.get_appearance_mode() == "Dark" else "☾")
        self.set_status(f"Using {service.current_provider_name()}. Search for a start and destination, "
                        "or right-click the map.")
        self.after(150, self.origin.entry.focus_set)

    # --- layout ----------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=420, fg_color=SURFACE, corner_radius=0,
                               border_width=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(5, weight=1, minsize=170)

        # Header
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 12))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="QK", width=40, height=40, corner_radius=10, fg_color=PRIMARY,
                     text_color="#FFFFFF", font=font(15, "bold")).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ctk.CTkLabel(header, text="Route Planner", text_color=TEXT, font=font(19, "bold"), anchor="w").grid(
            row=0, column=1, sticky="ew")
        self.provider_label = ctk.CTkLabel(header, text="", text_color=MUTED, font=font(11), anchor="w")
        self.provider_label.grid(row=1, column=1, sticky="ew")
        self.theme_button = ctk.CTkButton(
            header, text="☾", width=36, height=36, corner_radius=18, fg_color=SURFACE_ALT,
            hover_color=HOVER, text_color=TEXT, font=ctk.CTkFont(family="Segoe UI Symbol", size=16),
            command=self.toggle_theme)
        self.theme_button.grid(row=0, column=2, rowspan=2)

        # Trip options
        options = ctk.CTkFrame(sidebar, fg_color="transparent")
        options.grid(row=1, column=0, sticky="ew", padx=24)
        options.grid_columnconfigure((0, 1), weight=1, uniform="options")
        self._section_label(options, "Travel mode").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self._section_label(options, "Units").grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 6))
        segmented = dict(height=34, corner_radius=8, font=font(12, "bold"), fg_color=SURFACE_ALT,
                         selected_color=PRIMARY, selected_hover_color=PRIMARY_HOVER,
                         unselected_color=SURFACE_ALT, unselected_hover_color=HOVER,
                         text_color=TEXT)
        self.mode = Segmented(options, values=list(MODES), command=self._mode_changed, **segmented)
        self.mode.set("Car")
        self.mode.grid(row=1, column=0, sticky="ew")
        self.unit = Segmented(options, values=["Miles", "Kilometers"],
                                           command=lambda _v: self._render_route(), **segmented)
        self.unit.set("Miles")
        self.unit.grid(row=1, column=1, sticky="ew", padx=(12, 0))

        # Locations
        locations = ctk.CTkFrame(sidebar, fg_color="transparent")
        locations.grid(row=2, column=0, sticky="ew", padx=24, pady=(14, 0))
        locations.grid_columnconfigure(0, weight=1)
        title_row = ctk.CTkFrame(locations, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        title_row.grid_columnconfigure(0, weight=1)
        self._section_label(title_row, "Route").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(title_row, text="⇅  Swap", width=70, height=24, corner_radius=6, font=font(11, "bold"),
                      fg_color="transparent", hover_color=HOVER, text_color=PRIMARY,
                      command=self.swap_locations).grid(row=0, column=1)
        self.origin = LocationField(locations, self, "Starting location", "Choose starting point", START_COLOR)
        self.origin.grid(row=1, column=0, sticky="ew")
        self.destination = LocationField(locations, self, "Destination", "Choose destination", END_COLOR)
        self.destination.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        # Actions
        actions = ctk.CTkFrame(sidebar, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=24, pady=(10, 0))
        actions.grid_columnconfigure(0, weight=1)
        self.route_button = ctk.CTkButton(
            actions, text="Find route", height=44, corner_radius=10, font=font(14, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#FFFFFF", command=self.find_route)
        self.route_button.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(actions, text="Clear", width=80, height=44, corner_radius=10, font=font(13, "bold"),
                      fg_color=SURFACE_ALT, hover_color=HOVER, text_color=TEXT,
                      command=self.clear_all).grid(row=0, column=1, padx=(8, 0))

        # Summary
        summary = ctk.CTkFrame(sidebar, fg_color="transparent")
        summary.grid(row=4, column=0, sticky="ew", padx=24, pady=(14, 0))
        summary.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")
        self.distance_tile = StatTile(summary, "Distance")
        self.distance_tile.grid(row=0, column=0, sticky="ew")
        self.time_tile = StatTile(summary, "Duration")
        self.time_tile.grid(row=0, column=1, sticky="ew", padx=8)
        self.arrival_tile = StatTile(summary, "Arrive by")
        self.arrival_tile.grid(row=0, column=2, sticky="ew")

        # Directions
        directions = ctk.CTkFrame(sidebar, fg_color="transparent")
        directions.grid(row=5, column=0, sticky="nsew", padx=(24, 12), pady=(14, 0))
        directions.grid_columnconfigure(0, weight=1)
        directions.grid_rowconfigure(1, weight=1)
        head = ctk.CTkFrame(directions, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=(0, 6))
        head.grid_columnconfigure(0, weight=1)
        self.directions_title = self._section_label(head, "Directions")
        self.directions_title.grid(row=0, column=0, sticky="w")
        self.copy_button = ctk.CTkButton(
            head, text="Copy", width=56, height=24, corner_radius=6, font=font(11, "bold"),
            fg_color="transparent", hover_color=HOVER, text_color=PRIMARY, state="disabled",
            command=self.copy_directions)
        self.copy_button.grid(row=0, column=1)
        self.directions = DirectionsList(directions, self.focus_step)
        self.directions.grid(row=1, column=0, sticky="nsew")
        self.empty_state = ctk.CTkLabel(
            directions, text="Your turn-by-turn directions will appear here.\n"
                             "Tip: right-click the map to drop a start or destination.",
            text_color=MUTED, font=font(12), justify="center")
        self.empty_state.grid(row=1, column=0, sticky="n", pady=30)

        # Status bar
        status = ctk.CTkFrame(sidebar, fg_color=SURFACE_ALT, corner_radius=0, height=44)
        status.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        status.grid_columnconfigure(1, weight=1)
        status.grid_propagate(False)
        self.status_dot = ctk.CTkLabel(status, text="●", width=14, text_color=SUCCESS, font=font(12))
        self.status_dot.grid(row=0, column=0, padx=(24, 6), pady=12)
        self.status = ctk.CTkLabel(status, text="Ready", text_color=MUTED, font=font(11), anchor="w",
                                   wraplength=330, justify="left")
        self.status.grid(row=0, column=1, sticky="ew", padx=(0, 16))
        self.progress = ctk.CTkProgressBar(sidebar, mode="indeterminate", height=3, corner_radius=0,
                                           progress_color=PRIMARY, fg_color=SURFACE_ALT)

    def _build_map(self):
        holder = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        holder.grid(row=0, column=1, sticky="nsew")
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(0, weight=1)

        self.map = tkintermapview.TkinterMapView(holder, corner_radius=0, bg_color=BG[0])
        self.map.grid(row=0, column=0, sticky="nsew")
        self.basemap = "Dark" if ctk.get_appearance_mode() == "Dark" else "Streets"
        self._apply_basemap(self.basemap)
        self.map.set_position(*DEFAULT_CENTER)
        self.map.set_zoom(DEFAULT_ZOOM)
        self.map.add_right_click_menu_command("Set as starting location",
                                              lambda c: self.drop_pin(self.origin, c), pass_coords=True)
        self.map.add_right_click_menu_command("Set as destination",
                                              lambda c: self.drop_pin(self.destination, c), pass_coords=True)

        # Floating toolbar over the map
        toolbar = ctk.CTkFrame(self.map, fg_color=SURFACE, bg_color=SURFACE, corner_radius=0)
        toolbar.place(relx=1.0, x=-16, y=16, anchor="ne")
        ctk.CTkLabel(toolbar, text="Map style", text_color=MUTED, font=font(11, "bold")).grid(
            row=0, column=0, padx=(12, 6), pady=8)
        self.basemap_menu = ctk.CTkOptionMenu(
            toolbar, values=list(BASEMAPS), command=self._apply_basemap, width=120, height=30,
            corner_radius=8, font=font(12), dropdown_font=font(12), fg_color=SURFACE_ALT,
            button_color=SURFACE_ALT, button_hover_color=HOVER, text_color=TEXT)
        self.basemap_menu.set(self.basemap)
        self.basemap_menu.grid(row=0, column=1, pady=8)
        self.fit_button = ctk.CTkButton(
            toolbar, text="Fit route", width=86, height=30, corner_radius=8, font=font(12, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#FFFFFF", command=self.fit_view)
        self.fit_button.grid(row=0, column=2, padx=(8, 8), pady=8)

        self.attribution = ctk.CTkLabel(self.map, text="", text_color=MUTED, fg_color=SURFACE, bg_color=SURFACE,
                                        corner_radius=0, font=font(10))
        self.attribution.place(relx=1.0, rely=1.0, x=-6, y=-6, anchor="se")
        self._update_attribution()

    def _section_label(self, master, text):
        return ctk.CTkLabel(master, text=text.upper(), text_color=MUTED, font=font(11, "bold"), anchor="w")

    # --- status ----------------------------------------------------------
    def set_status(self, text, colour=MUTED, dot=SUCCESS):
        self.status.configure(text=text, text_color=colour)
        self.status_dot.configure(text_color=dot)

    def show_error(self, message):
        self.set_status(message, DANGER, DANGER)

    def set_busy(self, busy, message=None):
        if busy:
            self.progress.grid(row=7, column=0, sticky="ew")
            self.progress.start()
            self.set_status(message or "Working...", MUTED, PRIMARY)
        else:
            self.progress.stop()
            self.progress.grid_remove()

    # --- theme & basemap -------------------------------------------------
    def toggle_theme(self):
        dark = ctk.get_appearance_mode() == "Light"
        ctk.set_appearance_mode("dark" if dark else "light")
        self.theme_button.configure(text="☀" if dark else "☾")
        if dark and self.basemap in ("Streets", "Light"):
            self.basemap_menu.set("Dark")
            self._apply_basemap("Dark")
        elif not dark and self.basemap == "Dark":
            self.basemap_menu.set("Streets")
            self._apply_basemap("Streets")

    def _apply_basemap(self, name):
        url, max_zoom, _credit = BASEMAPS[name]
        self.basemap = name
        # Placeholder shown while tiles load, tinted to match the basemap.
        shade = {"Dark": (40, 40, 40), "Satellite": (24, 28, 34)}.get(name, (232, 232, 226))
        placeholder = ImageTk.PhotoImage(Image.new("RGB", (256, 256), shade))
        self.map.empty_tile_image = self.map.not_loaded_tile_image = placeholder
        self.map.canvas.configure(bg="#%02x%02x%02x" % shade)
        self.map.set_tile_server(url, max_zoom=max_zoom)
        if hasattr(self, "attribution"):
            self._update_attribution()
            self._draw_markers()

    def _label_colour(self):
        return "#F8FAFC" if self.basemap in ("Dark", "Satellite") else "#111827"

    def _update_attribution(self):
        credit = BASEMAPS[self.basemap][2]
        if service.last_provider:
            provider = service.PROVIDER_NAMES[service.last_provider]
        else:
            provider = service.current_provider_name()
        if provider == "OpenStreetMap":
            routing = "Routing © OpenStreetMap contributors (OSRM, Nominatim)"
        else:
            routing = "Routing by GraphHopper"
        self.attribution.configure(text=f"  {credit}  ·  {routing}  ")
        self.provider_label.configure(text=f"Quatro Kantos  ·  {provider}")

    # --- map drawing -----------------------------------------------------
    def fit_points(self, points):
        if not points:
            return
        top_left, bottom_right = padded_bounds(points)
        try:
            self.map.fit_bounding_box(top_left, bottom_right)
        except ValueError:
            self.map.set_position(*points[0])

    def fit_view(self):
        if self.route:
            self.fit_points(self.route.points)
            return
        points = [(f.selected.lat, f.selected.lng) for f in (self.origin, self.destination) if f.selected]
        if len(points) == 1:
            self.map.set_position(*points[0])
            self.map.set_zoom(14)
        elif points:
            self.fit_points(points)

    def show_candidates(self, field, matches):
        self._clear_candidates()
        for number, match in enumerate(matches, 1):
            marker = self.map.set_marker(
                match.lat, match.lng, text=f"{number}. {match.name.split(',')[0]}",
                marker_color_outside=CANDIDATE_COLOR[0], marker_color_circle=CANDIDATE_COLOR[1],
                text_color=self._label_colour(), font=(FONT_FAMILY, 10, "bold"),
                command=lambda _m, f=field, loc=match: f.select(loc))
            self.candidate_markers.append(marker)
        points = [(m.lat, m.lng) for m in matches]
        if len(points) == 1:
            self.map.set_position(*points[0])
            self.map.set_zoom(13)
        else:
            self.fit_points(points)

    def _clear_candidates(self):
        for marker in self.candidate_markers:
            marker.delete()
        self.candidate_markers = []

    def _draw_markers(self):
        for marker in self.markers.values():
            marker.delete()
        self.markers = {}
        for key, field, colour in (("start", self.origin, START_COLOR), ("end", self.destination, END_COLOR)):
            if field.selected:
                self.markers[key] = self.map.set_marker(
                    field.selected.lat, field.selected.lng, text=field.selected.name.split(",")[0],
                    marker_color_outside=colour[0], marker_color_circle=colour[1],
                    text_color=self._label_colour(), font=(FONT_FAMILY, 11, "bold"))

    def _clear_route_drawing(self):
        for path in self.route_paths:
            path.delete()
        self.route_paths = []
        if self.highlight_path:
            self.highlight_path.delete()
            self.highlight_path = None

    def _draw_route(self):
        self._clear_route_drawing()
        points = list(self.route.points)
        self.route_paths.append(self.map.set_path(points, color=ROUTE_CASING, width=9))
        self.route_paths.append(self.map.set_path(points, color=ROUTE_LINE, width=5))
        self._draw_markers()  # keep markers above the line
        self.fit_points(points)

    def focus_step(self, index):
        if not self.route:
            return
        if self.highlight_path:
            self.highlight_path.delete()
            self.highlight_path = None
        points = list(self.route.step_points(index))
        if len(points) >= 2:
            self.highlight_path = self.map.set_path(points, color=ROUTE_HIGHLIGHT, width=7)
            self._draw_markers()
            self.fit_points(points)
        elif points:
            self.map.set_position(*points[0])
            self.map.set_zoom(16)
        step = self.route.steps[index]
        self.set_status(f"Step {index + 1}: {step.text}")

    # --- actions ---------------------------------------------------------
    def location_changed(self):
        self._clear_candidates()
        if self.route and self.route_endpoints != (self.origin.selected, self.destination.selected):
            self._reset_route()
        self._draw_markers()
        selected = [f for f in (self.origin, self.destination) if f.selected]
        if len(selected) == 2:
            self.set_status("Both locations confirmed. Press Find route (Ctrl+Enter).", MUTED, SUCCESS)
            self.fit_view()
        elif selected:
            self.fit_view()
            missing = self.destination if self.origin.selected else self.origin
            self.set_status(f"Now choose the {missing.label.lower()}.")
            if not missing.entry.get().strip():
                missing.entry.focus_set()

    def drop_pin(self, field, coords):
        lat, lng = coords
        self.set_busy(True, "Looking up the dropped pin...")

        def done(location):
            self.set_busy(False)
            field.select(location)

        def failed(message):
            self.set_busy(False)
            field.select(Location(f"Dropped pin {lat:.5f}, {lng:.5f}", lat, lng))
            self.set_status(f"Pin placed; place name unavailable ({message})", MUTED, PRIMARY)

        self.tasks.run(lambda: reverse_geocode(lat, lng), done, failed)

    def swap_locations(self):
        had_route = self.route is not None
        start, end = self.origin.selected, self.destination.selected
        start_text, end_text = self.origin.entry.get(), self.destination.entry.get()
        self.origin.clear()
        self.destination.clear()
        for field, location, text in ((self.origin, end, end_text), (self.destination, start, start_text)):
            if location:
                field.select(location)
            elif text:
                field.entry.insert(0, text)
        self._draw_markers()
        if had_route and start and end:
            self.find_route()

    def clear_all(self):
        self.origin.clear()
        self.destination.clear()
        self._clear_candidates()
        self._reset_route()
        self._draw_markers()
        self.map.set_position(*DEFAULT_CENTER)
        self.map.set_zoom(DEFAULT_ZOOM)
        self.set_status("Cleared. Search for a start and destination.")
        self.origin.entry.focus_set()

    def _reset_route(self):
        self._route_request += 1
        self.route = None
        self.route_endpoints = None
        self._clear_route_drawing()
        self.directions.clear()
        self.empty_state.grid()
        self.copy_button.configure(state="disabled")
        self.directions_title.configure(text="DIRECTIONS")
        for tile in (self.distance_tile, self.time_tile, self.arrival_tile):
            tile.set("—")
        self.route_button.configure(state="normal", text="Find route")

    def _mode_changed(self, _value):
        if self.route:
            self.find_route()

    def find_route(self):
        for field in (self.origin, self.destination):
            if not field.selected:
                if field.entry.get().strip() and not field.matches:
                    field.search()
                    return
                field.entry.configure(border_color=DANGER[0])
                field.entry.focus_set()
                self.show_error(f"Choose a {field.label.lower()} first.")
                return
        origin, destination = self.origin.selected, self.destination.selected
        if (origin.lat, origin.lng) == (destination.lat, destination.lng):
            self.show_error("Start and destination are the same place. Choose a different destination.")
            return
        vehicle = MODES[self.mode.get()]
        self._route_request += 1
        request = self._route_request
        self.route_button.configure(state="disabled", text="Finding route...")
        self.set_busy(True, f"Calculating {self.mode.get().lower()} route...")
        self.tasks.run(
            lambda: get_route_details(origin, destination, vehicle),
            lambda route: self._route_ready(request, origin, destination, vehicle, route),
            lambda message: self._route_failed(request, message))

    def _route_failed(self, request, message):
        if request != self._route_request:
            return
        self.set_busy(False)
        self.route_button.configure(state="normal", text="Find route")
        self.show_error(message)

    def _route_ready(self, request, origin, destination, vehicle, route):
        if request != self._route_request:
            return
        self.set_busy(False)
        self.route_button.configure(state="normal", text="Find route")
        self.route = route
        self._update_attribution()
        self.route_endpoints = (origin, destination)
        self.route_vehicle = vehicle
        self._draw_route()
        self._render_route()
        self.set_status(f"Route found · {len(route.steps)} steps. Click a step to see it on the map.",
                        MUTED, SUCCESS)

    def _render_route(self):
        if not self.route:
            return
        unit = UNITS[self.unit.get()]
        self.distance_tile.set(format_distance(self.route.distance, unit))
        self.time_tile.set(format_duration(self.route.duration))
        arrival = datetime.now() + timedelta(milliseconds=self.route.duration)
        self.arrival_tile.set(arrival.strftime("%I:%M %p").lstrip("0"))
        self.empty_state.grid_remove()
        self.directions.show(self.route, unit)
        self.directions_title.configure(text=f"DIRECTIONS  ·  {len(self.route.steps)} STEPS")
        self.copy_button.configure(state="normal")

    def copy_directions(self):
        if not self.route:
            return
        origin, destination = self.route_endpoints
        text = format_trip(origin, destination, self.route_vehicle, UNITS[self.unit.get()], self.route)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status("Directions copied to the clipboard.", MUTED, SUCCESS)


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = RoutePlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
