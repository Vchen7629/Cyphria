import json, time
from data_processing_components.aspect_based_sentiment_analysis import (
    Aspect_Based_Sentiment_Analysis,
)
import pandas as pd


class TransformData:
    def __init__(
        self,
        consumer_instance,
        tokenizer,
        model,
    ):
        try:
            self.instance = consumer_instance
            self.Aspect_Instance = Aspect_Based_Sentiment_Analysis(
                tokenizer=tokenizer,
                model=model,
            )
        except Exception as e:
            print(f"Error initializing models: {e}")

    def poll_for_new_messages(
        self,
    ):
        extracted_data = []
        try:
            messages = self.instance.consumer_config.poll(timeout_ms=1000)

            if not messages:
                yield
                return

            for (
                tp,
                records,
            ) in messages.items():
                for record in records:
                    if record.value:
                        try:
                            message = json.loads(record.value)
                            if isinstance(
                                message,
                                list,
                            ):
                                extracted_data.extend(message)
                            elif isinstance(
                                message,
                                dict,
                            ):
                                extracted_data.append(message)
                            else:
                                print(
                                    f"ERROR: Cannot process non-list/non-dict JSON value. Type: {type(message)}"
                                )
                        except Exception as e:
                            print(f"An unexpected error occurred for offset {record.offset}: {e}")
                    else:
                        print("records doesnt have any values")

            if extracted_data:
                processed_data = self.Transform_Data(extracted_data)
                if processed_data is not None:
                    yield processed_data
                else:
                    yield None
            else:
                yield None
        except Exception as e:
            print(f"Error trasnform: {e}")

    def Transform_Data(
        self,
        data,
    ):
        if self.Aspect_Instance is None:
            print("ERROR: Aspect_Based_Sentiment_Analysis instance is not available.")
            return None

        if not data:
            print("ERROR: Data is not available.")
            return None

        try:
            start = time.time()
            dataframe = pd.DataFrame(data=data)

            required_cols = [
                "body",
                "keywords",
            ]
            if not all(col in dataframe.columns for col in required_cols):
                print(
                    f"ERROR: Input data missing required columns. Found: {dataframe.columns}. Required: {required_cols}"
                )
                return None

            sentence_keyword_pair = [
                (
                    index,
                    sentence,
                    keyword,
                )
                for index, sentence, keyword_list in zip(
                    dataframe.index,
                    dataframe["body"],
                    dataframe["keywords"],
                )
                if isinstance(
                    keyword_list,
                    list,
                )
                for keyword in keyword_list
                if isinstance(
                    keyword,
                    str,
                )
            ]

            print(f"time to generate sentence_keyword_pair: {time.time() - start}")

            if not sentence_keyword_pair:
                print("WARN: No valid sentence-keyword pairs generated.")
                dataframe["keyword_sentiments"] = pd.Series(
                    [{} for _ in range(len(dataframe))],
                    index=dataframe.index,
                )
                return dataframe

            sentiment_results = self.Aspect_Instance.SentimentAnalysis(pair=sentence_keyword_pair)
            print(f"time for sentiment_results: {time.time() - start}")

            if not sentiment_results or sentiment_results is None:
                print("No sentiment results returned")
                dataframe["keyword_sentiments"] = pd.Series(
                    [{} for _ in range(len(dataframe))],
                    index=dataframe.index,
                )
                return None

            start2 = time.time()
            sentiment_df = pd.DataFrame(
                sentiment_results,
                columns=[
                    "index",
                    "keyword",
                    "sentiment",
                ],
            )
            print(f"time for dataframe creation: {time.time() - start2}")

            start3 = time.time()
            aggregated_data = sentiment_df.groupby("index").apply(self.aggregate_results)
            print(f"time for groupby: {time.time() - start3}")

            aggregated_data.name = "keyword_sentiments"

            start4 = time.time()
            final_df = dataframe.join(
                aggregated_data,
                how="left",
            )
            print(f"time for join: {time.time() - start4}")
            print(f"time for processing: {time.time() - start}")

            return final_df
        except Exception as e:
            print(f"ERROR during groupby/apply: {e}")
            import traceback

            traceback.print_exc()
            dataframe["keyword_sentiments"] = pd.Series(
                [{} for _ in range(len(dataframe))],
                index=dataframe.index,
            )
            return dataframe

    def aggregate_results(
        self,
        group,
    ):
        try:
            return [
                {
                    "keyword": k,
                    "sentiment": s,
                }
                for k, s in zip(
                    group["keyword"],
                    group["sentiment"],
                )
            ]
        except Exception as e:
            print(f"ERROR inside aggregate_results for group index {group.name}: {e}")
            return []
