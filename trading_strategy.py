import os
import json
import logger

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

class TradingStrategy:
  def __init__(self, exchange_interface):
    self.exchange_interface = exchange_interface

  def execute(self):
    indicators = self.exchange_interface.get_trade_indicators()

    # Call GPT3 with indicators to decide if we should call GPT4
    resp = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "user",
          "content": "price and indicators of bitcoin" + str(indicators)
        },
        {
          "role": "system",
          "content": "Given the price and indicators of bitcoin, should we call GPT4 to make a trade decision based off the latest price movement and indicators? Answer this and provide a reason for your decision."
        }],
        functions=[{
          'name': 'should_call_gpt4',
          'description': 'Decide if we should call GPT4 to make trade decision based off the latest price movement and indicators.',
          'parameters': {
            'type': 'object',
            'properties': {
              'should_call': {
                'type': 'boolean',
              },
              'reasoning': {
                'type': 'string',
                'description': 'The reasoning behind the decision.',
              },
            }
          }
        }],
        function_call={"name": "should_call_gpt4"},
    )


    answer = json.loads(resp['choices'][0]['message']['function_call']['arguments'])

    # Log decision
    log_msg = "Decided to call GPT4: {}. Reasoning: {}".format(answer["should_call"], answer["reasoning"])
    logger.log(log_msg)

    if answer["should_call"]:
      # trading_instructions = openai.api_v1.gpt4.analyze(indicators)
      resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
          "role": "user",
          "content": "price and indicators of bitcoin" + str(indicators)
        },
        {
          "role": "system",
          "content": "Given the price and indicators of bitcoin, what is your trading decision"
        }],
        functions=[{
          'name': 'decide_trade',
          'description': 'Analyze the latest price movement and indicators to make a trading decision. Include the price, amount and side you would like to trade, given you have a total of £100 available in your porfolio.',
          'parameters': {
            'type': 'object',
            'properties': {
              'size': {
                'type': 'number',
                'description': 'The size of the trading order.',
              },
              'price': {
                'type': 'number',
                'description': 'The price of bitcoin at which to make the trade.',
              },
              'side': {
                'type': 'string',
                'enum': ['buy', 'sell'],
                'description': 'The side on which to make the order.',
              },
              'reasoning': {
                'type': 'string',
                'description': 'The reasoning behind the trading decision.',
              },
            }
          }
        }],
        function_call={"name": "decide_trade"},
      )

      trading_instructions = json.loads(resp['choices'][0]['message']['function_call']['arguments'])

      # Log trading decision
      log_msg = "Made trade decision based on indicators: {}. Trade instructions: {}".format(indicators, trading_instructions)
      logger.log(log_msg)

      # Execute trade
      self.exchange_interface.execute_trade(trading_instructions["size"], trading_instructions["price"])

      # Log trading decision
      log_msg = "Made trade decision based on indicators: {}. Trade instructions: {}".format(indicators, trading_instructions)
      logger.log(log_msg)