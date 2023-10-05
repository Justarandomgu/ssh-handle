import paramiko
import sys
import pyfiglet
import colorama
from colorama import Fore

class SSHSession:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = None
        self.current_directory = "~"  # Initialize the current directory to the home directory

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(self.host, self.port, self.username, self.password)
            print(f"Connected to {self.host}")
        except paramiko.AuthenticationException as auth_error:
            print(f"Authentication failed: {auth_error}")
        except paramiko.SSHException as ssh_error:
            print(f"SSH connection failed: {ssh_error}")
        except Exception as e:
            print(f"Error: {e}")

    def execute_command(self, command):
        if not self.ssh_client:
            print("Not connected to any SSH session. Please connect first.")
            return None

        if command.startswith("cd "):
            # Change the current directory locally
            new_directory = command[3:].strip()
            self.current_directory = new_directory
            return None

        try:
            # Add the current directory to the command
            full_command = f"cd {self.current_directory} && {command}"
            stdin, stdout, stderr = self.ssh_client.exec_command(full_command)
            return stdout.read().decode("utf-8")
        except Exception as e:
            print(f"Command execution failed: {e}")
            return None

    def close(self):
        if self.ssh_client:
            self.ssh_client.close()
            print(f"Connection to {self.host} closed")
        else:
            print("No active SSH session to close")

def main():
    # Print "SSH Handle" in ASCII art
    ascii_art = pyfiglet.figlet_format("SSH Handle")
    print(Fore.BLUE + ascii_art)
    print(Fore.GREEN)

    sessions = []

    while True:
        print("\nOptions:")
        print("1. Create a new SSH session")
        print("2. List active SSH sessions")
        print("3. Execute a command")
        print("4. Close an SSH session")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            host = input("Enter the SSH host: ")
            port = input("Enter the SSH port (default is 22): ") or "22"
            username = input("Enter the SSH username: ")
            password = input("Enter the SSH password: ")

            session = SSHSession(host, int(port), username, password)
            session.connect()
            sessions.append(session)

        elif choice == "2":
            print("Active SSH Sessions:")
            for idx, session in enumerate(sessions):
                print(f"{idx + 1}. {session.host}:{session.port} ({session.username})")

        elif choice == "3":
            if not sessions:
                print("No active SSH sessions. Please create a session first.")
                continue

            session_idx = int(input("Enter the session number to execute the command: ")) - 1

            if 0 <= session_idx < len(sessions):
                session = sessions[session_idx]

                while True:
                    command = input(f"Enter a command to execute in '{session.current_directory}' (or 'exit' to return to the main menu): ")
                    if command.lower() == "exit":
                        break

                    output = session.execute_command(command)
                    if output is not None:
                        print(output)
            else:
                print("Invalid session number. Please select a valid session.")

        elif choice == "4":
            if not sessions:
                print("No active SSH sessions to close.")
                continue

            session_idx = int(input("Enter the session number to close: ")) - 1

            if 0 <= session_idx < len(sessions):
                session = sessions.pop(session_idx)
                session.close()
            else:
                print("Invalid session number. Please select a valid session.")

        elif choice == "5":
            for session in sessions:
                session.close()
            sys.exit(0)

if __name__ == "__main__":
    main()
