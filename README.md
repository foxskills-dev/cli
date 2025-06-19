# 🦊 FoxSkills CLI

This CLI helps bridge your development environment with [FoxSkills](https://foxskills.dev).  
It allows you to initialize local projects and run tests without interacting directly with the FoxSkills website.

## Installation

```bash
git clone https://github.com/foxskills-dev/cli.git
cd cli/
python3 -m venv venv
. venv/bin/activate
# Will be replaced with a requirements.txt soon
pip install docker
```

## Usage

```bash
python3 cli.py <action> [...args]
```

### Initialize a local project

```bash
python3 cli.py init <challenge-name> <user-repo>
# Example:
python3 cli.py init helloworld https://github.com/zalo-alex/helloworld-test
```

### Test the local project

```bash
cd <project-name>/
. venv/bin/activate
pytest tests.py -v
```

### Verify tests in a container

```bash
python3 cli.py verify <challenge-name> <user-repo> <startup-command>
# Example with startup command:
python3 cli.py verify helloworld https://github.com/zalo-alex/helloworld-test "pip install -r requirements.txt --b && python3 app/app.py"
# Example without startup command:
python3 cli.py verify helloworld https://github.com/zalo-alex/helloworld-test None
```
