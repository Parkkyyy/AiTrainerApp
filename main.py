from kivymd.app import MDApp
import numpy as np
import cv2
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

import PoseModule as pm


screen_helper = """
ScreenManager:
    id: screen_manager

    MainScreen:
        name: "main_screen"

    Item1Screen:
        name: "item1_screen"

<MainScreen>:
    name:"main_screen"
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            left_action_items: [["menu", lambda x: x]]
            title: 'AiTrainer'
            right_action_items: [["magnify", lambda x: app.callback(),"Search"]]


        MDScrollView:
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height

                OneLineListItem:
                    text: "Bisceps Curl"
                    on_press: app.on_item_click("1")

                OneLineListItem:
                    text: "Pushups"
                    on_press: app.on_item_click("2")

                OneLineListItem:
                    text: "Squats"
                    on_press: app.on_item_click("3")


<Item1Screen>:
    name: "item1_screen"

"""


class MainScreen(MDScreen):
    pass


class Item1Screen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pose_detector = pm.poseDetector()
        self.detection_started = False
        self.image_index=0
        self.count=0
        self.dir=0
        self.cap = cv2.VideoCapture(0)


        # Create MDToolbar
        layout = MDBoxLayout(orientation="vertical")
        self.label = MDLabel(size_hint_y=None, size_hint=(1, 0.5), text="", halign="center",
                             valign="center")

        # Create MDToolbar
        self.toolbar = MDTopAppBar(title="My Screen",
                                   left_action_items=[["home", lambda x: self.home()]]
                                   )

        # Create MDLabel
        self.label1 = MDLabel(size_hint_y=None, size_hint=(1, 0.5), text="", halign="center",
                             valign="center")

        self.label2 = MDLabel(size_hint_y=None, size_hint=(1, 0.5), text="", halign="center",
                             valign="center")
        self.button_layout = MDBoxLayout(orientation="horizontal",
                                         spacing=30,
                                         padding=35,
                                         )
        self.button1 = MDRectangleFlatButton(text="Start Detection",
                                             size_hint=(0.3,1),
                                            md_bg_color=(0, 0, .5, 1),
                                            text_color=(1, 1, 1, 1),
                                            padding="20dp"
                                            )
        self.button2 = MDRectangleFlatButton(text="Switch Camera",
                                             size_hint=(0.3, 1),
                                             md_bg_color=(0, 0, .5, 1),
                                             text_color=(1, 1, 1, 1),
                                             padding="20dp"
                                             )


        self.button_layout.add_widget(self.button1)
        self.button_layout.add_widget(self.button2)
        self.button1.bind(on_release=self.button1_callback)
        self.button2.bind(on_release=self.button2_callback)

        #
        # Create Image
        self.image = Image(source="",
                           height="500dp",
                           size_hint=(1, None),
                           pos_hint={"center_x": 0.5},
                           )  # Replace "your_image_path.png" with your image path

        # self.image = Camera(resolution=(640, 880),
        #                     height="500dp",
        #                     size_hint=(1, None),
        #                     pos_hint={"center_x": 0.5},
        #                     )
        # self.image = Image(
        #     source="",
        #     size_hint=(1, 1),
        #     allow_stretch=True,
        #     keep_ratio=False
        # )

        # Add widgets to the layout
        layout.add_widget(self.toolbar)
        layout.add_widget(self.label)
        layout.add_widget(self.image)
        Clock.schedule_interval(self.update_image, 1.0 / 30.0)
        layout.add_widget(self.label1)

        layout.add_widget(self.button_layout)
        layout.add_widget(self.label2)

        # Add the layout to the screen
        self.add_widget(layout)

    def change_param(self,angle1,angle2,angle3,range1,range2):
        self.angle1=angle1
        self.angle2=angle2
        self.angle3=angle3
        self.range1=range1
        self.range2=range2

    def home(self):
        item = MainScreen()
        self.clear_widgets()
        self.add_widget(item)

    def change_label_text(self, new_text):
        self.label.text = new_text

    def change_label1_text(self, new_text):
        self.label1.text = new_text


    def start_detection(self):
        self.detection_started = True
        self.button1.text = "Stop Detection"  # Change button text to indicate detection is running

    def stop_detection(self):
        self.detection_started = False
        self.button1.text = "Start Detection"

    def button1_callback(self, instance):
        if not self.detection_started:
            self.start_detection()
            self.count=0

        else:
            self.stop_detection()
            if self.count>0:
                self.change_label1_text("Awesome you had "+str(self.count)+" reps !")
        # Add functionality for Button 1 here

    def button2_callback(self, instance):
        # Toggle between front and back cameras
        print("button2")
        if self.image_index == 1:
            self.cap=cv2.VideoCapture(0)
            self.image_index=0
        else:
            self.cap=cv2.VideoCapture(1)
            self.image_index=1


    def update_image(self, dt):
        # Capture frame from camera
        ret, frame = self.cap.read()
        if ret:
            if self.detection_started:
            # Process frame to detect poses
                frame = self.pose_detector.findPose(frame, draw=False)
                lmList = self.pose_detector.findPosition(frame, draw=False)
                if len(lmList) != 0:

                    angle =self.pose_detector.findAngle(frame, self.angle1,self.angle2,self.angle3)
                    perc = np.interp(angle, (self.range1,self.range2), (100, 0))
                    bar = np.interp(angle, (self.range1,self.range2), (100, 450))
                    color = (255, 0, 255)
                    if perc == 100:
                        color = (0, 255, 0)
                        if self.dir == 0:
                            self.count += 0.5
                            self.dir = 1
                    if perc == 0:
                        color = (0, 255, 0)
                        if self.dir == 1:
                            self.count += 0.5
                            self.dir = 0
                    cv2.rectangle(frame, (500, 100), (525, 450), color, 3)
                    cv2.rectangle(frame, (500, int(bar)), (525, 450), color, cv2.FILLED)

                    # cv2.rectangle(frame, (20, 20), (130, 130), (0, 255, 0), cv2.FILLED)
                    # cv2.putText(frame, f'{int(self.count)}', (45, 100), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                # Convert processed frame to texture for displaying in Kivy
                self.image.texture = self.texture_from_frame(frame)
                self.change_label1_text("Your rep count is " + str(int(self.count)))


            else:
                # Display raw camera feed if detection is not started
                self.image.texture = self.texture_from_frame(frame)

    def texture_from_frame(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

class DemoApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"

        return Builder.load_string(screen_helper)

    def on_item_click(self, item_text):
        if item_text == "1":
            item1_screen = Item1Screen()
            item1_screen.change_label_text("Bisceps Curl")
            item1_screen.change_param(12,14,16,60,160)
            self.root.clear_widgets()
            self.root.add_widget(item1_screen)
        elif item_text == "2":
            item1_screen = Item1Screen()
            item1_screen.change_label_text("Push-ups")
            self.root.clear_widgets()
            self.root.add_widget(item1_screen)
        elif item_text == "3":
            item1_screen = Item1Screen()
            item1_screen.change_label_text("Squats")
            self.root.clear_widgets()
            self.root.add_widget(item1_screen)

    def home(self):
        item = MainScreen()
        self.root.clear_widgets()
        self.root.add_widget(item)


DemoApp().run()
