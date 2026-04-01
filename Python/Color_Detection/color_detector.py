import sys
import cv2
import numpy as np

SAMPLE_RADIUS  = 6        # radius of pixel area to average (reduces noise)
BOX_W, BOX_H   = 280, 110 # size of the info overlay box
BOX_MARGIN     = 20        # gap between box and frame edge
CROSSHAIR_SIZE = 18        # length of crosshair arms in pixels
CROSSHAIR_THICK = 2
FONT           = cv2.FONT_HERSHEY_SIMPLEX


def get_center_color(frame: np.ndarray, radius: int) -> tuple[int, int, int]:
    """ Samples the RGB"""
    h, w  = frame.shape[:2]
    cx, cy = w // 2, h // 2
    patch  = frame[cy - radius: cy + radius, cx - radius: cx + radius]
    avg_bgr = patch.mean(axis=(0, 1))          # mean over all pixels in patch
    b, g, r = (int(round(v)) for v in avg_bgr)
    return r, g, b


def perceived_brightness(r: int, g: int, b: int) -> float:
    return 0.299 * r + 0.587 * g + 0.114 * b


def draw_crosshair(frame: np.ndarray, color: tuple[int, int, int]) -> None:
    """Crosshair"""
    h, w  = frame.shape[:2]
    cx, cy = w // 2, h // 2
    arm    = CROSSHAIR_SIZE
    t      = CROSSHAIR_THICK

    cv2.line(frame, (cx - arm, cy), (cx + arm, cy), color, t, cv2.LINE_AA)
    cv2.line(frame, (cx, cy - arm), (cx, cy + arm), color, t, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), SAMPLE_RADIUS, color, 1, cv2.LINE_AA)


def draw_info_box(frame: np.ndarray, r: int, g: int, b: int) -> None:
    """Color Box:"""
    fh, fw = frame.shape[:2]

    """Color Box position"""
    bx = fw - BOX_W - BOX_MARGIN
    by = fh - BOX_H - BOX_MARGIN
    bx2, by2 = bx + BOX_W, by + BOX_H

    """Background Pannel"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (bx, by), (bx2, by2), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    """Color Swatch"""
    swatch_x2 = bx + 85
    cv2.rectangle(frame, (bx + 6, by + 6), (swatch_x2, by2 - 6), (b, g, r), -1)
    cv2.rectangle(frame, (bx + 6, by + 6), (swatch_x2, by2 - 6), (200, 200, 200), 1)

    lum        = perceived_brightness(r, g, b)
    text_color = (0, 0, 0) if lum > 128 else (255, 255, 255)

    """RGB Label"""
    
    label = "RGB"
    (lw, lh), _ = cv2.getTextSize(label, FONT, 0.42, 1)
    lx = bx + 6 + (swatch_x2 - bx - 6) // 2 - lw // 2
    ly = by + 6 + (by2 - by - 6) // 2 + lh // 2
    cv2.putText(frame, label, (lx, ly), FONT, 0.42, text_color, 1, cv2.LINE_AA)

    """Rgb Numbers"""
    
    tx = swatch_x2 + 12
    hex_str = f"#{r:02X}{g:02X}{b:02X}"

    cv2.putText(frame, f"R:  {r:>3}", (tx, by + 32), FONT, 0.55, (80, 80, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, f"G:  {g:>3}", (tx, by + 58), FONT, 0.55, (80, 200, 80), 1, cv2.LINE_AA)
    cv2.putText(frame, f"B:  {b:>3}", (tx, by + 84), FONT, 0.55, (255, 120, 80), 1, cv2.LINE_AA)
    cv2.putText(frame, hex_str,       (tx, by + 104), FONT, 0.48, (210, 210, 210), 1, cv2.LINE_AA)

    """Box Border"""
    cv2.rectangle(frame, (bx, by), (bx2, by2), (180, 180, 180), 1)


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit("[ERROR] Cannot open camera.")

    """Resolution"""
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Camera Started,Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame read failed, retrying...")
            continue

        r, g, b = get_center_color(frame, SAMPLE_RADIUS)

        """Crosshair Color"""
        lum = perceived_brightness(r, g, b)
        ch_color = (255, 255, 255) if lum < 128 else (0, 0, 0)

        draw_crosshair(frame, ch_color)
        draw_info_box(frame, r, g, b)

        cv2.imshow("Color Detector", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):   # Q or ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera Inchisa.")


if __name__ == "__main__":
    main()
