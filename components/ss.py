from PIL import ImageGrab
import io

def get_screenshot_bytes():
    screenshot = ImageGrab.grab()

    ss = io.BytesIO()
    screenshot.save(ss, format='PNG')
    
    ss.seek(0)
    return ss