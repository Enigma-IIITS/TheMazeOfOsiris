# The Maze of Osiris

Welcome to **The Maze of Osiris** coding competition! This guide serves as your compass through this exciting labyrinth of challenges. Below, you'll find everything you need to get started, understand the project structure, explore challenges, and contribute to this immersive coding experience.

## Table of Contents

- [The Maze of Osiris](#the-maze-of-osiris)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Cloning the Repository](#cloning-the-repository)
    - [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
    - [Installing Dependencies](#installing-dependencies)
    - [Creating a .env File](#creating-a-env-file)
    - [Creating Test User](#creating-test-user)
    - [Running the Server](#running-the-server)
  - [Managing Teams](#managing-teams)
    - [Adding Teams](#adding-teams)
      - [Updating the `teams_list.csv` File](#updating-the-teams_listcsv-file)
      - [Command Usage](#command-usage)
    - [Example CSV File](#example-csv-file)
  - [Exploring Challenges](#exploring-challenges)
  - [Contributing](#contributing)

## Getting Started

### Cloning the Repository

Begin your journey by cloning the repository from GitHub:

```bash
git clone https://github.com/Enigma-IIITS/TheMazeOfOsiris.git
```

### Setting Up a Virtual Environment

Navigate to the project directory and create a virtual environment:

```bash
cd TheMazeOfOsiris
python -m venv venv
```

Activate the virtual environment:

On Windows:
```bash
venv\Scripts\activate
```

On macOS and Linux:
```bash
source venv/bin/activate
```

### Installing Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

### Creating a .env File

Create a `.env` file in the root directory of the project and add the following environment variables:

```
DATABASE_URL=your_database_url_here
BASE_URL=your_base_url_optional_here
PORT=your_port_optional_here
```

### Creating Test User

To create a test user, use the following command:

```bash
python -m app test
```

### Running the Server

To start the server, run the following command:

By default, the server starts with round_1:
```bash
python -m app
```

If you want to start the server for another round, use the command:
```bash
python -m app <round_folder_name>
```
For example:
```bash
python -m app round_1
```

## Managing Teams

In **The Maze of Osiris**, you have the power to orchestrate your own competitions and assemble teams to embark on thrilling coding adventures. Here's a guide on how to manage competitions and teams using the `teams_list.csv` file and a convenient command.

### Adding Teams

#### Updating the `teams_list.csv` File

To conduct your own competition, update the `teams_list.csv` file with the necessary information:

- **team_name**: Provide the name of each team participating in the competition.
- **email**: Optionally, include the email addresses associated with each team.
- **team_id**: Optionally, assign a unique identifier to each team. If no ID is provided, one will be generated automatically. 

Make sure to maintain the structure of the CSV file for smooth processing.

#### Command Usage

Once the `teams_list.csv` file is updated, you can use the following command to create teams and manage the competition:

```bash
python -m app create path_to_csv
```

### Example CSV File

Here's an example of how the `teams_list.csv` file should be structured:

```csv
team_name,email,team_id
CodeCrackers,test@gmail.com,1659936504ea49d386a6522171500fcb
Turing,test@gmail.com,
```

In this example:

- Team "CodeCrackers" has an associated email address and a manually assigned team ID.
- Team "Turing" has an associated email address but no manually assigned team ID, so one will be generated automatically.

## Exploring Challenges

To explore challenges and their solutions, navigate to the respective round and challenge directories. Each challenge directory contains a `readme.md` file with clear explanations about the challenge and its solution.

## Contributing

Contributions to **The Maze of Osiris** are welcome! While new challenges are not accepted for contribution in this repository, you can fork the repository and add challenges to your own version. Bug fixes and code improvements are still appreciated.