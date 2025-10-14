import os
import csv

def misclassified(corpus, y_pred_labels, y_test_labels, test_id) -> None:
        header = ["post", "predicted_category", "actual_category"]

        file_name = "misclassified_posts.csv"
        target_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "datasets",
        )
        
        filepath = os.path.join(target_dir, file_name)
        file_exists = os.path.isfile(filepath)

        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")
            return
        else:
            with open(filepath, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                if not file_exists:
                    writer.writerow(header)
                test_posts = [corpus[i] for i in test_id]
                for i in range(len(y_pred_labels)):
                    if y_pred_labels[i] != y_test_labels[i]:
                        writer.writerow(
                            [
                                test_posts[i],
                                y_pred_labels[i],
                                y_test_labels[i],
                            ]
                        )