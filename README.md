# mta-board

Show the upcoming trains.

A plugin for [mlb-led-scoreboard](https://github.com/WardBrian/mlb-led-scoreboard).

**Note**: This is just a personal project to use on my board during the baseball offseason, I probably
won't add any more features!

## Example config

`config.json`:

```json
{
  "rotation": {
    "screens": [
      { "kind": "trains", "seconds": 20, "with_priority": 0 }
    ]
  },
  "plugins": {
    "example": {
      "step": 3
    },
    "trains": {
      "skip_next_trains": 0,
      "num_trains": 3,
      "stops": {
        "6": ["631N"]
      }
    }
  }
}
```

`colors/scoreboard.json`:
```json
{
  "plugins" : {
    "trains":{
      "stop": {
        "r": 255,
        "g": 255,
        "b": 255
      },
      "eta": {
        "r": 255,
        "g": 255,
        "b": 255
      }
    }
  }
}
```

`coordinates/w64h32.json`:

```json
{
  "plugins": {
    "trains": {
      "stops_per_page": 2,
      "font_name": "5x7",
      "offset": 15,
      "eta": {
        "x": 16,
        "y": 13
      },
      "stop": {
        "x": 16,
        "y": 7,
        "width": 48
      },
      "line": {
        "x": 8,
        "y": 7,
        "font_name": "7x13B",
        "radius": 12
      }
    }
  }
}
```
