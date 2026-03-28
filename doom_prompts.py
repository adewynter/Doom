import base64


WALTHROUGH_E1_M1 = """1. You start out the game in a room with a blue pool.
2. Go across the pool.
3. Keep going straight into the hallway.
4.Go straight down the hall, and open the door. Enter the computer room.
5. Kill the two guys there. Go around the room with blue walls, and to the back right of the computer room, where there is an entrance to the bridge room (if you face the grey door, you need to turn around).
6. Make a right, kill the two guys, and cross the bridge. Don't fall into the green acid pool.
7. Go straight and open the door at the end of the bridge room. Kill the imp behind the door. Enter the loot room.
8. Go straight the loot room and open the next door. Enter the switch room.
9. Inside the switch room there is a switch on the right wall. Hit the switch after getting the items, if you need them.""" #, then return to the bigger room.Head back up the stairs, toward the beginning, then run into that opening and onto the ledge that dropped. When it rises, get the bonuses in the winding hallway. When you've had your fill, return to the "exit" room, and enter the exit door."""


def build_vision_prompt(image_path, is_phi: bool=False):
    """
    Vision prompt. 
    Parameters:
        image_path (str): a path to the image file. Pass in debug for testing.
        is_phi: Phi-4 is weird on how it handles requests. So, we'll do an interrupt. Ok, it might be the same, but tbh I'm so lost on the 38 offerings.
    """
    image_prompt = """This a screenshot from DOOM. Give me a description of the screenshot showing what you see, and what is in the HUD, in that order.
If there are enemies or objects, indicate their position on the screen (left, right, or centre), but ONLY if there are any.
Your response should be in JSON:
{{
    "Description": <the description>
}}    
"""
    if image_path == "debug":
        return {"messages": [{"role": "user", "content": ["test"]}]}
    encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
    usr_content = [{"type": "text", "text": image_prompt},
                   {"type": "image_url", "image_url": f"data:image/png;base64,{encoded_image}"}, 
                  ]

    if is_phi:
        usr_content = [{"type": "text", "text": image_prompt},
                       {"type": "image_url",  
                        "image_url": {"url": f"data:image/png;base64,{encoded_image}"}
                        }, 
                      ]

    return [{"role": "user", "content": usr_content}]


# Shared prompt components
AVAILABLE_ACTIONS = """# Available actions:
- UP: move forward
- DOWN: move backwards
- LEFT: turn left
- RIGHT: turn right
- STRAFE LEFT: strafe left
- STRAFE RIGHT: strafe right
- FIRE: fire your equipped weapon
- USE: use the item
- WAIT: wait for one second
- SPEED: move faster or slower
- 1: select weapon 1 (if available)
- 2: select weapon 2 (if available)
- 3: select weapon 3 (if available)
- 4: select weapon 4 (if available)
- 5: select weapon 5 (if available)
- 6: select weapon 6 (if available)
- 7: select weapon 7 (if available)"""

ADDITIONAL_INSTRUCTIONS = """Also:
- If the History shows that you have too many WAITs, UPs, DOWNs, LEFTs, or RIGHTs, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item or door, and USE it.
- If your health starts to decrease, you are taking damage! Align your weapon with the enemy and shoot it. If you can't see them, they are behind you! Turn around! (LEFT, LEFT or RIGHT, RIGHT)
- Make sure to avoid walking on acid!
- You cannot jump or go through windows."""

OUTPUT_FORMAT = """
Give your answer in JSON format as follows:
{{
    "Action": the action you'll take,
    "Step": the step _number_ from the walkthrough,
    "Explanation": a short, one-sentence explanation as to why
}}
Only use the keys "Action" (values from the list), "Step", and "Explanation".
"""


