: << 'END_WIN'
@ECHO OFF
:: This is the Windows part of the script
::
:: If this script is being run using curl it will need to save
:: itself to a temporary file. We do that here, and delete the
:: temporary file to clean up once we're finished.
:: We need to set a temporary install file path before
:: the pipe-check because expansion behaves differently
:: when executing from a pipe. Thanks cmd.exe!
SET "TEMP_INSTALL_SCRIPT=%TEMP%\%RANDOM%-%RANDOM%.cmd"
TIMEOUT /T 0 >NUL 2>NUL
IF ERRORLEVEL 1 (curl -sL https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example.cmd -o %TEMP_INSTALL_SCRIPT% && START /WAIT /I CMD /Q /K %TEMP_INSTALL_SCRIPT% >NUL 2>&1 & DEL %TEMP_INSTALL_SCRIPT% && EXIT /B)

ECHO I'm being executed as a batch file!

:: All done! Let's exit from the Windows part of the script
EXIT /B
END_WIN

# Now we're in the sh (or similar) part of the script.
# Line endings should be different here too - ensure line
# endings are correct by running adjust_line_endings.py
# before running or uploading this script.

echo "I'm being executed as a shell script!"
exit 0
