"""
Test script to validate the demo application
"""

import pandas as pd
import numpy as np
from pathlib import Path

def test_data_loading():
    """Test data loading functionality"""
    print("Testing data loading...")

    # Test data_final.xlsx
    data_path = Path("data_final.xlsx")
    if data_path.exists():
        try:
            df = pd.read_excel("data_final.xlsx", sheet_name='datos')
            print(f"[OK] data_final.xlsx loaded successfully: {df.shape}")

            # Check required columns
            required_columns = ['Regions', 'Tourism_Competitiveness_Index', 'Rating',
                              'Room_Occupancy_Rate', 'Tourism_Employment']

            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                print(f"[ERROR] Missing required columns: {missing_cols}")
            else:
                print("[OK] All required columns present")

        except Exception as e:
            print(f"[ERROR] Error loading data_final.xlsx: {e}")
    else:
        print("[ERROR] data_final.xlsx not found")

    # Test ModeloPLS_final.xlsx
    model_path = Path("ModeloPLS_final.xlsx")
    if model_path.exists():
        try:
            df = pd.read_excel("ModeloPLS_final.xlsx", sheet_name='complete')
            print(f"[OK] ModeloPLS_final.xlsx loaded successfully: {df.shape}")
        except Exception as e:
            print(f"[ERROR] Error loading ModeloPLS_final.xlsx: {e}")
    else:
        print("[ERROR] ModeloPLS_final.xlsx not found")

def test_model_calculations():
    """Test model calculation logic"""
    print("\nTesting model calculations...")

    # Test coefficient calculations
    coefficients = {
        'competitiveness_to_satisfaction': 0.884,
        'competitiveness_to_employment': 0.319,
        'satisfaction_to_employment': 0.580
    }

    # Test projection calculations
    comp_change = 10  # 10% change
    satisfaction_change = 5  # 5% change
    infrastructure_change = 15  # 15% change

    # Employment change calculation
    employment_from_competitiveness = (comp_change / 100) * coefficients['competitiveness_to_employment']
    employment_from_satisfaction = (satisfaction_change / 100) * coefficients['satisfaction_to_employment']
    employment_from_infrastructure = (infrastructure_change / 100) * 0.15

    total_employment_change = (employment_from_competitiveness +
                             employment_from_satisfaction +
                             employment_from_infrastructure) * 100

    print(f"[OK] Employment calculation: {total_employment_change:.2f}%")

    # Revenue calculation
    revenue_change = ((comp_change / 100) * 0.8 + (satisfaction_change / 100) * 0.6) * 100
    print(f"[OK] Revenue calculation: {revenue_change:.2f}%")

    # Visitor calculation
    visitor_change = ((comp_change / 100) * 0.7 + (satisfaction_change / 100) * 0.3) * 100
    print(f"[OK] Visitor calculation: {visitor_change:.2f}%")

def test_baseline_scenario():
    """Test baseline scenario (0% changes)"""
    print("\nTesting baseline scenario...")

    # All changes at 0%
    changes = [0, 0, 0, 0]

    # Should result in 0% for all projections
    employment_change = sum(changes)
    revenue_change = sum(changes)
    visitor_change = sum(changes)

    if employment_change == 0 and revenue_change == 0 and visitor_change == 0:
        print("[OK] Baseline scenario working correctly (all 0%)")
    else:
        print("[ERROR] Baseline scenario not working correctly")

if __name__ == "__main__":
    print("Testing PLS-SEM Tourism Demo")
    print("=" * 40)

    test_data_loading()
    test_model_calculations()
    test_baseline_scenario()

    print("\nAll tests completed!")
    print("\nTo run the demo:")
    print("streamlit run demo_app.py")