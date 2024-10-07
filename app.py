from dataclasses import dataclass

import pytesseract
from PIL import Image
from seleniumbase import Driver


@dataclass
class Canvas:
    pos_x: int
    pos_y: int
    width: int
    height: int

    def get_bottom_menu_axis(self) -> tuple[int, int, int, int]:
        return (
            self.pos_x,
            self.height - 50,
            self.pos_y - 35,
            self.height,
        )


class DinomuseumAutomation:
    def __init__(self, url: str):
        self.canvas_filename = "canvas.png"
        self.driver = Driver(uc=True)
        self.driver.uc_open_with_reconnect(url, 2)
        self.canvas_element = self.driver.find_element("canvas")
        if self.canvas_element is None:
            print("Canvas not found!")
            self.driver.quit()

        self.canvas = self.get_canvas_object()
        self.driver.save_screenshot("fullscreen.png")

    def get_canvas_object(self) -> Canvas:
        pos_x, pos_y = self.get_canvas_position()
        width, height = self.get_canvas_size()
        return Canvas(pos_x, pos_y, width, height)

    def get_canvas_position(self) -> tuple[int, int]:
        return self.canvas_element.location["x"], self.canvas_element.location["y"]

    def get_canvas_size(self) -> tuple[int, int]:
        return self.canvas_element.size["width"], self.canvas_element.size["height"]

    def make_screenshot_by_axis(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.driver.save_screenshot(self.canvas_filename)

        im = Image.open(self.canvas_filename)
        im = im.crop((x1, y1, x2, y2))
        im.save(self.canvas_filename)

    def get_text_from_last_screenshot(self) -> str:
        image = Image.open(self.canvas_filename)
        text = pytesseract.image_to_string(image)
        return text.strip().replace("  ", " ")

    def get_bottom_menu_text(self) -> str:
        self.make_screenshot_by_axis(*self.canvas.get_bottom_menu_axis())
        return self.get_text_from_last_screenshot()

    def loading_completed(self) -> bool:
        self.make_screenshot_by_axis(*self.canvas.get_bottom_menu_axis())
        text = self.get_bottom_menu_text()
        print(text)
        return text == "Managers Upgrades @EQI Milestones Investors"

    def wait_until_loading_not_finished(self) -> None:
        while not self.loading_completed():
            print("Loading still processing...")
            self.driver.sleep(1)

    def run(self):
        self.wait_until_loading_not_finished()
        print("Loading finished!!!")

        self.driver.sleep(100000)


if __name__ == "__main__":
    from environs import Env

    env = Env()
    env.read_env()
    try:
        dino_bot = DinomuseumAutomation(env.str("DINO_FULL_URL"))
        dino_bot.run()
    except KeyboardInterrupt:
        pass
