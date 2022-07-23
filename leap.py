import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import numpy as np
import sys
from matplotlib import pyplot as plt
import data_manipulator 

ctk.set_appearance_mode("Dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

plt.style.use("default")

# Optional starting directory
try:
	starting_dir = sys.argv[1]
except:
	starting_dir = "~"

# Add in cursor system
# When adding a product of an original graph it is possible to add multiples. Fix this.
# Point by point not working
# Add multiple graphs at the same tine in explorer
# Before first data need to move graph fix this to make it less annoying
# Try to update graph without redrawing the whole thing, messing up scales
# Derivatives or other manipulations don't show up
# Maybe try making it write to a csv file.
# vspace
# xi: = probe radius/ debye length
# formula for debye using epsilong * KT/ne^2
# save graph and data
# fix gui
# deal with multiple files
# error bounds
# set lower bound on isat not only upper
# Delete anything draastically out of average

class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		
		# Set up the basic window things	
		self.WIDTH = 1400
		self.HEIGHT = 5000
		self.title("Langmuir Experiment Analyzer Program")
		self.geometry("%ix%i" % (self.WIDTH, self.HEIGHT))
		self.img = tk.Image("photo", file="icon.png")
		self.tk.call('wm', 'iconphoto', self._w, self.img)
		self.data_analyzer = data_manipulator.data_manipulator()

		# This list holds the filenames of the graphs that are displayed, along with their data
		self.currently_displayed = {}
		self.selector_display = {}
		self.lin_log = 0
		self.next_index = 0
		self.select_all = tk.IntVar()
		self.legend_visibility = False
		self.fit_bound = [tk.IntVar(value=0), tk.IntVar(value=0)]
		self.cursor_positions = []	
		self.graph_indexes = {}

		# Frames 
		self.left_frame = ctk.CTkFrame()
		self.right_frame = ctk.CTkFrame()

		self.graph_frame = ctk.CTkFrame(master = self.left_frame) 	# Holds the graph
		self.adding_frame = ctk.CTkFrame(master = self.left_frame)	# Holds the controls for adding and removing files from the graph.


		self.control_frame = ctk.CTkFrame(master = self.right_frame)	# Holds the controls for manipulating the graphs.
		self.selector_frame = ctk.CTkFrame(master = self.right_frame)	
		self.select_all_frame = ctk.CTkFrame(master = self.selector_frame)
	
		self.options_frame = ctk.CTkFrame(master = self.control_frame)
		self.math_frame = ctk.CTkFrame(master = self.control_frame)


		self.cursor_frame = ctk.CTkFrame(master = self.options_frame)	

		# The figure that will contain the plot and adding the plot
		self.fig = Figure(figsize = (7,7), dpi = 100)
		self.plot1 = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.graph_frame)
		self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
		self.canvas.get_tk_widget().pack()

		self.plus_button = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(1),
			text = ">",
			width = 5)
		self.plus_button_l = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(10),
			text = ">>",
			width = 5)
		self.plus_button_el = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.incr(100),
			text = ">>>",
			width = 5)
		self.minus_button = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(1),
			text = "<",
			width = 5)
		self.minus_button_l = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(10),
			text = "<<",
			width = 5)
		self.minus_button_el = ctk.CTkButton(master = self.cursor_frame,
			command = lambda: self.minu(100),
			text = "<<<",
			width = 5)
		self.deletion_button = ctk.CTkButton(master = self.options_frame,
			command = self.delete_file,
	                text = "Delete")
		self.derivative_button = ctk.CTkButton(master = self.math_frame,
			command = self.derivative,
			text = "f'")
		self.scale_button = ctk.CTkButton(master = self.options_frame,
			command = self.toggle_graph_scale,
			text = "lin/log")
		self.legend_button = ctk.CTkButton(master = self.options_frame,
			command = self.toggle_legend,
			text = "legend")
		self.box_button = ctk.CTkButton(master = self.math_frame,
			command = self.box_average,
			text = "box average")
		self.select_all_button = ctk.CTkCheckBox(master = self.select_all_frame,
			command = self.all,
			variable = self.select_all,
			text = "")
		self.explorer_button = ctk.CTkButton(master = self.adding_frame,
			command = self.file_browser,
			text = "explorer")
		self.average_button = ctk.CTkButton(master = self.math_frame,
			command = self.average,
			text = "average")
		self.floating_potential_button = ctk.CTkButton(master = self.math_frame,
			command = self.floating,
			text = "floating potential")
		
		self.basic_isat_button = ctk.CTkButton(master = self.math_frame,
			command = self.basic_isat,
			text = "basic isat")
		self.savgol_button = ctk.CTkButton(master = self.math_frame,
			command = self.savgol,
			text = "savgol filter")
		self.eedf_button = ctk.CTkButton(master = self.math_frame,
			command = self.eedf,
			text = "EEDF")
		self.plasma_potential_button = ctk.CTkButton(master= self.math_frame,
			command = self.plasma_potential,
			text = "plasma potential")
		self.absolute_button = ctk.CTkButton(master = self.math_frame,
			command = self.absolute_v,
			text = "|f|")
		
		self.fit_counter = ctk.CTkLabel(master = self.cursor_frame, textvar = self.fit_bound[0])
		self.select_all_label = ctk.CTkLabel(master = self.select_all_frame, text = "Select All:")

		# Put the widgets on the screen
		self.redraw_widgets()

	def redraw_widgets(self):
		self.grid_columnconfigure(0,weight=1)
		self.grid_columnconfigure(1,weight=1)
		self.grid_rowconfigure(0,weight=1)

		self.left_frame.grid(row=0, column = 0, sticky="nsew")
		self.right_frame.grid(row=0, column = 1, sticky="nsew")
		
		self.left_frame.grid_rowconfigure(0, weight = 4)
		self.left_frame.grid_rowconfigure(1, weight = 1)
		self.left_frame.grid_columnconfigure(0, weight = 1)
		
		self.graph_frame.grid(row=0, column = 0, sticky = "nsew")
		self.adding_frame.grid(row=1, column = 0, sticky = "ew")
	
		self.explorer_button.pack()
		
		self.right_frame.grid_columnconfigure(0, weight=1)
		self.right_frame.grid_columnconfigure(1, weight=1)
		self.right_frame.grid_rowconfigure(0, weight=1)
		self.selector_frame.grid(row=0, column=0, sticky = "nsew")
		self.control_frame.grid(row=0, column=1, sticky = "nswe")

		self.control_frame.grid_columnconfigure(0, weight=1)
		self.control_frame.grid_rowconfigure(0, weight=1)
		self.control_frame.grid_rowconfigure(1, weight=2)

		self.options_frame.grid(row=0, column=0)
		self.math_frame.grid(row=1, column=0)	

		self.select_all_frame.pack()
		self.select_all_label.grid(row=0, column=0)
		self.select_all_button.grid(row=0, column=1)	

		self.deletion_button.pack()
		self.scale_button.pack()	
		self.legend_button.pack()

		self.derivative_button.pack()
		self.box_button.pack()
		self.average_button.pack()
		self.floating_potential_button.pack()		
		self.basic_isat_button.pack()
		self.savgol_button.pack()
		self.eedf_button.pack()
		self.plasma_potential_button.pack()
		self.absolute_button.pack()		

		self.cursor_frame.pack()
		self.minus_button_el.grid(row=0,column=0)
		self.minus_button_l.grid(row=0,column=1)
		self.minus_button.grid(row=0,column=2)
		self.plus_button.grid(row=0,column=4)
		self.plus_button_l.grid(row=0,column=5)
		self.plus_button_el.grid(row=0,column=6)
		self.fit_counter.grid(row=0,column=3)
	
	def absolute_v(self):
		fname = self.get_selected()[0]
		a = self.data_analyzer.absolute_val(self.currently_displayed[fname])[1]
		self.add_graph(fname + "_sav", self.currently_displayed[fname][0], a)

	def plasma_potential(self):
		fname = self.get_selected()[0]
		asdfasdf = self.data_analyzer.plasma_potential(self.currently_displayed[fname])
		print(asdfasdf)
		return asdfasdf	
				
	def eedf(self):
		fname = self.get_selected()[0]
		print(self.currently_displayed[fname])
		ee = self.data_analyzer.druyvesteyn(self.currently_displayed[fname],8)	
		self.add_graph(fname + "_ee", self.currently_displayed[fname][0], ee)

	def savgol(self):
		fname = self.get_selected()[0]
		smoothed = self.data_analyzer.savgol_smoothing(self.currently_displayed[fname])	
		self.add_graph(fname + "_sav", self.currently_displayed[fname][0], smoothed)

	# Get rid of the try except
	def basic_isat(self):
		fname = self.get_selected()[0]
		isat,electron_current = self.data_analyzer.ion_saturation_basic(self.currently_displayed[fname],self.fit_bound[0].get())	
		self.add_graph(fname + "_isat", self.currently_displayed[fname][0], isat)
		self.add_graph(fname + "_ecurr", self.currently_displayed[fname][0], electron_current)

	def file_browser(self):
		try:
			fnames = tk.filedialog.askopenfilenames(initialdir = starting_dir, title = "Select a File", filetypes = [("data files", "*.txt"), ("csv files", "*.csv"), ("all files","*.*")]) 
			for fname in fnames:
				if fname not in self.selector_display.keys():
					[x,y] = self.get_data(fname)
					self.add_graph(fname, x, y)
		except:
			pass

	def floating(self):
		fname = self.get_selected()[0]
		asdfasdf = self.data_analyzer.floating_potential(self.currently_displayed[fname])
		self.cursor_positions.append(asdfasdf[0])
		self.canvas.draw()
		return asdfasdf	

	def all(self):
		v = self.select_all.get()
		for key in self.selector_display:
			self.selector_display[key][1].set(v)

	def toggle_legend(self):
		if self.legend_visibility == False:
			self.legend_visibility = True
			self.plot1.legend(self.currently_displayed.keys())
		elif self.legend_visibility == True:
			self.legend_visibility = False
			self.plot1.get_legend().remove()
		self.canvas.draw()

	def toggle_graph_scale(self):
		if self.lin_log == 0:
			self.lin_log = 1
			self.plot1.set_yscale("log")			
		elif self.lin_log == 1:
			self.lin_log = 0
			self.plot1.set_yscale("linear")
		self.canvas.draw()

	def get_selected(self):
		selected = []
		for key in self.selector_display:
			if self.selector_display[key][0].winfo_children()[1].get() == 1:
				selected.append(key)
		return selected

	def box_average(self):
		for fname in self.get_selected():
			try:
				data = self.data_analyzer.box_average(self.currently_displayed[fname])
				prelim_fname = fname.split("/")[-1].split(".")[0] + "_box." + fname.split("/")[-1].split(".")[1]
				if prelim_fname not in list(self.graph_indexes.keys()):
					self.add_graph(prelim_fname, data[0], data[1])

			except KeyError:
				print("\a")

	# BETTER NAMES	
	def average(self):
		data_to_average = []
		for fname in self.get_selected():
			data_to_average.append(self.currently_displayed[fname])
		# TODO broken
		data = self.data_analyzer.average(data_to_average)
		self.add_graph("average", data[0], data[1])

	def incr(self,n):
		self.fit_bound[0].set(self.fit_bound[0].get()+n)		

	def minu(self,n):
		self.fit_bound[0].set(self.fit_bound[0].get()-n)

	def derivative(self):
		for fname in self.get_selected():
			try:		
				data = self.data_analyzer.derivative(self.currently_displayed[fname],1)
				prelim_fname = fname.split("/")[-1].split(".")[0] + "_der." + fname.split("/")[-1].split(".")[1]
				if prelim_fname not in list(self.graph_indexes.keys()):
					self.add_graph(prelim_fname, data[0], data[1])
			except KeyError:
				print("\a")


	def get_data(self, fname):
		f = open(fname, "r")
		vi_data = f.readlines()
		f.close()
		
		# Fix the data into a format usable by the code
		vi_data = vi_data[0]
		vi_data = vi_data.split(",")
		x = np.array([float(vi_data[i]) for i in range(len(vi_data)) if i % 2 == 0])
		y = np.array([float(vi_data[i]) for i in range(len(vi_data)) if i % 2 == 1])
		
		return x,y	

	def add_graph(self, f, x, y):
		self.currently_displayed.update({f: [x,y]})
	
		file_frame = ctk.CTkFrame(master = self.selector_frame)

		cb_value = tk.IntVar()
		label = ctk.CTkLabel(master = file_frame, text = f.split("/")[-1])
		cb = ctk.CTkCheckBox(master = file_frame, text = "",variable = cb_value)
		
		self.selector_display.update({f: [file_frame,cb_value]})
		self.update_next_index()
		self.graph_indexes.update({f: self.next_index})

		self.plot(x,y)
		file_frame.pack()
		label.grid(row=0, column=0)
		cb.grid(row=0, column=1)	

	def update_next_index(self):
		indexes = list(self.graph_indexes.values())
		indexes.sort()
		i=0
		while i in indexes:
			i += 1	

		self.next_index = i

	def delete_file(self):
		for s in self.get_selected():
			self.currently_displayed.pop(s)
			self.selector_display[s][0].pack_forget()
			self.selector_display[s][0].destroy()
			self.selector_display.pop(s)	
			self.plot1.get_lines()[self.graph_indexes[s]].remove()
			i = self.graph_indexes[s]
			del self.graph_indexes[s]
			for e in self.graph_indexes:
				if self.graph_indexes[e] > i:
					self.graph_indexes[e] -= 1

		self.canvas.draw()
	
	def plot(self,x,y):
		self.plot1.plot(x,y,'o')
		#for pos in self.cursor_positions:
		#	plot1.axvline(x=pos,ls="--")			

		self.canvas.draw()


if __name__ == "__main__":
	app = App()
	app.mainloop()
