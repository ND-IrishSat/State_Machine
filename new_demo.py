import tkinter as tk
import threading
import time
import random
from PIL import Image, ImageTk

bool_vars = {
    "SOC": False,
    "Sun_Side": False,
    "Ground_Station": False,
    "Doing_Research": False
}

flowchart = {
    "Launching": ["Detumbling"],
    "Detumbling": ["Deploy Solar/Mono"],
    "Deploy Solar/Mono": ["Idle"],
    "Idle": ["SOC_Check"],
    "SOC_Check": [
        "SOC_50_Check",
        "Ground_Station_Check",
        "Sun_Pointing",
        "Doing_Research_Check",
        "Hibernate"
    ],
    "SOC_50_Check": ["Idle"],
    "Ground_Station_Check": ["Comms Pointing", "Idle"],
    "Sun_Pointing": ["Idle"],
    "Doing_Research_Check": ["Research Pointing", "Idle"],
    "Hibernate": ["Idle"],
    "Comms Pointing": ["Up/Down Link", "Idle"],
    "Up/Down Link": ["Idle"],
    "Research Pointing": ["Idle"]
}

positions = {
    "Launching": (100, 100),
    "Detumbling": (100, 300),
    "Deploy Solar/Mono": (100, 500),
    "Idle": (300, 300),
    "SOC_Check": (500, 300),
    # "SOC_50_Check": (700, 100),
    "Ground_Station_Check": (700, 200),
    "Sun_Pointing": (700, 300),
    "Doing_Research_Check": (700, 400),
    "Hibernate": (700, 500),
    "Comms Pointing": (900, 200),
    "Up/Down Link": (1100, 200),
    "Research Pointing": (900, 500)
}

BOX_WIDTH = 160
BOX_HEIGHT = 80
HALF_WIDTH = BOX_WIDTH // 2
HALF_HEIGHT = BOX_HEIGHT // 2

current_node = "Launching"

def draw_connection(canvas, src, dest):
    x1, y1 = positions[src]
    x2, y2 = positions[dest]

    if src == "Doing_Research_Check" and dest == "Idle":
        p1 = (x1 + HALF_WIDTH, y1)
        p2 = (1000, y1)
        p3 = (1000, 700)
        p4 = (300, 700)
        p5 = (300, 340)
        canvas.create_line([p1, p2, p3, p4, p5], arrow=tk.LAST, width=2)
        return

    if src == "Sun_Pointing" and dest == "Idle":
        p1 = (x1 + HALF_WIDTH, y1)
        p2 = (1000, y1)
        p3 = (1000, 650)
        p4 = (300, 650)
        p5 = (300, 340)
        canvas.create_line([p1, p2, p3, p4, p5], arrow=tk.LAST, width=2)
        return

    if src == "Ground_Station_Check" and dest == "Idle":
        p1 = (x1 + HALF_WIDTH, y1)
        p2 = (800, y1)
        p3 = (800, 400)
        p4 = (1000, 400)
        p5 = (1000, 600)
        p6 = (300, 600)
        p7 = (300, 340)
        canvas.create_line([p1, p2, p3, p4, p5,p6,p7], arrow=tk.LAST, width=2)
        return

    if abs(x2 - x1) < 10:
        if y2 > y1:
            p1 = (x1, y1 + HALF_HEIGHT)
            p2 = (x2, y2 - HALF_HEIGHT)
        else:
            p1 = (x1, y1 - HALF_HEIGHT)
            p2 = (x2, y2 + HALF_HEIGHT)
        canvas.create_line(p1, p2, arrow=tk.LAST, width=2)
        return

    if x2 < x1:
        if dest == "Idle" and src in {"Hibernate", "Research Pointing"}:
            max_y = max(y for (_, y) in positions.values())
            route_y = max_y + HALF_HEIGHT + 20
            p1 = (x1, y1 + HALF_HEIGHT)
            p2 = (x1, route_y)
            p3 = (x2, route_y)
            p4 = (x2, y2 + HALF_HEIGHT)
            canvas.create_line([p1, p2, p3, p4], arrow=tk.LAST, width=2)
        else:
            min_y = min(y for (_, y) in positions.values())
            route_y = min_y - HALF_HEIGHT - 20
            p1 = (x1, y1 - HALF_HEIGHT)
            p2 = (x1, route_y)
            p3 = (x2, route_y)
            p4 = (x2, y2 - HALF_HEIGHT)
            canvas.create_line([p1, p2, p3, p4], arrow=tk.LAST, width=2)
    else:
        offset = 20
        p1 = (x1 + HALF_WIDTH, y1)
        p2 = (x1 + HALF_WIDTH + offset, y1)
        p3 = (x1 + HALF_WIDTH + offset, y2)
        p4 = (x2 - HALF_WIDTH, y2)
        canvas.create_line([p1, p2, p3, p4], arrow=tk.LAST, width=2)

def draw_flowchart(canvas):
    canvas.delete("all")
    canvas.create_rectangle(0, 0, 1600, 800, fill="#D0E0FF", outline="")

    for node, (cx, cy) in positions.items():
        fill_color = "yellow" if node == current_node else "white"
        canvas.create_rectangle(
            cx - HALF_WIDTH, cy - HALF_HEIGHT,
            cx + HALF_WIDTH, cy + HALF_HEIGHT,
            fill=fill_color, outline="black", width=2
        )
        canvas.create_text(cx, cy, text=node, font=("Arial", 12), fill="black")

    for src, dest_list in flowchart.items():
        for dest in dest_list:
            if src in positions and dest in positions:
                draw_connection(canvas, src, dest)

    canvas.create_text(800, 780, text=f"Booleans: {bool_vars}", font=("Arial", 14), fill="black")

def update_highlight(canvas):
    global current_node
    while True:
        if bool_vars["SOC"]:
            current_node = "SOC_50_Check"
        elif bool_vars["Ground_Station"]:
            current_node = "Ground_Station_Check"
        elif bool_vars["Sun_Side"]:
            current_node = "Sun_Pointing"
        elif bool_vars["Doing_Research"]:
            current_node = "Doing_Research_Check"
        else:
            next_states = flowchart.get(current_node, [])
            if next_states:
                current_node = random.choice(next_states)
        draw_flowchart(canvas)
        time.sleep(3)

def handle_keypress(event):
    key_map = {"a": "SOC", "b": "Sun_Side", "c": "Ground_Station", "d": "Doing_Research"}
    if event.keysym in key_map:
        bool_vars[key_map[event.keysym]] = not bool_vars[key_map[event.keysym]]
        draw_flowchart(canvas)

root = tk.Tk()
root.title("Infinite State Machine Flowchart")

canvas = tk.Canvas(root, width=1600, height=800, bg="#D0E0FF")
canvas.pack()

root.bind("<Key>", handle_keypress)

draw_flowchart(canvas)

threading.Thread(target=update_highlight, args=(canvas,), daemon=True).start()

root.mainloop()
