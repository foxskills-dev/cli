import docker
import re
import shutil
import subprocess
import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

try: client = docker.from_env()
except: client = None

def receive_post_request():
    result = {"path": None, "body": None}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            result["path"] = self.path
            content_length = int(self.headers.get('Content-Length', 0))
            result["body"] = self.rfile.read(content_length).decode('utf-8')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    server = HTTPServer(('0.0.0.0', 8080), Handler)
    server.handle_request()
    return result["path"], result["body"]

def get_repo_url(challenge_name):
    return f"https://github.com/foxskills-dev/challenge-{challenge_name}.git"

def repo_exists(repo_url):
    try:
        subprocess.run(
            ["git", "ls-remote", repo_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def get_last_commit_hash(repo_url):
    command = f"git ls-remote {repo_url} HEAD"
    output = subprocess.check_output(command, shell=True, text=True)
    return output.strip().split("\t")[0][:12]

def is_image_up_to_date(challenge_name):
    last_hash = get_last_commit_hash(get_repo_url(challenge_name))
    image_name = f"chall_{challenge_name}-{last_hash}"
    try:
        client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False

def clone_challenge(challenge_name):
    repo_url = get_repo_url(challenge_name)
    destination = f".build-context/{challenge_name}"

    subprocess.run(["git", "clone", repo_url, "."], cwd=destination)

def create_build_context(challenge_name):
    shutil.rmtree(f".build-context/{challenge_name}", ignore_errors=True)
    os.makedirs(f".build-context/{challenge_name}")
    clone_challenge(challenge_name)
    shutil.copytree("fs_lib", f".build-context/{challenge_name}/fs_lib")

def build_challenge_image(challenge_name):
    repo_url = get_repo_url(challenge_name)
    last_hash = get_last_commit_hash(get_repo_url(challenge_name))
    print("[ ! ] Building challenge image...")
    subprocess.run(["docker", "compose", "build"], cwd=f".build-context/{challenge_name}", check=True, env={
        "IMAGE_NAME": f"chall_{challenge_name}-{last_hash}",
        "ARGS": "",
        "RUNNER_CONFIG": json.dumps({
            "challengeRepo": repo_url,
            "additionalPackages": ""
        })
    })

def create_challenge_image(challenge_name):
    print("[ ! ] Creating challenge image...")
    create_build_context(challenge_name)
    build_challenge_image(challenge_name)

def run_challenge_runner(challenge_name, user_challenge_repo):
    if not repo_exists(user_challenge_repo) and not repo_exists(get_repo_url(challenge_name)):
        return False

    if not is_image_up_to_date(challenge_name) or True:
        create_challenge_image(challenge_name)

    last_hash = get_last_commit_hash(get_repo_url(challenge_name))
    args = [user_challenge_repo, "None", "http://192.168.1.71:8080", "123", "321"]
    print("[ ! ] Running challenge runner...")
    subprocess.run(["docker", "compose", "up", "-d"], cwd=f".build-context/{challenge_name}", check=True, env={ #, "-d"
        "IMAGE_NAME": f"chall_{challenge_name}-{last_hash}",
        "ARGS": " ".join(args)
    })

    print("[ ! ] Waiting for challenge runner to start...")
    path, body = receive_post_request()

    json.dump(json.loads(body), open("result.json", "w"), indent=4)

    print("[ ! ] Stopping challenge runner...")
    subprocess.run(["docker", "compose", "down"], cwd=f".build-context/{challenge_name}", check=True, env={
        "IMAGE_NAME": f"chall_{challenge_name}-{last_hash}"
    })

    return True

def create_user_challenge_folder(challenge_name, user_challenge_repo):
    destination = f"./{challenge_name}"
    index = 1
    
    while os.path.exists(destination):
        destination = f"./{challenge_name}-{index}"
        index += 1

    os.makedirs(destination)
    return destination

def init_user_challenge_repo(challenge_name, user_challenge_repo):
    if not repo_exists(user_challenge_repo) and not repo_exists(get_repo_url(challenge_name)):
        print("User challenge repo or challenge does not exist.")
        return

    folder = create_user_challenge_folder(challenge_name, user_challenge_repo)

    subprocess.run(["git", "clone", get_repo_url(challenge_name), folder], check=True)
    subprocess.run(["git", "clone", user_challenge_repo, f"{folder}/app"], check=True)
    shutil.copytree("fs_lib", folder + "/fs_lib")

    subprocess.run(["python3", "-m", "venv", folder + "/venv"], check=True)
    subprocess.run([folder + "/venv/bin/python3", "-m", "pip", "install", "-r", folder + "/fs_lib/build/requirements.txt"], check=True)

def main():
    action = sys.argv[1]

    if action == "verify":
        if not client:
            print("Cannot connect to docker.")
            return
        
        challenge_name = sys.argv[2]
        user_challenge_repo = sys.argv[3]

        print("Running challenge runner...")
        print(f"Challenge name: {challenge_name}")
        print(f"User challenge repo: {user_challenge_repo}")
        run_challenge_runner(challenge_name, user_challenge_repo)
    
    elif action == "init":
        challenge_name = sys.argv[2]
        user_challenge_repo = sys.argv[3]

        print("Initializing user challenge repo...")
        print(f"Challenge name: {challenge_name}")
        print(f"User challenge repo: {user_challenge_repo}")
        init_user_challenge_repo(challenge_name, user_challenge_repo)

if __name__ == "__main__":
    main()