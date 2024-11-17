import os
from endstone.event import event_handler, PlayerDeathEvent, PlayerJoinEvent, PlayerQuitEvent, ServerLoadEvent, EventPriority
from endstone.plugin import Plugin
from endstone import ColorFormat

def format_xp_info(player) -> str:
    """Helper to format player XP information"""
    return (
        f"Level: {player.exp_level} "
        f"XP: {player.total_exp} "
        f"Progress: {player.exp_progress:.1%}"
    )

config = {}

class LevelDeathPenalty(Plugin):
    prefix = "LevelDeathPenalty"
    api_version = "0.5"
    load = "POSTWORLD"

    def on_load(self) -> None:
        self.logger.info("[LevelDeathPenalty] Plugin loading...")

    def on_enable(self) -> None:
        self.logger.info("[LevelDeathPenalty] Plugin enabled!")
        self.server.broadcast_message(f"{ColorFormat.GREEN}[LevelDeathPenalty] XP Loss System Active!")
        self.save_default_config()  # Save default config if it doesn't exist
        self.load_config()  # Load the configuration
        self.register_events(self)  # Register event listeners defined directly in Plugin class

    def on_disable(self) -> None:
        self.logger.info("[LevelDeathPenalty] Plugin disabled!")

    def save_default_config(self) -> None:
        default_config = """
        OPTION1=true
        OPTION1_START_LEVEL=10
        OPTION1_PENALTY_PERCENT=-20
        OPTION2=false
        OPTION2_LEVEL_RANGES="10,30,-20;31,100,-50"
        """
        config_path = os.path.join(self.data_folder, 'config.toml')
        if not os.path.exists(config_path):
            # Create the directory if it doesn't exist
            os.makedirs(self.data_folder, exist_ok=True)
            try:
                with open(config_path, 'w') as file:
                    file.write(default_config)
                self.logger.info(f"[LevelDeathPenalty] Default config saved to {config_path}")
            except Exception as e:
                self.logger.error(f"[LevelDeathPenalty] Error saving default config: {str(e)}")

    def load_config(self) -> dict:
        config_path = os.path.join(self.data_folder, 'config.toml')
        if not os.path.exists(config_path):
            self.logger.error(f"[LevelDeathPenalty] Config file not found: {config_path}")
            return {}

        try:
            with open(config_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"')  # Remove quotes if present
            self.logger.info(f"[LevelDeathPenalty] Config loaded: {config}")
            return config
        except Exception as e:
            self.logger.error(f"[LevelDeathPenalty] Error loading config: {str(e)}")
            return {}

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        """Handle player join events to show their XP info"""
        try:
            player = event.player
            # Get player's current XP status
            current_level = player.exp_level
            current_exp = player.total_exp
            exp_progress = player.exp_progress

            # Show welcome message with XP info
            welcome_message = (
                f"\n{ColorFormat.GREEN}Welcome {player.name}!\n"
                f"{ColorFormat.YELLOW}Current Level: {ColorFormat.WHITE}{current_level}\n"
                f"{ColorFormat.YELLOW}Total XP: {ColorFormat.WHITE}{current_exp}\n"
                #f"{ColorFormat.YELLOW}Level Progress: {ColorFormat.WHITE}{exp_progress:.1%}"
            )

            # Send to joining player
            player.send_message(welcome_message)

            # Log join
            self.logger.info(f"[LevelDeathPenalty] Player {player.name} joined with level {current_level}")

        except Exception as e:
            self.logger.error(f"[LevelDeathPenalty] Error in join handler: {str(e)}")

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        player = event.player
        self.logger.info(ColorFormat.YELLOW + f"{player.name}[/{player.address}] left the game.")

    @event_handler
    def on_player_death(self, event: PlayerDeathEvent) -> None:
        """Handle player death events and apply XP penalty"""
        try:
            player = event.player
            self.logger.info(f"[LevelDeathPenalty] Death event for {player.name}")

            # Store initial values
            current_level = player.exp_level
            current_exp = player.total_exp

            # Get death cause if available
            death_cause = "Unknown"
            if hasattr(event, 'cause'):
                death_cause = str(event.cause)
            elif hasattr(event, 'death_message'):
                death_cause = str(event.death_message)

            self.logger.info(f"[LevelDeathPenalty] Death cause: {death_cause}")

            # Determine penalty based on configuration
            penalty_percent = 0
            if config.get("OPTION1", "false").lower() == "true":
                start_level = int(config.get("OPTION1_START_LEVEL", "10"))
                penalty_percent = int(config.get("OPTION1_PENALTY_PERCENT", "0"))
                if current_level >= start_level:
                    penalty_percent = int(config.get("OPTION1_PENALTY_PERCENT", "0"))
                else:
                    penalty_percent=0

            elif config.get("OPTION2", "false").lower() == "true":
                level_ranges = config.get("OPTION2_LEVEL_RANGES", "").split(';')
                for level_range in level_ranges:
                    level_range_parts = level_range.split(',')
                    if len(level_range_parts) != 3:
                        self.logger.error(f"[LevelDeathPenalty] Invalid level range format: {level_range}")
                        continue
                    min_level, max_level, penalty_percent_str = level_range_parts
                    min_level = int(min_level.strip())
                    max_level = int(max_level.strip())
                    penalty_percent = int(penalty_percent_str.strip())
                    if min_level <= current_level <= max_level:
                        break
                else:
                    penalty_percent = 0  # No penalty outside defined ranges

            # Apply penalty if penalty_percent is not zero
            if penalty_percent != 0:
                exp_penalty = int(current_exp * (penalty_percent / 100.0))
                new_exp = max(0, current_exp + exp_penalty)

                # Apply new experience
                player.exp_level = 0
                player.exp_progress = 0.0
                player.give_exp(new_exp)

                # Prepare death message
                death_message = (
                    f"{ColorFormat.RED}☠ {ColorFormat.YELLOW}"
                    f"{death_cause}\n"
                    f"{ColorFormat.RED}Lost {ColorFormat.YELLOW}{abs(exp_penalty)} XP "
                    f"({ColorFormat.RED}{penalty_percent}%{ColorFormat.YELLOW})"
                )

                # Message to the dead player
                player_message = (
                    f"\n{ColorFormat.RED}Death Penalty Applied:\n"
                    f"{ColorFormat.YELLOW}Previous Level: {ColorFormat.WHITE}{current_level}\n"
                    f"{ColorFormat.YELLOW}Previous XP: {ColorFormat.WHITE}{current_exp}\n"
                    f"{ColorFormat.RED}XP Lost: {ColorFormat.WHITE}{abs(exp_penalty)}\n"
                    f"{ColorFormat.YELLOW}New XP: {ColorFormat.WHITE}{new_exp}\n"
                    f"{ColorFormat.YELLOW}New Level: {ColorFormat.WHITE}{player.exp_level}"
                )

                # Send messages
                self.server.broadcast_message(death_message)  # To all players
                player.send_message(player_message)  # Details to dead player
                player.send_popup(
                    f"{ColorFormat.RED}{penalty_percent}% XP {ColorFormat.YELLOW}({abs(exp_penalty)} lost)")

                # Log the death penalty
                self.logger.info(
                    f"[LevelDeathPenalty] {player.name} died at level {current_level}. "
                    f"Lost {abs(exp_penalty)} XP. New total: {new_exp}"
                )
            else:
                # No penalty message
                no_penalty_message = (
                    f"{ColorFormat.YELLOW}{death_cause}\n"
                    f"{ColorFormat.GRAY}No XP penalty - level {current_level} not within configured ranges"
                )
                self.server.broadcast_message(no_penalty_message)

        except Exception as e:
            self.logger.error(f"[LevelDeathPenalty] Error in death handler: {str(e)}")
            self.server.broadcast_message(
                f"{ColorFormat.RED}Error applying death penalty for {player.name}"
            )

    @event_handler
    def on_server_load(self, event: ServerLoadEvent):
        self.logger.info(f"{event.event_name} is passed to on_server_load")

    @event_handler(priority=EventPriority.HIGH)
    def on_server_load_2(self, event: ServerLoadEvent):
        # This will be called after on_server_load because of a higher priority
        self.logger.info(f"{event.event_name} is passed to on_server_load2")