def slot_to_time(slot_number):
    """
    Converts a slot number (0-287) into a human-readable time string (HH:MM).
    Each slot is 5 minutes.
    """
    total_minutes = slot_number * 5
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"

# Example usage:
print(slot_to_time(0))     # 00:00
print(slot_to_time(144))   # 12:00
print(slot_to_time(168))   # 14:00 (2 PM)
print(slot_to_time(287))   # 23:55