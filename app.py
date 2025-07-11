import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime

# Mock functions for demo (replace with your actual imports)
try:
    from manager import organize_files, embedder, scan_and_save_files_to_chroma
    from my_chroma_utils import search_documents
except ImportError:
    def organize_files():
        time.sleep(2)
        return "Files organized successfully!"
    
    def search_documents(query, embedder=None):
        time.sleep(1)
        return {
            'documents': [['Somethignwent wrong,  document content about ' + query + 'was not found. Please try a scan for these documents']],
            'metadatas': [[{'file_path': '', 'page_number': 1, 'chunk_index': 0, 'title': 'Something went wrong'}]],
            'distances': [[0.8]]
        }
    
    embedder = None

class BeautifulDocumentMVP:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DocuMind - AI Document Manager MVP")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(True, True)
        
        # Dark theme colors
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d', 
            'bg_card': '#3a3a3a',
            'bg_input': '#2a2a2a',
            'accent': '#00d4ff',
            'accent_hover': '#00b8e6',
            'text_primary': '#ffffff',
            'text_secondary': '#b3b3b3',
            'text_muted': '#888888',
            'success': '#4caf50',
            'warning': '#ff9800',
            'highlight': '#444444'
        }
        
        # Current screen
        self.current_screen = "home"
        
        # Message queue
        self.message_queue = queue.Queue()
        
        # Search history
        self.search_history = []
        
        self.setup_styles()
        self.create_main_layout()
        self.show_home_screen()
        self.check_queue()
    
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='#000000',
                       font=('Segoe UI', 12, 'bold'),
                       focuscolor='none',
                       borderwidth=0,
                       relief='flat')
        
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', '#0099cc')])
        
        style.configure('Nav.TButton',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11),
                       focuscolor='none',
                       borderwidth=0)
        
        style.map('Nav.TButton',
                 background=[('active', self.colors['bg_card'])])
        
        style.configure('Small.TButton',
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 9),
                       focuscolor='none',
                       borderwidth=0)
        
        style.map('Small.TButton',
                 background=[('active', self.colors['highlight'])])
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Header
        self.header = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Navigation
        nav_frame = tk.Frame(self.header, bg=self.colors['bg_secondary'])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Logo and title
        title_frame = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT)
        
        logo_label = tk.Label(title_frame, text="🧠", font=('Segoe UI', 32), 
                             bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_frame, text="DocuMind", 
                              font=('Segoe UI', 24, 'bold'),
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        subtitle_label = tk.Label(title_frame, text="AI Document Manager", 
                                 font=('Segoe UI', 12),
                                 bg=self.colors['bg_secondary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Navigation buttons
        nav_buttons = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        nav_buttons.pack(side=tk.RIGHT)
        
        self.home_btn = ttk.Button(nav_buttons, text="🏠 Home", style='Nav.TButton',
                                  command=self.show_home_screen)
        self.home_btn.pack(side=tk.LEFT, padx=5)
        
        self.organize_btn = ttk.Button(nav_buttons, text="📁 Organize", style='Nav.TButton',
                                      command=self.show_organize_screen)
        self.organize_btn.pack(side=tk.LEFT, padx=5)
        
        self.search_btn = ttk.Button(nav_buttons, text="🔍 Search", style='Nav.TButton',
                                    command=self.show_search_screen)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=35)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                    font=('Segoe UI', 10),
                                    bg=self.colors['bg_secondary'], 
                                    fg=self.colors['text_secondary'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=8)
    
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home_screen(self):
        """Show the home/dashboard screen"""
        self.current_screen = "home"
        self.clear_content()
        
        # Create home content
        home_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        home_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=40)
        
        # Welcome section
        welcome_frame = tk.Frame(home_container, bg=self.colors['bg_primary'])
        welcome_frame.pack(fill=tk.X, pady=(0, 40))
        
        welcome_title = tk.Label(welcome_frame, text="Welcome to DocuMind", 
                                font=('Segoe UI', 28, 'bold'),
                                bg=self.colors['bg_primary'], 
                                fg=self.colors['text_primary'])
        welcome_title.pack()
        
        welcome_desc = tk.Label(welcome_frame, 
                               text="AI-powered document organization and intelligent search",
                               font=('Segoe UI', 14),
                               bg=self.colors['bg_primary'], 
                               fg=self.colors['text_secondary'])
        welcome_desc.pack(pady=(10, 0))
        
        # Feature cards
        cards_frame = tk.Frame(home_container, bg=self.colors['bg_primary'])
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Organize card
        organize_card = self.create_feature_card(cards_frame, 
                                               "📁 Smart Organization",
                                               "Automatically organize your PDF documents using AI clustering and semantic analysis",
                                               self.show_organize_screen)
        organize_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Search card  
        search_card = self.create_feature_card(cards_frame,
                                             "🔍 Intelligent Search", 
                                             "Search through your documents using natural language and semantic understanding",
                                             self.show_search_screen)
        search_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
    
    def create_feature_card(self, parent, title, description, command):
        """Create a feature card for the home screen"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', bd=1)
        
        # Card content
        content = tk.Frame(card, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content, text=title, font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 15))
        
        # Description
        desc_label = tk.Label(content, text=description, font=('Segoe UI', 12),
                             bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                             wraplength=300, justify=tk.CENTER)
        desc_label.pack(pady=(0, 25))
        
        # Action button
        action_btn = ttk.Button(content, text="Get Started", style='Accent.TButton',
                               command=command)
        action_btn.pack()
        
        return card
    
    def show_organize_screen(self):
        """Show the file organization screen"""
        self.current_screen = "organize"
        self.clear_content()
        
        # Main container
        organize_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        organize_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=40)
        
        # Header
        header_frame = tk.Frame(organize_container, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title = tk.Label(header_frame, text="📁 Document Organization", 
                        font=('Segoe UI', 24, 'bold'),
                        bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title.pack()
        
        desc = tk.Label(header_frame, 
                       text="AI will analyze and organize your PDF documents into meaningful clusters",
                       font=('Segoe UI', 12),
                       bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        desc.pack(pady=(10, 0))
        
        # Control panel
        control_panel = tk.Frame(organize_container, bg=self.colors['bg_card'], relief='raised', bd=1)
        control_panel.pack(fill=tk.X, pady=(0, 20))
        
        control_content = tk.Frame(control_panel, bg=self.colors['bg_card'])
        control_content.pack(fill=tk.X, padx=40, pady=30)
        
        # Start button
        self.start_org_btn = ttk.Button(control_content, text="🚀 Start Organization", 
                                       style='Accent.TButton',
                                       command=self.start_organization)
        self.start_org_btn.pack()
        
        # Progress section
        progress_frame = tk.Frame(control_content, bg=self.colors['bg_card'])
        progress_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.org_progress_label = tk.Label(progress_frame, text="Ready to organize documents", 
                                          font=('Segoe UI', 11),
                                          bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
        self.org_progress_label.pack()
        
        self.org_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.org_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Log panel
        log_panel = tk.Frame(organize_container, bg=self.colors['bg_card'], relief='raised', bd=1)
        log_panel.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Frame(log_panel, bg=self.colors['bg_card'])
        log_header.pack(fill=tk.X, padx=40, pady=(30, 10))
        
        log_title = tk.Label(log_header, text="📋 Organization Log", 
                            font=('Segoe UI', 16, 'bold'),
                            bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        log_title.pack()
        
        log_content = tk.Frame(log_panel, bg=self.colors['bg_card'])
        log_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))
        
        self.org_log = scrolledtext.ScrolledText(log_content, height=12,
                                               bg=self.colors['bg_primary'], 
                                               fg=self.colors['text_primary'],
                                               font=('Consolas', 10),
                                               insertbackground=self.colors['accent'],
                                               selectbackground=self.colors['accent'],
                                               selectforeground='#000000',
                                               relief='flat', bd=0)
        self.org_log.pack(fill=tk.BOTH, expand=True)
        
        # Initial log message
        self.add_org_log("System ready. Click 'Start Organization' to begin processing documents.")
    
    def show_search_screen(self):
        """Show the enhanced document search screen"""
        self.current_screen = "search"
        self.clear_content()
        
        # Main container with proper spacing
        search_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        search_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Header section
        header_frame = tk.Frame(search_container, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="🔍 Intelligent Document Search", 
                        font=('Segoe UI', 28, 'bold'),
                        bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title.pack()
        
        subtitle = tk.Label(header_frame, 
                           text="Search through your documents with AI-powered semantic understanding",
                           font=('Segoe UI', 14),
                           bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        subtitle.pack(pady=(8, 0))
        
        # Main content area - split into left and right panels
        main_content = tk.Frame(search_container, bg=self.colors['bg_primary'])
        main_content.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Search interface and history
        left_panel = tk.Frame(main_content, bg=self.colors['bg_primary'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Search input section
        search_section = tk.Frame(left_panel, bg=self.colors['bg_card'], relief='raised', bd=1)
        search_section.pack(fill=tk.X, pady=(0, 20))
        
        search_header = tk.Frame(search_section, bg=self.colors['bg_card'])
        search_header.pack(fill=tk.X, padx=25, pady=(25, 15))
        
        search_title = tk.Label(search_header, text="🎯 Search Query", 
                               font=('Segoe UI', 16, 'bold'),
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        search_title.pack(anchor='w')
        
        search_subtitle = tk.Label(search_header, text="Enter your question or topic", 
                                  font=('Segoe UI', 10),
                                  bg=self.colors['bg_card'], fg=self.colors['text_muted'])
        search_subtitle.pack(anchor='w', pady=(2, 0))
        
        # Enhanced search input
        search_input_frame = tk.Frame(search_section, bg=self.colors['bg_card'])
        search_input_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        
        # Search entry with better styling
        entry_container = tk.Frame(search_input_frame, bg=self.colors['bg_input'], relief='flat')
        entry_container.pack(fill=tk.X, pady=(0, 15))
        
        self.search_entry = tk.Text(entry_container, height=3, font=('Segoe UI', 12),
                                   bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                                   insertbackground=self.colors['accent'], wrap=tk.WORD,
                                   relief='flat', bd=0, padx=15, pady=12)
        self.search_entry.pack(fill=tk.BOTH, expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_text_change)
        self.search_entry.bind('<Control-Return>', lambda e: self.start_search())
        
        # Search controls
        controls_frame = tk.Frame(search_input_frame, bg=self.colors['bg_card'])
        controls_frame.pack(fill=tk.X)
        
        # Search button
        self.start_search_btn = ttk.Button(controls_frame, text="🔎 Search Documents", 
                                          style='Accent.TButton',
                                          command=self.start_search)
        self.start_search_btn.pack(side=tk.LEFT)
        
        # Clear button
        clear_btn = ttk.Button(controls_frame, text="✨ Clear", 
                              style='Small.TButton',
                              command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Search tips
        tips_frame = tk.Frame(search_input_frame, bg=self.colors['bg_card'])
        tips_frame.pack(fill=tk.X, pady=(10, 0))
        
        tips_label = tk.Label(tips_frame, text="💡 Tip: Try 'Ctrl+Enter' to search quickly", 
                             font=('Segoe UI', 9),
                             bg=self.colors['bg_card'], fg=self.colors['text_muted'])
        tips_label.pack(anchor='w')
        
        # Search history section
        history_section = tk.Frame(left_panel, bg=self.colors['bg_card'], relief='raised', bd=1)
        history_section.pack(fill=tk.BOTH, expand=True)
        
        history_header = tk.Frame(history_section, bg=self.colors['bg_card'])
        history_header.pack(fill=tk.X, padx=25, pady=(25, 15))
        
        history_title = tk.Label(history_header, text="📝 Recent Searches", 
                                font=('Segoe UI', 16, 'bold'),
                                bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        history_title.pack(anchor='w')
        
        # History list
        history_content = tk.Frame(history_section, bg=self.colors['bg_card'])
        history_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
        
        self.history_frame = tk.Frame(history_content, bg=self.colors['bg_card'])
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initially show empty state
        self.update_search_history()
        
        # Right panel - Search results
        right_panel = tk.Frame(main_content, bg=self.colors['bg_primary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Results section
        results_section = tk.Frame(right_panel, bg=self.colors['bg_card'], relief='raised', bd=1)
        results_section.pack(fill=tk.BOTH, expand=True)
        
        # Results header
        results_header = tk.Frame(results_section, bg=self.colors['bg_card'])
        results_header.pack(fill=tk.X, padx=30, pady=(30, 15))
        
        self.results_title = tk.Label(results_header, text="📊 Search Results", 
                                     font=('Segoe UI', 18, 'bold'),
                                     bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        self.results_title.pack(anchor='w')
        
        self.results_subtitle = tk.Label(results_header, text="Your search results will appear here", 
                                        font=('Segoe UI', 11),
                                        bg=self.colors['bg_card'], fg=self.colors['text_muted'])
        self.results_subtitle.pack(anchor='w', pady=(5, 0))
        
        # Results content with scrollable frame
        results_content = tk.Frame(results_section, bg=self.colors['bg_card'])
        results_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Canvas and scrollbar for custom scrolling
        self.results_canvas = tk.Canvas(results_content, bg=self.colors['bg_primary'], 
                                       highlightthickness=0, relief='flat')
        results_scrollbar = ttk.Scrollbar(results_content, orient="vertical", 
                                         command=self.results_canvas.yview)
        self.scrollable_results = tk.Frame(self.results_canvas, bg=self.colors['bg_primary'])
        
        self.scrollable_results.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        )
        
        self.results_canvas.create_window((0, 0), window=self.scrollable_results, anchor="nw")
        self.results_canvas.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_canvas.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel binding
        self.results_canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Initial welcome message
        self.show_initial_results_message()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_search_text_change(self, event=None):
        """Handle search text changes"""
        text = self.search_entry.get("1.0", tk.END).strip()
        if text:
            self.start_search_btn.config(text="🔎 Search Documents")
        else:
            self.start_search_btn.config(text="🔎 Search Documents")
    
    def clear_search(self):
        """Clear search input"""
        self.search_entry.delete("1.0", tk.END)
        self.show_initial_results_message()
    
    def update_search_history(self):
        """Update the search history display"""
        # Clear existing history items
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if not self.search_history:
            # Show empty state
            empty_label = tk.Label(self.history_frame, text="No recent searches", 
                                  font=('Segoe UI', 11),
                                  bg=self.colors['bg_card'], fg=self.colors['text_muted'])
            empty_label.pack(pady=20)
        else:
            # Show recent searches (max 5)
            for i, query in enumerate(reversed(self.search_history[-5:])):
                history_item = tk.Frame(self.history_frame, bg=self.colors['highlight'], 
                                       cursor='hand2', relief='flat')
                history_item.pack(fill=tk.X, pady=2)
                
                # Truncate long queries
                display_query = query[:40] + "..." if len(query) > 40 else query
                
                query_label = tk.Label(history_item, text=f"🔍 {display_query}", 
                                      font=('Segoe UI', 10),
                                      bg=self.colors['highlight'], fg=self.colors['text_secondary'],
                                      anchor='w', padx=15, pady=8)
                query_label.pack(fill=tk.X)
                
                # Bind click events
                def make_click_handler(q):
                    return lambda e: self.use_history_query(q)
                
                history_item.bind("<Button-1>", make_click_handler(query))
                query_label.bind("<Button-1>", make_click_handler(query))
                
                # Hover effects
                def on_enter(e, item=history_item):
                    item.config(bg=self.colors['bg_input'])
                    for child in item.winfo_children():
                        child.config(bg=self.colors['bg_input'])
                
                def on_leave(e, item=history_item):
                    item.config(bg=self.colors['highlight'])
                    for child in item.winfo_children():
                        child.config(bg=self.colors['highlight'])
                
                history_item.bind("<Enter>", on_enter)
                history_item.bind("<Leave>", on_leave)
                query_label.bind("<Enter>", on_enter)
                query_label.bind("<Leave>", on_leave)
    
    def use_history_query(self, query):
        """Use a query from search history"""
        self.search_entry.delete("1.0", tk.END)
        self.search_entry.insert("1.0", query)
        self.start_search()
    
    def show_initial_results_message(self):
        """Show initial message in results area"""
        # Clear results
        for widget in self.scrollable_results.winfo_children():
            widget.destroy()
        
        # Welcome message
        welcome_frame = tk.Frame(self.scrollable_results, bg=self.colors['bg_primary'])
        welcome_frame.pack(fill=tk.BOTH, expand=True, pady=50)
        
        icon_label = tk.Label(welcome_frame, text="🔍", font=('Segoe UI', 48),
                             bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
        icon_label.pack()
        
        welcome_text = tk.Label(welcome_frame, text="Start searching your documents", 
                               font=('Segoe UI', 16, 'bold'),
                               bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        welcome_text.pack(pady=(20, 10))
        
        tip_text = tk.Label(welcome_frame, 
                           text="Enter your question or topic in the search box\nand let AI find the most relevant content",
                           font=('Segoe UI', 12), justify=tk.CENTER,
                           bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
        tip_text.pack()
    
    def add_org_log(self, message):
        """Add message to organization log"""
        if hasattr(self, 'org_log'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.org_log.insert(tk.END, f"[{timestamp}] {message}\n")
            self.org_log.see(tk.END)
    
    def start_organization(self):
        """Start file organization"""
        self.start_org_btn.config(state='disabled', text="🔄 Processing...")
        self.org_progress.start()
        self.org_progress_label.config(text="Organizing documents...")
        self.status_label.config(text="Organization in progress...")
        
        # Clear log
        self.org_log.delete(1.0, tk.END)
        self.add_org_log("🚀 Starting document organization process...")
        
        # Start background thread
        thread = threading.Thread(target=self.organize_worker)
        thread.daemon = True
        thread.start()
    
    def organize_worker(self):
        """Background worker for organization"""
        try:
            self.message_queue.put(("org_log", "📁 Scanning for PDF documents..."))
            self.message_queue.put(("org_log", "🤖 Loading AI embeddings..."))
            self.message_queue.put(("org_log", "🔄 Processing document clusters..."))
            
            result = organize_files()
            
            self.message_queue.put(("org_log", "✅ Document organization completed successfully!"))
            self.message_queue.put(("org_done", "success"))
            
        except Exception as e:
            self.message_queue.put(("org_log", f"❌ Organization failed: {str(e)}"))
            self.message_queue.put(("org_done", "error"))
    
    def start_search(self):
        """Start document search"""
        query = self.search_entry.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Search Query", "Please enter a search query.")
            return
        
        # Add to search history
        if query not in self.search_history:
            self.search_history.append(query)
            self.update_search_history()
        
        self.start_search_btn.config(state='disabled', text="🔄 Searching...")
        self.status_label.config(text=f"Searching for: {query[:50]}...")
        
        # Show searching state
        self.show_searching_state(query)
        
        # Start background thread
        thread = threading.Thread(target=self.search_worker, args=(query,))
        thread.daemon = True
        thread.start()
    
    def show_searching_state(self, query):
        """Show searching animation/state"""
        # Clear results
        for widget in self.scrollable_results.winfo_children():
            widget.destroy()
        
        # Update results title
        self.results_title.config(text=f"🔍 Searching...")
        self.results_subtitle.config(text=f"Looking for: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Searching animation
        searching_frame = tk.Frame(self.scrollable_results, bg=self.colors['bg_primary'])
        searching_frame.pack(fill=tk.BOTH, expand=True, pady=100)
        
        spinner_label = tk.Label(searching_frame, text="⟳", font=('Segoe UI', 48),
                                bg=self.colors['bg_primary'], fg=self.colors['accent'])
        spinner_label.pack()
        
        searching_text = tk.Label(searching_frame, text="Searching through your documents...", 
                                 font=('Segoe UI', 16),
                                 bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        searching_text.pack(pady=(20, 10))
        
        detail_text = tk.Label(searching_frame, text="Using AI to find the most relevant content",
                              font=('Segoe UI', 12),
                              bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
        detail_text.pack()
    
    def search_worker(self, query):
        """Background worker for search"""
        try:
            results = search_documents(query, embedder=embedder)
            self.message_queue.put(("search_done", (query, results)))
            
        except Exception as e:
            self.message_queue.put(("search_error", str(e)))
    
    def display_search_results(self, query, results):
        """Display enhanced search results"""
        # Clear results
        for widget in self.scrollable_results.winfo_children():
            widget.destroy()
        
        try:
            if isinstance(results, dict) and 'documents' in results:
                documents = results.get('documents', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                # Update header
                if not documents:
                    self.results_title.config(text="📭 No Results Found")
                    self.results_subtitle.config(text=f"No matches for '{query}'")
                    self.show_no_results_message(query)
                    return
                
                # Show results count
                result_count = len(documents)
                self.results_title.config(text=f"📊 Search Results ({result_count})")
                self.results_subtitle.config(text=f"Found {result_count} relevant document{'s' if result_count != 1 else ''}")
                
                # Display each result as a card
                for i, doc in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    distance = distances[i] if i < len(distances) else 0.0
                    
                    self.create_result_card(doc, metadata, distance, i + 1)
                
                # Add summary at the end
                self.create_search_summary(query, result_count)
            
        except Exception as e:
            self.show_error_message(f"Error displaying results: {str(e)}")
    
    def create_result_card(self, document, metadata, distance, result_number):
        """Create an enhanced result card"""
        # Extract metadata
        file_path = metadata.get('file_path', 'Unknown')
        filename = self.extract_filename(file_path)
        page = metadata.get('page_number', 1)
        title = metadata.get('title', filename)
        chunk_index = metadata.get('chunk_index', 0)
        
        # Calculate relevance score
        relevance = max(0, min(100, int((2.0 - distance) * 50)))
        relevance_color = self.get_relevance_color(relevance)
        
        # Main card container
        card = tk.Frame(self.scrollable_results, bg=self.colors['bg_card'], 
                       relief='solid', bd=1)
        card.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        # Card header
        header = tk.Frame(card, bg=self.colors['bg_secondary'])
        header.pack(fill=tk.X, padx=1, pady=(1, 0))
        
        header_content = tk.Frame(header, bg=self.colors['bg_secondary'])
        header_content.pack(fill=tk.X, padx=20, pady=12)
        
        # Result number and title
        title_frame = tk.Frame(header_content, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.X)
        
        result_num_label = tk.Label(title_frame, text=f"#{result_number}", 
                                   font=('Segoe UI', 12, 'bold'),
                                   bg=self.colors['bg_secondary'], 
                                   fg=self.colors['accent'])
        result_num_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_frame, text=f"📄 {title}", 
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Relevance score
        relevance_label = tk.Label(title_frame, text=f"{relevance}% Match", 
                                  font=('Segoe UI', 11, 'bold'),
                                  bg=self.colors['bg_secondary'], 
                                  fg=relevance_color)
        relevance_label.pack(side=tk.RIGHT)
        
        # Metadata row
        meta_frame = tk.Frame(header_content, bg=self.colors['bg_secondary'])
        meta_frame.pack(fill=tk.X, pady=(8, 0))
        
        page_label = tk.Label(meta_frame, text=f"📑 Page {page}", 
                             font=('Segoe UI', 10),
                             bg=self.colors['bg_secondary'], 
                             fg=self.colors['text_muted'])
        page_label.pack(side=tk.LEFT)
        
        if chunk_index > 0:
            chunk_label = tk.Label(meta_frame, text=f"• Section {chunk_index}", 
                                  font=('Segoe UI', 10),
                                  bg=self.colors['bg_secondary'], 
                                  fg=self.colors['text_muted'])
            chunk_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # File path (truncated)
        path_display = self.truncate_path(file_path, 60)
        path_label = tk.Label(meta_frame, text=f"📁 {path_display}", 
                             font=('Segoe UI', 10),
                             bg=self.colors['bg_secondary'], 
                             fg=self.colors['text_muted'])
        path_label.pack(side=tk.RIGHT)
        
        # Content preview
        content_frame = tk.Frame(card, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.X, padx=20, pady=15)
        
        content_label = tk.Label(content_frame, text="📝 Content Preview:", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg_card'], 
                                fg=self.colors['text_primary'])
        content_label.pack(anchor='w', pady=(0, 8))
        
        # Format and display content
        content_preview = self.format_content_preview(document, 300)
        
        content_text = tk.Text(content_frame, height=4, wrap=tk.WORD,
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_secondary'],
                              font=('Segoe UI', 11), relief='flat', bd=0,
                              padx=15, pady=10, state='normal')
        content_text.pack(fill=tk.X)
        
        content_text.insert(tk.END, content_preview)
        content_text.config(state='disabled')  # Make read-only
        
        # Action buttons
        actions_frame = tk.Frame(card, bg=self.colors['bg_card'])
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        open_btn = ttk.Button(actions_frame, text="📖 Open Document", 
                             style='Small.TButton')
        open_btn.pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(actions_frame, text="📋 Copy Content", 
                             style='Small.TButton',
                             command=lambda: self.copy_to_clipboard(document))
        copy_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def extract_filename(self, file_path):
        """Extract filename from path"""
        if file_path == 'Unknown':
            return 'Unknown Document'
        return file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
    
    def truncate_path(self, path, max_length):
        """Truncate file path for display"""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
    
    def get_relevance_color(self, relevance):
        """Get color based on relevance score"""
        if relevance >= 80:
            return self.colors['success']
        elif relevance >= 60:
            return self.colors['warning']
        else:
            return self.colors['text_muted']
    
    def format_content_preview(self, content, max_chars):
        """Format content preview with highlighting"""
        if len(content) <= max_chars:
            return content
        
        # Find a good breaking point (end of sentence)
        preview = content[:max_chars]
        last_period = preview.rfind('.')
        last_space = preview.rfind(' ')
        
        if last_period > max_chars * 0.7:
            preview = content[:last_period + 1]
        elif last_space > max_chars * 0.8:
            preview = content[:last_space]
        
        return preview + "..."
    
    def copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_label.config(text="Content copied to clipboard")
        # Reset status after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))
    
    def create_search_summary(self, query, result_count):
        """Create search summary at the end"""
        summary_frame = tk.Frame(self.scrollable_results, bg=self.colors['bg_secondary'],
                                relief='solid', bd=1)
        summary_frame.pack(fill=tk.X, pady=(20, 0), padx=5)
        
        summary_content = tk.Frame(summary_frame, bg=self.colors['bg_secondary'])
        summary_content.pack(fill=tk.X, padx=20, pady=15)
        
        summary_title = tk.Label(summary_content, text="📈 Search Summary", 
                                font=('Segoe UI', 14, 'bold'),
                                bg=self.colors['bg_secondary'], 
                                fg=self.colors['text_primary'])
        summary_title.pack(anchor='w')
        
        summary_text = tk.Label(summary_content, 
                               text=f"Found {result_count} relevant document{'s' if result_count != 1 else ''} for your query: '{query}'",
                               font=('Segoe UI', 11),
                               bg=self.colors['bg_secondary'], 
                               fg=self.colors['text_secondary'],
                               wraplength=600, anchor='w', justify='left')
        summary_text.pack(anchor='w', pady=(5, 0))
        
        # Tips for better searching
        tips_text = tk.Label(summary_content, 
                            text="💡 Tip: Try different keywords or more specific questions for different results",
                            font=('Segoe UI', 10),
                            bg=self.colors['bg_secondary'], 
                            fg=self.colors['text_muted'],
                            wraplength=600, anchor='w', justify='left')
        tips_text.pack(anchor='w', pady=(8, 0))
    
    def show_no_results_message(self, query):
        """Show message when no results are found"""
        no_results_frame = tk.Frame(self.scrollable_results, bg=self.colors['bg_primary'])
        no_results_frame.pack(fill=tk.BOTH, expand=True, pady=80)
        
        icon_label = tk.Label(no_results_frame, text="🤷‍♂️", font=('Segoe UI', 64),
                             bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
        icon_label.pack()
        
        title_label = tk.Label(no_results_frame, text="No documents found", 
                              font=('Segoe UI', 20, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        title_label.pack(pady=(20, 10))
        
        desc_label = tk.Label(no_results_frame, 
                             text=f"We couldn't find any documents matching '{query}'\n\nTry these suggestions:",
                             font=('Segoe UI', 12), justify=tk.CENTER,
                             bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
        desc_label.pack(pady=(0, 20))
        
        # Suggestions
        suggestions = [
            "• Use different or more general keywords",
            "• Check spelling and try synonyms", 
            "• Try asking a question instead of keywords",
            "• Make sure your documents are organized first"
        ]
        
        for suggestion in suggestions:
            sugg_label = tk.Label(no_results_frame, text=suggestion,
                                 font=('Segoe UI', 11),
                                 bg=self.colors['bg_primary'], 
                                 fg=self.colors['text_muted'])
            sugg_label.pack(pady=2)
    
    def show_error_message(self, error_msg):
        """Show error message in results area"""
        # Clear results
        for widget in self.scrollable_results.winfo_children():
            widget.destroy()
        
        self.results_title.config(text="❌ Search Error")
        self.results_subtitle.config(text="An error occurred during search")
        
        error_frame = tk.Frame(self.scrollable_results, bg=self.colors['bg_primary'])
        error_frame.pack(fill=tk.BOTH, expand=True, pady=80)
        
        icon_label = tk.Label(error_frame, text="⚠️", font=('Segoe UI', 48),
                             bg=self.colors['bg_primary'], fg=self.colors['warning'])
        icon_label.pack()
        
        error_label = tk.Label(error_frame, text="Search Error", 
                              font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        error_label.pack(pady=(20, 10))
        
        detail_label = tk.Label(error_frame, text=error_msg,
                               font=('Segoe UI', 12),
                               bg=self.colors['bg_primary'], fg=self.colors['text_muted'],
                               wraplength=400, justify=tk.CENTER)
        detail_label.pack()
    
    def check_queue(self):
        """Check for messages from background threads"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "org_log":
                    self.add_org_log(data)
                
                elif msg_type == "org_done":
                    if hasattr(self, 'org_progress'):
                        self.org_progress.stop()
                        self.start_org_btn.config(state='normal', text="🚀 Start Organization")
                        if data == "success":
                            self.org_progress_label.config(text="✅ Organization completed successfully!")
                            self.status_label.config(text="Documents organized successfully")
                        else:
                            self.org_progress_label.config(text="❌ Organization failed")
                            self.status_label.config(text="Organization failed")
                
                elif msg_type == "search_done":
                    query, results = data
                    if hasattr(self, 'start_search_btn'):
                        self.start_search_btn.config(state='normal', text="🔎 Search Documents")
                        self.display_search_results(query, results)
                        self.status_label.config(text="Search completed")
                
                elif msg_type == "search_error":
                    if hasattr(self, 'start_search_btn'):
                        self.start_search_btn.config(state='normal', text="🔎 Search Documents")
                        self.show_error_message(data)
                        self.status_label.config(text="Search failed")
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BeautifulDocumentMVP()
    app.run()