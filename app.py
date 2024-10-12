from dataclasses import dataclass

from PIL import Image
from rich import print
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from seleniumbase import Driver

from ui_detection import UiDetection


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
        self.actions = ActionBuilder(self.driver)
        self.driver.uc_open_with_reconnect(url, 2)

        self.canvas_element = self.driver.find_element("canvas")
        if self.canvas_element is None:
            print("Canvas not found!")
            self.driver.quit()

        self.canvas = self.get_canvas_object()
        self.ui_detector = UiDetection(
            self.canvas_filename,
            "./assets/buy_button.png",
            "./assets/archeology.png",
            "./assets/close_button.png",
        )

    def get_canvas_object(self) -> Canvas:
        pos_x, pos_y = self.get_canvas_position()
        width, height = self.get_canvas_size()
        return Canvas(pos_x, pos_y, width, height)

    def get_canvas_position(self) -> tuple[int, int]:
        return self.canvas_element.location["x"], self.canvas_element.location["y"]

    def get_canvas_size(self) -> tuple[int, int]:
        return self.canvas_element.size["width"], self.canvas_element.size["height"]

    def make_screenshot(self) -> None:
        self.driver.save_screenshot(self.canvas_filename)

    def make_screenshot_by_axis(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.driver.save_screenshot(self.canvas_filename)

        im = Image.open(self.canvas_filename)
        im = im.crop((x1, y1, x2, y2))
        im.save(self.canvas_filename)

    def get_center_position(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> tuple[int, int]:
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        return x, y

    def click_by_cords(self, x1: int, y1: int, x2: int, y2: int) -> None:
        x, y = self.get_center_position(x1, y1, x2, y2)

        self.actions.pointer_action.move_to_location(x, y).click()
        self.actions.perform()
        self.driver.sleep(2)
        self.make_screenshot()

    def wait_until_loading_not_finished(self) -> None:
        self.make_screenshot()
        while not self.ui_detector.page_loaded():
            self.driver.sleep(1)
            self.make_screenshot()

    def close_notification(self) -> None:
        close_buttons = self.ui_detector.close_button()
        if len(close_buttons) > 0:
            for cords in close_buttons:
                self.click_by_cords(*cords)

    def buy_available_upgrades(self) -> None:
        buy_buttons_cords = self.ui_detector.get_buy_buttons()
        for cords in buy_buttons_cords:
            self.click_by_cords(*cords)

    def run(self):
        self.wait_until_loading_not_finished()
        self.close_notification()
        print("Game loading finished!!!")

        self.buy_available_upgrades()
        print("All upgrades buyed!")

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