def get_plan_prompt(state: str, history: str, walkthrough: str=WALTHROUGH_E1_M1, add_examples=False):
    """
    Plan prompt for hierarchical planning.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): The level walkthrough, defaulting to E1M1
    """
    sys_prompt = """# Instructions:
You are a planning bot instructing a player how to play Doom (1993).
Your job is to figure out a plan to get the player to traverse the level, kill enemies, ensure they have ammo and health.
You have access to a Walkthrough, the History of what was seen before, and the current State (i.e., what the player can see now).
Also:
- The player cannot walk on acid!
- The player cannot jump or go through windows.
- The player might be stuck, then you need to help them get unstuck.
- The player might not have output the right |step|. You have to determine that yourself.
{actions}

Answer the following:
- Where am I, respective to the Walkthrough?
- What actions should I do to finish the step, or go to the next step of the Walkthrough?

Your answer must be in JSON, with the keys "Step" (saying "You are in step <X> of the walkthrough"), "Action" (saying "You now need to do <the action>"), "Explanation" (a short sentence why)
{{
    "Step": "You are in step X of the walkthrough",
    "Action": "You now need to <the action>",
    "Explanation": a short one-sentence why.
}}

Only use the keys "Step", "Explanation", and "Action".
{examples}
"""

    examples = ""
    if add_examples:
        examples = """
For example:
<walkthrough>\n1. You start in the gore room. Interact with the switch in the wall to take the elevator up.\n2Enter the canyon room and kill both imps. Head to the left exit.\n2. Take the left exit to the acid pool room, where you will fight another zombie.\n</walkthrough>
<history>\n<state>\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n|Action| STRAFE RIGHT\n|step| 1\n|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\n<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n|Action| STRAFE LEFT\n|step| 1\n|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n</history></state>
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n</state></state>
Your response should be something like:
{{
    "Step": You are in step 2 of the walkthrough, in the canyon room,
    "Action": You are fighting both imps. After killing them (FIRE) take the left exit (STRAFE LEFT, UP) towards the acid pool room.
}}

Another example:
<walkthrough>\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n</walkthrough>
<history>\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\" in white, indicating that the player currently has no armor.\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\"\nState\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\"\n</history>
<state>\nIn the screenshot, we see a first-person view of a player holding a pistol in the center of the screen. The background appears to be a textured wall with vertical stripes in shades of brown, indicating an indoor or dungeon-like environment typical of the game's levels.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows various pieces of information:\n\n- On the left, there is a number \"47\" in white, which represents the current ammo count for the weapon in use.\n- Next to the ammo count, there is a red bar with \"100%\" in white, indicating the player's health level.\n- To the right of the health bar, there are small icons representing different weapons, with numbers next to them. These numbers show the ammo count for each respective weapon. In this case, the numbers are \"2\" for the shotgun, \"0\" for the chaingun, \"0\" for the rocket launcher, \"0\" for the plasma gun, and \"0\" for the BFG 9000.\n- On the far right, there is a blue bar with \"0%\" in white, indicating that the player currently has no armour\n</state></state>
Your response should be something like:
{{
    "Step": You are in step 1, and appear to be stuck running against a wall.
    "Action": Turn around (LEFT, LEFT, LEFT) or (RIGHT, RIGHT, RIGHT) and take another path.
}}
"""


    this_sys_prompt = sys_prompt.format(actions=AVAILABLE_ACTIONS, examples=examples)

    def process_history(hist):
        _hist = []
        for h in hist.split("\n"):
            if "|Action|" in h or "|Step|" in h or "|Explanation|" in h:
                continue
            _hist.append(h)
        return "\n".join(_hist)

    user_prompt = f"<history>\n{process_history(history).strip()}\n</history>"
    user_prompt += f"<walkthrough>\n{walkthrough.strip()}\n</walkthrough>\n"
    user_prompt += f"<state>\n{state.strip()}\n</state>\n"
    
    return [{"role": "system", "content": this_sys_prompt}, {"role": "user", "content": user_prompt}]


def play_prompt_naive(state: str, history: str, plan: str=None, add_examples: bool=False):
    """
    Naive prompt that also supports planning (not used because it doesn't support examples).

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
    """
    sys_prompt_no_plan = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to play the game: traverse the level, kill enemies, ensure you have ammo and health.
Every turn, take ONE action based on the state given; and the history of what you did before.
{available_actions}
# Additionally:
- If the History shows that you haven't left the room, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item to collect them. Walk UP to doors, and USE it to open it.
- If the History shows that you have too many WAITs, UPs, DOWNs, LEFTs, or RIGHTs, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item or door, and USE it.
{additional_instructions}
- If your HUD says that your health is 0%, output GAME OVER instead, but only if that is the case
- The player means YOU.

Return your output in JSON as follows:
{{
    "Action": <the action>
}}
Only use the key "Action" and the values from the list.

