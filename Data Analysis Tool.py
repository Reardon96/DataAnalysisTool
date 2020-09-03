# Import relevant modules
import tkinter as tk
from tkinter import filedialog 
from tkinter import ttk
import pandas as pd
import numpy as np
import os, pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI_Main:

    def __init__(self, master):
        # Configure window properties
        tk.frame = tk.Frame(master)
        tk.frame.pack()
     
        tk.frame_labels = tk.Frame(master)
        tk.frame_labels.pack()

        tk.frame_label_city = tk.Frame(master)
        tk.frame_label_city.pack()

        tk.frame_table_city = tk.Frame(master)
        tk.frame_table_city.pack()

        tk.frame_table_overall = tk.Frame(master)
        tk.frame_table_overall.pack()

        master.title("Data Analysis Tool")
        master.geometry("1800x900")
        self.master = master

        # Load data backup if it exists
        self.cwd = os.getcwd()
        self.pickle_df_filepath = self.cwd + "\dfbackup.p"
        self.pickle_filepath_filepath = self.cwd + "\currentfp.p"
        try:
            self.df = pd.read_pickle(self.pickle_df_filepath)
        except FileNotFoundError:
            self.df = pd.DataFrame()      
        try:
            self.current_file_loaded = pickle.load(open(self.pickle_filepath_filepath, "rb" ))
        except FileNotFoundError:
            self.current_file_loaded = ""
        
        # Configure buttons
        self.load_csv_button = tk.Button(tk.frame, text="Load CSV", command=self.load_csv)
        self.load_csv_button.pack(side=tk.LEFT, pady=(10,10))

        self.load_json_button =tk.Button(tk.frame, text="Load JSON", command=self.load_json)
        self.load_json_button.pack(side=tk.LEFT)

        self.save_as_json_button =tk.Button(tk.frame, text="Save As", command=self.save_as_json)
        self.save_as_json_button.pack(side=tk.LEFT)

        self.clean_button = tk.Button(tk.frame, text="Clean Data", command=lambda: self.clean_data(self.df))
        self.clean_button.pack(side=tk.LEFT, padx=(20,20))

        self.violation_button = tk.Button(tk.frame, text="Plot Violation Data", command=lambda: self.display_plot_violation_data(self.df))
        self.violation_button.pack(side=tk.LEFT)

        self.inspection_button = tk.Button(tk.frame, text="Plot Inspection Data", command=lambda: self.plot_tables(self.df))
        self.inspection_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(tk.frame, text="Quit", command=tk.frame.quit)
        self.quit_button.pack(side=tk.LEFT, padx=(20, 0))

        # Configure labels
        self.label = tk.Label(tk.frame_labels, text="STATUS:")
        self.label.pack(side=tk.LEFT)

        self.output_label = tk.Label(tk.frame_labels, text="OK")
        self.output_label.config(width=25, anchor=tk.W)
        self.output_label.pack(side=tk.LEFT)
        
        # Configure menu
        topMenu = tk.Menu(root)
    
    # Dialogs for loading/saving files    
    def load_csv(self):
        csv_filepath = filedialog.askopenfilename(initialdir=self.cwd, title="Select file", filetypes=[("csv", "*.csv")])
        self.df = self.csv_to_df(csv_filepath)
        self.current_file_loaded = csv_filepath
        self.save_df_as_pickle(self.df, self.pickle_df_filepath)
        self.save_filepath_as_pickle(self.current_file_loaded, self.pickle_filepath_filepath)

    def save_as_json(self):
        json_filepath = filedialog.asksaveasfilename(initialdir=self.cwd, title="Select file", filetypes=([("json","*.json")]))
        if json_filepath.endswith(".json") == False:
            json_filepath = json_filepath + ".json"
        self.df.to_json(json_filepath)
    
    def save_df_as_pickle(self, df, pickle_df_filepath):
        df.to_pickle(pickle_df_filepath)
    
    def save_filepath_as_pickle(self, current_filepath, pickle_filepath_filepath):
        pickle.dump(self.current_file_loaded, open( self.pickle_filepath_filepath, "wb"))

    def load_json(self):
            json_filepath = filedialog.askopenfilename(initialdir=self.cwd, title="Select file", filetypes=[("json", "*.json")])
            self.df = self.json_to_df(json_filepath)
            self.current_file_loaded = json_filepath
            self.save_df_as_pickle(self.df, self.pickle_df_filepath)
            self.save_filepath_as_pickle(self.current_file_loaded, self.pickle_filepath_filepath)

    # Reading/writing between formats
    def csv_to_df(self, csv_filepath):
        df = pd.read_csv(csv_filepath)
        return df

    def json_to_df(self, json_filepath):
        df = pd.read_json(json_filepath)
        return df
    
    # Cleaning loaded data
    def clean_data(self, df):
        column_key = "PROGRAM STATUS"
        column_condition = "INACTIVE"
        try:
            df.drop(df[(df[column_key] == column_condition)].index, inplace=True)
        except KeyError:
            pass
        df.dropna(how="any", inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    # Produce statistics on data
    def score_averages_overall(self, df):
        mean = df["SCORE"].mean().round()
        median = df["SCORE"].median()
        mode = df["SCORE"].agg(lambda x:x.value_counts().index[0])
        averages = ["Overall", mean, median, mode]
        return averages
    
    def score_averages_city(self, df):
        mean = df.groupby(["FACILITY CITY"])["SCORE"].mean().round(2).reset_index()
        median = df.groupby(["FACILITY CITY"])["SCORE"].median().reset_index()
        mode = df.groupby(["FACILITY CITY"])["SCORE"].agg(lambda x:x.value_counts().index[0]).reset_index()
        averages = pd.concat([mean["FACILITY CITY"], mean["SCORE"], median["SCORE"], mode["SCORE"]], axis=1, keys=["FACILITY CITY","MEAN", "MEDIAN", "MODE"])
        return averages
    
    def violations(self, df):
        number = df.groupby("VIOLATION CODE").size().reset_index()
        violation_type = list(number["VIOLATION CODE"])
        violation_count = list(number[0])
        combined = [violation_type, violation_count]
        data = {
            "VIOLATION TYPE": violation_type,
            "VIOLATION COUNT": violation_count,
        }
        data = pd.DataFrame(data, columns=["VIOLATION TYPE", "VIOLATION COUNT"])
        return data
        
    # Configure plots
    def prepare_plot_violation_data(self, df):
        figure = plt.Figure(figsize=(20,5), dpi=100)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        
        violation_plot = self.violations(df)
        violation_plot.plot(kind="bar", legend=True, ax=ax)
        ax.set_xticklabels(violation_plot["VIOLATION TYPE"])
        ax.set_xlabel("Violation Type")
        ax.set_ylabel("Violation Count")
        ax.set_title('Number of establishments that have committed each type of violation', fontsize=20)
        return canvas
     
    def display_plot_violation_data(self, df):    
        try:
            self.delete_all_tables()
            self.forget_table_frames()
        except AttributeError:
            pass

        if self.current_file_loaded.endswith("Violations.csv"):
            self.delete_all_plots()

            self.canv = self.prepare_plot_violation_data(self.df)
            self.output_label.config(text="OK")
        else:
            try:
                self.canv.get_tk_widget().destroy()
                self.output_label.config(text="Please load 'Violations.csv'")
            except (AttributeError, KeyError):           
                self.output_label.config(text="Please load 'Violations.csv'")

    # Configure tables
    def table_score_averages_city(self, df):

        data = self.score_averages_city(df)
        
        self.label_table = tk.Label(tk.frame_label_city, text="INSPECTION SCORE STATISTICS")
        self.label_table.pack(side=tk.LEFT)
        self.label_table.config(font=(None, 18, "bold"))

        self.tree_city = ttk.Treeview(tk.frame_table_city, columns=(1,2,3,4), height=30, show="headings")
        self.tree_city.pack(side=tk.LEFT)

        self.tree_city.heading(1, text="FACILITY CITY")
        self.tree_city.heading(2, text="MEAN")
        self.tree_city.heading(3, text="MEDIAN")
        self.tree_city.heading(4, text="MODE")
        self.tree_city.column(1, width=100)
        self.tree_city.column(2, width=100)
        self.tree_city.column(3, width=100)
        self.tree_city.column(4, width=100)

        self.scroll = ttk.Scrollbar(tk.frame_table_city, orient="vertical", command=self.tree_city.yview)
        self.scroll.pack(side=tk.RIGHT, fill='y')

        self.tree_city.configure(yscrollcommand=self.scroll.set)

        for index, row in data.iterrows():
            self.tree_city.insert('', 'end', values=(data.loc[index, "FACILITY CITY"], 
            data.loc[index, "MEAN"].item(), data.loc[index, "MEDIAN"].item(), 
            data.loc[index, "MODE"].item()))     

    def table_score_averages_overall(self, df):

        data = self.score_averages_overall(df)

        self.tree_overall = ttk.Treeview(tk.frame_table_overall, columns=(1,2,3,4), height=1, show="headings")
        self.tree_overall.pack(side=tk.LEFT, pady=(30,0))

        self.tree_overall.heading(1, text="FACILITY CITY")
        self.tree_overall.heading(2, text="MEAN")
        self.tree_overall.heading(3, text="MEDIAN")
        self.tree_overall.heading(4, text="MODE")
        self.tree_overall.column(1, width=100)
        self.tree_overall.column(2, width=100)
        self.tree_overall.column(3, width=100)
        self.tree_overall.column(4, width=100)

        self.tree_overall.insert('', 'end', values=(data[0], data[1], data[2], data[3]))
    
    # Plot tables
    def plot_tables(self, df):     
        self.delete_all_plots()
        try:
            self.remember_table_frames()
        except AttributeError:
            pass
        try:
            self.delete_all_tables()
            self.table_score_averages_city(df)
            self.table_score_averages_overall(df)
            self.output_label.config(text="OK")
        except (KeyError):
            print("Please load the 'Inspections.csv' data")
            self.output_label.config(text="Please load 'Inspections.csv'")
   
   # Delete tables to prevent duplication
    def delete_all_tables(self):
        try:
            self.tree_city.destroy()
            self.scroll.destroy()
        except AttributeError:
            pass
        try:
            self.tree_overall.destroy()
        except AttributeError:
            pass
        try:
            self.label_table.destroy()
        except AttributeError:
            pass
        
    def delete_all_plots(self):
        try:
            self.canv.get_tk_widget().destroy()
        except (AttributeError, KeyError):
            pass
    
    def forget_table_frames(self):
        tk.frame_table_overall.pack_forget()
        tk.frame_table_city.pack_forget()
        tk.frame_label_city.pack_forget()
    
    def remember_table_frames(self):
        tk.frame_label_city.pack()
        tk.frame_table_city.pack()
        tk.frame_table_overall.pack()

root = tk.Tk()
viewer = GUI_Main(root)

root.mainloop()


