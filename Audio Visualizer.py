import numpy, sys, os, tkinter, math, wave
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.ticker import Formatter
from io import BytesIO
from subprocess import Popen, PIPE, CREATE_NO_WINDOW

root = tkinter.Tk()
root.wm_title("Audio Visualizer")

if hasattr(sys, '_MEIPASS') or os.path.isfile(os.path.join(os.path.dirname(__file__), 'icon.ico')):
	root.iconbitmap(os.path.join(sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 'icon.ico'))

class NavigationToolbar(NavigationToolbar2Tk):
	def __init__(self,canvas_,parent_):
		self.toolitems = (
			('Home', 'Reset original view', 'home', 'home'),
			('Back', 'Back to previous view', 'back', 'back'),
			('Forward', 'Forward to next view', 'forward', 'forward'),
			(None, None, None, None),
			('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
			('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
			(None, None, None, None),
			('Save', 'Save the figure', 'filesave', 'save_figure'),
			(None, None, None, None),
			('New', 'Visualize a new file', 'subplots', 'newfile'),
		)
		NavigationToolbar2Tk.__init__(self,canvas_,parent_)
	def newfile(self):
		drawGraph()

class FormatTime(Formatter):
	def __init__(self):
		pass
	def __call__(self, x, post=None):
		vmin, vmax = self.axis.get_view_interval()
		if vmax - vmin > 3600:
			return '{:d}:{:02d}:{:02d}'.format(int(x / 3600.0), int(x / 60.0 % 60), int(x % 60))
		if vmax - vmin > 60:
			return'{:d}:{:02d}'.format(int(x / 60.0), int(x % 60))
		return'{:.2g}'.format(x)

def drawGraph():
	try:
		filename = tkinter.filedialog.askopenfilename()
		format_time = FormatTime()
		ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg.exe') if hasattr(sys, '_MEIPASS') else 'ffmpeg'
		p = Popen(
			[ffmpeg, '-loglevel', 'panic', '-y', '-i', filename, '-vn', '-maxrate', '440000', '-c:a', 'pcm_s16le', '-ac', '1', '-f', 'wav', '-'],
			stdin=PIPE, stdout=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW
		)
		sound = wave.open(BytesIO(p.communicate()[0]))
		signal = numpy.frombuffer(sound.readframes(-1), numpy.int16)
		framerate = sound.getframerate()
		time = [i/framerate for i in range(len(signal))]
		fig = Figure()
		sub = fig.add_axes((0.05,0.2,0.9,0.6))
		root.wm_title('Audio Visualization of ' + os.path.basename(filename))
		sub.set_title('Audio Visualization of ' + os.path.basename(filename))
		sub.set_xlabel('Time')
		sub.set_xlim(0.0, time[-1])
		sub.get_xaxis().set_major_formatter(format_time)
		def format_coord (x, y):
			return format_time(x)
		sub.format_coord = format_coord
		sub.get_yaxis().set_visible(False)
		denom = math.ceil(len(signal)/50000)
		sub.plot(time[::denom], signal[::denom], linewidth=0.25)
		for widget in root.winfo_children():
			widget.destroy()
		canvas = FigureCanvasTkAgg(fig, master=root)
		canvas.draw()
		toolbar = NavigationToolbar(canvas, root)
		toolbar.update()
		def on_key_press(event):
			key_press_handler(event, canvas, toolbar)
		canvas.mpl_connect("key_press_event", on_key_press)
		canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
		tkinter.mainloop()
	except:
		if filename:
			tkinter.messagebox.showerror('Error', 'An error has occured! Make sure the file is valid.')
			drawGraph()

drawGraph()
