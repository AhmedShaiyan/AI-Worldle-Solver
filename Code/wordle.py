from turtle_oxford import *

WORDLE_DARK_GREY = 0x3A3A3C
WORDLE_GREEN = 0x6ca965
WORDLE_YELLOW = 0xc8b653
WORDLE_BLACK = 0x121213
WORDLE_WHITE = 0xf8f8f8 

# English letter frequency roughly in order of most to least common
FREQUENCY_ORDER = 'etaoinshrdlcumwfgypbvkjxqz' 

#Load the list of 5-letter words from a text file
def load_words():
    with open("Code/sgb-words.txt", "r") as file:
        return [word.strip().upper() for word in file if len(word.strip()) == 5]

# Prompts the user to enter the target word for the program to guess.
def choose_word(words):

    print("Please enter a 5-letter English word as the target:")
    while True:
        user_input = input().strip().upper()
        if len(user_input) == 5 and user_input in words:
            return user_input
        else:
            print("Invalid word. Please ensure the word is 5 letters long and is a valid English word.")
            print("Please enter a 5-letter English word as the target:")

# Compare the guessed word with the target word
def get_color_mapping(guessed_word, target_word):
    color_mapping = [0x3A3A3C] * len(guessed_word)  
    target_word_list = list(target_word)

    # First pass for correct position (green)
    for i, letter in enumerate(guessed_word):
        if letter == target_word[i]:
            color_mapping[i] = 0x6ca965  # Green
            target_word_list[i] = None

    # Second pass for wrong position (yellow)
    for i, letter in enumerate(guessed_word):
        if color_mapping[i] == 0x6ca965:
            continue
        if letter in target_word_list:
            color_mapping[i] = 0xc8b653  # Yellow
            target_word_list[target_word_list.index(letter)] = None

    return color_mapping

def score_initial_guess(words):
    
    frequency_scores = {letter: len(FREQUENCY_ORDER) - idx for idx, letter in enumerate(FREQUENCY_ORDER)}

    scores = {}
    for word in words:
        seen_letters = set()
        score = 0
        for letter in word:
            if letter in seen_letters:
                # Penalize duplicate letters 
                score -= 10
            else:
                score += frequency_scores.get(letter, 0)
                seen_letters.add(letter)
        scores[word] = score
    return scores



def compute_guess(target_word, all_words):
    possible_words = all_words[:]
    correct_positions = [None] * 5
    present_letters = {}
    absent_letters = set()
    guesses = []

    # Calculate scores for all words based on letter frequency and diversity
    initial_scores = score_initial_guess(possible_words)
    first_guess = max(initial_scores, key=initial_scores.get)
    guesses.append(first_guess)
    feedback = get_color_mapping(first_guess, target_word)

    # Update known information based on feedback
    update_info(first_guess, feedback, correct_positions, present_letters, absent_letters, target_word)

    while len(guesses) < 6:

        
        filtered_words = [
            word for word in possible_words if is_fits_criteria(word, correct_positions, present_letters, absent_letters)
        ]

        if not filtered_words:
            print("No more possible words based on the criteria.")
            break

        scored_words = score_filtered_words(filtered_words, present_letters, absent_letters)
        guess = max(scored_words, key=scored_words.get)
        guesses.append(guess)
        feedback = get_color_mapping(guess, target_word)
        update_info(guess, feedback, correct_positions, present_letters, absent_letters, target_word)

        if all(color == WORDLE_GREEN  for color in feedback):
            break
        possible_words = filtered_words

    return guesses

def get_color_mapping(guessed_word, target_word):
    color_mapping = [WORDLE_DARK_GREY] * len(guessed_word)  
    target_word_list = list(target_word)

    # First pass for correct position (green)
    for i, letter in enumerate(guessed_word):
        if letter == target_word[i]:
            color_mapping[i] = WORDLE_GREEN
            target_word_list[i] = None  

    # Second pass for wrong position (yellow)
    for i, letter in enumerate(guessed_word):
        if color_mapping[i] == WORDLE_GREEN:  
            continue
        if letter in target_word_list:
            color_mapping[i] = WORDLE_YELLOW
            target_word_list[target_word_list.index(letter)] = None  

    return color_mapping

