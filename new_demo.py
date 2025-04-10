import tkinter as tk
import time
import random
from PIL import Image, ImageTk

# -----------------------------------------------------------------------------
# Boolean variables used to drive transitions.
# -----------------------------------------------------------------------------
bool_vars = {
    "SOC>50": False,            # Determines branch at SOC>50 Check
    "SOC>5": False,             # New boolean determining branch at SOC>5 Check
    "Sun_Side": False,          # Determines branch at Sun Side
    "Ground_Station": False,    # Determines branch at Ground Station node
    "Doing_Research": False,    # Determines branch at Doing Research diamond
    "Ground_Station_Soon": False  # Determines branch at Ground Station Soon
}

# -----------------------------------------------------------------------------
# Flowchart transitions for drawing arrows.
# (Used mainly for arrow drawing; dynamic logic is in update_state.)
# -----------------------------------------------------------------------------
flowchart = {
    "Launching": ["Detumbling"],
    "Detumbling": ["Deploy Solar/Mono"],
    "Deploy Solar/Mono": ["Idle"],
    "Idle": ["SOC>5 Check"],
    "SOC>5 Check": ["SOC>50 Check", "Hibernate"],
    "SOC>50 Check": ["Ground Station Soon", "Sun Side"],
    "Ground Station Soon": ["Doing Research", "Sun Side"],
    "Sun Side": ["Sun Pointing", "Idle"],
    "Doing Research": ["Research Pointing", "Comms Pointing"],
    "Research Pointing": ["Ground Station"],
    "Comms Pointing": ["Ground Station"],
    "Sun Pointing": ["Idle"],
    "Ground Station": ["Up/Down Link", "Idle"],
    "Up/Down Link": ["Idle"],
    "Hibernate": ["Idle"]
}

# -----------------------------------------------------------------------------
# Nodes definition: positions and shapes.
# 
# Left vertical stack:
#   "Launching"          at (100,100)
#   "Detumbling"         at (100,250)
#   "Deploy Solar/Mono"  at (100,400)
#   "Idle"               at (100,550)
#
# SOC branch:
#   "SOC>50 Check"       at (300,500) [diamond]  <-- placed above SOC>5 Check.
#   "SOC>5 Check"        at (300,600) [diamond]
#   "Hibernate"          at (300,700) [rect]
#
# Further right:
#   "Ground Station Soon" at (500,550) [diamond]
#   "Sun Side"           at (500,650) [diamond]
#   "Doing Research"     at (700,550) [diamond]
#   "Sun Pointing"       at (700,650) [rect]
#   "Research Pointing"  at (900,500) [rect]
#   "Comms Pointing"     at (900,600) [rect]
#   "Ground Station"     at (1100,550) [diamond]
#   "Up/Down Link"       at (1300,550) [rect]
# -----------------------------------------------------------------------------
nodes_info = {
    "Launching": {"pos": (100, 100), "shape": "rect"},
    "Detumbling": {"pos": (100, 250), "shape": "rect"},
    "Deploy Solar/Mono": {"pos": (100, 400), "shape": "rect"},
    "Idle": {"pos": (100, 550), "shape": "rect"},
    "SOC>50 Check": {"pos": (300, 500), "shape": "diamond"},
    "SOC>5 Check": {"pos": (300, 600), "shape": "diamond"},
    "Hibernate": {"pos": (300, 700), "shape": "rect"},
    "Ground Station Soon": {"pos": (500, 550), "shape": "diamond"},
    "Sun Side": {"pos": (500, 650), "shape": "diamond"},
    "Doing Research": {"pos": (700, 550), "shape": "diamond"},
    "Sun Pointing": {"pos": (700, 650), "shape": "rect"},
    "Research Pointing": {"pos": (900, 500), "shape": "rect"},
    "Comms Pointing": {"pos": (900, 600), "shape": "rect"},
    "Ground Station": {"pos": (1100, 550), "shape": "diamond"},
    "Up/Down Link": {"pos": (1300, 550), "shape": "rect"}
}

# -----------------------------------------------------------------------------
# Dimensions for nodes.
# -----------------------------------------------------------------------------
BOX_WIDTH = 160
BOX_HEIGHT = 80
HALF_WIDTH = BOX_WIDTH // 2
HALF_HEIGHT = BOX_HEIGHT // 2

# -----------------------------------------------------------------------------
# Global current state.
# -----------------------------------------------------------------------------
current_node = "Launching"

# -----------------------------------------------------------------------------
# Global dictionaries to hold canvas item IDs.
# -----------------------------------------------------------------------------
node_ids = {}   # keys: node name, value: shape item id (tagged "dynamic")
text_ids = {}   # keys: node name, value: text item id (tagged "dynamic")
arrow_ids = {}  # keys: (src, dest) tuple, value: line item id (tagged "dynamic")

