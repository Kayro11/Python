import subprocess
import tkinter as tk
from tkinter import ttk

class IperfGUI:
    def __init__(self):
        self.running = False
        self.process = None
        self.create_gui()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("iPerf3 Client")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_test)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_test)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button.config(state=tk.DISABLED)
        
        # Create output area
        self.output_area = tk.Text(main_frame, height=20, width=80)
        self.output_area.grid(row=1, column=0, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_area.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.output_area.configure(yscrollcommand=scrollbar.set)

    def run_iperf(self):
        try:
            iperf_path = r"C:\Users\Administrator\Documents\My Codes\Python\Python\Piperf\core\iperf3.exe"
            self.process = subprocess.Popen(
                [iperf_path, "-c", "192.168.1.5","-t","3"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            while self.running:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.output_area.insert(tk.END, output)
                    self.output_area.see(tk.END)
                    self.root.update()
            
            # Read any remaining output
            remaining_output = self.process.stdout.read()
            if remaining_output:
                self.output_area.insert(tk.END, remaining_output)
                self.output_area.see(tk.END)
                
        except Exception as e:
            self.output_area.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def start_test(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.run_iperf()

    def stop_test(self):
        self.running = False
        if self.process:
            self.process.terminate()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IperfGUI()
    app.run()