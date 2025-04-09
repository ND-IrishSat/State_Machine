import tkinter as tk
import threading
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
# (Mainly used for arrow drawing; dynamic logic is in update_highlight.)
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
#   "SOC>50 Check"       at (300,500) [diamond]  <-- above SOC>5 Check.
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
# Main GUI setup.
# -----------------------------------------------------------------------------
root = tk.Tk()
root.title("Optimized Flowchart with Revised SOC Checks and Club Logo")

# -----------------------------------------------------------------------------
# Now load your club logo image after creating the root window.
# Use a raw string for the file path to avoid escape sequence issues.
# -----------------------------------------------------------------------------
try:
    logo_img = Image.open(r".\SHAMROCKMissionPatch.png")
    logo_img = logo_img.resize((400, 400))
    logo_tk = ImageTk.PhotoImage(logo_img)
except Exception as e:
    print("Error loading club logo image:", e)
    logo_tk = None

# -----------------------------------------------------------------------------
# Drawing helper functions.
# -----------------------------------------------------------------------------
def draw_rectangle(canvas, cx, cy, highlight=False):
    fill_color = "yellow" if highlight else "white"
    canvas.create_rectangle(cx - HALF_WIDTH, cy - HALF_HEIGHT,
                            cx + HALF_WIDTH, cy + HALF_HEIGHT,
                            fill=fill_color, outline="black", width=2)

def draw_diamond(canvas, cx, cy, highlight=False):
    fill_color = "yellow" if highlight else "white"
    points = [
        (cx, cy - HALF_HEIGHT),
        (cx + HALF_WIDTH, cy),
        (cx, cy + HALF_HEIGHT),
        (cx - HALF_WIDTH, cy)
    ]
    canvas.create_polygon(points, fill=fill_color, outline="black", width=2)

# -----------------------------------------------------------------------------
# Draw arrow connections using straight lines with right angles.
#
# Special Cases:
# - For the arrow from "SOC>5 Check" to "SOC>50 Check": it exits the top of SOC>5 Check
#   and touches the bottom of SOC>50 Check.
# - For "SOC>5 Check" -> "Sun Side": route from the bottom of SOC>5 Check to the left side of Sun Side.
# - For leftward transitions into "Idle", the arrow enters at the bottom-center.
# -----------------------------------------------------------------------------
def draw_connection(canvas, src, dest):
    x1, y1 = nodes_info[src]["pos"]
    x2, y2 = nodes_info[dest]["pos"]

    # Special case for SOC>5 Check -> SOC>50 Check:
    if src == "SOC>5 Check" and dest == "SOC>50 Check":
        p1 = (x1, y1 - HALF_HEIGHT)  # Top center of SOC>5 Check.
        p2 = (x2, y2 + HALF_HEIGHT)  # Bottom center of SOC>50 Check.
        canvas.create_line([p1, p2], arrow=tk.LAST, width=2)
        return

    # Special case for SOC>5 Check -> Sun Side:
    if src == "SOC>5 Check" and dest == "Sun Side":
        p1 = (x1, y1 + HALF_HEIGHT)  # Bottom center of SOC>5 Check.
        p2 = (x1, y2)                # Move vertically to Sun Side level.
        p3 = (x2 - HALF_WIDTH, y2)    # Enter Sun Side from left.
        canvas.create_line([p1, p2, p3], arrow=tk.LAST, width=2)
        return

    # For nearly vertical alignment, use a direct vertical line.
    if abs(x2 - x1) < 10:
        if y2 > y1:
            p1 = (x1, y1 + HALF_HEIGHT)
            p2 = (x2, y2 - HALF_HEIGHT)
        else:
            p1 = (x1, y1 - HALF_HEIGHT)
            p2 = (x2, y2 + HALF_HEIGHT)
        canvas.create_line(p1, p2, arrow=tk.LAST, width=2)
        return

    # For leftward transitions into "Idle", route to bottom-center of Idle.
    if x2 < x1 and dest == "Idle":
        max_y = max(info["pos"][1] for info in nodes_info.values())
        route_y = max_y + HALF_HEIGHT + 20
        p1 = (x1, y1 + HALF_HEIGHT)
        p2 = (x1, route_y)
        p3 = (x2, route_y)
        p4 = (x2, y2 + HALF_HEIGHT)
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
# Draw the complete flowchart (nodes and arrows), display booleans, and club logo.
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
                
    # Display booleans in the specified order.
    order = ["SOC>5", "SOC>50", "Ground_Station_Soon", "Sun_Side", "Doing_Research", "Ground_Station"]
    bool_str = "   ".join(f"{key}: {bool_vars[key]}" for key in order)
    canvas.create_text(800, 780, text=bool_str, font=("Arial", 14), fill="black")
    
    # Draw the club logo image in the top-right corner.
    if logo_tk:
        canvas.create_image(600, 50, anchor=tk.NW, image=logo_tk)
        canvas.logo = logo_tk  # Keep reference!

# -----------------------------------------------------------------------------
# Update the current state using the following logic:
#
#   Launching → Detumbling → Deploy Solar/Mono → Idle → SOC>5 Check.
#   At SOC>5 Check:
#       if SOC>5 is true → SOC>50 Check,
#       else → Hibernate.
#   At SOC>50 Check:
#       if SOC>50 is true → Ground Station Soon,
#       else → Sun Side.
#   At Ground Station Soon:
#       if Ground_Station_Soon is true → Doing Research,
#       else → Sun Side.
#   At Sun Side:
#       if Sun_Side is true → Sun Pointing,
#       else → Idle.
#   At Hibernate:
#       Flow to Idle.
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
        draw_flowchart(canvas)
        time.sleep(3)
  
# -----------------------------------------------------------------------------
# Key handler to toggle boolean flags.
#
# Use number keys for toggling in this order:
#   1: SOC>5, 2: SOC>50, 3: Ground_Station_Soon, 4: Sun_Side, 5: Doing_Research, 6: Ground_Station.
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
        draw_flowchart(canvas)

# -----------------------------------------------------------------------------
# Main GUI setup.
# -----------------------------------------------------------------------------
root.geometry("1600x800")
root.title("Optimized Flowchart with Revised Boolean Order and Club Logo")

canvas = tk.Canvas(root, width=1600, height=800, bg="#D0E0FF")
canvas.pack()

root.bind("<Key>", handle_keypress)
draw_flowchart(canvas)
threading.Thread(target=update_highlight, args=(canvas,), daemon=True).start()
root.mainloop()
