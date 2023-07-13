def divide_with_reminder(a, b: int):
    multiplier = int(a / b)
    reminder = a - (multiplier * b)
    return multiplier, reminder

def update_coord_get_scroll_dir(self, cur, prev):
    scroll_every_n_pixels = self.controller.scroll_every_n_pixels
    diff = cur - prev
    if abs(diff) >= scroll_every_n_pixels:  # greater or EQUAL
        multiplier, remainder = divide_with_reminder(diff, scroll_every_n_pixels)
        prev = cur - remainder
        return prev, multiplier * self.controller.scroll_by
    else:
        return prev, 0
