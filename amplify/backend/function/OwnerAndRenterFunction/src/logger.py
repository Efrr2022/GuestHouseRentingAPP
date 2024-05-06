import logging
# Create a custom logger
logger = logging.getLogger()
    
# Create handlers
c_handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
#c_handler.setLevel(logging.INFO)

# Add handlers to the logger
logger.addHandler(c_handler)
    