def score_filtered_words(filtered_words, present_letters, absent_letters):
    letter_scores = get_letter_frequency_scores()
    word_scores = {}

    for word in filtered_words:
        score = 0
        letter_set = set(word)
        # Score based on frequency and present letters
        for letter in letter_set:
            if letter in present_letters and not any(word[pos] == letter for pos in present_letters[letter]):
                score += (letter_scores.get(letter, 1) * 2)  # Prioritize present letters
            elif letter not in absent_letters:
                score += letter_scores.get(letter, 1)
        # Add diversity bonus for words with more unique letters
        diversity_bonus = len(letter_set) / len(word)
        word_scores[word] = score * diversity_bonus
    
    return word_scores

def get_letter_frequency_scores():
    scores = {letter: (26 - i) for i, letter in enumerate(FREQUENCY_ORDER)}
    return scores


def update_info(guess, feedback, correct_positions, present_letters, absent_letters, target_word):
    for i, color in enumerate(feedback):
        if color == WORDLE_GREEN:  # Correct position
            correct_positions[i] = guess[i]
        elif color == WORDLE_YELLOW:  # Present but wrong position
            if guess[i] not in present_letters:
                present_letters[guess[i]] = set()
            present_letters[guess[i]].add(i)
        # Add to absent if letter is not present at all
        if color == WORDLE_DARK_GREY and guess[i] not in target_word:
            absent_letters.add(guess[i])

def is_fits_criteria(word, correct_positions, present_letters, absent_letters):
    for i, letter in enumerate(word):
        # Check if the letter at the current position is correct
        if correct_positions[i] is not None and letter != correct_positions[i]:
            return False
        
        if letter in absent_letters:
            return False
    
    for letter, incorrect_positions in present_letters.items():
        if word.count(letter) == 0:
            # If the letter is known to be present, it must appear in the word
            return False
        for pos in incorrect_positions:
            if word[pos] == letter:
                # The letter should not be in the positions where it was marked yellow
                return False
    return True


def main():
    words = load_words()
    target_word = choose_word(words)
    print("Target Word:", target_word) 
    guesses = compute_guess(target_word, words)

    draw_grid(target_word, guesses)



def draw_grid(target_word, guesses):
    with turtle_canvas(600, 600) as t:
        canvas(0, 0, 600, 600)
        blank(WORDLE_BLACK)
        thickness(5)
        start_x, start_y = 100, 100
        cell_size = 80
      

        for row in range(6):
            for col in range(5):
                setxy(start_x + col * cell_size, start_y + row * cell_size)
                box(cell_size, cell_size, WORDLE_BLACK, border=True)
        update()

        for row, guessed_word in enumerate(guesses):
            y_position = start_y + row * cell_size
            color_mapping = get_color_mapping(guessed_word, target_word)
            animate_guess(guessed_word, start_x, y_position, cell_size, color_mapping, WORDLE_WHITE, "Arial Bold", 36)
            pause(250)  

def animate_guess(word, start_x, start_y, cell_size, color_mapping, color, font, font_size):
    for i, letter in enumerate(word):
        center_x = start_x + i * cell_size
        center_y = start_y
        setxy(center_x, center_y)
        box(cell_size, cell_size, color_mapping[i], border=True)  
        
        if letter == 'W':
            letter_x_offset = 18
        elif letter == 'I':
            letter_x_offset = 32
        elif letter == 'O':
            letter_x_offset = 20
        else:
            letter_x_offset = 24
        
        setxy(center_x + letter_x_offset, center_y + 15)  # y axis offset is constant for all letters
        display(letter, font, font_size)
        update()
        pause(50)  


if __name__ == "__main__":
    main()