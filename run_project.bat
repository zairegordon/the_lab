@echo off
cd /d %~dp0
.venv\Scripts\python.exe -m pytest -q > run_project_output.txt 2>&1
if %ERRORLEVEL% neq 0 echo TESTS_FAILED >> run_project_output.txt
.venv\Scripts\python.exe -m src.fantasy_optimizer.cli --players players.csv --budget 500 >> run_project_output.txt 2>&1
echo RUN_COMPLETE >> run_project_output.txt
