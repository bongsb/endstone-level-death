# Level Death Penalty

A simple plugin that applies experience penalties when players die on Endstone Servers.

## Requirements
- [Endstone 5.0](https://github.com/EndstoneMC/endstone)

## Default Configuration

```plaintext
OPTION1=true
OPTION1_START_LEVEL=10
OPTION1_PENALTY_PERCENT=-20
OPTION2=false
OPTION2_LEVEL_RANGES=10,30,-10;31,100,-50
```

### Configuration Options Explained

1. **OPTION1**: `true` or `false`
   - Enables or disables the static penalty option.

2. **OPTION1_START_LEVEL**: `10`
   - The minimum level at which a player starts receiving the penalty. Players with a level equal to or higher than this value will lose a percentage of their experience upon death.

3. **OPTION1_PENALTY_PERCENT**: `-20`
   - Specifies the percentage of experience to be deducted when a player dies. In this case, 20% of the player's experience will be lost.

4. **OPTION2**: `true` or `false`
   - Enables or disables the range-based penalty option.

5. **OPTION2_LEVEL_RANGES**: `10,30,-10;31,100,-50`
   - Defines level ranges and corresponding penalties. For example:
     - Levels 10 to 30: Players lose 10% of their experience upon death.
     - Levels 31 to 100: Players lose 50% of their experience upon death.

### Important Note
Ensure that the world has the `keepInventory` rule enabled for the plugin to function correctly.

## Features
- [x] Editable configuration file
- [x] Displays information about experience loss
- [x] Options for static or range-based level penalties
- [ ] Command to reload the configuration (feature in development)

## License
This project is licensed under the MIT License.

