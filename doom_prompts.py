import base64


WALTHROUGH_E1_M1 = "1. You start out the game in a room with a blue pool.\n2. Go across the pool.\n3. Keep going straight into the hallway.\n4.Go straight down the hall, and open the door. Enter the computer room.\n5. Kill the two guys there. Go around the room with blue walls, and to the back right of the computer room, where there is an entrance to the bridge room (if you face the grey door, you need to turn around).\n6. Make a right, kill the two guys, and cross the bridge. Don't fall into the green acid pool.\n7. Go straight and open the door at the end of the bridge room. Kill the imp behind the door. Enter the loot room.\n8. Go straight the loot room and open the next door. Enter the switch room.\n9. Inside the switch room there is a switch on the right wall. Hit the switch after getting the items, if you need them."#, then return to the bigger room.Head back up the stairs, toward the beginning, then run into that opening and onto the ledge that dropped. When it rises, get the bonuses in the winding hallway. When you've had your fill, return to the "exit" room, and enter the exit door. 


def build_vision_prompt(image_path):
    """
    Vision prompt. It uses this weird Chat-like API so we need to adapt to it.

    Parameters:
        image_path (str): a path to the image file. Pass in debug for testing.
    """
    image_prompt = "This a screenshot from DOOM. Give me a description of the screenshot showing what you see, and what is in the HUD, in that order."
    # If there are enemies or objects, indicate their position on the screen (left, right, or centre), but ONLY if there are any."
    if image_path == "debug":
        return {"messages": [{"role": "user", "content": ["test"]}]}
    encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
    return {"messages": [
        {"role": "user",
          "content": [{"image": encoded_image}, image_prompt],
        }],}

# Shared prompt components
AVAILABLE_ACTIONS = "# Available actions:\n- UP: move forward\n- DOWN: move backwards\n- LEFT: turn left\n- RIGHT: turn right\n- STRAFE LEFT: strafe left\n- STRAFE RIGHT: strafe right\n- FIRE: fire your equipped weapon\n- USE: use the item\n- WAIT: wait for one second\n- SPEED: move faster or slower\n- 1: select weapon 1 (if available)\n- 2: select weapon 2 (if available)\n- 3: select weapon 3 (if available)\n- 4: select weapon 4 (if available)\n- 5: select weapon 5 (if available)\n- 6: select weapon 6 (if available)\n- 7: select weapon 7 (if available)\n"
ADDITIONAL_INSTRUCTIONS = "Also:\n- If the History shows that you have too many WAITs, UPs, DOWNs, LEFTs, or RIGHTs, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item or door, and USE it.\n- If your health starts to decrease, you are taking damage! Align your weapon with the enemy and shoot it. If you can't see them, they are behind you! Turn around! (LEFT, LEFT or RIGHT, RIGHT)\n- Make sure to avoid walking on acid!\n- You cannot jump or go through windows.\n"


def get_plan_prompt(state, history, walkthrough=WALTHROUGH_E1_M1):
    """
    Plan prompt for hierarchical planning.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): The level walkthrough, defaulting to E1M1
    """
    prompt = "# Instructions:\nYou are a planning bot instructiong a player how to play Doom (1993).\n"
    prompt += "Your job is to figure out a plan to get the player to traverse the level, kill enemies, ensure they have ammo and health.\n"
    prompt += "You have access to a Walkthrough, the History of what was seen before, and the current State (i.e., what the player can see now).\n"
    prompt += "Also:\n"
    prompt += "- The player cannot walk on acid!\n"
    prompt += "- The player cannot jump or go through windows.\n"
    prompt += "- The player might be stuck, then you need to help them get unstuck.\n"
    prompt += "- The player might not have output the right |step|. You have to determine that yourself.\n"
    prompt += AVAILABLE_ACTIONS

    prompt += "Answer the following:\n"
    prompt += "- Where am I, respective to the Walkthrough?\n"
    prompt += "- What actions should I do to finish the step, or go to the next step of the Walkthrough?\n"
    prompt += "- Also output an explanation why."
    prompt += "Give only one possible answer, in the format:\n"
    prompt += "Answer:\n- You are in step X of the walkthrough\n- You now need to...\n" 

    prompt += "For example:\n"
    prompt += "# Waltkthrough\n1. You start in the gore room. Interact with the switch in the wall to take the elevator up.\n2Enter the canyon room and kill both imps. Head to the left exit.\n2. Take the left exit to the acid pool room, where you will fight another zombie.\n"
    prompt += "|Begin History|\nState:\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n|Action| STRAFE RIGHT\n|step| 1\n|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\nState:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n|Action| STRAFE LEFT\n|step| 1\n|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n|End History|\n"
    prompt += "# State\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "Answer:\n"
    prompt += "- You are in step 2 of the walkthrough, in the canyon room.\n"
    prompt += "- You are fighting both imps. After killing them (FIRE) take the left exit (STRAFE LEFT, UP) towards the acid pool room.\n"
    prompt += "- The acid pool room is nearby, but you are taking damage and need to fight.\n\n"

    prompt += "Another example:\n"
    prompt += "# Walkthrough\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n"
    prompt += "|Begin History|\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\" in white, indicating that the player currently has no armor.\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\"\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\"\n|End History|\n"
    prompt += "# State\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\" in white, indicating that the player currently has no armor."
    prompt += "Answer:\n"
    prompt += "- You are in step 1, and appear to be stuck running against a wall.\n"
    prompt += "- Turn around (LEFT, LEFT, LEFT) or (RIGHT, RIGHT, RIGHT) and take another path.\n"
    prompt += "- The player has been running against a wall for a while.\n\n"

    def process_history(hist):
        _hist = []
        for h in hist.split("\n"):
            if "|Action|" in h or "|Step|" in h or "|Explanation|" in h:
                continue
            _hist.append(h)
        return "\n".join(_hist)
    
    prompt += "Player input begins:\n\n"
    prompt += "# Walkthrough:\n"
    prompt += walkthrough.strip() + "\n"
    prompt += "|Begin History|\n"
    prompt += process_history(history).strip() + "\n"
    prompt += "|End History|\n"
    prompt += "# State:\n"
    prompt += state.strip("\n\n") + "\n"
    prompt += "Answer:"
    return prompt


