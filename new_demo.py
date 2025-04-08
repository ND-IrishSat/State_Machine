import tkinter as tk
import threading
import time
import random
from PIL import Image, ImageTk

# -----------------------------------------------------------------------------
# Boolean variables used to drive transitions.
# -----------------------------------------------------------------------------
bool_vars = {
    "SOC": False,             # Determines branch at SOC_Check
    "Sun_Side": False,        # Determines branch at Sun Side
    "Ground_Station": False,  # Determines branch at Ground Station node
    "Doing_Research": False,  # Determines branch at Doing Research diamond
    "Ground_Station_Soon": False  # Determines branch at Ground Station Soon
}

# -----------------------------------------------------------------------------
# Flowchart transitions for drawing arrows.
# These serve mainly for arrow drawing (the dynamic logic is in update_highlight).
# -----------------------------------------------------------------------------
flowchart = {
    "Launching": ["Detumbling"],
    "Detumbling": ["Deploy Solar/Mono"],
    "Deploy Solar/Mono": ["Idle"],
    "Idle": ["SOC_Check"],
    "SOC_Check": ["Ground Station Soon", "Sun Side"],
    "Ground Station Soon": ["Doing Research", "Sun Side"],
    "Sun Side": ["Sun Pointing", "Idle"],
    "Doing Research": ["Research Pointing", "Comms Pointing"],
    "Research Pointing": ["Ground Station"],
    "Comms Pointing": ["Ground Station"],
    "Sun Pointing": ["Idle"],
    "Ground Station": ["Up/Down Link", "Idle"],
    "Up/Down Link": ["Idle"]
}

