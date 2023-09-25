import logging

def log(msg):
  logging.basicConfig(filename='bot.log', level=logging.INFO)
  logging.info(msg)