{examples}
"""

    sys_prompt_plan = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to play the game: traverse the level, kill enemies, ensure you have ammo and health.
Every turn, take ONE action based on the state given; the plan of what to do next, and the history of what you did before.
{available_actions}
# Additionally:
- Stick to the Plan.
{additional_instructions}
- If your HUD says that your health is 0%, output GAME OVER instead, but only if that is the case
- The player means YOU.

Return your output in JSON as follows:
{{
    "Action": <the action>
}}
Only use the key "Action" and the values from the list.
"""


    sys_prompt_no_plan_examples = """
# Examples:
<history>
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Action| UP
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Action| UP
</history>
<state>\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
Your output should be something like:
{{
    "Action": "LEFT"
}}


Another example:
<history>
<state>\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n</state>
|Action| STRAFE RIGHT
</history>
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.</state>
Your output should be something like:
{{
    "Action": "STRAFE LEFT"
}}


Another example:
<history>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n</state>
|Action| UP
</history>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n</state>
Your output should be something like:
{{
    "Action": "RIGHT"
}}

"""
    # This one should fix the issue around the model refusing to die, but might introduce false positives
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    if plan is None:
        examples = sys_prompt_no_plan_examples
        this_sys_prompt = sys_prompt_no_plan.format(available_actions=AVAILABLE_ACTIONS, 
                                                    additional_instructions="\n".join(ADDITIONAL_INSTRUCTIONS.split("\n")[2:]).strip() + "\n",
                                                    examples=examples)
    else:
        this_sys_prompt = sys_prompt_plan.format(available_actions=AVAILABLE_ACTIONS, 
                                                additional_instructions="\n".join(ADDITIONAL_INSTRUCTIONS.split("\n")[2:]).strip() + "\n",
                                                )

    user_prompt = f"<history>\n{history.strip()}\n</history>"
    if plan is not None: user_prompt += f"<plan>\n{plan.strip()}\n</plan>\n"
    user_prompt += f"<state>\n{state.strip()}\n</state>\n"

    return [{"role": "system", "content": this_sys_prompt}, {"role": "user", "content": user_prompt}]


def play_prompt_with_plan(state, history, walkthrough=WALTHROUGH_E1_M1, plan=None, add_examples=False):
    """
    Naive prompt with walkthrough and plan enabled. Currently just a fork of walkthrough.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
        plan (str): A plan generated by the planner
    """
    sys_prompt = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.
{additional_instructions}
- Prioritise fighting enemies over the walkthrough.
- Output the current |step| number of the walkthrough you are in.
- Follow the |plan| to finish the walkthrough
- The player means YOU
{available_actions}

{output_format}
{examples}
"""

    examples = ""
    if add_examples:
        examples = """
# Examples:
<walkthrough>
1. Once you have passed the computer room, you will find a room with two exits.
2. Take the left exit to the bridge.
</walkthrough>
<history>
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Action| UP
|step| 1
}}
</history>
<state>\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
Your output should be something like:
{{
    "Action": LEFT
    "step": 2
}}

Another example:
<walkthrough>\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n</walkthrough>
<history>
<state>\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.</state>
|Action| STRAFE RIGHT
|step| 1
|Explanation| I took the elevator. I'm taking damage. It must be the imps. I must dodge!\n" 
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.</state>
|Action| STRAFE LEFT
|step| 1
|Explanation| I took the elevator. I need to aim at the enemy and kill it. The enemy is to the left, so I strafe left.\n
</history>
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.</state>
Your output should be something like:
{{
    "Action": FIRE
    "step": 1
}}