def play_prompt_naive(state, history, plan=None):
    """
    Naive prompt that also supports planning (not used).

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
    """

    prompt = "# Instructions:\nYou are a videogame playing bot. You are playing 1993 DOOM.\n"
    prompt += "Your job is to play the game: traverse the level, kill enemies, ensure you have ammo and health.\n"
    if plan is None:
        prompt += "Every turn, take ONE action based on the state given; and the history of what you did before.\n"
    else:
        prompt += "Every turn, take ONE action based on the state given; the plan of what to do next, and the history of what you did before.\n"

    prompt += AVAILABLE_ACTIONS
    prompt += "# Additionally:\n"
    if plan is None:
        prompt += "- If the History shows that you haven't left the room, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item to collect them. Walk UP to doors, and USE it to open it.\n"
        prompt += "- If the History shows that you have too many WAITs, UPs, DOWNs, LEFTs, or RIGHTs, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item or door, and USE it.\n"
    else:
        prompt += "- Stick to the Plan.\n" 
    prompt += "\n".join(ADDITIONAL_INSTRUCTIONS.split("\n")[2:]).strip() + "\n"
    prompt += "- If your HUD says that your health is 0%, output GAME OVER instead, but only if that is the case\n"
    prompt += "- The player means YOU.\n\n"

    prompt += "# Examples:\n"
    prompt += "|History|\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| UP\n"
    prompt += "|Explanation| There is a bifurcation ahead, so the path is forward. I move closer.\n\n"    
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| UP\n"
    prompt += "|Explanation| There is a bifurcation ahead, so the path is forward. I need to get closer to the bifurcation.\n\n"    
    prompt += "State:\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| LEFT\n"
    prompt += "|Explanation| I will take the bridge, so I turn left.\n\n"       

    prompt += "Another example:\n"
    prompt += "|History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| STRAFE RIGHT\n"
    prompt += "|Explanation| I'm taking damage, I must dodge!\n\n"    
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| STRAFE LEFT\n"
    prompt += "|Explanation| I need to aim to the enemy.\n\n"

    prompt += "Another example:\n"
    prompt += "|History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| UP\n"
    prompt += "|Explanation| I will explore this room\n\n"    
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n"
    if plan is not None:
        prompt += "|Plan|\n\n"
    prompt += "|Action| RIGHT\n"
    prompt += "|Explanation| I seem to be stuck, this is the same as before. I also am taking damage. I will turn around\n\n"

    # This one should fix the issue around the model refusing to die, but might introduce false positives
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    prompt += "Play begins here!\n"
    prompt += "|History|\n"
    prompt += history.strip() + "\n\n"
    prompt += "State:\n"
    prompt += state.strip() + "\n"
    if plan is not None:
        prompt += "|Plan|\n{}\n".format(plan.strip())
    prompt += "|Action|"

    return prompt

