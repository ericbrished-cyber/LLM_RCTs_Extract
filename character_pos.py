def find_word_positions(text, word):
    """
    Find all occurrences of a word in text and return their character positions.
    
    Args:
        text (str): The text to search in
        word (str): The word to find
    
    Returns:
        list: List of tuples containing (start_pos, end_pos) for each occurrence
    """
    positions = []
    start = 0
    
    while True:
        # Find the next occurrence of the word
        pos = text.find(word, start)
        
        if pos == -1:  # No more occurrences found
            break
        
        # Calculate end position (exclusive, so if "Mean" starts at 0, it ends at 4)
        end_pos = pos + len(word)
        positions.append((pos, end_pos))
        
        # Move start position forward for next search
        start = pos + 1
    
    return positions


# Example usage
text = """Mean body weight gain: WGJ +50.6 g vs WA -0.7 g (n=30 per arm). Duration of illness (h): AJ 49.4 ± 32.6, WGJ 47.5 ± 38.9, WA 26.5 ± 27.4 (n=30/arm). Fecal losses (g/kg/h): AJ 3.94 ± 2.35, WGJ 3.59 ± 2.35, WA 2.19 ± 1.63 (n=30/arm)."""

# Test with "Mean"
word = "Mean"
positions = find_word_positions(text, word)

print(f"Word: '{word}'")
for start, end in positions:
    print(f"Position: {start} to {end}")
    print(f"Extracted text: '{text[start:end]}'")

print("\n" + "="*50 + "\n")

# Test with other words
test_words = ["30"]
for word in test_words:
    positions = find_word_positions(text, word)
    print(f"Word: '{word}'")
    if positions:
        for start, end in positions:
            print(f"  Position: {start} to {end}")
    else:
        print("  Not found")
    print()
