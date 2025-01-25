import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import hashlib
from PIL import Image, ImageTk, ImageDraw
from database import (verify_user, get_all_professors, get_professor_by_name,
                     delete_professor, update_professor_picture, get_all_users,
                     add_user, delete_user, add_professor, get_professor_schedule,
                     add_schedule as db_add_schedule, delete_schedule, get_schedules_by_day,
                     update_professor_schedule, update_professor, close_db,
                     update_single_schedule, get_db_connection)
from tkinter import filedialog
import shutil
import time
import json
import re

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Professor Checker System")
        self.root.geometry("1000x600")
        
        # Initialize variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        
        # Define colors
        self.colors = {
            'primary': '#8B0000',      # Dark Red
            'secondary': '#B22222',    # Light Red
            'background': '#f8f9fa',   # Light Gray
            'white': '#ffffff',
            'text': '#2d3436',         # Dark Gray
            'border': '#e0e0e0',        # Light Border
            'light_gray': '#E0E0E0'   # Light Gray for sidebar
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Add credentials file path
        self.credentials_file = 'user_credentials.json'
        
        # Create main container
        self.setup_main_container()
        
        # Initialize or load credentials
        self.initialize_credentials()
        
        # Bind destroy event
        self.root.protocol("WM_DELETE_WINDOW", self.on_destroy)
        
        # Try to load remembered credentials
        if os.path.exists('remembered_login.txt'):
            try:
                with open('remembered_login.txt', 'r') as f:
                    saved_username = f.readline().strip()
                    saved_hash = f.readline().strip()
                    if saved_username and saved_hash:
                        # Load credentials file to verify saved hash
                        if os.path.exists(self.credentials_file):
                            with open(self.credentials_file, 'r') as cred_file:
                                credentials = json.load(cred_file)
                                if saved_username in credentials:
                                    stored_user = credentials[saved_username]
                                    if isinstance(stored_user, dict) and stored_user.get('password') == saved_hash:
                                        self.username_var.set(saved_username)
                                        # Don't set the password var since we only have the hash
                                        self.remember_var.set(True)
            except Exception as e:
                # Remove corrupted remember file
                try:
                    os.remove('remembered_login.txt')
                except:
                    pass
        
    def hash_password(self, password):
        """Create a simple hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        """Handle login attempt"""
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            
            if not username or not password:
                messagebox.showwarning("Warning", "Please fill in all fields")
                return
                
            # Verify credentials
            is_verified, role = verify_user(username, password)
            
            if is_verified:
                self.root.withdraw()  # Hide login window
                
                # Open appropriate dashboard based on role
                if role == 'admin':
                    admin_root = tk.Toplevel()
                    AdminDashboard(admin_root, username)
                    admin_root.protocol("WM_DELETE_WINDOW", 
                        lambda: self.on_dashboard_close(admin_root))
                else:
                    student_root = tk.Toplevel()
                    StudentPanel(student_root, username)
                    student_root.protocol("WM_DELETE_WINDOW", 
                        lambda: self.on_dashboard_close(student_root))
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            
    def setup_main_container(self):
        # Step 1: Create main frame with padding
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=30)
        
        # Step 2: Create left panel (Welcome section)
        self.setup_left_panel()
        
        # Step 3: Create right panel (Login form)
        self.setup_right_panel()
        
    def setup_left_panel(self):
        # Step 4: Create and style left panel
        self.left_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 25))
        
        # Welcome text container
        welcome_frame = tk.Frame(self.left_frame, bg=self.colors['background'])
        welcome_frame.pack(expand=True, fill=tk.BOTH, pady=(50, 0))
        
        # Welcome messages
        tk.Label(welcome_frame, 
                text="Welcome to", 
                font=('Arial', 24),
                bg=self.colors['background'],
                fg=self.colors['text']).pack()
                
        tk.Label(welcome_frame,
                text="ProfBook",
                font=('Arial', 32, 'bold'),
                bg=self.colors['background'],
                fg=self.colors['primary']).pack(pady=(10, 0))
                
        tk.Label(welcome_frame,
                text="One way to connect with Professors",
                font=('Arial', 12),
                bg=self.colors['background'],
                fg=self.colors['text']).pack(pady=(20, 0))
        
    def setup_right_panel(self):
        # Step 5: Create and style right panel
        self.right_frame = tk.Frame(self.main_frame, 
                                  bg=self.colors['white'],
                                  highlightthickness=1,
                                  highlightbackground=self.colors['border'])
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(25, 0))
        
        # Login form container
        login_container = tk.Frame(self.right_frame, bg=self.colors['white'])
        login_container.pack(expand=True, fill=tk.BOTH, padx=40, pady=50)
        
        # Login header
        tk.Label(login_container,
                text="Login to Your Account",
                font=('Arial', 20, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Username field
        self.username_entry = self.create_input_field(login_container, "Username")
        
        # Password field with show/hide button
        self.create_password_field(login_container)
        
        # Login button
        self.create_login_button(login_container)
        
        # Separator
        self.create_separator(login_container)
        
        # Register button
        self.create_register_button(login_container)
        
    def create_input_field(self, parent, label_text):
        tk.Label(parent,
                text=label_text,
                font=('Arial', 12),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(anchor='w')
                
        entry = tk.Entry(parent,
                        font=('Arial', 12),
                        bg=self.colors['background'],
                        relief=tk.FLAT,
                        highlightthickness=1,
                        highlightbackground=self.colors['border'],
                        textvariable=self.username_var if label_text == "Username" else None)
        entry.pack(fill=tk.X, pady=(5, 20), ipady=8)
        return entry
        
    def create_password_field(self, parent):
        # Password label frame
        password_label_frame = tk.Frame(parent, bg=self.colors['white'])
        password_label_frame.pack(fill=tk.X)
        
        tk.Label(password_label_frame,
                text="Password",
                font=('Arial', 12),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
                
        # Show/Hide password button
        self.show_password_btn = tk.Button(password_label_frame,
                                         text="Show",
                                         font=('Arial', 10),
                                         bg=self.colors['white'],
                                         fg=self.colors['primary'],
                                         bd=0,
                                         cursor='hand2',
                                         activebackground=self.colors['white'],
                                         activeforeground=self.colors['secondary'],
                                         command=self.toggle_password)
        self.show_password_btn.pack(side=tk.RIGHT)
        
        # Password entry
        self.password_entry = tk.Entry(parent,
                                     font=('Arial', 12),
                                     bg=self.colors['background'],
                                     show='*',
                                     relief=tk.FLAT,
                                     highlightthickness=1,
                                     highlightbackground=self.colors['border'],
                                     textvariable=self.password_var)
        self.password_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)
        
        # Create remember password frame
        remember_frame = tk.Frame(parent, bg=self.colors['white'])
        remember_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Add remember password checkbox
        remember_checkbox = tk.Checkbutton(remember_frame,
                                         text="Remember Password",
                                         variable=self.remember_var,
                                         bg=self.colors['white'],
                                         fg=self.colors['text'],
                                         activebackground=self.colors['white'],
                                         activeforeground=self.colors['primary'],
                                         selectcolor=self.colors['white'])
        remember_checkbox.pack(side=tk.LEFT)
        
        # Add Forgot Password link
        forgot_password_btn = tk.Button(remember_frame,
                                      text="Forgot Password?",
                                      font=('Arial', 10),
                                      bg=self.colors['white'],
                                      fg=self.colors['primary'],
                                      bd=0,
                                      cursor='hand2',
                                      activebackground=self.colors['white'],
                                      activeforeground=self.colors['secondary'],
                                      command=self.show_forgot_password)
        forgot_password_btn.pack(side=tk.RIGHT)
        
    def create_login_button(self, parent):
        self.login_btn = tk.Button(parent,
                                 text="LOGIN",
                                 font=('Arial', 12, 'bold'),
                                 bg=self.colors['primary'],
                                 fg=self.colors['white'],
                                 activebackground=self.colors['secondary'],
                                 activeforeground=self.colors['white'],
                                 cursor='hand2',
                                 relief=tk.FLAT,
                                 command=self.login)
        self.login_btn.pack(fill=tk.X, ipady=10)
        
        # Add hover effect
        self.login_btn.bind('<Enter>', lambda e: self.login_btn.config(bg=self.colors['secondary']))
        self.login_btn.bind('<Leave>', lambda e: self.login_btn.config(bg=self.colors['primary']))
        
    def create_separator(self, parent):
        separator_frame = tk.Frame(parent, bg=self.colors['white'])
        separator_frame.pack(fill=tk.X, pady=30)
        
        tk.Frame(separator_frame, bg=self.colors['border'], height=1).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        tk.Label(separator_frame, text="OR", bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        tk.Frame(separator_frame, bg=self.colors['border'], height=1).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))
        
    def create_register_button(self, parent):
        self.register_btn = tk.Button(parent,
                                    text="REGISTER",
                                    font=('Arial', 12),
                                    bg=self.colors['white'],
                                    fg=self.colors['primary'],
                                    activebackground=self.colors['background'],
                                    activeforeground=self.colors['primary'],
                                    cursor='hand2',
                                    relief=tk.FLAT,
                                    command=self.show_register)
        self.register_btn.pack(fill=tk.X, ipady=10)
        
        # Add hover effect
        self.register_btn.bind('<Enter>', lambda e: self.register_btn.config(bg=self.colors['background']))
        self.register_btn.bind('<Leave>', lambda e: self.register_btn.config(bg=self.colors['white']))
        
    def toggle_password(self):
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
            self.show_password_btn.config(text='Hide')
        else:
            self.password_entry.config(show='*')
            self.show_password_btn.config(text='Show')
            
    def initialize_credentials(self):
        """Initialize or load user credentials"""
        try:
            # Create new credentials file if it doesn't exist
            if not os.path.exists(self.credentials_file):
                default_credentials = {
                    "admin": {
                        "password": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
                        "role": "admin"
                    },
                    "student": {
                        "password": self.hash_password("student123"),
                        "role": "student"
                    }
                }
                with open(self.credentials_file, 'w') as f:
                    json.dump(default_credentials, f, indent=4)
                return

            # Load and validate existing credentials
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)

            # Validate credentials format
            if not isinstance(credentials, dict):
                raise ValueError("Invalid credentials format")

            # Ensure admin and student accounts exist with correct format
            credentials["admin"] = {
                "password": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
                "role": "admin"
            }
            
            credentials["student"] = {
                "password": self.hash_password("student123"),
                "role": "student"
            }

            # Save the validated/fixed credentials
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=4)

        except Exception as e:
            # If there's any error, recreate the credentials file
            default_credentials = {
                "admin": {
                    "password": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
                    "role": "admin"
                },
                "student": {
                    "password": self.hash_password("student123"),
                    "role": "student"
                }
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(default_credentials, f, indent=4)
            messagebox.showwarning("Warning", "Credentials file has been reset.")
    
    def hash_password(self, password):
        """Create a simple hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def show_register(self):
        # Hide main frame
        self.main_frame.destroy()
        
        # Create registration frame
        self.register_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.register_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=30)
        
        # Title
        tk.Label(self.register_frame,
                text="Create New Account",
                font=('Arial', 24, 'bold'),
                bg=self.colors['background'],
                fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Username field
        self.reg_username_entry = self.create_input_field(self.register_frame, "Username")
        
        # Email field
        self.reg_email_entry = self.create_input_field(self.register_frame, "Email")
        
        # Password fields
        self.reg_password_entry = self.create_input_field(self.register_frame, "Password")
        self.reg_password_entry.config(show='*')
        
        self.reg_confirm_entry = self.create_input_field(self.register_frame, "Confirm Password")
        self.reg_confirm_entry.config(show='*')
        
        # Register button
        register_btn = tk.Button(self.register_frame,
                               text="REGISTER",
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['primary'],
                               fg=self.colors['white'],
                               activebackground=self.colors['secondary'],
                               activeforeground=self.colors['white'],
                               cursor='hand2',
                               relief=tk.FLAT,
                               command=self.register)
        register_btn.pack(fill=tk.X, ipady=10, pady=(20, 10))
        
        # Back to login button
        back_btn = tk.Button(self.register_frame,
                            text="BACK TO LOGIN",
                            font=('Arial', 12),
                            bg=self.colors['white'],
                            fg=self.colors['primary'],
                            activebackground=self.colors['background'],
                            activeforeground=self.colors['primary'],
                            cursor='hand2',
                            relief=tk.FLAT,
                            command=self.show_login)
        back_btn.pack(fill=tk.X, ipady=10)
        
        # Add hover effects
        for btn, from_color, to_color in [(register_btn, self.colors['primary'], self.colors['secondary']),
                                         (back_btn, self.colors['white'], self.colors['background'])]:
            btn.bind('<Enter>', lambda e, b=btn, c=to_color: b.config(bg=c))
            btn.bind('<Leave>', lambda e, b=btn, c=from_color: b.config(bg=c))
            
    def show_login(self):
        # Remove registration frame
        self.register_frame.destroy()
        # Recreate login interface
        self.setup_main_container()
        
    def register(self):
        """Handle user registration"""
        username = self.reg_username_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        
        # Validate input
        if not username or not password or not confirm_password or not email:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if username == "admin":
            messagebox.showerror("Error", "Cannot register with username 'admin'")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if not '@' in email or not '.' in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
            
        try:
            # Add user to database with email
            if add_user(username, password, email, "student"):
                messagebox.showinfo("Success", "Registration successful! You can now login.")
                self.show_login()
            else:
                messagebox.showerror("Error", "Username already exists")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def on_destroy(self):
        # Clean up any resources if needed
        self.root.destroy()

    def show_forgot_password(self):
        # Create password reset window
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("400x300")
        reset_window.configure(bg=self.colors['background'])
        
        # Center the window
        reset_window.transient(self.root)
        reset_window.grab_set()
        
        # Create main frame
        main_frame = tk.Frame(reset_window, bg=self.colors['white'],
                            highlightthickness=1,
                            highlightbackground=self.colors['border'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main_frame,
                text="Reset Password",
                font=('Arial', 16, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=20)
        
        # Email entry
        tk.Label(main_frame,
                text="Enter your email address:",
                font=('Arial', 12),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(anchor='w', padx=20)
        
        email_entry = tk.Entry(main_frame,
                             font=('Arial', 12),
                             bg=self.colors['background'],
                             relief=tk.FLAT,
                             highlightthickness=1,
                             highlightbackground=self.colors['border'])
        email_entry.pack(fill=tk.X, padx=20, pady=(5, 20), ipady=8)
        
        def submit_reset():
            email = email_entry.get().strip()
            if not email:
                messagebox.showerror("Error", "Please enter your email address")
                return
            
            # Here you would typically:
            # 1. Verify if email exists in your database
            # 2. Generate a reset token
            # 3. Send reset email to user
            # For now, we'll just show a success message
            messagebox.showinfo("Success", 
                              "If an account exists with this email, "
                              "you will receive password reset instructions shortly.")
            reset_window.destroy()
        
        # Submit button
        submit_btn = tk.Button(main_frame,
                             text="Send Reset Link",
                             font=('Arial', 12, 'bold'),
                             bg=self.colors['primary'],
                             fg=self.colors['white'],
                             activebackground=self.colors['secondary'],
                             activeforeground=self.colors['white'],
                             cursor='hand2',
                             relief=tk.FLAT,
                             command=submit_reset)
        submit_btn.pack(fill=tk.X, padx=20, pady=20, ipady=8)
        
        # Add hover effect
        submit_btn.bind('<Enter>', lambda e: submit_btn.config(bg=self.colors['secondary']))
        submit_btn.bind('<Leave>', lambda e: submit_btn.config(bg=self.colors['primary']))

class Professor:
    def __init__(self, Name, Department, Contact, Email, Picture=None):
        self.Name = Name
        self.Department = Department
        self.Contact = Contact
        self.Email = Email
        self.Schedule = []  # List of schedules
        self.Picture = Picture if Picture else "N/A"


class ProfessorDirectory:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Create header
        self.create_header()
        
        # Create search bar
        self.create_search_bar()
        
        # Create tree view
        self.setup_tree()
        
        # Initialize professors data
        self.professors = []
        self.load_professors_from_file()

    def setup_tree(self):
        # Create tree view frame
        tree_frame = tk.Frame(self.main_frame, bg=self.colors['white'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview
        columns = ("Name", "Department", "Contact", "Email")
        self.prof_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure column widths and headings
        widths = [200, 200, 150, 250]
        for col, width in zip(columns, widths):
            self.prof_tree.column(col, width=width, minwidth=width)
            self.prof_tree.heading(col, text=col)
        
        # Style configuration for headers
        style = ttk.Style()
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=('Arial', 12, 'bold'))
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.prof_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.prof_tree.xview)
        self.prof_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        self.prof_tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        
    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame,
                text="List of Professors",
                font=('Arial', 24, 'bold'),
                bg=self.colors['background'],
                fg=self.colors['primary']).pack(side=tk.LEFT)
        
    def create_search_bar(self):
        search_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=('Arial', 12),
                              bg=self.colors['white'],
                              fg=self.colors['text'],
                              relief=tk.FLAT,
                              highlightthickness=1,
                              highlightbackground=self.colors['border'])
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        search_button = tk.Button(search_frame,
                                text="Search",
                                font=('Arial', 12),
                                bg=self.colors['primary'],
                                fg=self.colors['white'],
                                activebackground=self.colors['secondary'],
                                activeforeground=self.colors['white'],
                                cursor='hand2',
                                relief=tk.FLAT,
                                command=self.search_professors)
        search_button.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=8)
        
    def create_logout_button(self):
        self.logout_button = tk.Button(self.main_frame,
                                     text="LOGOUT",
                                     font=('Arial', 12),
                                     bg=self.colors['primary'],
                                     fg=self.colors['white'],
                                     command=self.logout)
        self.logout_button.pack(pady=(20, 0), ipadx=30, ipady=8)
        
    def display_professors(self, professors=None):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        if professors is None:
            professors = self.professors
            
        for professor in professors:
            # Create frame for each professor
            professor_frame = tk.Frame(self.list_frame, bg=self.colors['white'], cursor='hand2')
            professor_frame.pack(fill=tk.X, pady=10, padx=20)
            
            # Add picture frame
            picture_frame = tk.Frame(professor_frame, bg=self.colors['white'])
            picture_frame.pack(side=tk.LEFT, padx=(10, 20))
            
            # Load and display picture
            try:
                if professor.Picture and professor.Picture != "N/A":
                    image = Image.open(professor.Picture)
                    image = image.resize((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    photo_label = tk.Label(picture_frame, image=photo, bg=self.colors['white'])
                    photo_label.image = photo  # Keep a reference!
                else:
                    # Create a default image with initials if no picture
                    na_image = Image.new('RGB', (100, 100), color='lightgray')
                    self.default_photo = ImageTk.PhotoImage(na_image)
                    photo_label = tk.Label(picture_frame, image=self.default_photo, bg=self.colors['white'])
                    photo_label.image = self.default_photo
            except Exception as e:
                # If there's any error loading the image, use default
                na_image = Image.new('RGB', (100, 100), color='lightgray')
                self.default_photo = ImageTk.PhotoImage(na_image)
                photo_label = tk.Label(picture_frame, image=self.default_photo, bg=self.colors['white'])
                photo_label.image = self.default_photo
            
            photo_label.pack()
            
            # Add name label
            name_label = tk.Label(professor_frame,
                                text=professor.Name,
                                font=('Arial', 14, 'bold'),
                                bg=self.colors['white'],
                                fg=self.colors['text'])
            name_label.pack(side=tk.LEFT, pady=10)
            
            # Bind click event to show profile
            def bind_double_click(widget, professor):
                widget.bind('<Double-1>', lambda e, p=professor: self._show_profile(p))
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Frame, tk.Label)):
                        child.bind('<Double-1>', lambda e, p=professor: self._show_profile(p))
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                subchild.bind('<Double-1>', lambda e, p=professor: self._show_profile(p))
            
            professor_frame.bind('<Enter>', lambda e, frame=professor_frame: frame.configure(bg='#f5f5f5'))
            professor_frame.bind('<Leave>', lambda e, frame=professor_frame: frame.configure(bg=self.colors['white']))
            bind_double_click(professor_frame, professor)
        
    def _mask_contact(self, contact):
        # Return actual contact number
        return contact

    def _mask_email(self, email):
        # Return actual email
        return email
        
    def _show_profile(self, professor):
        # Create profile window
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Professor Profile - {professor.Name}")
        profile_window.geometry("1000x700")  # Made window larger
        profile_window.configure(bg=self.colors['background'])
        
        # Create main content frame
        content_frame = tk.Frame(profile_window, bg=self.colors['white'],
                               highlightthickness=1,
                               highlightbackground=self.colors['border'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Top section - Basic Info with Picture
        top_frame = tk.Frame(content_frame, bg=self.colors['white'])
        top_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Picture on the left
        picture_frame = tk.Frame(top_frame, bg=self.colors['white'])
        picture_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        if professor.Picture == "N/A":
            na_image = Image.new('RGB', (100, 100), color='lightgray')
            self.default_photo = ImageTk.PhotoImage(na_image)
            photo_label = tk.Label(picture_frame, image=self.default_photo, bg=self.colors['white'])
            photo_label.image = self.default_photo
        else:
            try:
                img = Image.open(professor.Picture)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                photo_label = tk.Label(picture_frame, image=photo, bg=self.colors['white'])
                photo_label.image = photo
            except:
                na_image = Image.new('RGB', (100, 100), color='lightgray')
                self.default_photo = ImageTk.PhotoImage(na_image)
                photo_label = tk.Label(picture_frame, image=self.default_photo, bg=self.colors['white'])
                photo_label.image = self.default_photo
        photo_label.pack()
        
        # Information on the right
        info_frame = tk.Frame(top_frame, bg=self.colors['white'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Name and Department
        tk.Label(info_frame,
                text=professor.Name,
                font=('Arial', 24, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(anchor='w')
        
        tk.Label(info_frame,
                text=professor.Department,
                font=('Arial', 16),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(anchor='w', pady=(5, 20))
        
        # Contact and Email
        contact_frame = tk.Frame(info_frame, bg=self.colors['white'])
        contact_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(contact_frame,
                text="Contact: ",
                font=('Arial', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        
        tk.Label(contact_frame,
                text=self._mask_contact(professor.Contact),
                font=('Arial', 12),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        
        email_frame = tk.Frame(info_frame, bg=self.colors['white'])
        email_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(email_frame,
                text="Email: ",
                font=('Arial', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        
        tk.Label(email_frame,
                text=self._mask_email(professor.Email),
                font=('Arial', 12),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, padx=20, pady=20)
        
        # Schedule section with border
        schedule_frame = tk.Frame(content_frame, bg=self.colors['white'], bd=1, relief=tk.SOLID)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20,0))
        
        # Schedule header
        tk.Label(schedule_frame,
                text="Class Schedule",
                font=('Arial', 18, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text']).pack(anchor='w', pady=(10, 20), padx=10)
        
        # Create Treeview for schedule
        columns = ("Subject", "Day", "Time")
        tree = ttk.Treeview(schedule_frame, columns=columns, show='headings', height=10)
        
        # Configure column widths and headings
        widths = [400, 200, 200]
        for col, width in zip(columns, widths):
            tree.column(col, width=width, minwidth=width)
            tree.heading(col, text=col)
        
        # Style configuration for headers
        style = ttk.Style()
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=('Arial', 12, 'bold'))
        
        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        
        # Insert schedule data
        if professor.Schedule:
            for schedule in professor.Schedule:
                tree.insert('', tk.END, values=(
                    schedule['subject'],
                    schedule['day'],
                    schedule['time']
                ))
        else:
            tree.insert('', tk.END, values=('No schedules available', '', ''))
        
        # Close button at bottom
        close_btn = tk.Button(profile_window,
                            text="Close",
                            font=('Arial', 12),
                            bg=self.colors['primary'],
                            fg=self.colors['white'],
                            activebackground='#990000',  # Darker red
                            activeforeground=self.colors['white'],
                            cursor='hand2',
                            relief=tk.FLAT,
                            command=profile_window.destroy)
        close_btn.pack(pady=20, ipadx=30, ipady=8)
        
        # Add hover effect to close button
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#990000'))  # Darker red
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg=self.colors['primary']))
        
    def search_professors(self):
        query = self.search_var.get().lower()
        results = [professor for professor in self.professors if query in professor.Name.lower() or query in professor.Department.lower() or query in professor.Contact.lower() or query in professor.Email.lower()]
        self.display_professors(results)
        
    def logout(self):
        self.main_frame.destroy()
        LoginWindow(self.root)

    def delete_professor(self):
        selected = self.prof_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a professor to delete")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this professor?"):
            return
            
        professor_to_remove = self.prof_tree.item(selected[0])['values'][0]
        
        try:
            # Connect to database
            conn = sqlite3.connect('profbook.db')
            cursor = conn.cursor()
            
            # Get professor ID
            cursor.execute('SELECT id FROM professors WHERE name = ?', (professor_to_remove,))
            prof_id = cursor.fetchone()
            
            if prof_id:
                # Delete schedules first (due to foreign key constraint)
                cursor.execute('DELETE FROM schedules WHERE professor_id = ?', (prof_id[0],))
                # Then delete the professor
                cursor.execute('DELETE FROM professors WHERE id = ?', (prof_id[0],))
                conn.commit()
                
                # Update the tree view
                self.prof_tree.delete(selected[0])
                messagebox.showinfo("Success", "Professor deleted successfully")
            else:
                messagebox.showerror("Error", "Professor not found in database")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    def load_professors_from_file(self):
        try:
            # Get professors from database
            professors = get_all_professors()
            
            # Clear existing items in tree
            for item in self.prof_tree.get_children():
                self.prof_tree.delete(item)
            
            # Add to tree view
            for prof in professors:
                try:
                    values = (
                        prof['name'],
                        prof['department'],  # Changed from 'title' to 'department'
                        prof['contact'],
                        prof['email']
                    )
                    self.prof_tree.insert("", "end", values=values)
                except Exception as e:
                    print(f"Error loading professor: {str(e)}")
                    continue
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load professors: {str(e)}")

class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to ProfBook")
        self.root.geometry("800x500")
        
        # Define colors (same as other windows)
        self.colors = {
            'primary': '#8B0000',      # Dark Red
            'secondary': '#B22222',    # Light Red
            'background': '#f8f9fa',   # Light Gray
            'white': '#ffffff',
            'text': '#2d3436',         # Dark Gray
            'border': '#e0e0e0',        # Light Border
            'light_gray': '#E0E0E0'   # Light Gray for sidebar
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Create main container with fixed size
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'], width=800, height=500)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.main_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Content frame for centered alignment
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors['background'], width=600)
        self.content_frame.pack(expand=True, pady=(50, 0))
        
        # Create all widgets with initial transparency
        self.widgets = []
        
        # Welcome message
        welcome_label = tk.Label(self.content_frame,
                text="Welcome to ProfBook",
                font=('Arial', 32, 'bold'),
                bg=self.colors['background'],
                fg=self.colors['background'],  # Start with background color (invisible)
                wraplength=600)
        welcome_label.pack(pady=(0, 20))
        self.widgets.append((welcome_label, self.colors['primary']))
        
        # Subtitle
        subtitle_label = tk.Label(self.content_frame,
                text="Student Management System",
                font=('Arial', 18),
                bg=self.colors['background'],
                fg=self.colors['background'],
                wraplength=600)
        subtitle_label.pack(pady=(0, 40))
        self.widgets.append((subtitle_label, self.colors['text']))
        
        # Description
        description = """ProfBook is your comprehensive solution for managing 
student-professor interactions and schedules.

Get started by clicking the button below."""
        desc_label = tk.Label(self.content_frame,
                text=description,
                font=('Arial', 12),
                bg=self.colors['background'],
                fg=self.colors['background'],
                justify=tk.CENTER,
                wraplength=600)
        desc_label.pack(pady=(0, 40))
        self.widgets.append((desc_label, self.colors['text']))
        
        # Get Started button
        self.start_btn = tk.Button(self.content_frame,
                            text="Get Started",
                            font=('Arial', 14, 'bold'),
                            bg=self.colors['primary'],
                            fg=self.colors['white'],
                            activebackground=self.colors['secondary'],
                            activeforeground=self.colors['white'],
                            cursor='hand2',
                            relief=tk.FLAT,
                            width=15,  # Set fixed width
                            pady=5,    # Add vertical padding
                            command=self.show_login)
        self.start_btn.pack(pady=20)
        self.start_btn.configure(bg=self.colors['background'])  # Start invisible
        
        # Add hover effect
        self.start_btn.bind('<Enter>', self.on_hover_enter)
        self.start_btn.bind('<Leave>', self.on_hover_leave)
        
        # Center the window
        self.center_window()
        
        # Start fade-in animation
        self.fade_in(0)
        
        # Start button pulse animation
        self.pulse_button()
    
    def fade_in(self, index, alpha=0):
        if not hasattr(self, '_animation_active'):
            self._animation_active = True
            
        if not self._animation_active:
            return
            
        if index < len(self.widgets):
            widget, final_color = self.widgets[index]
            if alpha < 1:
                current_color = self.interpolate_color(self.colors['background'], final_color, alpha)
                widget.configure(fg=current_color)
                self.root.after(20, self._continue_fade_in, index, alpha + 0.1)
            else:
                widget.configure(fg=final_color)
                self.root.after(100, self._continue_fade_in, index + 1, 0)
        else:
            self._start_button_fade()
    
    def _continue_fade_in(self, index, alpha):
        if hasattr(self, '_animation_active') and self._animation_active:
            self.fade_in(index, alpha)
    
    def _start_button_fade(self):
        if hasattr(self, '_animation_active') and self._animation_active:
            self.fade_in_button(0)
    
    def fade_in_button(self, alpha):
        if not hasattr(self, '_animation_active'):
            return
            
        if alpha < 1:
            current_color = self.interpolate_color(self.colors['background'], self.colors['primary'], alpha)
            self.start_btn.configure(bg=current_color)
            self.root.after(20, self._continue_button_fade, alpha + 0.1)
        else:
            self._start_pulse_animation()
    
    def _continue_button_fade(self, alpha):
        if hasattr(self, '_animation_active') and self._animation_active:
            self.fade_in_button(alpha)
    
    def pulse_button(self):
        self._pulse_scale = 1.0
        self._pulse_increasing = True
        self._animate_pulse()
    
    def _animate_pulse(self):
        if not hasattr(self, '_animation_active') or not self._animation_active:
            return
            
        if not hasattr(self, 'start_btn') or not self.start_btn.winfo_exists():
            return
            
        if self._pulse_increasing and self._pulse_scale < 1.1:
            self._pulse_scale += 0.005
        elif not self._pulse_increasing and self._pulse_scale > 1.0:
            self._pulse_scale -= 0.005
        else:
            self._pulse_increasing = not self._pulse_increasing
            
        new_font = ('Arial', int(14 * self._pulse_scale), 'bold')
        self.start_btn.configure(font=new_font)
        
        self.root.after(50, self._animate_pulse)
    
    def _start_pulse_animation(self):
        if hasattr(self, '_animation_active') and self._animation_active:
            self.pulse_button()
            
    def on_hover_enter(self, event):
        self.start_btn.config(bg=self.colors['secondary'])
    
    def on_hover_leave(self, event):
        self.start_btn.config(bg=self.colors['primary'])
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        login_window = tk.Toplevel()
        login_app = LoginWindow(login_window)
        self.root.withdraw()  # Hide welcome window
        
        def on_login_close():
            login_window.destroy()
            self.root.deiconify()  # Show welcome window again
            
        login_window.protocol("WM_DELETE_WINDOW", on_login_close)
    
    def on_login_close(self, login_window):
        login_window.destroy()
        self.root.destroy()

    def interpolate_color(self, start_color, end_color, alpha):
        """Interpolate between two hex colors for fade animation
        
        Args:
            start_color (str): Starting hex color code
            end_color (str): Ending hex color code
            alpha (float): Interpolation factor between 0 and 1
            
        Returns:
            str: Interpolated hex color
        """
        # Convert hex to RGB
        start_rgb = tuple(int(start_color[i:i+2], 16) for i in (1, 3, 5))
        end_rgb = tuple(int(end_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Interpolate between colors
        current_rgb = tuple(
            int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * alpha)
            for i in range(3)
        )
        
        # Convert back to hex
        return f'#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}'


class AdminDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Setup colors and styles for the dashboard"""
        self.colors = {
            'primary': '#8B0000',  # Dark red
            'primary_dark': '#660000',  # Darker red for hover effects
            'secondary': '#CD5C5C',  # Indian red
            'white': '#FFFFFF',
            'black': '#000000',
            'text': '#333333',
            'light_gray': '#F5F5F5',
            'hover': '#F0F0F0',
            'error': '#FF0000',
            'background': '#f8f9fa'
        }
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Configure Dashboard styles
        style.configure('Dashboard.Treeview',
            background=self.colors['white'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['white'],
            rowheight=35,
            font=('Arial', 10)
        )
        
        style.configure('Dashboard.Treeview.Heading',
            background=self.colors['primary'],
            foreground=self.colors['white'],
            relief='flat',
            font=('Arial', 11, 'bold')
        )
        
        style.map('Dashboard.Treeview.Heading',
            background=[('active', self.colors['primary_dark'])]
        )
        
        # Configure button styles
        style.configure('Dashboard.TButton',
            background=self.colors['primary'],
            foreground=self.colors['white'],
            padding=(10, 5),
            font=('Arial', 10)
        )
        
        style.map('Dashboard.TButton',
            background=[('active', self.colors['primary_dark'])]
        )
        
        # Set default picture
        self.default_picture = 'profile_pics/default.png'
        if not os.path.exists('profile_pics'):
            os.makedirs('profile_pics')
        if not os.path.exists(self.default_picture):
            # Create a default profile picture
            img = Image.new('RGB', (150, 150), color='lightgray')
            img.save(self.default_picture)
        
    def setup_ui(self):
        """Setup the main UI components"""
        self.root.title("Admin Dashboard")
        self.root.geometry("1000x600")
        
        # Configure root window
        self.root.configure(bg=self.colors['white'])
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg=self.colors['white'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = tk.Frame(self.main_frame, bg=self.colors['primary'])
        header_frame.pack(fill=tk.X)
        
        # Title and logout button container
        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            header_content,
            text="Admin Dashboard",
            font=('Arial', 24, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(side=tk.LEFT)
        
        # Logout button
        logout_btn = tk.Button(
            header_content,
            text="Logout",
            command=self.logout,
            bg=self.colors['secondary'],
            fg=self.colors['white'],
            font=('Arial', 11),
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        logout_btn.pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Professors tab
        self.professors_tab = tk.Frame(self.notebook, bg=self.colors['white'])
        self.notebook.add(self.professors_tab, text='Professors')
        
        # Create Users tab
        self.users_tab = tk.Frame(self.notebook, bg=self.colors['white'])
        self.notebook.add(self.users_tab, text='Users')
        
        # Setup button frame in Professors tab
        button_frame = tk.Frame(self.professors_tab, bg=self.colors['white'])
        button_frame.pack(pady=10)
        
        # Add buttons
        buttons = [
            ("Add Professor", self.add_professor),
            ("Edit Professor", self.edit_professor),
            ("Delete Professor", self.delete_professor),
            ("Edit Schedule", self.edit_schedule_wrapper)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=self.colors['primary'],
                fg=self.colors['white'],
                font=('Arial', 11),
                relief=tk.FLAT,
                padx=20,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.add_button_hover(btn)
        
        # Setup professors and users interfaces
        self.setup_professors_ui()
        self.setup_users_ui()
        
    def edit_schedule_wrapper(self):
        """Wrapper function to handle professor selection before editing schedule"""
        try:
            selected_item = self.prof_tree.selection()[0]
            prof_name = self.prof_tree.item(selected_item)['values'][0]
            self.edit_professor_schedule(prof_name)
        except IndexError:
            messagebox.showerror("Error", "Please select a professor first")
        
    def setup_professors_ui(self):
        """Setup the professors management interface"""
        # Create professors frame
        self.professors_frame = tk.Frame(self.professors_tab, bg=self.colors['white'])
        self.professors_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure("Custom.Treeview",
            background=self.colors['white'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['white'],
            rowheight=30
        )
        style.configure("Custom.Treeview.Heading",
            background=self.colors['primary'],
            foreground=self.colors['black'],
            relief='flat'
        )
        style.map("Custom.Treeview.Heading",
            background=[('active', self.colors['secondary'])]  # Change color on hover
        )
        
        # Create tree frame
        tree_frame = tk.Frame(self.professors_frame, bg=self.colors['white'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ('Name', 'Department', 'Contact', 'Email')
        self.prof_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                          style="Custom.Treeview", height=15)
        
        # Configure columns
        self.prof_tree.heading('Name', text='Name')
        self.prof_tree.heading('Department', text='Department')
        self.prof_tree.heading('Contact', text='Contact')
        self.prof_tree.heading('Email', text='Email')
        
        # Set column widths
        self.prof_tree.column('Name', width=250)
        self.prof_tree.column('Department', width=150)
        self.prof_tree.column('Contact', width=150)
        self.prof_tree.column('Email', width=250)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.prof_tree.yview)
        self.prof_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.prof_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load professors
        self.load_professors()
        
    def add_professor(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Professor")
        dialog.geometry("400x600")  # Made taller to accommodate picture
        
        # Configure dialog
        dialog.configure(bg=self.colors['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main container
        main_frame = tk.Frame(dialog, bg=self.colors['white'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Entries dictionary to store input fields
        entries = {}
        
        # Name field
        tk.Label(main_frame,
            text="Name",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        name_entry = ttk.Entry(main_frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        entries['name'] = name_entry
        
        # Department field
        tk.Label(main_frame,
            text="Department",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        dept_entry = ttk.Entry(main_frame, width=40)
        dept_entry.pack(fill=tk.X, pady=(0, 15))
        entries['department'] = dept_entry
        
        # Contact field
        tk.Label(main_frame,
            text="Contact",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        contact_entry = ttk.Entry(main_frame, width=40)
        contact_entry.pack(fill=tk.X, pady=(0, 15))
        entries['contact'] = contact_entry
        
        # Email field
        tk.Label(main_frame,
            text="Email",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        email_entry = ttk.Entry(main_frame, width=40)
        email_entry.pack(fill=tk.X, pady=(0, 15))
        entries['email'] = email_entry
        
        # Picture section
        tk.Label(main_frame,
            text="Picture",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        # Frame for picture preview
        picture_frame = tk.Frame(main_frame, bg=self.colors['white'])
        picture_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Default picture
        default_image = Image.new('RGB', (150, 150), color='lightgray')
        draw = ImageDraw.Draw(default_image)
        draw.ellipse([30, 10, 120, 100], fill='gray')  # Head
        draw.rectangle([45, 100, 105, 150], fill='gray')  # Body
        photo = ImageTk.PhotoImage(default_image)
        
        # Picture preview label
        picture_label = tk.Label(picture_frame, image=photo, bg=self.colors['white'])
        picture_label.image = photo
        picture_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Variable to store picture path
        entries['picture'] = tk.StringVar()
        entries['picture'].set('')
        
        def choose_picture():
            file_path = filedialog.askopenfilename(
                title="Choose Picture",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                try:
                    # Update preview
                    image = Image.open(file_path)
                    image = image.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    picture_label.configure(image=photo)
                    picture_label.image = photo  # Keep reference!
                    entries['picture'].set(file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {str(e)}")
        
        # Choose picture button
        choose_btn = ttk.Button(picture_frame,
            text="Choose Picture",
            command=choose_picture
        )
        choose_btn.pack(side=tk.LEFT, pady=5)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
            text="Cancel",
            font=('Arial', 11),
            bg=self.colors['light_gray'],
            fg=self.colors['text'],
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = tk.Button(button_frame,
            text="Save",
            font=('Arial', 11),
            bg=self.colors['primary'],
            fg=self.colors['white'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['white'],
            cursor='hand2',
            relief=tk.FLAT,
            command=lambda: self.save_professor(entries, dialog)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add hover effects
        self.add_button_hover(cancel_btn)
        self.add_button_hover(save_btn)

    def save_professor(self, entries, dialog):
        # Get values, removing placeholders
        name = entries['name'].get()
        department = entries['department'].get()
        contact = entries['contact'].get()
        email = entries['email'].get()
        picture = entries['picture'].get()
        
        # Remove placeholder text if present
        if name == "":
            name = ""
        if department == "":
            department = ""
        if contact == "":
            contact = ""
        if email == "":
            email = ""
        if picture == "":
            picture = ""
            
        # Strip whitespace
        name = name.strip()
        department = department.strip()
        contact = contact.strip()
        email = email.strip()
        picture = picture.strip()
        
        # Validate required fields
        if not name or not department:
            messagebox.showerror("Error", "Name and Department are required fields")
            return
            
        try:
            # Add professor to database
            if add_professor(name, department, contact, email, picture):
                messagebox.showinfo("Success", "Professor added successfully")
                dialog.destroy()
                # Refresh professor list
                self.load_professors()
            else:
                messagebox.showerror("Error", "Failed to add professor. The professor may already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding professor: {str(e)}")

    def delete_professor(self):
        try:
            # Get selected professor
            selected = self.prof_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a professor to delete")
                return
                
            # Get professor details
            item = self.prof_tree.item(selected[0])
            if not item or not item['values']:
                messagebox.showerror("Error", "Invalid selection")
                return
                
            prof_name = item['values'][0]  # Name is the first column
            
            # Additional validation for the professor name
            if not prof_name or len(prof_name.strip()) == 0:
                messagebox.showerror("Error", "Invalid professor name")
                return
                
            # Store the selection ID for later use
            selection_id = selected[0]
                
            # Confirm deletion with more detailed message
            if not messagebox.askyesno("Confirm Delete", 
                f"Are you sure you want to delete professor {prof_name}?\n\n"
                "This will:\n"
                "1. Delete all associated schedules\n"
                "2. Remove the professor from the system\n\n"
                "This action cannot be undone."):
                return
                
            # Attempt to delete the professor
            if delete_professor(prof_name.strip()):
                # First remove from tree view
                try:
                    if selection_id in self.prof_tree.get_children():
                        self.prof_tree.delete(selection_id)
                except tk.TclError:
                    pass  # Ignore if item is already gone
                    
                messagebox.showinfo("Success", f"Professor {prof_name} has been deleted successfully")
                # Refresh the list to ensure consistency
                self.load_professors()
            else:
                messagebox.showerror("Error", 
                    f"Failed to delete professor {prof_name}.\n"
                    "The professor may have already been deleted or there might be a database error.")
                # Refresh the list to ensure consistency
                self.load_professors()
                
        except Exception as e:
            messagebox.showerror("Error", 
                f"An unexpected error occurred while deleting professor.\n"
                f"Error details: {str(e)}")
            # Refresh the list to ensure consistency
            self.load_professors()
    
    def edit_professor_schedule(self, prof_name):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Schedule - {prof_name}")
        dialog.geometry("800x600")
        dialog.configure(bg=self.colors['white'])
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + (self.root.winfo_width() / 2 - 400),
            self.root.winfo_y() + (self.root.winfo_height() / 2 - 300)
        ))
        
        # Create main frame with padding
        main_frame = tk.Frame(dialog, bg=self.colors['white'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(main_frame,
            text=f"Schedule for {prof_name}",
            font=('Arial', 16, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Schedule list frame with border
        schedule_frame = tk.Frame(main_frame, bg=self.colors['white'], bd=1, relief=tk.SOLID)
        schedule_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure("Custom.Treeview",
            background=self.colors['white'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['white'],
            rowheight=30
        )
        style.configure("Custom.Treeview.Heading",
            background=self.colors['primary'],
            foreground=self.colors['white'],
            relief='flat'
        )
        
        columns = ('Day', 'Time', 'Subject')
        tree = ttk.Treeview(schedule_frame, columns=columns, show='headings', 
                           style="Custom.Treeview", height=10)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
        tree.column('Day', width=150)
        tree.column('Time', width=250)
        tree.column('Subject', width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Load existing schedules
        schedules = []
        cursor = get_db_connection().cursor()
        cursor.execute('SELECT id FROM professors WHERE name = ?', (prof_name,))
        prof_row = cursor.fetchone()
        if prof_row:
            schedules = get_professor_schedule(prof_row['id'])
        if schedules:
            for schedule in schedules:
                time_slot = f"{schedule['start_time']} - {schedule['end_time']}"
                tree.insert('', tk.END, values=(schedule['day'], time_slot, schedule.get('subject', 'N/A')))
        
        # Add Schedule Frame
        add_frame = tk.Frame(main_frame, bg=self.colors['white'])
        add_frame.pack(fill=tk.X, pady=20)
        
        # Day dropdown
        day_label = tk.Label(add_frame, text="Day:", bg=self.colors['white'], font=('Arial', 11))
        day_label.pack(side=tk.LEFT)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_var = tk.StringVar(value=days[0])
        day_combo = ttk.Combobox(add_frame, textvariable=day_var, values=days, width=12, state='readonly')
        day_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        # Time entry
        time_label = tk.Label(add_frame, text="Time:", bg=self.colors['white'], font=('Arial', 11))
        time_label.pack(side=tk.LEFT)
        
        time_entry = tk.Entry(add_frame, width=25, font=('Arial', 11))
        time_entry.insert(0, "e.g., 9:00 AM - 10:30 AM")
        time_entry.config(fg='gray')
        time_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Subject entry
        subject_label = tk.Label(add_frame, text="Subject:", bg=self.colors['white'], font=('Arial', 11))
        subject_label.pack(side=tk.LEFT)
        
        subject_entry = tk.Entry(add_frame, width=35, font=('Arial', 11))
        subject_entry.pack(side=tk.LEFT, padx=5)
        
        # Time entry focus handlers
        def on_time_focus_in(event):
            if time_entry.get() == "e.g., 9:00 AM - 10:30 AM":
                time_entry.delete(0, tk.END)
                time_entry.config(fg='black')
        
        def on_time_focus_out(event):
            if not time_entry.get():
                time_entry.insert(0, "e.g., 9:00 AM - 10:30 AM")
                time_entry.config(fg='gray')
        
        time_entry.bind('<FocusIn>', on_time_focus_in)
        time_entry.bind('<FocusOut>', on_time_focus_out)
        
        # Schedule management functions
        def add_schedule():
            day = day_var.get()
            time_str = time_entry.get()
            subject = subject_entry.get()
            
            if not day or not time_str or time_str == "e.g., 9:00 AM - 10:30 AM" or not subject:
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            try:
                if '-' not in time_str:
                    raise ValueError("Time must contain a hyphen (-) to separate start and end times")
                    
                start_time, end_time = time_str.split('-')
                start_time = start_time.strip()
                end_time = end_time.strip()
                
                for t in [start_time, end_time]:
                    if 'AM' not in t.upper() and 'PM' not in t.upper():
                        raise ValueError("Times must include AM or PM")
                    if ':' not in t:
                        raise ValueError("Times must be in HH:MM format")
                    
                    try:
                        time_parts = t.replace('AM', ' AM').replace('PM', ' PM').strip().split(':')
                        if len(time_parts) != 2:
                            raise ValueError
                        hour = int(time_parts[0])
                        minute = int(time_parts[1].split()[0])
                        period = time_parts[1].split()[1].upper()
                        
                        if hour < 1 or hour > 12 or minute < 0 or minute > 59:
                            raise ValueError
                        if period not in ['AM', 'PM']:
                            raise ValueError
                    except:
                        raise ValueError(f"Invalid time format: {t}")
                
                # Get professor ID
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM professors WHERE name = ?', (prof_name,))
                prof_row = cursor.fetchone()
                
                if not prof_row:
                    raise ValueError(f"Professor {prof_name} not found")
                
                # Add schedule to database
                if db_add_schedule(prof_row['id'], day, start_time, end_time, subject):
                    # If successful, add to treeview
                    tree.insert('', tk.END, values=(day, time_str, subject))
                    
                    # Clear inputs
                    time_entry.delete(0, tk.END)
                    time_entry.insert(0, "e.g., 9:00 AM - 10:30 AM")
                    time_entry.config(fg='gray')
                    subject_entry.delete(0, tk.END)
                else:
                    raise ValueError("Failed to add schedule to database")
                
            except ValueError as e:
                messagebox.showerror("Error", str(e) if str(e) else "Invalid time format. Use format: HH:MM AM - HH:MM PM")
        
        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selection Error", "Please select a schedule to delete")
                return
            
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected schedule(s)?"):
                for item in selected:
                    tree.delete(item)
        
        def save_schedules():
            try:
                schedules = []
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    time_str = values[1]
                    start_time, end_time = map(str.strip, time_str.split('-'))
                    
                    schedules.append({
                        'day': values[0],
                        'start_time': start_time,
                        'end_time': end_time,
                        'subject': values[2]
                    })
                
                if update_professor_schedule(prof_name, schedules):
                    messagebox.showinfo("Success", "Schedules updated successfully!")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update schedules")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving schedules: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add Schedule button
        add_button = tk.Button(button_frame, text="Add Schedule",
                             command=add_schedule,
                             bg=self.colors['primary'],
                             fg=self.colors['white'],
                             font=('Arial', 11),
                             relief=tk.FLAT,
                             padx=20)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Delete Selected button
        delete_button = tk.Button(button_frame, text="Delete Selected",
                                command=delete_selected,
                                bg=self.colors['secondary'],
                                fg=self.colors['white'],
                                font=('Arial', 11),
                                relief=tk.FLAT,
                                padx=20)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel",
                                command=dialog.destroy,
                                bg=self.colors['light_gray'],
                                fg=self.colors['text'],
                                font=('Arial', 11),
                                relief=tk.FLAT,
                                padx=20)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Save Changes button
        save_button = tk.Button(button_frame, text="Save Changes",
                              command=save_schedules,
                              bg=self.colors['primary'],
                              fg=self.colors['white'],
                              font=('Arial', 11, 'bold'),
                              relief=tk.FLAT,
                              padx=20)
        save_button.pack(side=tk.RIGHT, padx=5)
        
    def edit_professor(self):
        selected = self.prof_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a professor first")
            return
        
        item = selected[0]
        values = self.prof_tree.item(item)['values']
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Professor")
        dialog.geometry("400x600")
        dialog.configure(bg=self.colors['white'])
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Main frame with padding
        main_frame = tk.Frame(dialog, bg=self.colors['white'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Profile Picture Section
        profile_frame = tk.Frame(main_frame, bg=self.colors['white'])
        profile_frame.pack(pady=(0, 15))
        
        # Get professor's current picture
        prof_data = get_professor_by_name(values[0])
        current_picture = prof_data.get('picture') if prof_data and prof_data.get('picture') != "N/A" else self.default_picture
        
        # Create profile picture label
        profile_label = tk.Label(profile_frame, bg=self.colors['white'])
        profile_label.pack()
        
        # Function to update profile picture display
        def update_profile_display(picture_path):
            try:
                with Image.open(picture_path) as img:
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    profile_label.configure(image=photo)
                    profile_label.image = photo  # Keep reference!
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update display: {str(e)}")
        
        # Initial display of profile picture
        update_profile_display(current_picture)
        
        # Add Change Picture Button
        change_pic_btn = tk.Button(
            profile_frame,
            text="Change Picture",
            command=lambda: self.change_profile_picture(profile_label, values[0]),
            bg=self.colors['primary'],
            fg=self.colors['white'],
            font=('Arial', 10),
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        change_pic_btn.pack(pady=10)
        
        # Fields dictionary to store input fields
        fields = {}
        
        # Name field
        tk.Label(main_frame,
            text="Name",
            font=('Arial', 11),
            bg=self.colors['white']
        ).pack(anchor='w')
        
        name_entry = tk.Entry(main_frame, font=('Arial', 11))
        name_entry.insert(0, values[0])
        name_entry.pack(fill=tk.X, pady=(0, 15))
        fields['name'] = name_entry
        
        # Department field
        tk.Label(main_frame,
            text="Department",
            font=('Arial', 11),
            bg=self.colors['white']
        ).pack(anchor='w')
        
        dept_entry = tk.Entry(main_frame, font=('Arial', 11))
        dept_entry.insert(0, values[1])
        dept_entry.pack(fill=tk.X, pady=(0, 15))
        fields['department'] = dept_entry
        
        # Contact field
        tk.Label(main_frame,
            text="Contact",
            font=('Arial', 11),
            bg=self.colors['white']
        ).pack(anchor='w')
        
        contact_entry = tk.Entry(main_frame, font=('Arial', 11))
        contact_entry.insert(0, values[2])
        contact_entry.pack(fill=tk.X, pady=(0, 15))
        fields['contact'] = contact_entry
        
        # Email field
        tk.Label(main_frame,
            text="Email",
            font=('Arial', 11),
            bg=self.colors['white']
        ).pack(anchor='w')
        
        email_entry = tk.Entry(main_frame, font=('Arial', 11))
        email_entry.insert(0, values[3])
        email_entry.pack(fill=tk.X, pady=(0, 15))
        fields['email'] = email_entry
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
            text="Cancel",
            font=('Arial', 11),
            bg=self.colors['light_gray'],  
            fg=self.colors['text'],
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = tk.Button(button_frame,
            text="Save",
            font=('Arial', 11),
            bg=self.colors['primary'],  
            fg=self.colors['white'],
            command=lambda: self.update_professor(values[0], fields, dialog)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
    def change_profile_picture(self, profile_label, prof_name):
        file_types = [('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if not file_path:
            return

        temp_file = None
        new_filename = None
        
        try:
            # Create profile_pics directory if it doesn't exist
            os.makedirs('profile_pics', exist_ok=True)
            
            # Get professor data first to validate
            prof_data = get_professor_by_name(prof_name)
            if not prof_data:
                messagebox.showerror("Error", "Professor not found in database")
                return
            
            # Generate unique filename with timestamp to prevent caching
            file_ext = os.path.splitext(file_path)[1].lower()
            timestamp = int(time.time())
            new_filename = f"profile_pics/{prof_name}_{timestamp}{file_ext}"
            temp_file = f"profile_pics/temp_{timestamp}{file_ext}"
            
            # Process image first before touching the database
            with Image.open(file_path) as img:
                # Convert to RGB to ensure compatibility
                img = img.convert('RGB')
                # Resize maintaining aspect ratio
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                # Save to temporary file first
                img.save(temp_file, format='JPEG', quality=95)
            
            # If we got here, image processing succeeded
            shutil.move(temp_file, new_filename)
            temp_file = None  # Don't delete the temp file since we moved it
            
            # Update database with new picture path
            if update_professor_picture(prof_name, new_filename):
                # Update display only after successful database update
                try:
                    with Image.open(new_filename) as img:
                        photo = ImageTk.PhotoImage(img)
                        profile_label.configure(image=photo)
                        profile_label.image = photo  # Keep reference
                    
                    # Force refresh of student panels
                    refresh_all_student_panels()
                    
                    # Force refresh of admin panel
                    self.load_professors()
                    
                    messagebox.showinfo("Success", "Profile picture updated successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update display: {str(e)}")
            else:
                raise Exception("Failed to update profile picture in database")
                
        except Exception as e:
            # Clean up any temporary or new files on error
            for file_to_cleanup in [f for f in [temp_file, new_filename] if f and os.path.exists(f)]:
                try:
                    os.remove(file_to_cleanup)
                except:
                    pass
            messagebox.showerror("Error", f"Failed to update profile picture: {str(e)}")
        
    def update_professor(self, old_name, fields, dialog):
        values = {field: entry.get().strip() for field, entry in fields.items()}
        if not all(values.values()):
            messagebox.showerror("Error", "All fields are required")
            return
            
        try:
            update_professor(old_name, values['name'], values['department'], values['contact'], values['email'])
            dialog.destroy()
            self.load_professors()
            messagebox.showinfo("Success", "Professor updated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update professor: {str(e)}")

    def logout(self):
        """Handle logout action"""
        try:
            # Remove remembered login file if it exists
            if os.path.exists('remembered_login.txt'):
                os.remove('remembered_login.txt')
        except Exception as e:
            print(f"Failed to remove remembered login during logout: {str(e)}")
            
        # Cancel any pending animations or after callbacks
        for widget in self.root.winfo_children():
            if hasattr(widget, '_after_id'):
                self.root.after_cancel(widget._after_id)
        
        # Destroy the current window
        self.root.destroy()
        
        # Create new welcome window
        new_root = tk.Tk()
        new_root.protocol("WM_DELETE_WINDOW", lambda: (new_root.quit(), new_root.destroy()))
        welcome = WelcomeWindow(new_root)
        new_root.mainloop()

    def add_button_hover(self, button):
        def on_enter(e):
            if button['state'] != 'disabled':
                if button['bg'] == self.colors['primary']:
                    button['bg'] = self.colors['secondary']
                else:
                    button['bg'] = '#D0D0D0'  # Slightly darker gray for non-primary buttons
                
        def on_leave(e):
            if button['state'] != 'disabled':
                if button['bg'] == self.colors['secondary']:
                    button['bg'] = self.colors['primary']
                else:
                    button['bg'] = self.colors['light_gray']
                    
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
    def load_professors(self):
        try:
            # Clear existing items
            for item in self.prof_tree.get_children():
                self.prof_tree.delete(item)
                
            professors = get_all_professors()
            print(f"[DEBUG] Loading {len(professors)} professors")
            
            for prof in professors:
                try:
                    values = (
                        prof.get('name', 'N/A'),
                        prof.get('department', 'N/A'),
                        prof.get('contact', 'N/A'),
                        prof.get('email', 'N/A')
                    )
                    self.prof_tree.insert("", "end", values=values)
                    print(f"[DEBUG] Added professor: {values[0]}")
                except Exception as e:
                    print(f"[DEBUG] Error loading professor: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"[DEBUG] Failed to load professors: {str(e)}")
            messagebox.showerror("Error", "Failed to load professors")
    
    def setup_users_ui(self):
        """Setup the users management interface"""
        # Create main container
        main_frame = tk.Frame(self.users_tab, bg=self.colors['white'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title = tk.Label(main_frame, 
            text="User Management",
            font=('Arial', 24, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text']
        )
        title.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add User button
        add_btn = tk.Button(button_frame,
            text="Add User",
            command=self.add_user_dialog,
            bg=self.colors['primary'],
            fg=self.colors['white'],
            font=('Arial', 11),
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete User button
        delete_btn = tk.Button(button_frame,
            text="Delete User",
            command=self.delete_user,
            bg=self.colors['primary'],
            fg=self.colors['white'],
            font=('Arial', 11),
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Add hover effects
        self.add_button_hover(add_btn)
        self.add_button_hover(delete_btn)
        
        # Create users treeview
        tree_frame = tk.Frame(self.users_tab, bg=self.colors['white'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Users.Treeview",
            background=self.colors['white'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['white'],
            rowheight=30
        )
        style.configure("Users.Treeview.Heading",
            background=self.colors['primary'],
            foreground=self.colors['black'],
            relief='flat'
        )
        style.map("Users.Treeview.Heading",
            background=[('active', self.colors['primary_dark'])]
        )
        
        # Create Treeview
        columns = ('Username', 'Email', 'Role')
        self.users_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                     style="Users.Treeview", height=15)
        
        # Configure columns
        self.users_tree.heading('Username', text='Username')
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Role', text='Role')
        
        self.users_tree.column('Username', width=200)
        self.users_tree.column('Email', width=300)
        self.users_tree.column('Role', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load users
        self.load_users()
        
        # Setup auto-refresh every 5 seconds
        self.auto_refresh_users()
        
    def auto_refresh_users(self):
        """Auto refresh users list every 5 seconds"""
        self.load_users()
        self.root.after(5000, self.auto_refresh_users)
        
    def load_users(self):
        """Load users into the treeview"""
        print("[DEBUG] Loading users into treeview")
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        try:
            users = get_all_users()
            print(f"[DEBUG] Got {len(users)} users from database")
            for user in users:
                values = (
                    user['username'],
                    user.get('email', 'N/A'),  # Use get() to handle missing email
                    user['role']
                )
                self.users_tree.insert('', tk.END, values=values)
                print(f"[DEBUG] Added user to treeview: {values}")
                
        except Exception as e:
            print(f"[DEBUG] Error loading users: {str(e)}")
            messagebox.showerror("Error", "Failed to load users")
            
    def add_user_dialog(self):
        """Show dialog to add a new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['white'])
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_x() + (self.root.winfo_width() / 2 - 200),
            self.root.winfo_y() + (self.root.winfo_height() / 2 - 150)
        ))
        
        # Create main frame
        main_frame = tk.Frame(dialog, bg=self.colors['white'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username field
        tk.Label(main_frame,
            text="Username",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=40)
        username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password field
        tk.Label(main_frame,
            text="Password",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, width=40, show='*')
        password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Role selection
        tk.Label(main_frame,
            text="Role",
            font=('Arial', 12),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        role_var = tk.StringVar(value='student')
        roles_frame = tk.Frame(main_frame, bg=self.colors['white'])
        roles_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(roles_frame,
            text="Student",
            variable=role_var,
            value='student'
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(roles_frame,
            text="Admin",
            variable=role_var,
            value='admin'
        ).pack(side=tk.LEFT, padx=10)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame,
            text="Cancel",
            font=('Arial', 11),
            bg=self.colors['light_gray'],
            fg=self.colors['text'],
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = tk.Button(button_frame,
            text="Save",
            font=('Arial', 11),
            bg=self.colors['primary'],
            fg=self.colors['white'],
            command=lambda: self.save_new_user({
                'username': username_var,
                'password': password_var,
                'role': role_var
            }, dialog)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add hover effects
        self.add_button_hover(cancel_btn)
        self.add_button_hover(save_btn)

    def save_new_user(self, fields, dialog):
        """Save a new user to the database"""
        # Get values
        username = fields['username'].get().strip()
        password = fields['password'].get().strip()
        role = fields['role'].get().strip()
        
        # Validate fields
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
            
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
            
        try:
            # Add user to database
            if add_user(username, password, role):
                messagebox.showinfo("Success", "User added successfully")
                dialog.destroy()
                # Refresh users list
                self.load_users()
            else:
                messagebox.showerror("Error", "Failed to add user. The username may already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding user: {str(e)}")
            
    def delete_user(self):
        """Delete selected user"""
        try:
            # Get selected user
            selected = self.users_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a user to delete")
                return
                
            # Get user details
            item = self.users_tree.item(selected[0])
            if not item or not item['values']:
                messagebox.showerror("Error", "Invalid selection")
                return
                
            username = item['values'][0]
            
            # Prevent deleting yourself
            if username == self.username:
                messagebox.showerror("Error", "You cannot delete your own account")
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete",
                f"Are you sure you want to delete user {username}?\n\n"
                "This action cannot be undone."):
                return
                
            # Delete user
            if delete_user(username):
                messagebox.showinfo("Success", f"User {username} deleted successfully")
                # Refresh users list
                self.load_users()
            else:
                messagebox.showerror("Error", "Failed to delete user")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting user: {str(e)}")

class StudentPanel:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
        # Initialize storage for profile photos first
        self.profile_photos = {}
        
        # Initialize UI components
        self.setup_styles()
        self.setup_ui()
        
        # Store animation IDs
        self.animation_ids = []
        
        # Register for refresh notifications
        if 'student_panels' not in globals():
            global student_panels
            student_panels = []
        student_panels.append(self)
    
    def __del__(self):
        # Cleanup any remaining animations
        for after_id in getattr(self, 'animation_ids', []):
            try:
                self.root.after_cancel(after_id)
            except:
                pass
        
        # Remove from global list
        if 'student_panels' in globals():
            if self in student_panels:
                student_panels.remove(self)
        
    def setup_styles(self):
        self.colors = {
            'primary': '#8B0000',  # Dark red
            'white': '#FFFFFF',
            'light_gray': '#F5F5F5',
            'text': '#000000',
            'hover': '#F0F0F0',
            'error': '#FF0000'
        }
        
    def setup_ui(self):
        self.root.title("Student Panel")
        self.root.geometry("1200x700")
        
        # Configure root window
        self.root.configure(bg=self.colors['white'])
        
        # Create main container
        main_container = tk.Frame(self.root, bg=self.colors['white'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame,
            text="Professor Directory",
            font=('Arial', 24, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # User info and logout
        user_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        user_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(user_frame,
            text=f"Student: {self.username}",
            font=('Arial', 12),
            bg=self.colors['primary'],
            fg=self.colors['white']
        ).pack(side=tk.LEFT, padx=10)
        
        logout_btn = tk.Button(user_frame,
            text="Logout",
            font=('Arial', 11),
            bg=self.colors['primary'],  
            fg=self.colors['white'],
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT,
            command=self.logout)
        logout_btn.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = tk.Frame(main_container, bg=self.colors['white'])
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_professors())
        
        search_entry = tk.Entry(search_frame,
            textvariable=self.search_var,
            font=('Arial', 11),
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=10)
        
        # Professors frame
        self.professors_frame = tk.Frame(main_container, bg=self.colors['white'])
        self.professors_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create container for professors
        scroll_container = tk.Frame(self.professors_frame, bg=self.colors['white'])
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(scroll_container, bg=self.colors['white'])
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure canvas
        self.canvas.configure(xscrollcommand=x_scrollbar.set)
        
        # Create professors frame inside canvas
        self.professors_frame_inside = tk.Frame(self.canvas, bg=self.colors['white'])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.professors_frame_inside, anchor="nw")
        
        # Bind events for scrolling
        self.professors_frame_inside.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel)
        
        # Load professors
        self.load_professors()
        
    def create_professor_card(self, professor):
        # Create card frame
        card = tk.Frame(self.professors_frame_inside, bg=self.colors['white'], relief='solid', bd=1)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=10, ipady=10)
        
        try:
            # Get fresh data from database to ensure we have the latest picture
            prof_data = get_professor_by_name(professor['name'])
            if not prof_data:
                raise Exception(f"Professor {professor['name']} not found in database")
                
            # Clear the old photo from cache if it exists
            if professor['name'] in self.profile_photos:
                del self.profile_photos[professor['name']]
            
            # Load and process image
            image = None
            try:
                if prof_data.get('picture') and os.path.exists(prof_data['picture']):
                    image = Image.open(prof_data['picture'])
                    image.load()  # Force load the image data
                else:
                    image = Image.open(create_default_profile_picture())
                    
                # Resize image
                image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Store reference to prevent garbage collection
                self.profile_photos[professor['name']] = photo
                
                # Profile picture label
                profile_label = tk.Label(card, image=photo, bg=self.colors['white'])
                profile_label.image = photo  # Keep reference to prevent garbage collection
                profile_label.pack(pady=(10, 5))
                
            except Exception as img_error:
                messagebox.showerror("Error", f"Failed to load image for {professor['name']}: {str(img_error)}")
                profile_label = tk.Label(card, text="No Image", bg=self.colors['white'])
                profile_label.pack(pady=(10, 5))
            finally:
                if image:
                    image.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load professor data: {str(e)}")
            profile_label = tk.Label(card, text="Error Loading Data", bg=self.colors['white'])
            profile_label.pack(pady=(10, 5))
        
        # Professor details
        tk.Label(card, text=professor['name'], font=('Arial', 12, 'bold'), bg=self.colors['white']).pack()
        tk.Label(card, text=professor['department'], font=('Arial', 10), bg=self.colors['white']).pack()
        tk.Label(card, text=professor['contact'], font=('Arial', 10), bg=self.colors['white']).pack()
        tk.Label(card, text=professor['email'], font=('Arial', 10), bg=self.colors['white']).pack()
        
        # View Schedule button
        view_schedule_button = tk.Button(
            card,
            text="View Schedule",
            bg=self.colors['primary'],  
            fg=self.colors['white'],
            font=('Arial', 10),
            command=lambda p=professor: self.view_schedule(p)
        )
        view_schedule_button.pack(pady=10)

    def load_professors(self):
        # Clear existing professors
        for widget in self.professors_frame_inside.winfo_children():
            widget.destroy()
            
        # Clear the photo cache
        self.profile_photos.clear()
        
        # Reload professors
        try:
            professors = get_all_professors()
            if not professors:
                # Show message if no professors found
                msg_label = tk.Label(
                    self.professors_frame_inside,
                    text="No professors found",
                    font=('Arial', 14),
                    bg=self.colors['white']
                )
                msg_label.pack(expand=True, pady=20)
                return
                
            for prof in professors:
                self.create_professor_card(prof)
                
            # Update the frame
            self.professors_frame_inside.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh professors: {str(e)}")

    def search_professors(self):
        search_term = self.search_var.get().lower()
        
        # Clear existing professors
        for widget in self.professors_frame_inside.winfo_children():
            widget.destroy()
            
        try:
            professors = get_all_professors()
            for prof in professors:
                if (search_term in prof['name'].lower() or
                    search_term in prof['department'].lower() or
                    search_term in str(prof['contact']).lower() or
                    search_term in str(prof['email']).lower()):
                    self.create_professor_card(prof)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search professors: {str(e)}")
    
    def view_schedule(self, professor):
        # Create a new window for the schedule
        schedule_window = tk.Toplevel(self.root)
        schedule_window.title(f"Schedule - {professor['name']}")
        schedule_window.geometry("600x400")
        schedule_window.configure(bg=self.colors['white'])
        
        # Create a frame for professor info
        info_frame = tk.Frame(schedule_window, bg=self.colors['white'])
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # Display professor information
        tk.Label(info_frame, text=f"Professor: {professor['name']}", 
                font=('Arial', 12, 'bold'), bg=self.colors['white']).pack(anchor='w')
        tk.Label(info_frame, text=f"Department: {professor['department']}", 
                font=('Arial', 10), bg=self.colors['white']).pack(anchor='w')
        tk.Label(info_frame, text=f"Contact: {professor['contact']}", 
                font=('Arial', 10), bg=self.colors['white']).pack(anchor='w')
        tk.Label(info_frame, text=f"Email: {professor['email']}", 
                font=('Arial', 10), bg=self.colors['white']).pack(anchor='w')
        
        # Create a separator
        ttk.Separator(schedule_window, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # Create a frame for the schedule
        schedule_frame = tk.Frame(schedule_window, bg=self.colors['white'])
        schedule_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Get schedule from database
        schedules = []
        cursor = get_db_connection().cursor()
        cursor.execute('SELECT id FROM professors WHERE name = ?', (professor['name'],))
        prof_row = cursor.fetchone()
        if prof_row:
            schedules = get_professor_schedule(prof_row['id'])
        
        if schedules:
            # Create headers
            headers = ['Day', 'Time', 'Subject']
            for i, header in enumerate(headers):
                tk.Label(schedule_frame, text=header, font=('Arial', 10, 'bold'),
                        bg=self.colors['white']).grid(row=0, column=i, padx=5, pady=5, sticky='w')
            
            # Display schedule
            for i, entry in enumerate(schedules, start=1):
                tk.Label(schedule_frame, text=entry['day'], bg=self.colors['white']).grid(
                    row=i, column=0, padx=5, pady=2, sticky='w')
                tk.Label(schedule_frame, text=entry['start_time'] + ' - ' + entry['end_time'], bg=self.colors['white']).grid(
                    row=i, column=1, padx=5, pady=2, sticky='w')
                tk.Label(schedule_frame, text=entry['subject'], bg=self.colors['white']).grid(
                    row=i, column=2, padx=5, pady=2, sticky='w')
        else:
            tk.Label(schedule_frame, text="No schedule available", 
                    font=('Arial', 10, 'italic'), bg=self.colors['white']).pack(pady=20)
        
        # Close button
        close_btn = tk.Button(schedule_window,
            text="Close",
            font=('Arial', 11),
            bg=self.colors['primary'],  
            fg=self.colors['white'],
            activebackground='#990000',  # Darker red
            activeforeground=self.colors['white'],
            cursor='hand2',
            relief=tk.FLAT,
            command=schedule_window.destroy)
        close_btn.pack(pady=(20, 0))
        
        # Add hover effect to close button
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#990000'))  # Darker red
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg=self.colors['primary']))
        
    def logout(self):
        try:
            # Check if remember me was unchecked
            if not self.remember_var.get():
                # Remove remembered login file
                if os.path.exists('remembered_login.txt'):
                    os.remove('remembered_login.txt')
        except:
            pass
            
        # Clean up any animation timers
        for anim_id in self.animation_ids:
            self.root.after_cancel(anim_id)
        
        # Close the current window and show login
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
    
    def refresh_professors(self):
        """Refresh the professor cards display"""
        try:
            # Clear existing professors
            for widget in self.professors_frame_inside.winfo_children():
                widget.destroy()
                
            # Clear photo references
            for photo in self.profile_photos.values():
                if hasattr(photo, 'close'):
                    photo.close()
            self.profile_photos.clear()
            
            # Force garbage collection to clean up old images
            import gc
            gc.collect()
            
            # Reload professors
            professors = get_all_professors()
            if not professors:
                # Show message if no professors found
                msg_label = tk.Label(
                    self.professors_frame_inside,
                    text="No professors found",
                    font=('Arial', 14),
                    bg=self.colors['white']
                )
                msg_label.pack(expand=True, pady=20)
                return
                
            for prof in professors:
                self.create_professor_card(prof)
                
            # Update the frame
            self.professors_frame_inside.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh professors: {str(e)}")

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_canvas_configure(self, event):
        """When the canvas is resized, ensure proper display"""
        width = max(event.width, self.professors_frame_inside.winfo_reqwidth())
        self.canvas.itemconfig(self.canvas_window, width=width)
        
    def _on_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + Mouse wheel"""
        self.canvas.xview_scroll(int(-1 * (event.delta/120)), "units")

def refresh_all_student_panels():
    """Refresh all open student panels"""
    if 'student_panels' in globals():
        for panel in student_panels[:]:  # Create a copy to avoid modification during iteration
            try:
                if panel.root.winfo_exists():  # Check if window still exists
                    panel.refresh_professors()
                else:
                    student_panels.remove(panel)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to refresh student panel: {str(e)}")
                # If panel is no longer valid, remove it from the list
                if panel in student_panels:
                    student_panels.remove(panel)

def create_default_profile_picture():
    """Create a default profile picture if it doesn't exist"""
    default_pic_dir = "profile_pics"
    default_pic_path = os.path.join(default_pic_dir, "default.png")
    
    # Create directory if it doesn't exist
    os.makedirs(default_pic_dir, exist_ok=True)
    
    # Create default profile picture if it doesn't exist
    if not os.path.exists(default_pic_path):
        # Create a simple default profile picture
        img = Image.new('RGB', (150, 150), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple avatar shape
        draw.ellipse([30, 30, 120, 120], fill='darkgray')  # Head
        draw.rectangle([60, 90, 90, 130], fill='lightgray')  # Body
        
        # Save the default picture
        img.save(default_pic_path)
    
    return default_pic_path

def main():
    root = tk.Tk()
    welcome = WelcomeWindow(root)
    
    # Register database cleanup on window close
    def on_closing():
        close_db()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    finally:
        close_db()