import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import sqlite3
from tkinter import ttk

# Function to open the settings window


def open_settings_window(root, category_mapping):
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x400")
    settings_window.minsize(400, 400)

    selected_code_index = None  # Track the selected code index

    # Function to update the codes for the selected category
    def update_codes(event):
        selected_category = category_var.get()

        if selected_category in category_mapping:
            codes_listbox.delete(0, tk.END)
            for code in category_mapping[selected_category]:
                codes_listbox.insert(tk.END, code)

    # Function to edit the selected code
    def edit_code():
        selected_category = category_var.get()
        selected_code = codes_listbox.get(selected_code_index)

        if selected_code:

            # Open a new window for code editing
            edit_window = tk.Toplevel(settings_window)
            edit_window.title("Edit Code")
            edit_window.geometry("200x200")

            # Create an entry field with the selected code
            code_entry = tk.Entry(edit_window)
            code_entry.insert(tk.END, selected_code)
            code_entry.pack()

            # Function to update the edited code
            def update_code():
                new_code = code_entry.get()
                if selected_category in category_mapping:
                    category_mapping[selected_category][selected_code_index] = new_code

                    # Update the database
                    conn = sqlite3.connect('category_mapping.db')
                    c = conn.cursor()
                    c.execute("UPDATE mapping SET codes = ? WHERE category = ?", (','.join(
                        category_mapping[selected_category]), selected_category))
                    conn.commit()
                    conn.close()

                    # Update the codes in the listbox
                    update_codes(None)

                    # Close the edit window
                    edit_window.destroy()

            # Create a button to update the code
            update_button = tk.Button(
                edit_window, text="Update", command=update_code)
            update_button.pack()

    # Function to remove the selected code
    def remove_code():
        selected_category = category_var.get()
        selected_code = codes_listbox.get(selected_code_index)

        if selected_category in category_mapping:
            category_mapping[selected_category].remove(selected_code)

            # Update the database
            conn = sqlite3.connect('category_mapping.db')
            c = conn.cursor()
            c.execute("UPDATE mapping SET codes = ? WHERE category = ?", (','.join(
                category_mapping[selected_category]), selected_category))
            conn.commit()

            # Insert the removed code into the deleted_records table
            # c.execute("INSERT INTO deleted_records VALUES (?, ?)", (selected_category, selected_code))
            # conn.commit()

            conn.close()

            # Update the codes in the listbox
            update_codes(None)

    def add_code():
        selected_category = category_var.get()
        new_code = new_code_entry.get()

        if selected_category and new_code:
            if selected_category in category_mapping:
                if new_code not in category_mapping[selected_category]:
                    
                    if len(category_mapping[selected_category]) > 0:
                        category_mapping[selected_category].append(new_code)
                        conn = sqlite3.connect('category_mapping.db')
                        c = conn.cursor()

                        # Update the existing codes for the specified category
                        query = f"UPDATE mapping SET codes = codes || ',{new_code}' WHERE category = '{selected_category}'"
                        c.execute(query)

                        conn.commit()
                        conn.close()

                    else:
                        category_mapping[selected_category].append(new_code)
                        conn = sqlite3.connect('category_mapping.db')
                        c = conn.cursor()

                        # Update the existing codes for the specified category
                        query = f"UPDATE mapping SET codes = '{new_code}' WHERE category = '{selected_category}'"
                        c.execute(query)

                        conn.commit()
                        conn.close()
                else:
                    messagebox.showerror(
                        "Error", f"Code: {new_code} already exists")
            else:
                category_mapping[selected_category] = [new_code]

            # Clear the new code entry field
            new_code_entry.delete(0, tk.END)

            # Update the codes in the text widget
            update_codes(None)

    category_var = tk.StringVar(settings_window)
    category_var.set("")  # Set an initial empty value

    # Create a Combobox instead of an OptionMenu
    category_dropdown = ttk.Combobox(settings_window, textvariable=category_var, values=list(
        category_mapping.keys()), state='readonly')
    category_dropdown.pack()

    # Bind the test function to the combobox selection event
    category_dropdown.bind("<<ComboboxSelected>>", update_codes)

    # Create a listbox to display the codes
    codes_listbox = tk.Listbox(settings_window, height=10, width=40)
    codes_listbox.pack()

    # Bind the listbox selection event
    def select_code(event):
        nonlocal selected_code_index

        if codes_listbox.curselection():
            selected_code_index = codes_listbox.curselection()[0]

        else:
            selected_code_index = None

    codes_listbox.bind('<<ListboxSelect>>', select_code)

    # Create a label and entry field for adding new codes
    new_code_label = tk.Label(settings_window, text="New Code:")
    new_code_label.pack()

    new_code_entry = tk.Entry(settings_window)
    new_code_entry.pack()

    # Create a button to add a new code for the selected category
    add_code_button = tk.Button(
        settings_window, text="Add Code", command=add_code)
    add_code_button.pack()

    # Create a button to edit the selected code
    edit_code_button = tk.Button(
        settings_window, text="Edit Code", command=edit_code)
    edit_code_button.pack()

    # Create a button to remove the selected code
    remove_code_button = tk.Button(
        settings_window, text="Remove Code", command=remove_code)
    remove_code_button.pack()

    # Run the settings window
    settings_window.mainloop()

    # Create a frame for the settings content
    settings_frame = tk.Frame(settings_window)
    settings_frame.pack(padx=10, pady=10)

    # Create a label and dropdown menu for selecting categories
    category_select_label = tk.Label(settings_frame, text="Select Category:")
    category_select_label.pack()

    category_var = tk.StringVar(settings_frame)
    category_var.set("")  # Set an initial empty value
    category_dropdown = tk.OptionMenu(settings_frame, category_var, *category_mapping.keys())
    category_dropdown.pack()

    # Create a frame for the buttons
    buttons_frame = tk.Frame(settings_frame)
    buttons_frame.pack(pady=10)

    # Create a button to update the codes for the selected category
    update_codes_button = tk.Button(buttons_frame, text="Update Codes", command=update_codes)
    update_codes_button.pack(side=tk.LEFT, padx=5)

    # Create a label and entry field for adding new codes
    new_code_label = tk.Label(settings_frame, text="New Code:")
    new_code_label.pack()

    new_code_entry = tk.Entry(settings_frame)
    new_code_entry.pack()

    # Create a button to add a new code for the selected category
    add_code_button = tk.Button(buttons_frame, text="Add Code", command=add_code)
    add_code_button.pack(side=tk.LEFT, padx=5)

    # Create a text widget to display the codes
    codes_text = tk.Text(settings_frame, height=10, width=30)
    codes_text.pack()

