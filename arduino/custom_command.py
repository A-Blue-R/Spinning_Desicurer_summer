import tkinter as tk
from tkinter import messagebox, ttk
import serial
import serial.tools.list_ports
import time

class LEDControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Motor & LED Control")
        master.geometry("600x400")

        # Initialize serial connection variables
        self.ser = None
        self.is_connected = False

        # COM Port Selection
        port_frame = tk.Frame(master)
        port_frame.pack(pady=20)

        port_label = tk.Label(port_frame, text="Select COM Port:", font=("Helvetica", 12))
        port_label.pack(side=tk.LEFT, padx=10)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(port_frame, textvariable=self.port_var, state="readonly", font=("Helvetica", 12))
        self.port_dropdown['values'] = self.get_serial_ports()
        if self.port_dropdown['values']:
            self.port_dropdown.current(0)
        self.port_dropdown.pack(side=tk.LEFT, padx=10)

        connect_button = tk.Button(port_frame, text="Connect", command=self.connect_serial, font=("Helvetica", 12), bg='green', fg='white')
        connect_button.pack(side=tk.LEFT, padx=10)

        # Refresh Button
        refresh_button = tk.Button(port_frame, text="Refresh", command=self.refresh_ports, font=("Helvetica", 12), bg='blue', fg='white')
        refresh_button.pack(side=tk.LEFT, padx=10)

        # Duration Entry
        input_frame = tk.Frame(master)
        input_frame.pack(pady=20)

        motor_label = tk.Label(input_frame, text="Motor Duration (seconds):", font=("Helvetica", 12))
        motor_label.pack(side=tk.LEFT, padx=10)

        self.motor_var = tk.StringVar()
        self.motor_entry = tk.Entry(input_frame, textvariable=self.motor_var, font=("Helvetica", 12), width=10)
        self.motor_entry.pack(side=tk.LEFT, padx=10)

        led_label = tk.Label(input_frame, text="LED Duration (seconds):", font=("Helvetica", 12))
        led_label.pack(side=tk.LEFT, padx=10)

        self.led_var = tk.StringVar()
        self.led_entry = tk.Entry(input_frame, textvariable=self.led_var, font=("Helvetica", 12), width=10)
        self.led_entry.pack(side=tk.LEFT, padx=10)

        # Control Buttons
        control_frame = tk.Frame(master)
        control_frame.pack(pady=20)

        self.start_button = tk.Button(control_frame, text="Send Command", command=self.send_command, font=("Helvetica", 14), bg='blue', fg='white', height=2, width=15)
        self.start_button.pack(side=tk.LEFT, padx=20)

        self.close_button = tk.Button(control_frame, text="Close", command=self.on_closing, font=("Helvetica", 14), bg='red', fg='white', height=2, width=15)
        self.close_button.pack(side=tk.LEFT, padx=20)

        # Status label
        self.status = tk.Label(master, text="Select COM port and connect.", font=("Helvetica", 12), fg="black")
        self.status.pack(pady=10)

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

    def connect_serial(self):
        """Establish serial connection based on user selection"""
        if self.is_connected:
            messagebox.showinfo("Already Connected", "Serial connection is already established.")
            return

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

    def send_command(self):
        """Send formatted command to Arduino for controlling motor and LED"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to a COM port first.")
            return

        # Get the motor and LED durations
        motor_duration = self.motor_var.get()
        led_duration = self.led_var.get()

        if not motor_duration.isdigit() or int(motor_duration) < 0:
            messagebox.showwarning("Invalid Input", "Please enter a valid positive number for motor duration.")
            return
        if not led_duration.isdigit() or int(led_duration) < 0:
            messagebox.showwarning("Invalid Input", "Please enter a valid positive number for LED duration.")
            return

        # Construct command: "FORWARD <motor_duration> LED <led_duration>"
        command = f"FORWARD {motor_duration} LED {led_duration}"
        try:
            self.ser.write((command + '\n').encode())  # Send command to Arduino
            self.status.config(text=f"Command sent: {command}")
            messagebox.showinfo("Command Sent", f"Command '{command}' successfully sent.")
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Failed to send command.\nError: {e}")
            self.status.config(text="Failed to send command.")

    def on_closing(self):
        """Handle application closing"""
        if self.ser and self.ser.is_open:
            self.ser.close()  # Close serial connection
        self.master.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = LEDControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