def play_prompt_with_plan(state, history, walkthrough=WALTHROUGH_E1_M1, plan=""):
    """
    Naive prompt with walkthrough and plan enabled. Currently just a fork of walkthrough.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
        plan (str): A plan generated by the planner
    """
    prompt = "# Instructions:\nYou are a videogame playing bot. You are playing 1993 DOOM.\n"
    prompt += "Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.\n"
    prompt += ADDITIONAL_INSTRUCTIONS
    prompt += "- Prioritise fighting enemies over the walkthrough.\n"
    prompt += "- Output the current |step| number of the walkthrough you are in.\n"
    prompt += "- Follow the |plan| to finish the walkthrough\n"
    prompt += "- The player means YOU\n\n"
    prompt += AVAILABLE_ACTIONS
    
    prompt += "# Examples:\n"
    prompt += "|Walkthrough|\n1. Once you have passed the computer room, you will find a room with two exits.\n2. Take the left exit to the bridge.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room. Now I need to approach the exits. The walkthrough says to take the left exit.\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room, and now I need to get closer to the exits. The walkthrough says to take the left exit. I have finished 1.\n"
    prompt += "|End History|\n"
    prompt += "State:\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| LEFT\n"
    prompt += "|step| 2\n"
    prompt += "|Explanation| I have finished step 1. The walkthrough in step 2 says to take the bridge, so I turn left.\n\n"       

    prompt += "Another example:\n"
    prompt += "|Walkthrough|\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n"
    prompt += "|Action| STRAFE RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\n"    
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Action| STRAFE LEFT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n\n"
    prompt += "|End History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Action| FIRE\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I have aimed at the enemy. I fire my gun.\n\n"

    prompt += "Another example:\n"
    prompt += "|Walkthrough|\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I will explore this room to find the items the walkthrough suggested.\n"    
    prompt += "|End History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n"
    prompt += "|plan| "
    prompt += "|Action| RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I seem to be stuck, this is the same as before. I also am taking damage and can't see the switch. I will turn around and seek out the items.\n\n"

    # This one should fix the issue around the model refusing to die, but introduced false positives    
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    prompt += "The level begins...\n"
    prompt += "|Begin History|\n"
    prompt += history.strip() + "\n"
    prompt += "|End History|\n"
    prompt += "|Walkthrough|\n"
    prompt += walkthrough.strip() + "\n"
    prompt += "|Plan|\n"
    prompt + plan.strip() + "\n"
    prompt += "State:\n"
    prompt += state.strip() + "\n"
    prompt += "|Action|"
    return prompt

def play_prompt_with_klevels(state, history, klevels, plan=None, walkthrough=WALTHROUGH_E1_M1):
    """
    Naive prompt with walkthrough, planning, and k-levels enabled.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        klevels (List[str]): The klevels predictions, formatted as ACTION because EXPLANATION.
        plan (str, None): Candidate plan
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
    """
    prompt = "# Instructions:\nYou are a videogame playing bot. You are playing 1993 DOOM.\n"
    prompt += "Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.\n"
    prompt += ADDITIONAL_INSTRUCTIONS
    prompt += "- Prioritise fighting enemies over the walkthrough.\n"
    prompt += "- Output the current |step| number of the walkthrough you are in.\n"
    prompt += "- Follow the |plan| to finish the walkthrough\n"
    prompt += "- The player means YOU\n\n"
    prompt += AVAILABLE_ACTIONS
    
    prompt += "# Examples:\n"
    prompt += "|Walkthrough|\n1. Once you have passed the computer room, you will find a room with two exits.\n2. Take the left exit to the bridge.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Experts|\nP1 picked UP because the room bifurcates ahead; P2 picked LEFT because the bridge is to the left; P3 picked UP because we need to move forward.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room. Now I need to approach the exits. The walkthrough says to take the left exit.\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Experts|\nP1 picked UP because we need to get closer to the bridge; P2 picked UP because we need to go towards the exit; P3 picked LEFT because the bridge is to the left.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room, and now I need to get closer to the exits. The walkthrough says to take the left exit. I have finished 1.\n"
    prompt += "|End History|\n"
    prompt += "State:\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Experts|\nP1 UP because the bridge is up ahead; P2 picked RIGHT because we need to go to the bridge; P3 UP because we need to get closer to the bridge.\n"
    prompt += "|Action| LEFT\n"
    prompt += "|step| 2\n"
    prompt += "|Explanation| I have finished step 1. The walkthrough in step 2 says to take the bridge, so I turn left.\n\n"       

    prompt += "Another example:\n"
    prompt += "|Walkthrough|\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n"
    prompt += "|Experts|\nP1 picked UP because we need to get closer to shoot; P2 picked RIGHT to avoid the explosion; P3 picked STRAFE RIGHT to dodge the bullets.\n"
    prompt += "|Action| STRAFE RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\n"    
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Experts|\nP1 picked STRAFE RIGHT to dodge the bullets; P2 picked STRAFE LEFT to aim to the demonic creature; P3 picked STRAFE LEFT to shoot the creature.\n"
    prompt += "|Action| STRAFE LEFT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n\n"
    prompt += "|End History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Experts|\nP1 picked STRAFE RIGHT to dodge the bullets; P2 picked FIRE to shoot the demon; P3 picked FIRE to fight the creature.\n"
    prompt += "|Action| FIRE\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I have aimed at the enemy. I fire my gun.\n\n"

    prompt += "Another example:\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n"
    prompt += "|Experts|\nP1 picked RIGHT to rotate; P2 picked UP to enter the room; P3 picked UP to enter the room.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I will explore this room to find the items the walkthrough suggested.\n"    
    prompt += "|End History|\n"
    prompt += "|Walkthrough| 1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n"    
    prompt += "|plan| "
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n"
    prompt += "|Experts|\nP1 picked RIGHT to rotate; P2 picked RIGHT to get unstuck; P3 picked UP to continue forward.\n"
    prompt += "|Action| RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I seem to be stuck, this is the same as before. I also am taking damage and can't see the switch. I will turn around and seek out the items.\n\n"

    # This one should fix the issue around the model refusing to die, but might introduce false positives    
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n
    def format_experts(klevels):
        _hist = ""
        for i, h in enumerate(klevels):
            _hist += f"P{i + 1} picked {h}; "
        return _hist[:-2]

    prompt += "The level begins...\n"
    prompt += "|Begin History|\n"
    prompt += history.strip() + "\n"
    prompt += "|End History|\n"
    prompt += "|Walkthrough|\n"
    prompt += walkthrough.strip() + "\n"
    prompt += "|Plan|\n"
    prompt + plan.strip() + "\n"
    prompt += "State:\n"
    prompt += state.strip() + "\n"
    prompt += "|Experts|\n"
    prompt += format_experts(klevels) + "\n"
    prompt += "|Action|"
    return prompt


