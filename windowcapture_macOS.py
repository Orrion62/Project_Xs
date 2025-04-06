
import numpy as np
import cv2
from PIL import Image
import Quartz
import AppKit

class WindowCapture:
    def __init__(self, window_title_keyword, crop=False):
        self.window_title_keyword = window_title_keyword
        self.crop = crop
        self.window = self._find_window()

    def _find_window(self):
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

        for window in window_list:
            owner_name = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')
            if self.window_title_keyword in name or self.window_title_keyword in owner_name:
                bounds = window['kCGWindowBounds']
                return {
                    'x': int(bounds['X']),
                    'y': int(bounds['Y']),
                    'width': 960,
                    'height': 540,
                    'window_id': window['kCGWindowNumber']
                }
        raise Exception(f"No window found with title keyword: {self.window_title_keyword}")

    def read(self):
        if self.window is None:
            raise Exception("No window to capture.")

        img = Quartz.CGWindowListCreateImage(
            Quartz.CGRectMake(
                self.window['x'],
                self.window['y'],
                self.window['width'],
                self.window['height']
            ),
            Quartz.kCGWindowListOptionIncludingWindow,
            self.window['window_id'],
            Quartz.kCGWindowImageDefault)

        if img is None:
            return None, None

        width = Quartz.CGImageGetWidth(img)
        height = Quartz.CGImageGetHeight(img)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(img)
        data_provider = Quartz.CGImageGetDataProvider(img)
        data = Quartz.CGDataProviderCopyData(data_provider)
        img_buffer = np.frombuffer(data, dtype=np.uint8)

        img_buffer.shape = (height, bytes_per_row // 4, 4)
        frame = img_buffer[:, :, :3]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        frame = cv2.resize(frame, (960, 540))
        return True, frame
