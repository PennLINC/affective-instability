"""Determine the reasons for classifications in TEDANA and AROMA."""

import os
import pandas as pd


def main():
    status_table = "status_table.tsv"
    tedana_decision_tree = "decision_tree.json"
    metrics = "metrics.tsv"

    # Load the status table
    status_df = pd.read_table(status_table, index_col="Component")

    # Load the decision tree
    with open(tedana_decision_tree, "r") as f:
        tedana_decision_tree = json.load(f)

    # Load the metrics
    metrics_df = pd.read_table(metrics, index_col="Component")

    # Compare the classifications
    # The index of the status table is the same as the index of the metrics table (Component)
    for component in status_df.index:
        # AROMA reasons for classification are in metrics_df["classification_tags"]
        # as semicolon-separated values
        aroma_reasons = metrics_df.loc[component, "classification_tags"]
        aroma_reasons = aroma_reasons.split(";")
        aroma_reasons = [reason for reason in aroma_reasons if reason.startswith("AROMA")]

        # The TEDANA reasons need to be inferred from the status table and the decision tree.
        # The status table has a column for each node in the decision tree, with a value of
        # accepted or rejected in the last column.
        # We need to find the earliest column with the same value as the last column,
        # and then locate the node in the decision tree that corresponds to that column.
        # The "node_label" field in the status table's corresponding dictionary contains the reason
        # for the classification.
        status_row = status_df.loc[component]
        final_column = status_row.index[-1]
        final_value = status_row[final_column]
        node = None
        for column in status_row.index[::-1]:
            node = column
            if status_row[column] != final_value:
                break

        node_number = int(node.split("Node ")[1])
        node = tedana_decision_tree["nodes"][node_number]
        assert node["outputs"]["decision_node_idx"] == node_number
        tedana_reason = node["outputs"]["node_label"]

        print(component)
        print(aroma_reasons)
        print(tedana_reason)
        print()
