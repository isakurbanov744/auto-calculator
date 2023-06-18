import tkinter as tk
import sqlite3

class DBFilenameWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Enter Database File Name")

        # Create a label for the entry field
        self.label = tk.Label(self.master, text="Enter database file name:")
        self.label.pack(pady=10)

        # Create an entry field to input the file name
        self.filename_entry = tk.Entry(self.master)
        self.filename_entry.pack(pady=5)

        # Create a button to submit the file name
        self.submit_btn = tk.Button(self.master, text="Submit", command=self.submit_filename)
        self.submit_btn.pack(pady=5)

    def submit_filename(self):
        db_file = self.filename_entry.get()
        if db_file:
            self.master.destroy()  # Close the filename window
            self.start_application(db_file)

    def start_application(self, db_file):
        root = tk.Tk()
        app = DBViewerApp(root, db_file)
        root.mainloop()

class DBViewerApp:
    def __init__(self, master, db_file):
        self.master = master
        self.master.title("DB Viewer")

        # Create a text box for SQL commands
        self.sql_entry = tk.Text(self.master, height=5, width=50)
        self.sql_entry.pack(pady=10)

        # Create a button to execute SQL commands
        self.execute_btn = tk.Button(self.master, text="Execute", command=self.execute_sql)
        self.execute_btn.pack(pady=5)

        # Create a button to view database rows and columns
        self.view_btn = tk.Button(self.master, text="View Database", command=self.view_database)
        self.view_btn.pack(pady=5)

        # Create a text box to display query results
        self.result_text = tk.Text(self.master, height=15, width=50)
        self.result_text.pack(pady=10)

        # Connect to the database
        self.conn = None
        self.cursor = None

        self.connect_to_database(db_file)

    def connect_to_database(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            print("Connected to the database successfully.")
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def execute_sql(self):
        sql_query = self.sql_entry.get("1.0", tk.END).strip()

        try:
            self.cursor.execute(sql_query)
            rows = self.cursor.fetchall()

            # Clear the result text box
            self.result_text.delete("1.0", tk.END)

            # Display the query result
            for row in rows:
                self.result_text.insert(tk.END, str(row) + "\n")
            print("SQL query executed successfully.")
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")

    def view_database(self):
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()

            # Clear the result text box
            self.result_text.delete("1.0", tk.END)

            # Display the table names
            for table in tables:
                self.result_text.insert(tk.END, f"Table: {table[0]}\n")

                # Get the column names for the table
                self.cursor.execute(f"PRAGMA table_info({table[0]});")
                columns = self.cursor.fetchall()
                column_names = [column[1] for column in columns]
                self.result_text.insert(tk.END, f"Columns: {', '.join(column_names)}\n\n")

            print("Database structure displayed.")
        except sqlite3.Error as e:
            print(f"Error viewing database: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    filename_window = DBFilenameWindow(root)
    root.mainloop()
