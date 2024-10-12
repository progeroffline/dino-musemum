import cv2
import numpy as np


class UiDetection:
    def __init__(
        self,
        ui_image_path: str,
        buy_button_image_template_path: str,
        archeology_image_template_path: str,
        close_button_image_template_path: str,
    ):
        self.ui_image_path = ui_image_path
        self.buy_button_image_template_path = buy_button_image_template_path
        self.archeology_image_template_path = archeology_image_template_path
        self.close_button_image_template_path = close_button_image_template_path

    def detect_image(self, image_path: str) -> list[tuple[int, ...]]:
        ui = cv2.imread(self.ui_image_path, cv2.IMREAD_UNCHANGED)
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(ui, image, cv2.TM_CCOEFF_NORMED)
        w = image.shape[1]
        h = image.shape[0]

        threshold = 0.60
        yloc, xloc = np.where(result >= threshold)
        rectangles = [[x, y, x + w, y + h] for x, y in zip(xloc, yloc)]
        rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.2)

        return [
            tuple([int(cords) for cords in rect_cords]) for rect_cords in rectangles
        ]

    def get_buy_buttons(self) -> list[tuple[int, ...]]:
        return self.detect_image(self.buy_button_image_template_path)

    def page_loaded(self) -> bool:
        return len(self.detect_image(self.archeology_image_template_path)) > 0

    def close_button(self) -> list[tuple[int, ...]]:
        return self.detect_image(self.close_button_image_template_path)


if __name__ == "__main__":
    obj = UiDetection(
        "canvas.png",
        "buy_button.png",
        "archeology.png",
        "close_button.png",
    )
    print(obj.page_loaded())
