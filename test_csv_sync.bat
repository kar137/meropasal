@echo off
echo Generating demo data for CSV sync testing...
echo.

cd /d "%~dp0ml_backend"

echo Creating demo Flutter CSV files...
python generate_demo_data.py

echo.
echo Testing the sync system...
python sync_data.py

echo.
echo Checking results...
python -c "import os; files=['customers.csv','products.csv','shops.csv','transactions.csv','extracted_features.csv']; [print(f'{f}: {os.path.getsize(f)} bytes') if os.path.exists(f) else print(f'{f}: NOT FOUND') for f in files]"

echo.
echo Demo completed!
pause