def play_prompt_with_walkthrough(state, history, walkthrough=WALTHROUGH_E1_M1):
    """
    Naive prompt with walkthrough enabled.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
    """
    
    prompt = "# Instructions:\nYou are a videogame playing bot. You are playing 1993 DOOM.\n"
    prompt += "Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.\n"
    prompt += ADDITIONAL_INSTRUCTIONS
    prompt += "- Prioritise fighting enemies over the walkthrough.\n"
    prompt += "- Output the current |step| number of the walkthrough you are in.\n"
    prompt += "- The player means YOU\n\n"
    prompt += AVAILABLE_ACTIONS
    
    prompt += "# Examples:\n"
    prompt += "|Walkthrough|\n1. Once you have passed the computer room, you will find a room with two exits.\n2. Take the left exit to the bridge.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room. Now I need to approach the exits. The walkthrough says to take the left exit.\n"
    prompt += "State:\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I've passed the computer room, and now I need to get closer to the exits. The walkthrough says to take the left exit. I have finished 1.\n"
    prompt += "|End History|\n"
    prompt += "State:\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n"
    prompt += "|Action| LEFT\n"
    prompt += "|step| 2\n"
    prompt += "|Explanation| I have finished step 1. The walkthrough in step 2 says to take the bridge, so I turn left.\n\n"       

    prompt += "Another example:\n"
    prompt += "|Walkthrough|\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n"
    prompt += "|Action| STRAFE RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\n"    
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Action| STRAFE LEFT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n\n"
    prompt += "|End History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n"
    prompt += "|Action| FIRE\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I have aimed at the enemy. I fire my gun.\n\n"

    prompt += "Another example:\n"
    prompt += "|Walkthrough| 1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n"
    prompt += "|Begin History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n"
    prompt += "|Action| UP\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I will explore this room to find the items the walkthrough suggested.\n"    
    prompt += "|End History|\n"
    prompt += "State:\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n"
    prompt += "|Action| RIGHT\n"
    prompt += "|step| 1\n"
    prompt += "|Explanation| I seem to be stuck, this is the same as before. I also am taking damage and can't see the switch. I will turn around and seek out the items.\n\n"

    # This one should fix the issue around the model refusing to die, but introduced false positives    
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    prompt += "The level begins...\n"
    prompt += "|Walkthrough|\n"
    prompt += walkthrough.strip() + "\n"
    prompt += "|Begin History|\n"
    prompt += history.strip() + "\n"
    prompt += "|End History|\n"
    prompt += "State:\n"
    prompt += state.strip() + "\n"
    prompt += "|Action|"
    return prompt
