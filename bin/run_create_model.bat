@echo off
cd ../src/modeling/
set conda_path=%UserProfile%\anaconda3\scripts\activate.bat
set env_path=%UserProfile%\anaconda3
call "%conda_path%" "%env_path%"
python createModel.py 
call conda deactivate
pause