# -----------------------------------------------------------------------------
# Create the main GUI.
# -----------------------------------------------------------------------------
root = tk.Tk()
root.geometry("1600x800")
root.title("Optimized Flowchart with Revised SOC Checks and Club Logo")

canvas = tk.Canvas(root, width=1600, height=800, bg="#ede8de")
canvas.pack()

# -----------------------------------------------------------------------------
# Load the club logo image after the root window is created.
# Use a raw string to avoid escape sequences.
# Resize the image as needed.
# -----------------------------------------------------------------------------
try:
    logo_img = Image.open(r".\SHAMROCKMissionPatch.png")
    logo_img = logo_img.resize((400, 400))
    logo_tk = ImageTk.PhotoImage(logo_img)
except Exception as e:
    print("Error loading club logo image:", e)
    logo_tk = None

# -----------------------------------------------------------------------------
# Create static items that will not be deleted on each update (e.g., the logo and background).
# We'll draw the logo once and tag it "logo" so we don't delete it.
# -----------------------------------------------------------------------------
def create_static_items():
    # Create a background rectangle (if desired) that will remain
    # Otherwise, just create the logo.
    if logo_tk:
        # Draw the club logo once with tag "logo"
        canvas.create_image(600, 50, anchor=tk.NW, image=logo_tk, tags="logo")
        # Keep a reference on the canvas:
        canvas.logo = logo_tk

# -----------------------------------------------------------------------------
# Create node items once (all dynamic items will have the tag "dynamic").
# -----------------------------------------------------------------------------
def create_nodes():
    for node, info in nodes_info.items():
        cx, cy = info["pos"]
        if info["shape"] == "diamond":
            node_ids[node] = canvas.create_polygon(
                cx, cy - HALF_HEIGHT,
                cx + HALF_WIDTH, cy,
                cx, cy + HALF_HEIGHT,
                cx - HALF_WIDTH, cy,
                fill="white", outline="#C19932", width=2,
                tags=("dynamic", "node", node)
            )
        else:
            node_ids[node] = canvas.create_rectangle(
                cx - HALF_WIDTH, cy - HALF_HEIGHT,
                cx + HALF_WIDTH, cy + HALF_HEIGHT,
                fill="white", outline="#C19932", width=2,
                tags=("dynamic", "node", node)
            )
        text_ids[node] = canvas.create_text(
            cx, cy, text=node, font=("Arial", 12), fill="white", tags=("dynamic", "text", node)
        )

# -----------------------------------------------------------------------------
# Create arrow items once (all dynamic).
# -----------------------------------------------------------------------------
def get_arrow_coords(src, dest):
    # Replicates the logic in your draw_connection() to compute arrow coordinates.
    x1, y1 = nodes_info[src]["pos"]
    x2, y2 = nodes_info[dest]["pos"]

    # Special case: SOC>5 Check -> SOC>50 Check.
    if src == "SOC>5 Check" and dest == "SOC>50 Check":
        return [x1, y1 - HALF_HEIGHT, x2, y2 + HALF_HEIGHT]

    # Special case: SOC>5 Check -> Sun Side.
    if src == "SOC>5 Check" and dest == "Sun Side":
        return [x1, y1 + HALF_HEIGHT, x1, y2, x2 - HALF_WIDTH, y2]

    # Nearly vertical:
    if abs(x2 - x1) < 10:
        if y2 > y1:
            return [x1, y1 + HALF_HEIGHT, x2, y2 - HALF_HEIGHT]
        else:
            return [x1, y1 - HALF_HEIGHT, x2, y2 + HALF_HEIGHT]

    # Leftward transitions into "Idle":
    if x2 < x1 and dest == "Idle":
        max_y = max(info["pos"][1] for info in nodes_info.values())
        route_y = max_y + HALF_HEIGHT + 20
        return [x1, y1 + HALF_HEIGHT, x1, route_y, x2, route_y, x2, y2 + HALF_HEIGHT]
    elif x2 < x1:
        min_y = min(info["pos"][1] for info in nodes_info.values())
        route_y = min_y - HALF_HEIGHT - 20
        return [x1, y1 - HALF_HEIGHT, x1, route_y, x2, route_y, x2, y2 - HALF_HEIGHT, x2 - HALF_WIDTH, y2]

    # Rightward transitions:
    offset = 20
    return [x1 + HALF_WIDTH, y1, x1 + HALF_WIDTH + offset, y1, x1 + HALF_WIDTH + offset, y2, x2 - HALF_WIDTH, y2]

