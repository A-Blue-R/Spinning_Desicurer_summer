import tkinter as tk
from tkinter import messagebox, font as tkfont  # Use tkfont for custom fonts
import serial
import time
from threading import Thread

class App:
    def __init__(self, master):
        self.master = master
        master.title("Control Protocol")
        master.attributes('-fullscreen', True)  # Make the window fullscreen

        # Custom font for better visibility on touchscreen
        self.button_font = tkfont.Font(family='Helvetica', size=40, weight='bold')
        self.small_button_font = tkfont.Font(family='Helvetica', size=20, weight='bold')  # Smaller font for the close button

        # Styling for buttons
        button_style = {
            'font': self.button_font,
            'bg': '#DC143C',  # Crimson red background
            'fg': 'white',  # White text color
            'height': 5,
            'width': 15,
            'relief': 'ridge'  # Add some relief to the button for better tactile feedback on touchscreens
        }

        # Button to start the protocol
        self.start_btn = tk.Button(master, text="Start Procedure", command=self.start_protocol, **button_style)
        self.start_btn.place(relx=0.3, rely=0.5, anchor='center')

        # Button to continue the protocol, initially disabled
        self.continue_btn = tk.Button(master, text="Continue", state=tk.DISABLED, command=self.continue_protocol, **button_style)
        self.continue_btn.place(relx=0.7, rely=0.5, anchor='center')

        # Close button with custom style
        self.close_btn = tk.Button(master, text="Close", command=self.on_closing,
                                   font=self.small_button_font, bg='red', fg='white', height=2, width=8, relief='ridge')
        self.close_btn.place(relx=0.5, rely=0.9, anchor='center')

        # Status label
        self.status = tk.Label(master, text="Waiting to start...", fg="black", font=self.button_font)
        self.status.pack(pady=20)

        # Establish a connection to the Arduino
        self.ser = serial.Serial('COM3', 9600)  # Adjust as per your actual COM port
        time.sleep(2)  # Wait for the connection to establish

    def send_command(self, movement, motor_duration, led_duration):
        command = f"{movement} {motor_duration} LED {led_duration}"
        self.ser.write((command + '\n').encode())
        self.status.config(text=f"Command sent: {command}")

    def protocol(self):
        self.send_command("FORWARD", 30, 0)  # two_minute duration
        time.sleep(121)
        self.send_command("FORWARD", 60, 60)  # one_minute duration and LED on
        time.sleep(61)
        self.continue_btn.config(state=tk.NORMAL)  # Enable continue button
        self.status.config(text="Click Continue to proceed...")

    def start_protocol(self):
        self.start_btn.config(state=tk.DISABLED)
        self.status.config(text="Protocol started...")
        Thread(target=self.protocol).start()

    def continue_protocol(self):
        self.continue_btn.config(state=tk.DISABLED)
        Thread(target=self.continue_steps).start()

    def continue_steps(self):
        self.send_command("FORWARD", 60, 60)
        time.sleep(61)
        self.send_command("FORWARD", 120, 0)
        time.sleep(121)
        self.status.config(text="Finished")
        self.start_btn.config(state=tk.NORMAL)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.ser.close()  # Close serial connection
            self.master.destroy()

root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
