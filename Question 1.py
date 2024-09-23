import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2  # OpenCV for video handling
from functools import wraps  # for decorators

# Base Class for handling the video files (Encapsulation example)
class VideoHandler:
    def __init__(self):
        self._video_list = []  # Private list to store videos (Encapsulation)
        self._current_video = None  # Private variable to store current video path

    def add_video(self, video):
        self._video_list.append(video)  # Encapsulation: adding video to private list

    def get_videos(self):
        return self._video_list  # Encapsulation: retrieve video list

    def set_current_video(self, video):
        self._current_video = video  # Encapsulation: setting current video path

    def get_current_video(self):
        return self._current_video  # Encapsulation: retrieve current video path

# Multiple Decorators Example: Logging and confirmation decorators
def confirm_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        answer = messagebox.askyesno("Confirmation", "Are you sure?")
        if answer:
            return func(*args, **kwargs)
    return wrapper

def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Action: {func.__name__} has been executed.")
        return func(*args, **kwargs)
    return wrapper

# Multiple Inheritance Example: Inheriting from Tkinter Frame and VideoHandler
class YouTubeApp(tk.Frame, VideoHandler):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)  # Calling Frame initializer
        VideoHandler.__init__(self)  # Calling VideoHandler initializer
        self.parent = parent
        self.parent.title("YouTube Like Application")
        self.pack()

        self._create_widgets()  # Encapsulation: Create widgets method
        self.video_label = tk.Label(self)  # Label to display video frames
        self.video_label.pack(pady=10)

    # Create the widgets for the interface
    def _create_widgets(self):
        # Title label
        self.title_label = tk.Label(self, text="YouTube Like Interface", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Upload button
        self.upload_button = tk.Button(self, text="Upload Video", command=self._upload_video)
        self.upload_button.pack(pady=5)

        # Search Entry
        self.search_entry = tk.Entry(self, width=50)
        self.search_entry.pack(pady=5)

        # Search button
        self.search_button = tk.Button(self, text="Search Video", command=self._search_video)
        self.search_button.pack(pady=5)

        # Listbox to display uploaded videos
        self.video_listbox = tk.Listbox(self, width=50, height=10)
        self.video_listbox.pack(pady=10)

        # Play Video button
        self.play_button = tk.Button(self, text="Play Video", command=self._play_video)
        self.play_button.pack(pady=5)

    # Method overriding: Custom behavior for uploading videos
    @confirm_action  # Using decorator for confirmation
    @log_action  # Using decorator for logging
    def _upload_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if file_path:
            video_name = file_path.split("/")[-1]  # Extract video name from the file path
            self.add_video((video_name, file_path))  # Encapsulation: Add video tuple (name, path)
            self.video_listbox.insert(tk.END, video_name)
            messagebox.showinfo("Success", f"Video '{video_name}' uploaded successfully!")

    # Polymorphism Example: Custom search logic
    def _search_video(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Search", "Please enter a search term.")
            return

        # Clear the current video list
        self.video_listbox.delete(0, tk.END)

        # Retrieve video list using encapsulation and search for the term
        found_videos = [video for video in self.get_videos() if search_term.lower() in video[0].lower()]

        if found_videos:
            for video in found_videos:
                self.video_listbox.insert(tk.END, video[0])
        else:
            messagebox.showinfo("Search", "No videos found.")

    # Method overriding: Custom behavior for playing videos
    @log_action  # Logging decorator
    def _play_video(self):
        selected_index = self.video_listbox.curselection()  # Get selected video index
        if selected_index:
            selected_video = self.get_videos()[selected_index[0]]  # Get video tuple (name, path)
            video_path = selected_video[1]  # Extract the file path

            self.set_current_video(video_path)  # Set the current video path
            self._start_video_playback()  # Start playing the video
        else:
            messagebox.showwarning("Play Video", "Please select a video to play.")

    # Function to start video playback
    def _start_video_playback(self):
        video_path = self.get_current_video()
        if video_path:
            cap = cv2.VideoCapture(video_path)  # Open the video file with OpenCV

            def play_frame():
                ret, frame = cap.read()  # Read the next frame
                if ret:
                    # Convert frame to RGB for Tkinter
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = ImageTk.PhotoImage(Image.fromarray(frame))
                    self.video_label.config(image=img)
                    self.video_label.image = img  # Keep a reference to avoid garbage collection
                    self.after(20, play_frame)  # Call the next frame after 20 ms (50 FPS approx)
                else:
                    cap.release()  # Release the video capture when done

            play_frame()  # Start playing the first frame

# Multiple Inheritance and Method Overriding Example
class YouTubeProApp(YouTubeApp):
    def __init__(self, parent):
        super().__init__(parent)  # Call the base class initializer

    # Overriding the upload video method to allow batch upload (polymorphism)
    @log_action  # Reusing the logging decorator
    def _upload_video(self):
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if files:
            for file in files:
                video_name = file.split("/")[-1]
                self.add_video((video_name, file))  # Store video names and paths in tuples
                self.video_listbox.insert(tk.END, video_name)
            messagebox.showinfo("Success", f"{len(files)} videos uploaded successfully!")

# Main Application Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeProApp(root)  # Using the YouTubeProApp (demonstrating inheritance)
    root.mainloop()
