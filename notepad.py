import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog, font
from spellchecker import SpellChecker  # Ensure you have installed pyspellchecker using `pip install pyspellchecker`
import os.path
import time
import threading

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Notepad App")
        self.text_widget = tk.Text(root, wrap= "word", bg= "white",
                                  fg= "black", font= ("Arial", 12), undo= True)
        self.text_widget.pack(expand= True, fill= "both")

        # Flag for dark mode state
        self.is_dark_mode = False

        # Start autosave every 5 minutes (300,000 ms)
        self.autosave_interval = 120000  # 2 mins
        self.autosave_thread = threading.Thread(target=self.autosave)
        self.autosave_thread.daemon = True  # Daemon thread so it stops with the app
        self.autosave_thread.start()

        # Spell checker object
        self.spell = SpellChecker()

        self.create_menu()

    # This function creates a menubar
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu= menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff= 0)
        menubar.add_cascade(label= "File", menu= file_menu)

        file_menu.add_command(label= "New", command= self.new_file)
        file_menu.add_command(label= "Open", command= self.open_file)
        file_menu.add_command(label= "Save", command= self.save_file)
        file_menu.add_command(label="Print", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label= "Exit", command= self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Bold", command=self.make_bold)
        edit_menu.add_command(label="Italic", command=self.make_italic)
        edit_menu.add_command(label="Font Size", command=self.font_size)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Replace", command=self.replace_text)

        # Options menu
        options_menu = tk.Menu(menubar, tearoff= 0)
        menubar.add_cascade(label= "Options", menu= options_menu)

        options_menu.add_command(label= "Background Colour", command= self.bg_color)
        options_menu.add_command(label="Light/Dark Mode", command=self.toggle_dark_mode)

        # Info menu
        info_menu = tk.Menu(menubar, tearoff= 0)
        menubar.add_cascade(label= "Info", menu= info_menu)

        info_menu.add_command(label= "About App", command= self.info)

        # Dummy menu (Adds a "spacer" to push menu functions to the right)
        dummy_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=" " * 100, menu=dummy_menu)  # Adjust the number of spaces as needed

        # Undo, Redo & Spell check menu
        menubar.add_cascade(label= "↩", command= self.text_widget.edit_undo) # Undo
        menubar.add_cascade(label= "↪", command= self.text_widget.edit_redo) # Redo
        menubar.add_cascade(label= "🔎 Check Spelling", command= self.spell_check) # 🔍

    ## FUNCTIONS IN FILE MENU
    # Function for new file
    def new_file(self):
        self.text_widget.delete(1.0, tk.END)
        self.root.title("Notepad App")

    # Function to open file
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes= [("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, file.read())
            self.current_file = file_path  # Save file path as current file
            self.root.title(f"Notepad App   -   {os.path.basename(self.current_file)}")  # Update title with file name

    # Function to save file
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension= "*.txt",
                                                 filetypes= [("Text File", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
                messagebox.showinfo("Info", "File saved successfully")
            self.current_file = file_path  # Save file path as current file
            self.root.title(f"Notepad App   -   {os.path.basename(self.current_file)}")

    # Function to Print
    def print_file(self):
        print("Printing document...")
        print(self.text_widget.get(1.0, tk.END))

    ## FUNCTIONS IN EDIT MENU
    # Function to bold text
    def make_bold(self):
        if self.text_widget.tag_ranges("sel"): # Check if there is a text selection
            current_tags = self.text_widget.tag_names("sel.first")
            if "bold" in current_tags:
                self.text_widget.tag_remove("bold", "sel.first", "sel.last")
            else:
                bold_font = font.Font(self.text_widget, self.text_widget.cget("font"))
                bold_font.configure(weight="bold")
                self.text_widget.tag_configure("bold", font=bold_font)
                self.text_widget.tag_add("bold", "sel.first", "sel.last")
        else:
            messagebox.showinfo("Info", "Please select some text to bold.")

    # Function of italic text
    def make_italic(self):
        if self.text_widget.tag_ranges("sel"): # Check if there is a text selection
            current_tags = self.text_widget.tag_names("sel.first")
            if "italic" in current_tags:
                self.text_widget.tag_remove("italic", "sel.first", "sel.last")
            else:
                italic_font = font.Font(self.text_widget, self.text_widget.cget("font"))
                italic_font.configure(slant="italic")
                self.text_widget.tag_configure("italic", font=italic_font)
                self.text_widget.tag_add("italic", "sel.first", "sel.last")
        else:
            messagebox.showinfo("Info", "Please select some text to italicize.")

    # Function to change text size
    def font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter Font Size:", parent=self.root)
        if size and self.text_widget.tag_ranges("sel"):
            selected_font = font.Font(self.text_widget, self.text_widget.cget("font"))
            selected_font.configure(size=size)

            self.text_widget.tag_configure("selected_size", font= selected_font)# Configure a tag with the new font
            self.text_widget.tag_add("selected_size", "sel.first", "sel.last") # Apply the tag to the selected text
        else:
            messagebox.showinfo("Info", "Please select some text to change its font size.")

    # Function to Find text
    def find_text(self):
        find_word = simpledialog.askstring("Find", "Enter text to find:")
        if find_word:
            self.text_widget.tag_remove("found", "1.0", tk.END)
            start_pos = "1.0"
            while True:
                start_pos = self.text_widget.search(find_word, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(find_word)}c"
                self.text_widget.tag_add("found", start_pos, end_pos)
                start_pos = end_pos
            self.text_widget.tag_config("found", foreground="blue")

    # Function to Replace text
    def replace_text(self):
        find_word = simpledialog.askstring("Replace", "Enter text to find:")
        replace_word = simpledialog.askstring("Replace", "Enter replacement text:")
        if find_word and replace_word:
            content = self.text_widget.get(1.0, tk.END)
            new_content = content.replace(find_word, replace_word)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, new_content)

    ## FUNCTIONS IN OPTIONS MENU
    # Function to change background colour
    def bg_color(self):
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.text_widget.config(bg= color)

    # Function for Dark mode toggle
    def toggle_dark_mode(self):
        if not self.is_dark_mode:
            self.text_widget.config(bg="#333333", fg="#FFFFFF", insertbackground= "white")
            self.is_dark_mode = True
        else:
            self.text_widget.config(bg="white", fg="black",  insertbackground= "black")
            self.is_dark_mode = False

    # Autosave function
    def autosave(self):
        while True:
            time.sleep(self.autosave_interval / 1000)  # Convert milliseconds to seconds
            with open("autosave.txt", "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
            print("Autosaved at", time.ctime())

    # Spell check function
    def spell_check(self):
        # Retrieve the text as a list of words
        text = self.text_widget.get("1.0", tk.END).split()
        misspelled = self.spell.unknown(text)

        # Iterate through each misspelled word
        for word in misspelled:
            # Get suggestions for the misspelled word
            suggestions = self.spell.candidates(word)
            suggestions_str = ', '.join(suggestions)

            # Display suggestions to the user
            if suggestions:
                messagebox.showinfo("Spelling Suggestion",
                                    f"The word '{word}' is misspelled.\nSuggested corrections: {suggestions_str}")

            # Highlight the misspelled word in red
            start = "1.0"
            while True:
                start = self.text_widget.search(word, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.text_widget.tag_add("misspelled", start, end)
                self.text_widget.tag_config("misspelled", foreground="red")
                start = end

    # This function gives information about the Notepad App
    def info(self):
        info_window = tk.Toplevel(self.root)  # Create a Toplevel window tied to the main root window
        info_window.title("About App")
        info_window.geometry("400x300")  # Set size of the window

        # App Information Text
        tk.Label(info_window, text="The Notepad App", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        tk.Label(info_window, text="A simple text editor for quick note-taking.", font=("Arial", 12)).pack()

        # Key Features Section
        features_text = (
            "KEY FEATURES:\n\n"
            "1. Create, open, and save text files.\n"
            "2. Customize background color.\n"
            "3. Enable light/dark mode.\n"
            "4. Spell check with suggestions.\n"
            "5. Text formatting: bold, italic, and font size adjustment.\n"
            "6. Undo/Redo, autosave every 2 minutes.\n"
            "7. Basic find and replace functionality.\n"
            "8. Print the contents of the file."
        )
        tk.Label(info_window, text=features_text, font=("Arial", 10), justify="left").pack(pady=(10, 10), padx=10)

        # Creator Information
        tk.Label(info_window, text="Created by Awad Abdulmajeed", font=("Arial", 10, "italic"), fg="blue").pack(
            pady=(10, 10))

        # Close Button
        tk.Button(info_window, text="Close", command=info_window.destroy, font=("Arial", 10)).pack(pady=(10, 5))


root = tk.Tk()
app = NotepadApp(root)

root.mainloop()
