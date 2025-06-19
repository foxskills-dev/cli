# 🦊 FoxSkills CLI

This CLI will help you to make the link between your developpement environement and FoxSkills. You will also be able to start local projects and tests without any interractions with the FoxSkills website.

## Installation

```bash
git clone https://github.com/foxskills-dev/cli.git
cd cli/
python3 -m venv venv
. venv/bin/activate
# This will be changed to a requirements.txt later
pip install docker
```

## Usage

```bash
python3 cli.py <action> [...args]
```

### Initialize a local project

```bash
python3 cli.py init <challenge-name> <user-repo>
python3 cli.py init helloworld https://github.com/zalo-alex/helloworld-test
```

### Test local project

```bash
cd <project-name>/
. venv/bin/activate
pytest tests.py -v
```

### Verify tests in a container

```bash
python3 cli.py verify <challenge-name> <user-repo> <startup-command>
python3 cli.py verify helloworld https://github.com/zalo-alex/helloworld-test "pip install -r requirements.txt --b && python3 app/app.py"
python3 cli.py verify helloworld https://github.com/zalo-alex/helloworld-test None
```
