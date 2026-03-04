"""
Central CSV data loader and manager for the Grocery Price Comparator app.
Handles reading and writing all CSV files with pandas.
Singleton pattern - imported and used globally across all routes.
"""

import pandas as pd
import os
from pathlib import Path


class DataLoader:
    """
    Singleton class that loads all CSV files into pandas DataFrames.
    Provides methods to save modified DataFrames back to CSV files.
    """

    _instance = None

    def __new__(cls, data_dir="data/"):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_dir="data/"):
        # Only initialize once
        if self._initialized:
            return

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        self.data_dir = data_dir
        self._load_all_data()
        self._initialized = True

    def _load_all_data(self):
        """Load all CSV files into memory with error handling."""
        try:
            self.stores = pd.read_csv(os.path.join(self.data_dir, "stores.csv"))
            self.products = pd.read_csv(os.path.join(self.data_dir, "products.csv"))
            self.prices = pd.read_csv(os.path.join(self.data_dir, "product_prices.csv"))
            self.price_history = pd.read_csv(
                os.path.join(self.data_dir, "price_history.csv")
            )
            self.ratings = pd.read_csv(os.path.join(self.data_dir, "store_ratings.csv"))
            self.budget_sessions = pd.read_csv(
                os.path.join(self.data_dir, "budget_sessions.csv")
            )
            self.budget_items = pd.read_csv(
                os.path.join(self.data_dir, "budget_items.csv")
            )
            self.categories = pd.read_csv(os.path.join(self.data_dir, "categories.csv"))

            # --- Normalise products column names ---
            if (
                "id" in self.products.columns
                and "product_id" not in self.products.columns
            ):
                self.products = self.products.rename(columns={"id": "product_id"})
            if (
                "name" in self.products.columns
                and "product_name" not in self.products.columns
            ):
                self.products = self.products.rename(columns={"name": "product_name"})

            # --- Normalise product_prices column names ---
            if "id" in self.prices.columns and "price_id" not in self.prices.columns:
                self.prices = self.prices.rename(columns={"id": "price_id"})

            # Ensure correct data types
            self.products["product_id"] = self.products["product_id"].astype(int)
            self.prices["product_id"] = self.prices["product_id"].astype(int)
            self.prices["store_id"] = self.prices["store_id"].astype(int)
            self.prices["price"] = self.prices["price"].astype(float)

            self.price_history["product_id"] = self.price_history["product_id"].astype(
                int
            )
            self.price_history["store_id"] = self.price_history["store_id"].astype(int)
            self.price_history["price"] = self.price_history["price"].astype(float)

            self.ratings["store_id"] = self.ratings["store_id"].astype(int)
            self.ratings["rating"] = self.ratings["rating"].astype(int)

            if len(self.budget_sessions) > 0:
                self.budget_sessions["total_budget"] = self.budget_sessions[
                    "total_budget"
                ].astype(float)

            if len(self.budget_items) > 0:
                self.budget_items["product_id"] = self.budget_items[
                    "product_id"
                ].astype(int)
                self.budget_items["store_id"] = self.budget_items["store_id"].astype(
                    int
                )
                self.budget_items["price_at_add"] = self.budget_items[
                    "price_at_add"
                ].astype(float)
                self.budget_items["quantity"] = self.budget_items["quantity"].astype(
                    int
                )

        except Exception as e:
            raise Exception(f"Error loading CSV files: {str(e)}")

    def reload_all(self):
        """Reload all CSV files from disk."""
        self._load_all_data()

    def save_ratings(self):
        """Save ratings DataFrame to CSV."""
        try:
            self.ratings.to_csv(
                os.path.join(self.data_dir, "store_ratings.csv"), index=False
            )
        except Exception as e:
            raise Exception(f"Error saving ratings: {str(e)}")

    def save_budget_sessions(self):
        """Save budget sessions DataFrame to CSV."""
        try:
            self.budget_sessions.to_csv(
                os.path.join(self.data_dir, "budget_sessions.csv"), index=False
            )
        except Exception as e:
            raise Exception(f"Error saving budget sessions: {str(e)}")

    def save_budget_items(self):
        """Save budget items DataFrame to CSV."""
        try:
            self.budget_items.to_csv(
                os.path.join(self.data_dir, "budget_items.csv"), index=False
            )
        except Exception as e:
            raise Exception(f"Error saving budget items: {str(e)}")

    def save_prices(self):
        """Save prices DataFrame to CSV."""
        try:
            self.prices.to_csv(
                os.path.join(self.data_dir, "product_prices.csv"), index=False
            )
        except Exception as e:
            raise Exception(f"Error saving prices: {str(e)}")


# Create singleton instance
data_loader = DataLoader(data_dir="data/")