Another example:
<walkthrough>\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n</walkthrough>
<history>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.</state>
|Action| UP
|step| 1
</history>
<state>
In the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.
Your output should be something like:
{{
    "Action": RIGHT
    "step": 1
}}
"""

    this_sys_prompt = sys_prompt.format(additional_instructions=ADDITIONAL_INSTRUCTIONS,
                                        available_actions=AVAILABLE_ACTIONS, 
                                        examples=examples,
                                        output_format=OUTPUT_FORMAT)

    # This one should fix the issue around the model refusing to die, but introduced false positives    
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    user_prompt = f"<history>\n{history.strip()}\n</history>"
    user_prompt += f"<walkthrough>\n{walkthrough.strip()}\n</walkthrough>\n"
    if plan is not None: user_prompt += f"<plan>\n{plan.strip()}\n</plan>\n"
    user_prompt += f"<state>\n{state.strip()}\n</state>"

    return [{"role": "system", "content": this_sys_prompt}, {"role": "user", "content": user_prompt}]


def play_prompt_with_klevels(state: str, history: str, klevels: list, plan: str=None, walkthrough: str=WALTHROUGH_E1_M1, add_examples: bool=False) -> list:
    """
    Naive prompt with walkthrough, planning, and k-levels enabled.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        klevels (List[str]): The klevels predictions, formatted as ACTION because EXPLANATION.
        plan (str, None): Candidate plan
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
    """

    sys_prompt = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.
{additional_instructions}
- Prioritise fighting enemies over the walkthrough.
- Output the current |step| number of the walkthrough you are in.
- Follow the |plan| to finish the walkthrough
- The player means YOU
{available_actions}

{output_format}

{examples}
"""
    
    examples = ""
    if add_examples:
        examples = """
# Examples:
<walkthrough>\n1. Once you have passed the computer room, you will find a room with two exits.\n2. Take the left exit to the bridge.\n</walkthrough>
<history>
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Experts|\nP1 picked UP because the room bifurcates ahead; P2 picked LEFT because the bridge is to the left; P3 picked UP because we need to move forward.\n
|Action| UP
|step| 1
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.</state>
|Experts|\nP1 picked UP because we need to get closer to the bridge; P2 picked UP because we need to go towards the exit; P3 picked LEFT because the bridge is to the left.
|Action| UP
|step| 1
</history>
<state>\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
<experts>\nP1 UP because the bridge is up ahead; P2 picked RIGHT because we need to go to the bridge; P3 UP because we need to get closer to the bridge.\n</experts>
Your output should be something like:
{{
    "Action": LEFT
    "step": 2
}}


Another example:
<walkthrough>\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n</walkthrough>
<history>
<state>\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n</state>
|Experts|\nP1 picked UP because we need to get closer to shoot; P2 picked RIGHT to avoid the explosion; P3 picked STRAFE RIGHT to dodge the bullets.
|Action| STRAFE RIGHT
|step| 1
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n</state>
|Experts|\nP1 picked STRAFE RIGHT to dodge the bullets; P2 picked STRAFE LEFT to aim to the demonic creature; P3 picked STRAFE LEFT to shoot the creature.
|Action| STRAFE LEFT
|step| 1
</history>
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n</state>
<experts>\nP1 picked STRAFE RIGHT to dodge the bullets; P2 picked FIRE to shoot the demon; P3 picked FIRE to fight the creature.\n</experts>
Your output should be something like:
{{
    "Action": FIRE
    "step": 1
}}

Another example:
<history>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n</state>
|Experts|\nP1 picked RIGHT to rotate; P2 picked UP to enter the room; P3 picked UP to enter the room.
|Action| UP
|step| 1
</history>
<walkthrough>\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.</walkthrough>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.\n"</state>
<experts>\nP1 picked RIGHT to rotate; P2 picked RIGHT to get unstuck; P3 picked UP to continue forward.\n</experts>
Your output should be something like:
{{
    "Action": RIGHT
    "step": 1
}}
"""
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
    
    this_sys_prompt = sys_prompt.format(additional_instructions=ADDITIONAL_INSTRUCTIONS,
                                        available_actions=AVAILABLE_ACTIONS,
                                        output_format=OUTPUT_FORMAT,
                                        examples=examples)

    user_prompt = f"<history>\n{history.strip()}\n</history>"
    user_prompt += f"<walkthrough>\n{walkthrough.strip()}\n</walkthrough>\n"
    if plan is not None: user_prompt += f"<plan>\n{plan.strip()}\n</plan>\n"
    user_prompt += f"<state>\n{state.strip()}\n</state>\n"
    user_prompt += f"<experts>\n{format_experts(klevels)}</experts>"

    return [{"role": "system", "content": this_sys_prompt}, {"role": "user", "content": user_prompt}]



