# Polyglot: Simultaneously Valid batch and shell Scripts

## Introduction
Polyglot is a script format that is simultaneously a valid Batch (.BAT, .CMD) file able to be executed on Windows and a valid shell script (bash, sh etc) that can be executed on *nix platforms.

### What is a Polyglot?
In computing, a polyglot is a program or script that is valid in multiple programming languages. [Wikipedia](https://en.wikipedia.org/wiki/Polyglot_(computing)) has a good introduction to the concept.

### Running a polygot script in Windows...
![Running on Windows](https://www.github.com/toru173/polyglot/images/windows.png)

### Linux...
![Running on Linux](https://www.github.com/toru173/polyglot/images/linux.png)

### And in macOS!
![Running on macOS](https://www.github.com/toru173/polyglot/images/macos.png)

## How does it work?
We can combine the two because a line starting with `:; ...(other commands)` is treated as a single line by cmd.exe, but as multiple lines in a shell script. That means we can put in additional commands specific to bash, such as a command that captures all of the contents of the script up to a delimiter keyword - representing the Batch component of the script - and redirecting it to /dev/null. Execution then proceeds as expected in our chosen *nix shell.

A simple example polyglot is as follows:

```
:; cat > /dev/null << END_WIN
:: This is the Windows part of the script
ECHO I'm being executed as a batch file!
EXIT /B
END_WIN

# Now we're in the bash (or similar) part of the script.
echo "I'm being executed as a shell script!"
exit 0
```

There are some additional issues. Batch files behave very differently when being piped to cmd.exe instead of being run directly; see this [stack overflow](https://stackoverflow.com/questions/8192318#8194279) article for more information. The best approach appears to be running the script locally when possible using `start example`. This can be done programmatically if attempting to execute the script via cURL by detecting that the script is being piped to cmd.exe and downloading the script to disk to execute from there.

```
SET "TEMP_INSTALL_SCRIPT=%TEMP%\%RANDOM%-%RANDOM%.cmd"
TIMEOUT /T 0 >NUL 2>NUL
IF ERRORLEVEL 1 (curl -sL https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example -o %TEMP_INSTALL_SCRIPT% && START /WAIT /I CMD /D /Q /K %TEMP_INSTALL_SCRIPT% & DEL %TEMP_INSTALL_SCRIPT% && EXIT /B)
```

Additionally, batch file labels may not work reliably when [using LF line endings only](https://www.dostips.com/forum/viewtopic.php?t=8988) and [bash doesn't like CRLF line endings](https://unix.stackexchange.com/questions/577663/handling-bash-script-with-crlf-carriage-return-in-linux-as-in-msys2). `adjust_line_endings.py` inserts the correct line endings for each section. The heredoc is also sensitive to this 

It is critical that Git doesn't try to normallise the line endings of any polyglot script. The script name needs to be added to .gitattributes to disable line ending normalisation:

```
example -text
```

## Limitations
Windows will only recognise this file as executable if the extension is `.bat` or `.cmd`. If attempting to distribute the script to users this must be taken into consideration. Linux or macOS don't care about the extension but the file cannot be run directly as there is no [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)). The shell cannot guess what program should be used to run the script; it can still be run directly with `bash example`.

## Why did you do this?
I have a project that benefits from having a single script that behaves differently (but correctly) depending on the platform it runs on. I spent far too much time learning about different ways to implement this solution and decided to share my knowledge!

## Try it yourself!

This repository contains an example script [here](https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example). You can run it on either Windows or macOS/Linux by copying and pasting these commands into your platform's command line interpreter.

### Windows
```
curl -sL https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example | cmd
```

### macOS or Linux
```
curl -sL https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example | bash
```

You can quickly copy example code from GitHub by clicking the clipboard icon to the right of the code:

![GitHub Clipboard Icon](https://www.github.com/toru173/polyglot/images/clipboard_icon.png)

Please quickly read through the [example script](https://raw.githubusercontent.com/toru173/polyglot/refs/heads/main/example) before downloading as it's never a good idea to blindly download and run code from the internet!

## Contributing or Feedback
If you have questions, comments or feedback, please [open an issue](https://github.com/toru173/polyglot/issues/new/choose) to start the conversation!
