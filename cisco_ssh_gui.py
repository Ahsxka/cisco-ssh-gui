import sys
import threading
import re
import customtkinter as ctk
import markdown
from customtkinter import CTkOptionMenu
from tkhtmlview import HTMLLabel
import cisco_ssh_py.cisco_ssh
import tkinter as tk
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

commands_map = {
    "1": "show running-config",
    "2": "show ip route",
    "3": "show ip interface brief",
    "4": "show interfaces",
    "5": "show version",
    "6": "show mac-address-table",
    "7": "show interface status",
    "8": "show vlan brief",
    "9": "show cdp neighbors",
    "10": "show tech-support",
}


class title_frame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        title_label = ctk.CTkLabel(self, text="Cisco SSH", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(padx=20, pady=20, sticky="ew")
        self.configure(fg_color="#3e9f76")


def right_callback(selected_mode, rightFrame, currentSettingsFrame):
    global mode
    mode = selected_mode
    if mode == "show":
        rightFrame.create_show_content(currentSettingsFrame)
    elif mode == "config":
        rightFrame.create_config_content(currentSettingsFrame)


class left_frame(ctk.CTkScrollableFrame):
    def __init__(self, master=None, rightFrame=None, currentSettingsFrame=None, **kwargs):
        super().__init__(master, **kwargs)

        self.ip_file_path = tk.StringVar()
        self.password_file_path = tk.StringVar()
        self.export_folder_path = tk.StringVar()

        self.grid(row=1, column=0, padx=(20, 10), pady=20, rowspan=2, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)

        self.fileTitle = ctk.CTkLabel(self, text="File select", fg_color="gray30", corner_radius=6,
                                      font=ctk.CTkFont(size=15, weight="bold"))
        self.fileTitle.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

        self.ipFileButton = ctk.CTkButton(self, text="IP File",
                                          command=lambda: self.browse_ip_file(currentSettingsFrame))
        self.ipFileButton.grid(row=1, column=0, padx=5, pady=5, sticky=None)

        self.passwordFileButton = ctk.CTkButton(self, text="Password File",
                                                command=lambda: self.browse_password_file(currentSettingsFrame))
        self.passwordFileButton.grid(row=2, column=0, padx=5, pady=5)

        self.exportFolderButton = ctk.CTkButton(self, text="Export Folder", command=lambda: self.browse_export_folder())
        self.exportFolderButton.grid(row=3, column=0, padx=5, pady=5)

        self.ipFile = ctk.CTkLabel(self, textvariable=self.ip_file_path, width=40)
        self.ipFile.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.passwordFile = ctk.CTkLabel(self, textvariable=self.password_file_path, width=40)
        self.passwordFile.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.exportFolder = ctk.CTkLabel(self, textvariable=self.export_folder_path, width=40)
        self.exportFolder.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.modeTitle = ctk.CTkLabel(self, text="Mode", fg_color="gray30", corner_radius=6,
                                      font=ctk.CTkFont(size=15, weight="bold"))
        self.modeTitle.grid(row=4, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

        self.modeMenu = ctk.CTkOptionMenu(self, dynamic_resizing=False, values=["show", "config"],
                                          command=lambda selected_mode: right_callback(selected_mode, rightFrame,
                                                                                       currentSettingsFrame))
        self.modeMenu.grid(row=5, column=0, padx=20, pady=(20, 10), columnspan=2)

        """self.optionTitle = ctk.CTkLabel(self, text="Options", fg_color="gray30", corner_radius=6,
                                        font=ctk.CTkFont(size=15, weight="bold"))
        self.optionTitle.grid(row=6, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

        self.verboseSwitch = ctk.CTkSwitch(self, text="Verbose mode")
        self.verboseSwitch.grid(row=7, column=0)"""

    def browse_ip_file(self, currentSettingsFrame):
        global ip_list
        file_path = filedialog.askopenfilename()
        self.ip_file_path.set(file_path)
        ip_list = cisco_ssh_py.cisco_ssh.read_file(self.ip_file_path.get())
        current_settings_frame.update_host_count(currentSettingsFrame)

    def browse_password_file(self, currentSettingsFrame):
        global user_pass_file
        global number_of_password
        user_pass_file = filedialog.askopenfilename()
        try:
            with open(user_pass_file, "r") as f:
                number_of_password = len(f.readlines()) - 1
        except:
            pass
        self.password_file_path.set(user_pass_file)
        current_settings_frame.update_password_count(currentSettingsFrame)

    def browse_export_folder(self):
        global export_folder
        folder_path = filedialog.askdirectory()
        self.export_folder_path.set(folder_path)
        export_folder = self.export_folder_path.get()


class right_frame(ctk.CTkFrame):
    def __init__(self, master=None, currentSettingsFrame=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command_file_path = tk.StringVar()
        self.commandFile = tk.StringVar()
        self.columnconfigure(0, weight=1)

    def create_show_content(self, currentSettingsFrame):
        if hasattr(self, "listShowCommands"):
            self.listShowCommands.destroy()
            del self.listShowCommands
        if hasattr(self, "commandFileButton"):
            self.commandFileButton.destroy()
            del self.commandFileButton
        if hasattr(self, "modeTitle"):
            self.modeTitle.destroy()
            del self.modeTitle

        try:
            if hasattr(self, "commandFile"):
                self.commandFile.destroy()
                del self.commandFile
        except:
            pass

        self.modeTitle = ctk.CTkLabel(self, text="Show commands", fg_color="gray30", corner_radius=6,
                                      font=ctk.CTkFont(size=15, weight="bold"))
        self.modeTitle.grid(row=0, column=0, padx=10, pady=10, columnspan=1, sticky="ew")
        self.listShowCommands = ctk.CTkOptionMenu(self, dynamic_resizing=False,
                                                  values=list(commands_map.values()),
                                                  command=lambda command: self.set_command_to_choice(command),
                                                  width=200)
        self.listShowCommands.grid(row=1, column=0, padx=5, pady=5)
        currentSettingsFrame.update_command_count()
        self.set_command_to_choice("show running-config")

    def create_config_content(self, currentSettingsFrame):
        if hasattr(self, "listShowCommands"):
            self.listShowCommands.destroy()
            del self.listShowCommands
        if hasattr(self, "commandFileButton"):
            self.commandFileButton.destroy()
            del self.commandFileButton
        if hasattr(self, "modeTitle"):
            self.modeTitle.destroy()
            del self.modeTitle
        try:
            if hasattr(self, "commandFile"):
                self.commandFile.destroy()
                del self.commandFile
        except:
            pass

        self.modeTitle = ctk.CTkLabel(self, text="Config commands", fg_color="gray30", corner_radius=6,
                                      font=ctk.CTkFont(size=15, weight="bold"))
        self.modeTitle.grid(row=0, column=0, padx=10, pady=10, columnspan=1, sticky="ew")

        self.commandFileButton = ctk.CTkButton(self, text="Command File",
                                               command=lambda: self.browse_command_file(currentSettingsFrame))
        self.commandFileButton.grid(row=1, column=0, padx=5, pady=5)

        self.commandFile = ctk.CTkLabel(self, textvariable=self.command_file_path, width=40)
        self.commandFile.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        currentSettingsFrame.update_command_count(config=True)

    def browse_command_file(self, currentSettingsFrame):
        global commands_list
        global finalCommandSent
        file_path = filedialog.askopenfilename()
        self.command_file_path.set(file_path)
        commands_list = cisco_ssh_py.cisco_ssh.read_file(self.command_file_path.get())
        finalCommandSent = commands_list
        currentSettingsFrame.update_command_count(config=True)

    def set_command_to_choice(self, passedCommand):
        global command
        global finalCommandSent
        command = passedCommand
        finalCommandSent = command


class current_settings_frame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.currentSettingsTitle = ctk.CTkLabel(self, text="Current settings", fg_color="gray30", corner_radius=6,
                                                 font=ctk.CTkFont(size=15, weight="bold"))
        self.currentSettingsTitle.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.numberOfHosts = ctk.CTkLabel(self, text=(f"Number of hosts : " + str(len(ip_list))))
        self.numberOfHosts.grid(row=1, column=0, sticky="w", padx=20)
        self.numberOfCommands = ctk.CTkLabel(self, text=(f"Number of commands : 1"))
        self.numberOfCommands.grid(row=2, column=0, sticky="w", padx=20)
        self.numberOfPasswords = ctk.CTkLabel(self, text=(f"Number of password to try : " + str(len(user_pass_file))))
        self.numberOfPasswords.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 20))

    def update_host_count(self):
        self.numberOfHosts.configure(text=f"Number of hosts : {len(ip_list)}")

    def update_command_count(self, config=None):
        if not config:
            self.numberOfCommands.configure(text=f"Number of commands : 1")
        else:
            if isinstance(commands_list, str):
                self.numberOfCommands.configure(text=f"Number of commands : 0")
            else:
                self.numberOfCommands.configure(text=f"Number of commands : {len(commands_list)}")

    def update_password_count(self):
        self.numberOfPasswords.configure(text=f"Number of password to try : {number_of_password}")


class run_script_frame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.call = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.runScriptTitle = ctk.CTkLabel(self, text="Run Script", fg_color="gray30", corner_radius=6,
                                           font=ctk.CTkFont(size=15, weight="bold"))

        self.runScriptTitle.grid(row=0, column=0, padx=10, pady=10, rowspan=1, sticky="new")

        # Bouton pour lancer le script
        self.startButton = ctk.CTkButton(self, text="Start", command=lambda: self.on_start_button_clicked(),
                                         state="normal")
        self.startButton.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Bouton pour arrêter le script
        self.stopButton = ctk.CTkButton(self, text="Stop", command=lambda: self.on_stop_button_clicked(),
                                        fg_color="red", hover_color="darkred")
        self.stopButton.grid(row=2, column=0, padx=10, pady=10, sticky="sew")

    def on_start_button_clicked(self):
        self.call = threading.Thread(target=lambda: cisco_ssh_py.cisco_ssh.inicio_gui(ip_list, user_pass_file, finalCommandSent,
                                                                           verbose, mode, export_folder), daemon=True,
                                     name="cisco_ssh_py")
        self.call.start()

        self.startButton.configure(state="disabled", text="Running...")
        self.check_thread()

    def check_thread(self):
        # print("####################")
        if self.call and self.call.is_alive():
            self.after(100, self.check_thread)
        else:
            self.startButton.configure(self, text="Start", command=lambda: self.on_start_button_clicked(),
                                       state="normal")

    def on_stop_button_clicked(self):
        for e in threading.enumerate():
            print("Active threads : " + e.name)
        if self.call and self.call.is_alive():
            self.call.join(timeout=1)
        self.startButton.configure(state="normal", text="Start")


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)

        if "Info" in clean_text:
            self.text_widget.insert(tk.END, clean_text, "info")
        elif "Warning" in clean_text:
            self.text_widget.insert(tk.END, clean_text, "warning")
        elif "Succes" in clean_text:
            self.text_widget.insert(tk.END, clean_text, "success")
        elif "Error" in clean_text:
            self.text_widget.insert(tk.END, clean_text, "error")
        else:
            self.text_widget.insert(tk.END, clean_text)

        self.text_widget.see(tk.END)

    def flush(self):
        pass


