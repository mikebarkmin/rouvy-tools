Rouvy tools is integrated into [bycycling](https://github.com/mikebarkmin/bycycling). There you can find an [online version of the tool](https://www.bycycling.eu/tools/mrc-workout-creator).

# Rouvy Tools

This is a collection of python script to make working out in Rouvy better. For example by converting Zwift workouts to mrc so that they can be imported. Zwift Academy in Rouvy - here we go!

## Whatsonzwift to MRC Converter

Copy the content of the workout summary from https://whatsonzwift.com. For example:

```
10min from 50 to 80% FTP
1min from 80 to 95% FTP
3min @ 60% FTP
2min @ 115% FTP
```

Save the content into a file. For example "wild-starts".

Call the script with the path to the file.

```
python woz-to-mrc wild-starts
```

The script will create a new file in the same folder. For example: `wild-starts.mrc`.

This file can be imported in other programs like Rouvy.

### Developer

Run `python woz-to-mrc.py` to run the doctests.

## Roadmap

Maybe in the future the tools will be converted to JavaScript and I will build a website around them.
If you have other suggestions for tools, which could be helpful for Rouvy, write a new issue.