def play_prompt_with_walkthrough(state: str, history: str, walkthrough: str=WALTHROUGH_E1_M1, add_examples: bool=False) -> list:
    """
    Naive prompt with walkthrough enabled.

    Parameters:
        state (str): Current description of the game (i.e., Vision output)
        history (str): Concatenated history of the game so far
        walkthrough (str): Full walkthrough of the level. Defaults to E1M1
    """
    
    sys_prompt = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to, given a Walkthrough and a |state| plan what to do next: determine how to traverse the level, kill demons, ensure you have ammo and health.
{additional_instructions}
- Prioritise fighting enemies over the walkthrough.
- Output the current |step| number of the walkthrough you are in.
- The player means YOU

{available_actions}

{output_format}

{examples}
"""

    examples = ""
    if add_examples:
        examples = """
# Examples:
<walkthrough>\n1. Once you have passed the computer room, you will find a room with two exits.\n2. Take the left exit to the bridge.\n</walkthrough>
<history>
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Action| UP
|step| 1
<state>\nYou are in a dimly lit room that bifurcates ahead. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
|Action| UP
|step| 1
</history>
<state>\nYou are facing two hallways. To the left there is a bridge with pools of acid, to the right a stair leading down.\n</state>
Your output should be something like:
{{
    "Action": LEFT
    "step": 2
}}

Another example:
<walkthrough>\n1.Take the elevator up, and kill both imps.\n2. take the second exit towards the canyon, where you will fight another zombie.\n</walkthrough>
<history>
<state>\nIn the screenshot, we see a first-person view of a red-tinted environment, suggesting that the player character is taking damage or is at critically low health. The surroundings appear to be a rocky, outdoor landscape with jagged terrain and a sky that matches the red hue of the scene. There is a large explosion or burst of energy in the center of the screen, which could be the result of a weapon's impact or an enemy attack. The player is holding a pistol, which is visible in the lower center of the screen.\n\nThe Heads-Up Display (HUD) at the bottom of the screen shows various pieces of information:\n\n- On the left side, there is an ammo counter indicating that the player has 47 bullets remaining for the currently equipped weapon.\n- In the center, there are three numerical values: the first, labeled \"HEALTH,\" shows that the player has 7% health remaining, indicating a critical state. The second, labeled \"ARMS,\" is not visible in the screenshot. The third, labeled \"ARMOR,\" shows that the player has 0% armor, meaning they have no damage protection.\n- On the right side, there is an inventory of ammunition types and their respective counts: \"BULL\" (bullets) with 47 available, \"SHEL\" (shells) with 0, \"ROCK\" (rockets) with 0, and \"CELL\" (energy cells) with 200.\n</state>
|Action| STRAFE RIGHT
|step| 1
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in the distance, standing on the left side of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.\n</state>
|Action| STRAFE LEFT
|step| 1
</history>
<state>\nIn the screenshot, we see a first-person view of a barren, red landscape with rocky terrain and a dark sky. There is a large demonic creature in center of the screen. In the center, there is a pentagram-like symbol drawn on the ground with what appears to be blood.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information:\n- Ammo: 47\n- Health: 7%\n- Armor: 0%\n- Arms: A small graphic indicating the currently equipped weapon, which looks like a pistol.\n- Ammo counts for different weapon types: BUL (Bullets) - 47, SHEL (Shells) - 0, ROCK (Rockets) - 0, CELL (Cells for energy weapons) - 0\n- A face in the center of the HUD that represents the player's character, which appears to be bloodied and grimacing, indicating low health.</state>
Your output should be something like:
{{
    "Action": FIRE
    "step": 1
}}

