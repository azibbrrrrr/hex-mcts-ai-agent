"""This script runs a game of Hex.

Using this script, students can test their agents' performance. If
fewer than two agents are specified, the missing agents will be
replaced with the default agent. The first specified agent is Red,
the second specified agent is Blue. If the user wants to test
their agent as Blue against the default agent as Red, the order
can be switched.

Possible arguments:
* "agent=name;command" or "a=name;command" specifies one agent
with the given name, that can be run by the given command.
* "-verbose" or "-v" prints the progress of the game in real time.
Use this argument to visualise the match.
* "-print_protocol" or "-p" prints the protocol messages. It will
print all received messages, but only those sent to Red. Use
this argument to understand the protocol.
* "board_size=n" or "b=n" creates a custom square board of size
nxn. Use this argument in conjunction with "-p" for more human-
readable protocol messages.
* "-log" or "-l" saves the match to a csv file under src/logs.
It will record all moves and the end state of the game. Check
the documentation pdf for more details.
* "-switch" or "-s" will invert the order of agents playing. Use
this argument to quickly test your agent as Blue instead of Red.
"""
import shlex
import subprocess
from sys import argv, platform
from os.path import realpath, sep
import re

agent = []

def extract_agents(arguments):
    """Returns two lists with agents separated from other arguments.
    Ignores first argument because that is the name of the script.

    Any badly formatted agents will be printed and ignored.
    """

    agents = []
    other_args = []
    for argument in arguments:
        if ("a=" in argument or "-agent" in argument):
            try:
                name, cmd = argument.split("=")[1].split(";")
                agents.append(f'"{argument}"')
                agent.append(name)
            except Exception:
                print(f"Agent '{argument}' is not in correct format.")
        else:
            other_args.append(argument)
    return (agents, other_args[1:])


def get_main_cmd():
    """Checks the OS to specify python or python3 and creates a relative path
    command to src/main.py.
    """

    main_cmd = "python"
    if (platform != "win32"):
        main_cmd += "3"

    main_path = sep.join(realpath(__file__).split(sep)[:-1])
    main_path += f"{sep}src{sep}main.py"

    main_cmd += " " + main_path
    return main_cmd


def main():
    """Checks that at most two agents are specified and that they
    are unique, then runs the main script with the given args.
    """

    agents, arguments = extract_agents(argv)
    if (len(agents)) > 2:
        print("ERROR: Too many agents specified. Aborted.")
        return
    elif (len(agents) != len(set(agents))):
        print("ERROR: Agent strings must be unique. Aborted.")

    cmd = (
        get_main_cmd() + " " +
        " ".join(arguments) + " " +
        " ".join(agents)
    )
    if (platform != "win32"):
        cmd = shlex.split(cmd)
    
    wins_1stAgent = 0
    wins_2ndAgent = 0


    for i in range(10):

        turns_1stAgent = 0
        turns_2ndAgent = 0

        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        last_lines = result.stdout.strip().split('\n')[-4:]

        # Check which agent won
        if f'{agent[0]} has won' in last_lines[0]:
            wins_1stAgent += 1
        elif f'{agent[1]} has won' in last_lines[0]:
            wins_2ndAgent += 1

        turns = {agent[0]: 0, agent[1]: 0}

        for a, line in zip(agent, last_lines[2:4]):
            match = re.search(rf'{a} took (\d+) turns', line)
            if match:
                turns[a] += int(match.group(1))

        turns_1stAgent = turns[agent[0]]
        turns_2ndAgent = turns[agent[1]]

        # Write the game result to the file
        with open("game_results.txt", "a") as file:
            file.write(f"""Game {i+1}: {last_lines[0]}
        Total turns taken by {agent[0]}: {turns_1stAgent}
        Total turns taken by {agent[1]}: {turns_2ndAgent}""")

    with open("game_results.txt", "a") as file:
        file.write(f"""
    Total wins for {agent[0]}: {wins_1stAgent}
    Total wins for {agent[1]}: {wins_2ndAgent}
    """)



if __name__ == "__main__":
    main()