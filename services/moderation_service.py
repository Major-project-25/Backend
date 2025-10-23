# Backend/services/moderation_service.py

from detoxify import Detoxify

# --- MODEL LOADING ---
# This is the core of the service. We load the model into memory only ONCE
# when the application starts. This makes the checking process very fast.
# The model will be downloaded from the internet on the first run.
print("Loading NLP moderation model...")
try:
    # Using the 'unbiased' model which is good for general purpose toxicity detection.
    model = Detoxify('unbiased')
    MODERATION_MODEL_AVAILABLE = True
    print("NLP moderation model loaded successfully.")
except Exception as e:
    MODERATION_MODEL_AVAILABLE = False
    print(f"Could not load NLP moderation model. Moderation will be disabled. Error: {e}")


# --- CONFIGURATION ---
# We set a threshold for what we consider "toxic".
# A value of 0.8 means we are fairly confident the content is offensive.
# You can adjust this value to be more or less strict.
TOXICITY_THRESHOLD = 0.5

def is_message_offensive(message: str) -> bool:
    """
    Checks if a given message is offensive based on the loaded NLP model.

    Args:
        message (str): The text content of the user's message.

    Returns:
        bool: True if the message is deemed offensive, False otherwise.
    """
    if not MODERATION_MODEL_AVAILABLE:
        # If the model failed to load, we default to not flagging any message.
        return False

    try:
        # The model returns a dictionary of scores for different categories.
        # We are primarily interested in the 'toxicity' score.
        predictions = model.predict(message)
        
        # --- NEW DEBUG LOG ---
        # Print the score for EVERY message so we can see what's happening.
        toxicity_score = predictions['toxicity']
        print(f"[Moderation Log] Message: '{message}' | Toxicity Score: {toxicity_score:.4f}")
        # ---------------------
        
        # Check if the toxicity score exceeds our defined threshold.
        if toxicity_score > TOXICITY_THRESHOLD:
            print(f"      -> ACTION: Blocked")
            return True
        else:
            print(f"      -> ACTION: Allowed")
            return False
            
    except Exception as e:
        print(f"An error occurred during message prediction: {e}")
        # Default to not flagging the message if an error occurs.
        return False