# -----------------------------------------------------------------------------
# Nodes definition: positions and shapes.
#
# The new layout arranges a vertical stack in the left column:
#    "Launching"    at (100,100)
#    "Detumbling"   at (100,250)
#    "Deploy Solar/Mono" at (100,400)
#    "Idle"         at (100,550)
#
# Then the branch nodes:
#    "SOC_Check"          at (300,550) [diamond]
#    "Ground Station Soon" at (500,550) [diamond]
#    "Sun Side"           at (500,650) [diamond]
#
# Then subsequent nodes:
#    "Doing Research"     at (700,550) [diamond]
#    "Sun Pointing"       at (700,650) [rect]
#    "Research Pointing"  at (900,500) [rect]
#    "Comms Pointing"     at (900,600) [rect]
#    "Ground Station"     at (1100,550) [diamond] - aligned horizontally with SOC_Check
#    "Up/Down Link"       at (1300,550) [rect]
# -----------------------------------------------------------------------------
nodes_info = {
    "Launching": {"pos": (100, 100), "shape": "rect"},
    "Detumbling": {"pos": (100, 250), "shape": "rect"},
    "Deploy Solar/Mono": {"pos": (100, 400), "shape": "rect"},
    "Idle": {"pos": (100, 550), "shape": "rect"},
    "SOC_Check": {"pos": (300, 550), "shape": "diamond"},
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
# Drawing helper functions.
# -----------------------------------------------------------------------------
def draw_rectangle(canvas, cx, cy, highlight=False):
    fill_color = "yellow" if highlight else "white"
    canvas.create_rectangle(
        cx - HALF_WIDTH, cy - HALF_HEIGHT,
        cx + HALF_WIDTH, cy + HALF_HEIGHT,
        fill=fill_color, outline="black", width=2
    )

def draw_diamond(canvas, cx, cy, highlight=False):
    fill_color = "yellow" if highlight else "white"
    points = [
        (cx, cy - HALF_HEIGHT),   # Top
        (cx + HALF_WIDTH, cy),      # Right
        (cx, cy + HALF_HEIGHT),   # Bottom
        (cx - HALF_WIDTH, cy)       # Left
    ]
    canvas.create_polygon(points, fill=fill_color, outline="black", width=2)

# -----------------------------------------------------------------------------
# Draw arrow connections using straight lines with right angles.
#
# --- Special case: if src == "SOC_Check" and dest == "Sun Side",
#     we route the arrow to exit from the bottom of SOC_Check and
#     enter the left side of Sun Side.
# -----------------------------------------------------------------------------
def draw_connection(canvas, src, dest):
    x1, y1 = nodes_info[src]["pos"]
    x2, y2 = nodes_info[dest]["pos"]

    # Special case for SOC_Check -> Sun Side.
    if src == "SOC_Check" and dest == "Sun Side":
        p1 = (x1, y1 + HALF_HEIGHT)            # Bottom center of SOC_Check.
        p2 = (x1, y2)                          # Move vertically down to level of Sun Side.
        p3 = (x2 - HALF_WIDTH, y2)              # Enter Sun Side from its left side.
        canvas.create_line([p1, p2, p3], arrow=tk.LAST, width=2)
        return

    # For nearly vertical alignment, draw a straight vertical line.
    if abs(x2 - x1) < 10:
        if y2 > y1:
            p1 = (x1, y1 + HALF_HEIGHT)
            p2 = (x2, y2 - HALF_HEIGHT)
        else:
            p1 = (x1, y1 - HALF_HEIGHT)
            p2 = (x2, y2 + HALF_HEIGHT)
        canvas.create_line(p1, p2, arrow=tk.LAST, width=2)
        return

    # For leftward transitions into "Idle", route to the bottom-center of Idle.
    if x2 < x1 and dest == "Idle":
        max_y = max(info["pos"][1] for info in nodes_info.values())
        route_y = max_y + HALF_HEIGHT + 20
        p1 = (x1, y1 + HALF_HEIGHT)
        p2 = (x1, route_y)
        p3 = (x2, route_y)
        p4 = (x2, y2 + HALF_HEIGHT)  # Bottom-center entry for Idle.
        canvas.create_line([p1, p2, p3, p4], arrow=tk.LAST, width=2)
        return
    elif x2 < x1:
        # For other leftward transitions, route above.
        min_y = min(info["pos"][1] for info in nodes_info.values())
        route_y = min_y - HALF_HEIGHT - 20
        p1 = (x1, y1 - HALF_HEIGHT)
        p2 = (x1, route_y)
        p3 = (x2, route_y)
        p4 = (x2, y2 - HALF_HEIGHT)
        p5 = (x2 - HALF_WIDTH, y2)
        canvas.create_line([p1, p2, p3, p4, p5], arrow=tk.LAST, width=2)
        return

    # For rightward transitions, use a horizontal offset.
    offset = 20
    p1 = (x1 + HALF_WIDTH, y1)
    p2 = (x1 + HALF_WIDTH + offset, y1)
    p3 = (x1 + HALF_WIDTH + offset, y2)
    p4 = (x2 - HALF_WIDTH, y2)
    canvas.create_line([p1, p2, p3, p4], arrow=tk.LAST, width=2)

# -----------------------------------------------------------------------------
# Draw the complete flowchart (nodes and arrows).
# -----------------------------------------------------------------------------
def draw_flowchart(canvas):
    canvas.delete("all")
    canvas.create_rectangle(0, 0, 1600, 800, fill="#D0E0FF", outline="")
    for node, info in nodes_info.items():
        cx, cy = info["pos"]
        highlight = (node == current_node)
        if info["shape"] == "diamond":
            draw_diamond(canvas, cx, cy, highlight=highlight)
        else:
            draw_rectangle(canvas, cx, cy, highlight=highlight)
        canvas.create_text(cx, cy, text=node, font=("Arial", 12), fill="black")
    for src, dest_list in flowchart.items():
        for dest in dest_list:
            if src in nodes_info and dest in nodes_info:
                draw_connection(canvas, src, dest)
    canvas.create_text(800, 780, text=f"Booleans: {bool_vars}",
                       font=("Arial", 14), fill="black")

# -----------------------------------------------------------------------------
# Update the current state using the following logic:
#
#   Launching → Detumbling → Deploy Solar/Mono → Idle → SOC_Check.
#   At SOC_Check:
#       if SOC is true → Ground Station Soon,
#       else → Sun Side.
#   At Ground Station Soon:
#       if Ground_Station_Soon is true → Doing Research,
#       else → Sun Side.
#   At Sun Side:
#       if Sun_Side is true → Sun Pointing,
#       else → Idle.
#   At Doing Research:
#       if Doing_Research is true → Research Pointing,
#       else → Comms Pointing.
#   At Research Pointing or Comms Pointing → Ground Station.
#   At Ground Station:
#       if Ground_Station is true → Up/Down Link,
#       else → Idle.
#   Up/Down Link → Idle.
# -----------------------------------------------------------------------------
def update_highlight(canvas):
    global current_node
    while True:
        if current_node == "Launching":
            current_node = "Detumbling"
        elif current_node == "Detumbling":
            current_node = "Deploy Solar/Mono"
        elif current_node == "Deploy Solar/Mono":
            current_node = "Idle"
        elif current_node == "Idle":
            current_node = "SOC_Check"
        elif current_node == "SOC_Check":
            if bool_vars["SOC"]:
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
        draw_flowchart(canvas)
        time.sleep(3)

# -----------------------------------------------------------------------------
# Key handler to toggle boolean flags.
# Keys:
#   'a': SOC, 'b': Sun_Side, 'c': Ground_Station, 'd': Doing_Research, 'e': Ground_Station_Soon.
# -----------------------------------------------------------------------------
def handle_keypress(event):
    key_map = {
        "a": "SOC",
        "b": "Sun_Side",
        "c": "Ground_Station",
        "d": "Doing_Research",
        "e": "Ground_Station_Soon"
    }
    if event.keysym in key_map:
        bool_vars[key_map[event.keysym]] = not bool_vars[key_map[event.keysym]]
        draw_flowchart(canvas)

# -----------------------------------------------------------------------------
# Main GUI setup.
# -----------------------------------------------------------------------------
root = tk.Tk()
root.title("Optimized Flowchart with Vertical Stack including Idle and Updated Arrow Routing")

canvas = tk.Canvas(root, width=1600, height=800, bg="#D0E0FF")
canvas.pack()

root.bind("<Key>", handle_keypress)
draw_flowchart(canvas)
threading.Thread(target=update_highlight, args=(canvas,), daemon=True).start()
root.mainloop()
