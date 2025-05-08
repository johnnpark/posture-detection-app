import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import cv2
from posture_detector import PostureDetector

class FullScreenRedBorder(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.3)
        self.configure(bg="red")
        self.withdraw()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        try:
            self.attributes("-disabled", True)
        except:
            pass

    def show(self):
        self.deiconify()

    def hide(self):
        self.withdraw()


class PosturiteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Posturite")
        self.geometry("1000x700")
        self.resizable(False, False)

        self.detector = PostureDetector()

        # Load and resize background
        self.bg_image = Image.open("Hoohacks-7.jpg").resize((1000, 700))
        self.bg_blurred = self.bg_image.filter(ImageFilter.GaussianBlur(8))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_blurred_photo = ImageTk.PhotoImage(self.bg_blurred)

        # Canvas
        self.canvas = tk.Canvas(self, width=1000, height=700, highlightthickness=0)
        self.canvas_bg = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.canvas.pack()

        # Logo
        self.logo_image = Image.open("IMG_A60BCABA778B-1.jpeg").resize((120, 25))
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.canvas.create_image(40, 25, anchor="nw", image=self.logo_photo)

        # Start button
        self.start_button_shape = self.create_rounded_rect(400, 200, 600, 240, radius=20, fill="#c0392b", outline="")
        self.start_button_text = self.canvas.create_text(500, 220, text="Start Session", fill="white",
                                                         font=("Helvetica", 12, "bold"), anchor="center")
        self.canvas.tag_bind(self.start_button_shape, "<Button-1>", lambda e: self.start_session())
        self.canvas.tag_bind(self.start_button_text, "<Button-1>", lambda e: self.start_session())

        # End button
        self.end_button_shape = self.create_rounded_rect(400, 500, 600, 540, radius=20, fill="#c0392b", outline="")
        self.end_button_text = self.canvas.create_text(500, 520, text="End Session", fill="white",
                                                       font=("Helvetica", 12, "bold"), anchor="center")
        self.canvas.tag_bind(self.end_button_shape, "<Button-1>", lambda e: self.end_session())
        self.canvas.tag_bind(self.end_button_text, "<Button-1>", lambda e: self.end_session())
        self.canvas.itemconfig(self.end_button_shape, state="hidden")
        self.canvas.itemconfig(self.end_button_text, state="hidden")

        # Warning Label
        self.warning_label = tk.Label(self, text="", font=("Helvetica", 24, "bold"), fg="white", bg="black")
        self.warning_label.place(relx=0.5, y=90, anchor="center")
        self.warning_label.place_forget()

        # Countdown label
        self.countdown_label = tk.Label(self, text="", font=("Helvetica", 32, "bold"), fg="white", bg="black")
        self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")
        self.countdown_label.place_forget()

        # Camera feed
        self.video_image_id = None
        self.cap = None
        self.running = False

        # Red border overlay
        self.screen_overlay = FullScreenRedBorder()

    def create_rounded_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def start_session(self):
        self.canvas.itemconfig(self.start_button_shape, state="hidden")
        self.canvas.itemconfig(self.start_button_text, state="hidden")
        self.canvas.itemconfig(self.canvas_bg, image=self.bg_blurred_photo)
        self.canvas.itemconfig(self.end_button_shape, state="normal")
        self.canvas.itemconfig(self.end_button_text, state="normal")

        # Init camera and show countdown
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.countdown_time = 3
        self.countdown_label.config(text="Calibrating in 3...", fg="white")
        self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")
        self.after(1000, self.run_countdown)

    def run_countdown(self):
        self.countdown_time -= 1
        if self.countdown_time > 0:
            self.countdown_label.config(text=f"Calibrating in {self.countdown_time}...")
            self.after(1000, self.run_countdown)
        else:
            self.countdown_label.place_forget()
            self.detector.calibrated_z = None
            self.detector.calibrating = True
            self.detector.calibration_data = []

            self.warning_label.config(text="Sit upright... Calibrating posture", fg="white")
            self.warning_label.place(relx=0.5, y=90, anchor="center")
            self.show_frame()

    def show_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = self.detector.findPose(frame)
                lmList = self.detector.findPosition(frame)

                if self.detector.detectForwardHead(lmList):
                    self.warning_label.config(text="⚠️ Forward Head Detected!", fg="red")
                    self.warning_label.place(relx=0.5, y=90, anchor="center")
                    self.toggle_posture_alert(True)
                else:
                    self.warning_label.config(text="Good Posture", fg="green")
                    self.warning_label.place(relx=0.5, y=90, anchor="center")
                    self.toggle_posture_alert(False)

                self.warning_label.update_idletasks()

                frame = cv2.resize(frame, (700, 400))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                rounded = self.add_rounded_corners(img, radius=25)
                imgtk = ImageTk.PhotoImage(image=rounded)

                if self.video_image_id:
                    self.canvas.itemconfig(self.video_image_id, image=imgtk)
                else:
                    self.video_image_id = self.canvas.create_image(500, 250, image=imgtk)

                self.video_frame_imgtk = imgtk

            self.after(10, self.show_frame)

    def end_session(self):
        self.running = False
        if self.cap:
            self.cap.release()

        self.canvas.delete(self.video_image_id)
        self.video_image_id = None
        self.canvas.itemconfig(self.canvas_bg, image=self.bg_photo)
        self.canvas.itemconfig(self.end_button_shape, state="hidden")
        self.canvas.itemconfig(self.end_button_text, state="hidden")
        self.canvas.itemconfig(self.start_button_shape, state="normal")
        self.canvas.itemconfig(self.start_button_text, state="normal")
        self.warning_label.config(text="")
        self.warning_label.place_forget()
        self.toggle_posture_alert(False)

    def add_rounded_corners(self, img, radius):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)

        img = img.convert("RGBA")
        img.putalpha(mask)
        bg = Image.new("RGBA", img.size, (30, 30, 30, 255))
        rounded = Image.composite(img, bg, mask)
        return rounded.convert("RGB")

    def toggle_posture_alert(self, active):
        if active:
            self.screen_overlay.show()
        else:
            self.screen_overlay.hide()


if __name__ == "__main__":
    app = PosturiteApp()
    app.mainloop()
