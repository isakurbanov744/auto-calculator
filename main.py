import glob
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from utils import process_excel_file, save_results_to_excel
import pandas as pd
from tkinter import ttk
from template_generator import file_generator
import sqlite3
from settings_window import open_settings_window


# Function to process and save the Excel files
def save_processed_file():
    directory = filedialog.askdirectory(title="Select Sales Directory")
    if directory:
        excel_files = glob.glob(directory + '/*.xls')

        if not excel_files:
            messagebox.showinfo(
                "No Files Found", "No Excel files found in the selected directory.")
            return

        total_files = len(excel_files)
        processed_files = 0

        for file_path in excel_files:
            try:
                # Assuming you have defined this function
                results = process_excel_file(file_path)
                save_results_to_excel(results, file_path.replace(
                    '.xls', '_category_sales.xlsx'))
                processed_files += 1
                progress = int((processed_files / total_files) * 100)
            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while processing '{file_path}': {str(e)}")

        messagebox.showinfo(
            "Process Complete", f"{processed_files} files processed and saved successfully.")
    else:
        messagebox.showinfo("No Directory Selected",
                            "Please select a directory to process.")


# Function to view the Excel data
def view_excel_data():
    file_path = filedialog.askopenfilename(title="Select Excel File")
    if file_path:
        try:
            df = pd.read_excel(file_path)

            top = tk.Toplevel()
            top.title("Excel Data")
            top.geometry("800x600")
            top.minsize(800, 600)

            filter_frame = tk.Frame(top)
            filter_frame.pack(pady=5)

            filter_label = tk.Label(filter_frame, text="Group:")
            filter_label.pack(side=tk.LEFT)

            filter_entry = tk.Entry(filter_frame, width=20)
            filter_entry.pack(side=tk.LEFT)

            search_button = tk.Button(filter_frame, text="Search",
                                      command=lambda: apply_filter(treeview, df, filter_entry.get()))
            search_button.pack(side=tk.LEFT, padx=5)

            clear_button = tk.Button(filter_frame, text="Clear",
                                     command=lambda: clear_filter(treeview, df))
            clear_button.pack(side=tk.LEFT, padx=5)

            treeview = ttk.Treeview(top)
            treeview["columns"] = list(df.columns)

            # Configure treeview columns
            treeview.column("#0", width=30, anchor=tk.W)
            for column in list(df.columns):
                treeview.heading(column, text=column, anchor=tk.W)
                treeview.column(column, width=100, anchor=tk.W)

            # Format numbers to two decimal points
            df = df.round(2)

            # Insert data into treeview
            for i, row in df.iterrows():
                values = [f"{value}" if isinstance(
                    value, (int, float)) else value for value in row]
                treeview.insert("", tk.END, text=str(i), values=tuple(values))

            # Configure column headings to be bold
            style = ttk.Style()
            style.configure("Treeview.Heading", font=(
                "TkDefaultFont", 10, "bold"))

            treeview.pack(expand=True, fill=tk.BOTH)

            # Enable vertical scrolling
            y_scrollbar = ttk.Scrollbar(
                top, orient="vertical", command=treeview.yview)
            treeview.configure(yscroll=y_scrollbar.set)
            y_scrollbar.pack(side="right", fill="y")

            # Enable horizontal scrolling
            x_scrollbar = ttk.Scrollbar(
                top, orient="horizontal", command=treeview.xview)
            treeview.configure(xscroll=x_scrollbar.set)
            x_scrollbar.pack(side="bottom", fill="x")

            # Enable column resizing
            treeview.column("#0", stretch=tk.NO)
            for column in list(df.columns):
                treeview.heading(
                    column, anchor=tk.W, command=lambda c=column: sort_column(treeview, df, c))

        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while opening '{file_path}': {str(e)}")


# Function to apply filter to the treeview data
def apply_filter(treeview, df, filter_text):
    treeview.delete(*treeview.get_children())

    filtered_df = df[df.apply(lambda row: any(
        str(value).lower().startswith(filter_text.lower()) for value in row), axis=1)]

    for i, row in filtered_df.iterrows():
        values = [f"{value}" if isinstance(
            value, (int, float)) else value for value in row]
        treeview.insert("", tk.END, text=str(i), values=tuple(values))

# Function to clear the filter and display all data


def clear_filter(treeview, df):
    treeview.delete(*treeview.get_children())

    for i, row in df.iterrows():
        values = [f"{value}" if isinstance(
            value, (int, float)) else value for value in row]
        treeview.insert("", tk.END, text=str(i), values=tuple(values))

# Function to sort the treeview columns


def sort_column(treeview, df, column, reverse=False):
    df.sort_values(by=column, ascending=reverse, inplace=True)
    treeview.delete(*treeview.get_children())

    for i, row in df.iterrows():
        values = [f"{value}" if isinstance(
            value, (int, float)) else value for value in row]
        treeview.insert("", tk.END, text=str(i), values=tuple(values))




# Function to save the category and code to the database
def save_to_database(category, code):
    # Connect to the database
    conn = sqlite3.connect('category_mapping.db')
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS mapping
                 (category text PRIMARY KEY, code text)''')

    # Insert or update the mapping in the table
    c.execute("INSERT OR REPLACE INTO mapping (category, code) VALUES (?, ?)", (category, code))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Load the category_mapping from the database
def load_category_mapping():
    conn = sqlite3.connect('category_mapping.db')
    c = conn.cursor()
    c.execute("SELECT category, codes FROM mapping")
    rows = c.fetchall()
    conn.close()

    return dict(rows)

# Function to load the category mapping from the database
def load_category_mapping():
    conn = sqlite3.connect('category_mapping.db')
    c = conn.cursor()
    c.execute("SELECT category, codes FROM mapping")
    rows = c.fetchall()
    conn.close()

    category_mapping = {}
    for row in rows:
        category = row[0]
        if row[1] != None:
            codes = row[1].split(',')
            category_mapping[category] = codes
        else:
            category_mapping[category] = []

    return category_mapping



# Create the main application window
root = tk.Tk()
root.title("Sales Data Processing")

# Load the category_mapping from the database
category_mapping = load_category_mapping()

# Set the window size and position it in the center of the screen
window_width = 800
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.LEFT, padx=20, pady=20)

# Calculate the maximum button width
button_width = max(len("Save Processed Files"), len("View Excel Data"), len("Generate Template")) + 6  # Adjust padding as needed

# Create a button to save the processed files
save_button = tk.Button(button_frame, text="Save Processed Files", command=save_processed_file, width=button_width, padx=10, pady=5)
save_button.pack(pady=5)

# Create a button to view the exported Excel data
view_data_button = tk.Button(button_frame, text="View Excel Data", command=view_excel_data, width=button_width, padx=10, pady=5)
view_data_button.pack(pady=5)

# Create a button to generate a template
generate_template_button = tk.Button(button_frame, text="Generate Template", command=lambda: file_generator(), width=button_width, padx=10, pady=10)
generate_template_button.pack(pady=5)

# Button to open settings window
settings_button = tk.Button(button_frame, text="Settings", command=lambda: open_settings_window(root, category_mapping), width=button_width, padx=10, pady=5)
settings_button.pack(pady=5)



# Configure a custom color scheme
root.configure(bg="#f2f2f2")
button_frame.configure(bg="#f2f2f2")




# Start the Tkinter event loop
root.mainloop()
