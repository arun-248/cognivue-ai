
import sys
from pathlib import Path

# Ensure project root is available
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.model_loader import (
    load_all_models,
    get_model_information,
)

print("\n" + "=" * 60)
print("COGNIVUE AI - MODEL LOADER TEST")
print("=" * 60)

try:
    models = load_all_models()

    information = get_model_information(models)

    print("\nMODEL INFORMATION")
    print("-" * 60)

    for key, value in information.items():
        print(f"{key}: {value}")

    print("\nMODEL OBJECT CHECKS")
    print("-" * 60)

    assert models["random_forest"] is not None
    assert models["kmeans_model"] is not None
    assert models["kmeans_scaler"] is not None
    assert models["kmeans_pca"] is not None

    assert len(models["feature_order"]) == 9

    print("Random Forest: PASSED")
    print("K-Means: PASSED")
    print("K-Means Scaler: PASSED")
    print("K-Means PCA: PASSED")
    print("Feature Order: PASSED")

    print("\n" + "=" * 60)
    print("ALL MODEL LOADER TESTS PASSED")
    print("=" * 60)

except Exception as error:
    print("\nMODEL LOADING FAILED")
    print("-" * 60)
    print(type(error).__name__ + ":", error)
    raise