class help_label(HTMLLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Read the content of the README.md file
        with open("README.md", "r") as readme_file:
            readme_content = readme_file.read()

        # Convert Markdown to HTML and coloring text
        html_content = markdown.markdown(readme_content)
        html_content = re.sub(r'<p>', r'<p style="color:lightgrey;">', html_content)
        html_content = re.sub(r'<li>', r'<li style="color:lightgrey;">', html_content)
        html_content = re.sub(r'<h1>', r'<h1 style="color:lightgrey;">', html_content)
        html_content = re.sub(r'<h2>', r'<h2 style="color:lightgrey;">', html_content)
        html_content = re.sub(r'<h3>', r'<h3 style="color:lightgrey;">', html_content)

        self.set_html(html=html_content)


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("Parameters")
        self.add("Logs")
        self.add("Help")
        self.tab("Parameters").columnconfigure((0, 1), weight=1)
        self.tab("Parameters").rowconfigure(0, weight=1)
        self.tab("Logs").columnconfigure(0, weight=1)
        self.tab("Logs").rowconfigure(0, weight=1)
        self.tab("Help").columnconfigure(0, weight=1)
        self.tab("Help").rowconfigure(0, weight=1)

        rightFrame = right_frame(master=self.tab("Parameters"), fg_color="#242424")
        rightFrame.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), rowspan=1, columnspan=2, sticky="nsew")

        currentSettingsFrame = current_settings_frame(master=self.tab("Parameters"), fg_color="#242424")
        currentSettingsFrame.grid(row=1, column=1, padx=(10, 10), pady=(10, 20), rowspan=1, sticky="nsew")

        leftFrame = left_frame(master=self.tab("Parameters"), rightFrame=rightFrame,
                               currentSettingsFrame=currentSettingsFrame, fg_color="#242424")
        leftFrame.grid(row=0, column=0, sticky="nsew")
        right_callback("show", rightFrame, currentSettingsFrame)

        runScriptFrame = run_script_frame(master=self.tab("Parameters"), fg_color="#242424")
        runScriptFrame.grid(row=1, column=2, padx=(10, 20), pady=(10, 20), sticky="nsew")

        self.logs_text = ctk.CTkTextbox(self.tab("Logs"), fg_color="#2b2b2b", wrap="word")
        self.logs_text.columnconfigure(0, weight=1)
        self.logs_text.grid(row=0, column=0, sticky="nsew")

        self.logs_text.tag_config("success", foreground="#4bc313")
        self.logs_text.tag_config("error", foreground="#ff3f4e")
        self.logs_text.tag_config("info", foreground="#1fafff")
        self.logs_text.tag_config("warning", foreground="#e4be04")

        helpLabel = help_label(self.tab("Help"), background="#2b2b2b")
        helpLabel.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        # Redirection de stdout vers le widget de texte
        sys.stdout = StdoutRedirector(self.logs_text)


class App(ctk.CTk):
    showCommands: CTkOptionMenu

    def __init__(self):
        super().__init__()

        self.title("Cisco SSH")
        self.geometry(f"{1100}x{580}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title = title_frame()
        self.title.grid(row=0, column=0, pady=20,)

        self.tab_view = MyTabView(master=self)  # , fg_color="#242424")
        self.tab_view.grid(row=1, column=0, padx=20,  sticky="nsew")


ip_list = []
user_pass_file = ""
command = ""
commands_list = []
finalCommandSent = ""
verbose = "y"
mode = "show"
export_folder = ""

app = App()
app.mainloop()
