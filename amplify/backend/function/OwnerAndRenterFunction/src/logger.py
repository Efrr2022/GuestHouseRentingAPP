import logging
 # Create a custom logger
logger = logging.getLogger()
    
# Create handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)

# Add handlers to the logger
logger.addHandler(c_handler)
    