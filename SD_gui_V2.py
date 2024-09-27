import tkinter as tk
from tkinter import messagebox, font as tkfont, ttk  # Use ttk for modern widgets
import serial
import serial.tools.list_ports
import time
from threading import Thread, Event

class App:
    def __init__(self, master):
        self.master = master
        master.title("Control Protocol")
        master.attributes('-fullscreen', True)  # Make the window fullscreen

        # Initialize serial connection variables
        self.ser = None
        self.is_connected = False

        # Thread control variables
        self.protocol_thread = None
        self.pause_event = Event()
        self.stop_event = Event()

        # Custom fonts for better visibility on touchscreen
        self.button_font = tkfont.Font(family='Helvetica', size=40, weight='bold')
        self.small_button_font = tkfont.Font(family='Helvetica', size=12, weight='bold')  # Smaller font for the close button

        # Styling for buttons (green theme)
        button_style = {
            'font': self.button_font,
            'bg': 'green',  # Green background
            'fg': 'white',  # White text color
            'activebackground': '#32CD32',  # LimeGreen when pressed
            'activeforeground': 'white',
            'height': 5,
            'width': 15,
            'relief': 'ridge'  # Add some relief to the button for better tactile feedback on touchscreens
        }

        # COM Port Selection Frame
        port_frame = tk.Frame(master)
        port_frame.pack(pady=20)

        port_label = tk.Label(port_frame, text="Select COM Port:", font=self.button_font)
        port_label.pack(side=tk.LEFT, padx=10)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(port_frame, textvariable=self.port_var, state="readonly", font=self.button_font)
        self.port_dropdown['values'] = self.get_serial_ports()
        if self.port_dropdown['values']:
            self.port_dropdown.current(0)
        self.port_dropdown.pack(side=tk.LEFT, padx=10)

        refresh_button = tk.Button(port_frame, text="Refresh", command=self.refresh_ports, font=40, bg='blue', fg='white', relief='ridge')
        refresh_button.pack(side=tk.LEFT, padx=10)

        connect_button = tk.Button(port_frame, text="Connect", command=self.connect_serial, font=40, bg='green', fg='white', relief='ridge')
        connect_button.pack(side=tk.LEFT, padx=10)

        # Protocol Buttons Frame
        buttons_frame = tk.Frame(master)
        buttons_frame.pack(pady=20)

        # Step 1 Button
        self.step1_btn = tk.Button(master, text="Step 1", command=self.start_protocol, **button_style)
        self.step1_btn.place(relx=0.3, rely=0.5, anchor='center')

        # Step 2 Button
        self.step2_btn = tk.Button(master, text="Step 2", command=self.continue_protocol, **button_style)
        self.step2_btn.place(relx=0.7, rely=0.5, anchor='center')

        # Pause Button
        self.pause_btn = tk.Button(master, text="Pause", command=self.pause_protocol, font=self.button_font, bg='orange', fg='white', height=1, width=7, relief='ridge')
        self.pause_btn.place(relx=0.1, rely=0.85, anchor='center')

        # Resume Button
        self.resume_btn = tk.Button(master, text="Resume", command=self.resume_protocol, font=self.button_font, bg='yellow', fg='black', height=1, width=7, relief='ridge')
        self.resume_btn.place(relx=0.3, rely=0.85, anchor='center')

        # Close button with custom style
        self.close_btn = tk.Button(master, text="Close", command=self.on_closing,
                                   font=self.button_font, bg='red', fg='white', height=1, width=7, relief='ridge')
        self.close_btn.place(relx=0.5, rely=0.85, anchor='center')

        # Status label
        self.status = tk.Label(master, text="Select COM port and connect.", fg="black", font=self.button_font)
        self.status.pack(pady=0)

        # Automatically try to connect to the first available COM port
        self.auto_connect()

    def get_serial_ports(self):
        """Returns a list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        """Refresh the list of available COM ports"""
        ports = self.get_serial_ports()
        self.port_dropdown['values'] = ports
        if ports:
            self.port_dropdown.current(0)
        self.status.config(text="COM ports refreshed.")

    def auto_connect(self):
        """Attempt to auto-connect to the first available COM port"""
        ports = self.get_serial_ports()
        if len(ports) == 1:
            self.connect_serial(auto_connect=True)
        else:
            self.status.config(text="Please select a COM port to connect.")

    def connect_serial(self, auto_connect=False):
        """Establish serial connection based on user selection or automatically"""
        if self.is_connected:
            messagebox.showinfo("Already Connected", "Serial connection is already established.")
            return
        
        if auto_connect:
            ports = self.get_serial_ports()
            if len(ports) == 1:
                selected_port = ports[0]  # Auto-select the only available port
                self.port_var.set(selected_port)
            else:
                messagebox.showwarning("Multiple Ports", "Multiple COM ports found. Please select one.")
                return
        else:
            selected_port = self.port_var.get()

        if not selected_port:
            messagebox.showwarning("No Port Selected", "Please select a COM port to connect.")
            return
        
        try:
            self.ser = serial.Serial(selected_port, 9600, timeout=1)
            time.sleep(2)  # Wait for the connection to establish
            self.is_connected = True
            self.status.config(text=f"Connected to {selected_port}.")
            messagebox.showinfo("Connected", f"Successfully connected to {selected_port}.")
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {selected_port}.\nError: {e}")
            self.status.config(text="Connection failed.")

    def send_command(self, movement, motor_duration, led_duration):
        """Send command to Arduino"""
        if not self.is_connected:
            self.status.config(text="Not connected to any COM port.")
            return
        command = f"{movement} {motor_duration} LED {led_duration}"
        try:
            self.ser.write((command + '\n').encode())
            self.status.config(text=f"Command sent: {command}")
        except serial.SerialException as e:
            self.status.config(text="Failed to send command.")
            messagebox.showerror("Serial Error", f"Failed to send command.\nError: {e}")

    def protocol_steps(self, steps):
        """Execute a list of protocol steps"""
        for step in steps:
            if self.stop_event.is_set():
                self.status.config(text="Protocol stopped.")
                return
            while self.pause_event.is_set():
                time.sleep(0.5)  # Wait while paused
            movement, motor_duration, led_duration = step
            self.send_command(movement, motor_duration, led_duration)
            time.sleep(motor_duration + 0.1)  # Wait for the duration plus a small buffer
        
        self.protocol_finished()  # Enable buttons once the protocol is finished

    def start_protocol(self):
        """Start Step 1 protocol"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a COM port first.")
            return
        if self.protocol_thread and self.protocol_thread.is_alive():
            messagebox.showwarning("Protocol Running", "A protocol is already running.")
            return
        self.status.config(text="Starting Step 1 Protocol...")
        # Define Step 1 steps
        steps = [
            ("FORWARD", 30, 0),
            ("FORWARD", 30, 0),
            ("FORWARD", 30, 0),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 0, 0)
        ]
        self.stop_event.clear()
        self.pause_event.clear()
        self.protocol_thread = Thread(target=self.protocol_steps, args=(steps,))
        self.protocol_thread.start()
        self.step1_btn.config(state=tk.DISABLED)
        self.step2_btn.config(state=tk.DISABLED)
        self.status.config(text="Step 1 Protocol running...")

    def continue_protocol(self):
        """Start Step 2 protocol"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a COM port first.")
            return
        if self.protocol_thread and self.protocol_thread.is_alive():
            messagebox.showwarning("Protocol Running", "A protocol is already running.")
            return
        self.status.config(text="Starting Step 2 Protocol...")
        # Define Step 2 steps
        steps = [
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 30),
            ("FORWARD", 30, 0),
            ("FORWARD", 30, 0),
            ("FORWARD", 30, 0),
            ("FORWARD", 0, 0)
        ]
        self.stop_event.clear()
        self.pause_event.clear()
        self.protocol_thread = Thread(target=self.protocol_steps, args=(steps,))
        self.protocol_thread.start()
        self.step1_btn.config(state=tk.DISABLED)
        self.step2_btn.config(state=tk.DISABLED)
        self.status.config(text="Step 2 Protocol running...")

    def pause_protocol(self):
        """Pause the running protocol"""
        if self.protocol_thread and self.protocol_thread.is_alive():
            self.pause_event.set()
            self.status.config(text="Protocol paused (allow command to finish)")
        else:
            messagebox.showinfo("No Protocol Running", "There is no protocol running to pause.")

    def resume_protocol(self):
        """Resume the paused protocol"""
        if self.protocol_thread and self.protocol_thread.is_alive() and self.pause_event.is_set():
            self.pause_event.clear()
            self.status.config(text="Protocol resumed.")
        else:
            messagebox.showinfo("No Protocol Paused", "There is no protocol paused to resume.")

    def protocol_finished(self):
        """Handle the end of the protocol"""
        self.status.config(text="Step Completed")
        self.step1_btn.config(state=tk.NORMAL)  # Re-enable Step 1 button
        self.step2_btn.config(state=tk.NORMAL)  # Re-enable Step 2 button

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_event.set()  # Signal the thread to stop
            if self.protocol_thread and self.protocol_thread.is_alive():
                self.protocol_thread.join()
            if self.ser and self.ser.is_open:
                self.ser.close()  # Close serial connection
            self.master.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
