import serial
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import webbrowser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler

# Configure Serial Port
SERIAL_PORT = 'COM3'  # Replace with your ESP32's serial port
BAUD_RATE = 115200

# Function to read data from ESP32
def read_serial_data():
    global x_data, ph_data, tds_data, air_temp_data, humidity_data, water_temp_data
    try:
        if esp32.in_waiting > 0:
            data = esp32.readline().decode('utf-8').strip()
            if "Error" not in data:
                # Split the received data
                readings = {}
                pairs = data.split(',')
                for pair in pairs:
                    key, value = pair.split(':')
                    readings[key.strip()] = value.strip()

                # Update labels
                ph_label.config(text=f"pH: {readings.get('pH', '--')}")
                air_temp_label.config(text=f"Air Temp: {readings.get('AirTemp', '--')} °C")
                humidity_label.config(text=f"Humidity: {readings.get('Humidity', '--')} %")
                water_temp_label.config(text=f"Water Temp: {readings.get('WaterTemp', '--')} °C")
                tds_label.config(text=f"TDS: {readings.get('TDS', '--')} ppm")

                # Update graph data
                x_data.append(datetime.datetime.now().strftime("%H:%M:%S"))
                ph_data.append(float(readings.get('pH', 0)))
                tds_data.append(float(readings.get('TDS', 0)))
                air_temp_data.append(float(readings.get('AirTemp', 0)))
                humidity_data.append(float(readings.get('Humidity', 0)))
                water_temp_data.append(float(readings.get('WaterTemp', 0)))

                # Update graphs
                update_graphs()
    except Exception as e:
        print(f"Error reading data: {e}")
    root.after(1000, read_serial_data)

# Function to update the graphs
def update_graphs():
    # Update pH vs Time graph
    ax1.clear()
    ax1.plot(x_data, ph_data, label="pH", color="green")
    ax1.set_title("pH vs Time")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("pH")
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid()
    
    # Update TDS vs Time graph
    ax2.clear()
    ax2.plot(x_data, tds_data, label="TDS", color="gold")
    ax2.set_title("TDS vs Time")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("TDS (ppm)")
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid()

    # Update Room Temp, Water Temp, and Humidity vs Time graph
    ax3.clear()
    ax3.plot(x_data, air_temp_data, label="Air Temp", color="red")
    ax3.plot(x_data, water_temp_data, label="Water Temp", color="blue")
    ax3.plot(x_data, humidity_data, label="Humidity", color="purple")
    ax3.set_title("Room Temp, Water Temp, and Humidity vs Time")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Values")
    ax3.tick_params(axis='x', rotation=45)
    ax3.legend()
    ax3.grid()

    graph_canvas.draw()

# Setup Serial Connection
try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Failed to connect to ESP32: {e}")
    exit()

# Tkinter GUI
root = tk.Tk()
root.geometry("1700x800")
root.title("Aeroponics")
root.iconbitmap(r"C:\\Users\\Shreyash Patukale\\Desktop\\logo.ico")

# Create a frame for the header (navigation bar) on the left side
nav_frame = ttk.Frame(root, padding="10", style="Nav.TFrame")
nav_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.N, tk.S, tk.W))

# Configure the grid for the left frame to take the full height of the window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=0)

# Create a style for the navigation frame
style = ttk.Style()
style.configure("Nav.TFrame", background="sea green", padding=0)
style.configure("TButton", background="sea green", foreground="white", font=("Arial", 14))

# Add buttons for navigation
home_icon = Image.open(r"C:\\Users\\Shreyash Patukale\\Desktop\\home.png")
home_icon=home_icon.resize((50, 50), Image.LANCZOS)
home_icon = ImageTk.PhotoImage(home_icon)   

ml_icon = Image.open(r"C:\Users\Shreyash Patukale\Desktop\ml.png")  # Replace with your home icon path
ml_icon = ml_icon.resize((50, 50), Image.LANCZOS)  # Resize as needed
ml_icon = ImageTk.PhotoImage(ml_icon)

bot_icon = Image.open(r"C:\Users\Shreyash Patukale\Desktop\bot.png")  # Replace with your home icon path
bot_icon = bot_icon.resize((50, 50), Image.LANCZOS)  # Resize as needed
bot_icon = ImageTk.PhotoImage(bot_icon)

trade_icon = Image.open(r"C:\Users\Shreyash Patukale\Desktop\trade.png")  # Replace with your home icon path
trade_icon = trade_icon.resize((50, 50), Image.LANCZOS)  # Resize as needed
trade_icon = ImageTk.PhotoImage(trade_icon)

home_button = ttk.Button(nav_frame, image=home_icon, command=lambda: show_page("Home"))
home_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

ml_button = ttk.Button(nav_frame, image=ml_icon, command=lambda: show_page("ml"))
ml_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

bot_button = ttk.Button(
    nav_frame,
    image=bot_icon,
    command=lambda: webbrowser.open(r"http://localhost:3000/")  # Replace with the desired URL
)
bot_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