def create_arrows():
    for src, dest_list in flowchart.items():
        for dest in dest_list:
            coords = get_arrow_coords(src, dest)
            arrow_id = canvas.create_line(*coords, arrow=tk.LAST, width=2, tags=("dynamic", "arrow", f"{src}_{dest}"))
            arrow_ids[(src, dest)] = arrow_id

# -----------------------------------------------------------------------------
# Update dynamic items without full redraw.
# -----------------------------------------------------------------------------
def update_items():
    # Update node colors.
    for node, item_id in node_ids.items():
        new_color = "#C19932" if node == current_node else "#001f3f"
        canvas.itemconfig(item_id, fill=new_color)
    # Update arrow coordinates.
    for (src, dest), arrow_id in arrow_ids.items():
        coords = get_arrow_coords(src, dest)
        canvas.coords(arrow_id, *coords)
    # Update status text.
    order = ["SOC>5", "SOC>50", "Ground_Station_Soon", "Sun_Side", "Doing_Research", "Ground_Station"]
    bool_str = "   ".join(f"{key}: {bool_vars[key]}" for key in order)
    canvas.itemconfig("status_text", text=bool_str)

# -----------------------------------------------------------------------------
# Set up status text (for booleans).
# -----------------------------------------------------------------------------
def create_status_text():
    return canvas.create_text(800, 780, text="", font=("Arial", 14), fill="black", tags="status_text")

# -----------------------------------------------------------------------------
# Redraw dynamic items.
# -----------------------------------------------------------------------------
def update_flowchart():
    update_items()
    root.after(100, update_flowchart)

# -----------------------------------------------------------------------------
# Update current state (same logic as before).
# -----------------------------------------------------------------------------
def update_state():
    global current_node
    # Enforce boolean constraints: if SOC>50 is true, then SOC>5 must be true.
    if bool_vars["SOC>50"] and not bool_vars["SOC>5"]:
        bool_vars["SOC>5"] = True
    if not bool_vars["SOC>5"] and bool_vars["SOC>50"]:
        bool_vars["SOC>50"] = False

    if current_node == "Launching":
        current_node = "Detumbling"
    elif current_node == "Detumbling":
        current_node = "Deploy Solar/Mono"
    elif current_node == "Deploy Solar/Mono":
        current_node = "Idle"
    elif current_node == "Idle":
        current_node = "SOC>5 Check"
    elif current_node == "SOC>5 Check":
        if bool_vars["SOC>5"]:
            current_node = "SOC>50 Check"
        else:
            current_node = "Hibernate"
    elif current_node == "SOC>50 Check":
        if bool_vars["SOC>50"]:
            current_node = "Ground Station Soon"
        else:
            current_node = "Sun Side"
    elif current_node == "Ground Station Soon":
        if bool_vars["Ground_Station_Soon"]:
            current_node = "Doing Research"
        else:
            current_node = "Sun Side"
    elif current_node == "Sun Side":
        if bool_vars["Sun_Side"]:
            current_node = "Sun Pointing"
        else:
            current_node = "Idle"
    elif current_node == "Hibernate":
        current_node = "Idle"
    elif current_node == "Doing Research":
        if bool_vars["Doing_Research"]:
            current_node = "Research Pointing"
        else:
            current_node = "Comms Pointing"
    elif current_node in {"Research Pointing", "Comms Pointing"}:
        current_node = "Ground Station"
    elif current_node == "Sun Pointing":
        current_node = "Idle"
    elif current_node == "Ground Station":
        if bool_vars["Ground_Station"]:
            current_node = "Up/Down Link"
        else:
            current_node = "Idle"
    elif current_node == "Up/Down Link":
        current_node = "Idle"
    else:
        next_states = flowchart.get(current_node, [])
        if next_states:
            current_node = random.choice(next_states)
    root.after(3000, update_state)

# -----------------------------------------------------------------------------
# Key handler to toggle boolean flags.
#
# Number keys: 1: SOC>5, 2: SOC>50, 3: Ground_Station_Soon, 4: Sun_Side, 5: Doing_Research, 6: Ground_Station.
# -----------------------------------------------------------------------------
def handle_keypress(event):
    key_map = {
        "1": "SOC>5",
        "2": "SOC>50",
        "3": "Ground_Station_Soon",
        "4": "Sun_Side",
        "5": "Doing_Research",
        "6": "Ground_Station"
    }
    if event.keysym in key_map:
        bool_vars[key_map[event.keysym]] = not bool_vars[key_map[event.keysym]]
        update_items()

# -----------------------------------------------------------------------------
# Main GUI setup.
# -----------------------------------------------------------------------------
root.bind("<Key>", handle_keypress)
create_nodes()
create_arrows()
create_status_text()
create_static_items()
update_flowchart()   # Update dynamic items every 100 ms.
root.after(3000, update_state)  # Update state every 3 seconds.
root.mainloop()
