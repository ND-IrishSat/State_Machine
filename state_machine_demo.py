import tkinter as tk
import threading
import time
import random
from PIL import Image, ImageTk

# Define boolean variables (change dynamically)
bool_vars = {
    "SOC": False,
    "Sun_Side": False,
    "Ground_Station": False,
    "Doing_Research": False
}

# Define flowchart structure (connections)
flowchart = {
    "Launching": ["Detumbling"],
    "Detumbling": ["Deploy Solar/Mono"],
    "Deploy Solar/Mono": ["Idle"],
    "Idle": ["SOC_Check"],
    "SOC_Check": ["Hibernate", "SOC_50_Check"],
    "SOC_50_Check": ["Ground_Station_Check", "Sun_Pointing"],
    "Ground_Station_Check": ["Comms Pointing", "Doing_Research_Check"],
    "Doing_Research_Check": ["Research Pointing", "End"],
    "Comms Pointing": ["Up/Down Link", "End"],
    "Sun_Pointing": ["End"],
    "Research Pointing": ["End"],
    "Up/Down Link": ["End"],
    "End": []
}

# Node positions (horizontal layout)
positions = {
    "Launching": (100, 300),
    "Detumbling": (200, 300),
    "Deploy Solar/Mono": (300, 300),
    "Idle": (400, 300),
    "SOC_Check": (500, 300),
    "Hibernate": (500, 500),
    "SOC_50_Check": (600, 300),
    "Ground_Station_Check": (700, 200),
    "Sun_Pointing": (700, 400),
    "Doing_Research_Check": (800, 100),
    "Comms Pointing": (800, 200),
    "Research Pointing": (900, 100),
    "Up/Down Link": (900, 200),
    "End": (1000, 300)
}

# Current active node
current_node = "Launching"

def draw_flowchart(canvas):
    """Draws the flowchart on the canvas."""
    canvas.delete("all")
    canvas.create_rectangle(0, 0, 1200, 600, fill="#4682B4", outline="")  # Lighter blue
    for node, pos in positions.items():
        x, y = pos
        color = "yellow" if node == current_node else "white"
        canvas.create_rectangle(x-60, y-30, x+60, y+30, fill=color, outline="black")
        canvas.create_text(x, y, text=node, font=("Arial", 12))
    for node, next_nodes in flowchart.items():
        x1, y1 = positions[node]
        for next_node in next_nodes:
            x2, y2 = positions[next_node]
            canvas.create_line(x1+60, y1, x2-60, y2, arrow=tk.LAST)
    canvas.create_text(600, 550, text=f"Booleans: {bool_vars}", font=("Arial", 14), fill="white")
    
    # Placeholder for an image in the upper left corner
    img = Image.open("SHAMROCKMissionPatch.png")

    img_tk = ImageTk.PhotoImage(img)

    canvas.create_image(600, 600, anchor=tk.NW)
    canvas.image = img_tk  # Keep reference

def update_highlight(canvas):
    """Updates the highlighted rectangle based on boolean conditions."""
    global current_node
    while True:
        if bool_vars["SOC"]:
            current_node = "SOC_50_Check"
        elif bool_vars["Ground_Station"]:
            current_node = "Comms Pointing"
        elif bool_vars["Sun_Side"]:
            current_node = "Sun_Pointing"
        elif bool_vars["Doing_Research"]:
            current_node = "Research Pointing"
        else:
            next_nodes = flowchart.get(current_node, [])
            if next_nodes:
                current_node = random.choice(next_nodes)
        draw_flowchart(canvas)
        time.sleep(3)

def handle_keypress(event):
    """Handles keyboard input to toggle boolean values."""
    key_map = {"a": "SOC", "b": "Sun_Side", "c": "Ground_Station", "d": "Doing_Research"}
    if event.keysym in key_map:
        bool_vars[key_map[event.keysym]] = not bool_vars[key_map[event.keysym]]  # Toggle boolean
        draw_flowchart(canvas)

# Create GUI
root = tk.Tk()
root.title("Flowchart GUI")
canvas = tk.Canvas(root, width=1200, height=600, bg="#4682B4")  # Lighter blue
canvas.pack()
root.bind("<Key>", handle_keypress)

draw_flowchart(canvas)

# Start background thread for updating highlights
threading.Thread(target=update_highlight, args=(canvas,), daemon=True).start()

# Run the GUI event loop
root.mainloop()