trade_button = ttk.Button(
    nav_frame,
    image=trade_icon,
    command=lambda: webbrowser.open(r"C:\Users\Shreyash Patukale\Desktop\proj\LAST.html")  # Replace with the desired URL)
)    
trade_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

# Create global labels and graph variables
ph_label = air_temp_label = humidity_label = water_temp_label = tds_label = None
x_data, ph_data, tds_data, air_temp_data, humidity_data, water_temp_data = [], [], [], [], [], []

# Function to display content based on the selected page
def show_page(page_name):
    for widget in content_frame.winfo_children():
        widget.grid_forget()
    if page_name == "Home":
        show_home_page()
    elif page_name == "ml":
        show_ml_page()

def show_home_page():
    global ph_label, air_temp_label, humidity_label, water_temp_label, tds_label, graph_canvas, ax1, ax2, ax3

    # Sensor data boxes
#box1
    ph_label = tk.Label(
    content_frame,
    text="pH: --",
    width=4,               # Adjusts the width
    height=5,               # Adjusts the height in lines
    bg="sea green",         # Background color
    fg="white",             # Text color
    borderwidth=2,          # Border thickness
    relief="solid",         # Border style
    font=("Bahnschrift SemiBold", 20)      # Font settings
)
    ph_label.grid(row=0, column=0, padx=0, pady=0, sticky="ew")  # Adds spacing outside

#box2
    tds_label = tk.Label( 
    content_frame,
    text="TDS: -- ppm",
    width=4,               # Adjusts the width
    height=5,               # Adjusts the height in lines
    bg="goldenrod",         # Background color
    fg="white",             # Text color
    borderwidth=2,          # Border thickness
    relief="solid",         # Border style
    font=("Bahnschrift SemiBold", 20)      # Font settings
    )
    tds_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    air_temp_label = tk.Label( 
    content_frame,
    text="Temperature: -- 0°C",
    width=5,               # Adjusts the width
    height=5,               # Adjusts the height in lines
    bg="tomato",         # Background color
    fg="white",             # Text color
    borderwidth=2,          # Border thickness
    relief="solid",         # Border style
    font=("Bahnschrift SemiBold", 20)  
    )
    air_temp_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    humidity_label = tk.Label(    content_frame,
    text="Humidity: -- %",
    width=5,               # Adjusts the width
    height=5,               # Adjusts the height in lines
    bg="lightblue",         # Background color
    fg="white",             # Text color
    borderwidth=2,          # Border thickness
    relief="solid",         # Border style
    font=("Bahnschrift SemiBold", 20)  )
    humidity_label.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    water_temp_label = tk.Label(    content_frame,
    text="Water: -- %",
    width=5,               # Adjusts the width
    height=5,               # Adjusts the height in lines
    bg="blue",         # Background color
    fg="white",             # Text color
    borderwidth=2,          # Border thickness
    relief="solid",         # Border style
    font=("Bahnschrift SemiBold", 20)  )
    water_temp_label.grid(row=0, column=4, padx=5, pady=5, sticky="ew")


    # Matplotlib Figures for graphs
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    graph_canvas = FigureCanvasTkAgg(fig, master=content_frame)
    graph_canvas.get_tk_widget().grid(row=2, column=0, columnspan=5, pady=10)

# Create a frame for content area
content_frame = ttk.Frame(root, padding="10")
content_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.grid_forget()
#----------------------------------------------------------------------------------------------------------------------
def show_ml_page():
    # Clear existing widgets before displaying the new content
    clear_frame(content_frame)

    # Load the dataset and perform your machine learning operations
    lettuce_df = pd.read_csv(r"sample.csv")
    cleaned_df = lettuce_df.dropna()

    X = cleaned_df.drop(['roomtemp', 'tds'], axis=1)
    y = cleaned_df['ph']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scaling the data
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Random Forest
    rf_model = RandomForestRegressor(random_state=42)
    rf_model.fit(X_train_scaled, y_train)

    y_rf_pred = rf_model.predict(X_test_scaled)

    # Creating a DataFrame for comparison
    model_values_comparison = pd.DataFrame({
        'Actual Values': y_test.reset_index(drop=True),
        'Random Forest Predicted Values': y_rf_pred
    })

    # Create the figure for plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting the Actual vs Predicted values as a line graph
    ax.plot(model_values_comparison.index, model_values_comparison['Actual Values'], color='green', label='Actual Values', marker='o', linestyle='-', linewidth=2)
    ax.plot(model_values_comparison.index, model_values_comparison['Random Forest Predicted Values'], color='purple', label='Predicted Values', marker='x', linestyle='-', linewidth=2)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('pH')
    ax.set_title('Prediction of ph')
    ax.legend()
    ax.grid()

    # Display the plot on Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=content_frame)  # A canvas to embed the figure
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

    # Optional: Display DataFrame as text (for comparison) below the plot
    result_text = tk.Text(content_frame, height=10, width=80)
    result_text.insert(tk.END, model_values_comparison.to_string())
    result_text.grid(row=1, column=0)
#-----------------------------------------------------------------------------------------------------------------------

# Display the home page initially
show_page("Home")

# Start reading data
root.after(1000, read_serial_data)

# Run the Tkinter event loop
root.mainloop()
