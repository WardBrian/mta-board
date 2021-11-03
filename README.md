# mta-board

Show the upcoming trains, current weather, and some coming soon days.

Based on [mlb-led-scoreboard](https://github.com/WardBrian/mlb-led-scoreboard).

Requires a Raspberry Pi and an LED board hooked up via the GPIO pins.


**Currently supported boards:**
 * 32x32 (Limited number of features)
 * 64x32 (the _most_ supported)
 * 64x64
 * 128x32
 * 128x64

If you'd like to see support for another set of board dimensions, or have design suggestions for an existing one, file an issue!

**Pi's with known issues**
 * Raspberry Pi Zero has had numerous reports of slowness and unreliabilty during installation and running the software.

## Installation
### Hardware Assembly
[See the wiki page for the original project for a step-by-step guide.](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki) This README is primarily focused on the MLB software, but for those coming here from Reddit or elsewhere never having built things with a Raspberry Pi, this should help get you going.

My parts list specifically is located [here](https://www.adafruit.com/wishlists/527606)

### Software Installation
#### Requirements
You need Git for cloning this repo and PIP for installing the scoreboard software.
```
sudo apt-get update
sudo apt-get install git python3-pip
```

#### Installing the scoreboard software
This installation process will take about 10-15 minutes. Raspberry Pis aren't the fastest of computers, so be patient!

```
git clone https://github.com/WardBrian/mlb-led-scoreboard.git
cd mlb-led-scoreboard/
sudo ./install.sh
```

This will install the rgbmatrix binaries, which we get from [another open source library](https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python#building). It controls the actual rendering of the scoreboard onto the LEDs. If you're curious, you can read through their documentation on how all of the lower level stuff works.

It will also install the following python libraries that are required for certain parts of the scoreboard to function.

* [tzlocal](https://github.com/regebro/tzlocal): Timezone libraries. These allow the scoreboard to convert times to your local timezone
* [feedparser](https://pypi.org/project/feedparser/): Used to fetch and parse RSS feeds. The scoreboard uses this to show news headlines.
* [pyowm](https://github.com/csparpa/pyowm): OpenWeatherMap API interactions. We use this to get the local weather for display on the offday screen. For more information on how to finish setting up the weather, visit the [weather section](#weather) of this README.
* [underground](https://github.com/nolanbconaway/underground): The main library that fetches and parses all of the actual MTA data being displayed


#### Updating
* Run `git pull` in your mlb-led-scoreboard folder to fetch the latest changes. A lot of the time, this will be enough, but if something seems broken:
    * **Re-run the install file**. Run `sudo ./install.sh` again. Any additional dependencies that were added with the update will be installed this way. If you are moving to a new major release version, answer "Y" to have it make you a new config file.
    * **Check your custom layout/color files if you made any**. There's a good chance some new keys were added to the layout and color files. These changes should just merge right in with the customized .json file you have but you might want to look at the new .json.example files and see if there's anything new you want to customize.

That should be it! Your latest version should now be working with whatever new fangled features were just added.

#### Time Zones
Make sure your Raspberry Pi's timezone is configured to your local time zone. They'll often have London time on them by default. You can change the timezone of your raspberry pi by running `sudo raspi-config`.

## Usage
`sudo python main.py` Running as root is 100% an absolute must, or the matrix won't render.

**Adafruit HAT/Bonnet users: You must supply a command line flag:**

`sudo python main.py --led-gpio-mapping="adafruit-hat"`

See the Flags section below for more flags you can optionally provide.

### Configuration

A default `config.json.example` file is included for reference. Copy this file to `config.json` and modify the values as needed.

### Flags

You can configure your LED matrix with the same flags used in the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library. More information on these arguments can be found in the library documentation.
```
--led-rows                Display rows. 16 for 16x32, 32 for 32x32. (Default: 32)
--led-cols                Panel columns. Typically 32 or 64. (Default: 32)
--led-chain               Daisy-chained boards. (Default: 1)
--led-parallel            For Plus-models or RPi2: parallel chains. 1..3. (Default: 1)
--led-pwm-bits            Bits used for PWM. Range 1..11. (Default: 11)
--led-brightness          Sets brightness level. Range: 1..100. (Default: 100)
--led-gpio-mapping        Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm
--led-scan-mode           Progressive or interlaced scan. 0 = Progressive, 1 = Interlaced. (Default: 1)
--led-pwm-lsb-nanosecond  Base time-unit for the on-time in the lowest significant bit in nanoseconds. (Default: 130)
--led-show-refresh        Shows the current refresh rate of the LED panel.
--led-slowdown-gpio       Slow down writing to GPIO. Range: 0..4. (Default: 1)
--led-no-hardware-pulse   Don't use hardware pin-pulse generation.
--led-rgb-sequence        Switch if your matrix has led colors swapped. (Default: RGB)
--led-pixel-mapper        Apply pixel mappers. e.g Rotate:90, U-mapper
--led-row-addr-type       0 = default; 1 = AB-addressed panels. (Default: 0)
--led-multiplexing        Multiplexing type: 0 = direct; 1 = strip; 2 = checker; 3 = spiral; 4 = Z-strip; 5 = ZnMirrorZStripe; 6 = coreman; 7 = Kaler2Scan; 8 = ZStripeUneven. (Default: 0)
--led-limit-refresh=<Hz>  : Limit refresh rate to this frequency in Hz. Useful to keep a constant refresh rate on loaded system. 0=no limit. Default: 0
--led-pwm-dither-bits   : Time dithering of lower bits (Default: 0)
--config                  Specify a configuration file name other, omitting json xtn (Default: config)
```

## Personalization
If you're feeling adventurous (and we highly encourage it!), the sections below outline how you can truly personalize your scoreboard and make it your own!
### Custom Board Layout
You have the ability to customize the way things are placed on the board (maybe you would prefer to see scrolling text for a pregame a bit higher or lower). See the `coordinates/` directory for more information.

### Custom Colors
You have the ability to customize the colors of everything on the board. See the `colors/` directory for more information.

### Weather
This scoreboard will use a weather API to gather weather information at various times. This information is displayed on your teams offdays for your area and also displayed during each game's pregame information. The weather API we use is from OpenWeatherMaps. OpenWeatherMaps API requires an API key to fetch this data so you will need to take a quick minute to sign up for an account and copy your own API key into your `config.json`.

You can find the signup page for OpenWeatherMaps at [https://home.openweathermap.org/users/sign_up](https://home.openweathermap.org/users/sign_up). Once logged in, you'll find an `API keys` tab where you'll find a default key was already created for you. You can copy this key and paste it into the `conig.json` under `"weather"`, `"apikey"`.

You can change the location used by entering your city, state, and country code separated by commas. If you wish to use metric measurments, set the `"metric"` option to `true`.

## Sources
This project relies on:
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) is the library used for making everything work with the LED board.

## Help and Contributing
If you run into any issues and have steps to reproduce, open an issue. If you have a feature request, open an issue. If you want to contribute a small to medium sized change, open a pull request. If you want to contribute a new feature, open an issue first before opening a PR.

## Licensing
This project as of v1.1.0 uses the GNU Public License. If you intend to sell these, the code must remain open source.
