@ECHO off

SETLOCAL

SET PYTHONPATH="%PYTHONPATH%;bots;jm17290-src;"
SET games=200
SET generations=5

python run_initialise.py
FOR /L %%A IN (1,1,%generations%) DO (
CD ..
python competition.py %games% jm17290_ea.JM17290Bot intermediates.Simpleton intermediates.Trickerton intermediates.Bounder intermediates.Logicalton
CD jm17290-src
python run_next_generation.py
)

ENDLOCAL
pause