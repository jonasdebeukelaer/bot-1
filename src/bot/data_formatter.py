from typing import Dict, List
from datetime import datetime

from util import five_sig_fig
from logger import logger


class DataFormatter:
    def __init__(self):
        pass

    def format_hourly_data(self, taapi_indicators: list) -> str:
        logger.log_info("Format hourly indicators...")
        indicators_history = self._restructure_indicators_history(taapi_indicators)
        return self._stringify_indicators(indicators_history)

    def format_daily_data(self, taapi_indicators: list, alternative_me: list) -> str:
        logger.log_info("Format daily indicators...")
        indicators_history = self._restructure_indicators_history(taapi_indicators)
        indicators_history = self._append_fear_greed_index(indicators_history, alternative_me)
        return self._stringify_indicators(indicators_history)

    def _restructure_indicators_history(self, taapi_indicators: list) -> list:
        indicators_history = []
        for taapi_indicator in taapi_indicators:
            indicators = self._get_timestamp_features(taapi_indicator["id"])

            for j in range(len(taapi_indicator["data"])):
                indicator_name = taapi_indicator["data"][j]["id"]
                indicator_data = taapi_indicator["data"][j]["result"]
                indicators[indicator_name] = indicator_data

            indicators_history.append(indicators)

        return indicators_history

    def _get_timestamp_features(self, raw_timestamp: str) -> Dict:
        temporal_data = raw_timestamp.split(" ")
        ts = " ".join(temporal_data[0:2])
        dow = temporal_data[2][1:-1]

        return {"timestamp": ts, "day_of_week": dow}

    def _append_fear_greed_index(self, indicators_history: list, alternative_me: list) -> list:
        alternative_me_indicators = {}
        for alt_me_indicator in alternative_me:
            indicator_key = alt_me_indicator["data"]["timestamp"]
            indicator_classification = alt_me_indicator["data"]["value_classification"]
            alternative_me_indicators[indicator_key] = indicator_classification

        for i, indicators in enumerate(indicators_history):
            alt_me_formatted_date = datetime.strptime(indicators["timestamp"].split(" ")[0], "%Y-%m-%d").strftime(
                "%d-%m-%Y"
            )

            if alt_me_formatted_date in alternative_me_indicators:
                indicators_history[i]["fear_greed_index_class"] = alternative_me_indicators[alt_me_formatted_date]
            else:
                indicators_history[i]["fear_greed_index_class"] = "Unknown"

        return indicators_history

    def _stringify_indicators(self, indicators_history: list) -> str:
        formatted_indicators = ""
        for inds in indicators_history:
            for indicator_name, indicator_result in inds.items():
                if indicator_name == "candle":
                    formatted_indicators += f"candle_volume: {five_sig_fig(indicator_result['volume'])}, "
                    formatted_indicators += f"candle_high: {five_sig_fig(indicator_result['high'])}, "
                    formatted_indicators += f"candle_low: {five_sig_fig(indicator_result['low'])}, "
                    formatted_indicators += f"candle_open: {five_sig_fig(indicator_result['open'])}, "
                    formatted_indicators += f"candle_close: {five_sig_fig(indicator_result['close'])}, "

                elif indicator_name == "MACD":
                    formatted_indicators += f"MACD: {five_sig_fig(indicator_result['valueMACD'][0])}, "
                    formatted_indicators += f"MACD_signal: {five_sig_fig(indicator_result['valueMACDSignal'][0])}, "
                    formatted_indicators += f"MACD_hist: {five_sig_fig(indicator_result['valueMACDHist'][0])}, "

                elif isinstance(indicator_result, dict) and "value" in indicator_result:
                    formatted_indicators += f"{indicator_name}: {five_sig_fig(indicator_result['value'][0])}, "
                else:
                    formatted_indicators += f"{indicator_name}: {indicator_result}, "

            formatted_indicators = formatted_indicators[:-2] + "\n"

        return formatted_indicators[:-1] if len(formatted_indicators) > 1 else "No data available"

    def format_news(self, news_items: List[Dict]) -> str:
        """Format news items into a readable text block."""
        logger.log_info("Format latest news...")

        formatted_text = ""
        for i, item in enumerate(news_items, 1):
            formatted_text += f"News {i}: "
            formatted_text += f"Published: {item['data']['published']} "
            formatted_text += f"Title: {item['data']['title']} "
            formatted_text += f"Summary: {item['data']['summary']}\n"
        return formatted_text