Another example:
<walkthrough>\n1. Enter the control room and collect all the items.\n2. Seek the switch on the left wall and exit.\n</walkthrough>
<history>\n
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 9%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 3% armor remaining.\n</state>
|Action| UP
|step| 1
</history>
<state>\nIn the screenshot, we see a first-person view of a room with a futuristic design. The walls are adorned with panels that have various lights and screens, some displaying green digital patterns. The floor and ceiling have a simple, flat texture, giving the room a clean, industrial look. The room is well-lit, with the light source seemingly coming from the bright white panels on the walls.\nThe Heads-Up Display (HUD) at the bottom of the screen shows several pieces of information:\n- On the left, there is an \"AMMO\" section with numbers indicating the amount of ammunition for different weapon types.\n- In the center, there is a \"HEALTH\" section displaying a percentage of the player's current health, which is at 5%.\n- To the right of the health, there is an \"ARMOR\" section, showing that the player has 0% armor remaining.</state>
Your output should be something like:
{{
    "Action": RIGHT
    "step": 1
}}
"""

    # This one should fix the issue around the model refusing to die, but introduced false positives    
    #prompt += "Another example:\n"
    #prompt += "State\n:"
    #prompt += "In the screenshot, we see a first-person view of the player facing a large, brown, muscular demon with horns and red eyes. The demon appears to be charging towards the player. In the background, there are rocky, red mountains and a dark sky, giving the impression of a hellish landscape.\n\nThe HUD (Heads-Up Display) at the bottom of the screen shows the following information from left to right:\n- Ammo: 46\n- Health: 0%\n- Arms: A graphic indicating the currently selected weapon, which is not clearly visible.\n- Armor: 0%\n- Below the health and armor percentages, there is a graphic of the player character's face with a pained expression and blood on the forehead, indicating critical health status.\n- To the right, there are numerical counts for different types of ammo: BULL (Bullets) 46, SHEL (Shells) 50, ROCK (Rockets) 0, CELL (Cells) 200.\n"
    #prompt += "Action: GAME OVER\n"
    #prompt += |Explanation|: I have Health at 0%\n\n

    this_sys_prompt = sys_prompt.format(available_actions=AVAILABLE_ACTIONS, 
                                        additional_instructions=ADDITIONAL_INSTRUCTIONS,
                                        output_format=OUTPUT_FORMAT, 
                                        examples=examples)

    user_prompt = f"<history>\n{history.strip()}\n</history>"
    user_prompt += f"<walkthrough>\n{walkthrough.strip()}\n</walkthrough>\n"
    user_prompt += f"<state>\n{state.strip()}\n</state>\n"

    return [{"role": "system", "content": this_sys_prompt}, {"role": "user", "content": user_prompt}]


def get_unified_prompt(image_path: str, history: str, plan: str=None, is_phi: bool=False):
    """
    Unified vision-action prompt.

    Parameters:
        image_path (str): Path to the image
        history (str): Concatenated history of the game so far
        is_phi (bool): Phi requires a weird signature
    """
    sys_prompt_no_plan = """# Instructions:
You are a videogame playing bot. You are playing 1993 DOOM.
Your job is to play the game: traverse the level, kill enemies, ensure you have ammo and health.

You will get a screenshot from the game. 
First output a description of the screenshot showing what you see, and what is in the HUD, in that order.
If there are enemies or objects, indicate their position on the screen (left, right, or centre), but ONLY if there are any.

Then, based on that, take ONE action based on the state given; and the history of what you did before.
{available_actions}
# Additionally:
- If the History shows that you haven't left the room, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item to collect them. Walk UP to doors, and USE it to open it.
- If the History shows that you have too many WAITs, UPs, DOWNs, LEFTs, or RIGHTs, try exploring (UP/DOWN/LEFT/RIGHT), using items or doors. Walk UP to the item or door, and USE it.
{additional_instructions}
- If your HUD says that your health is 0%, output GAME OVER instead, but only if that is the case
- The player means YOU.

# Important note:

Return your output in JSON as follows:
{{
    "Description": <a short description of the room>,
    "Action": <only the action: UP, DOWN, FIRE, etc>
}}
Only use the keys "Description", "Action" and the values from the list. 
"""

    this_sys_prompt = sys_prompt_no_plan.format(available_actions=AVAILABLE_ACTIONS, 
                                                additional_instructions="\n".join(ADDITIONAL_INSTRUCTIONS.split("\n")[2:]).strip() + "\n"
                                                )


    user_prompt_str = f"<history>\n{history.strip()}\n</history>"
    if plan is not None: user_prompt_str += f"<plan>\n{plan.strip()}\n</plan>\n"

    encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
    usr_content = [{"type": "text", "text": user_prompt_str},
                   {"type": "image_url", "image_url": f"data:image/png;base64,{encoded_image}"}, 
                  ]

    if is_phi:
        usr_content = [{"type": "text", "text": user_prompt_str},
                       {"type": "image_url",  
                        "image_url": {"url": f"data:image/png;base64,{encoded_image}"}
                        }, 
                      ]

    return [{"role": "system", "content": this_sys_prompt}, 
            {"role": "user", "content": usr_content}]

