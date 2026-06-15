#!/usr/bin/env python3
import os
import sys
import shutil
import argparse

def install_path(src, dst, use_symlink=False, relative=False):
    """
    Installs src to dst by either symlinking or copying.
    If dst already exists, it is removed first to ensure a clean install.
    If use_symlink is True, a symlink is created.
    If use_symlink is False, files/directories are copied.
    """
    if os.path.realpath(src) == os.path.realpath(dst):
        print(f"Source and destination resolve to the same path: {dst}. Skipping.")
        return

    if os.path.lexists(dst):
        if os.path.islink(dst):
            print(f"Removing existing symlink: {dst}")
            os.unlink(dst)
        elif os.path.isdir(dst):
            print(f"Removing existing directory: {dst}")
            shutil.rmtree(dst)
        else:
            print(f"Removing existing file: {dst}")
            os.remove(dst)
            
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    
    if use_symlink:
        if relative:
            abs_src = os.path.abspath(src)
            abs_dst_dir = os.path.dirname(os.path.abspath(dst))
            link_target = os.path.relpath(abs_src, abs_dst_dir)
        else:
            link_target = os.path.abspath(src)
            
        os.symlink(link_target, dst)
        print(f"Created symlink: {dst} -> {link_target}")
    else:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            print(f"Copied directory: {src} -> {dst}")
        else:
            shutil.copy2(src, dst)
            print(f"Copied file: {src} -> {dst}")

def add_to_gitignore(repo_path, folder_name):
    """
    Adds the given folder name to the repository's .gitignore file if not already present.
    """
    gitignore_path = os.path.join(repo_path, ".gitignore")
    already_ignored = False
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            line_strip = line.strip()
            # Match variations like folder_name, folder_name/, or lines starting with it
            if line_strip == folder_name or line_strip == f"{folder_name}/" or line_strip.startswith(f"{folder_name} "):
                already_ignored = True
                break
                
    if not already_ignored:
        print(f"Adding {folder_name}/ to {gitignore_path}")
        has_content = os.path.exists(gitignore_path) and os.path.getsize(gitignore_path) > 0
        mode = "a" if has_content else "w"
        with open(gitignore_path, mode) as f:
            if has_content:
                # Ensure there is a newline at the end of the file before appending
                with open(gitignore_path, "r") as f_read:
                    content = f_read.read()
                if content and not content.endswith("\n"):
                    f.write("\n")
            f.write(f"{folder_name}/\n")

def install_skills_and_context(skills_src_dir, agents_src_file, skills_dst_dir, agents_dst_files, skills, use_symlink=False, relative=False):
    """
    Helper function to install skills and context files to a target directory.
    """
    # 1. Install skills
    if skills_dst_dir:
        for skill in skills:
            install_path(
                os.path.join(skills_src_dir, skill),
                os.path.join(skills_dst_dir, skill),
                use_symlink=use_symlink,
                relative=relative
            )
            
    # 2. Install context/AGENTS file(s)
    for dst_file in agents_dst_files:
        install_path(agents_src_file, dst_file, use_symlink=use_symlink, relative=relative)

def main():
    parser = argparse.ArgumentParser(
        description="Install AI agent skills and context files (Gemini, Claude, Pi) globally or locally to a repository."
    )
    parser.add_argument(
        "-u", "--user",
        action="store_true",
        help="Install globally to the current user's home directory (covers Gemini, Claude, Pi)."
    )
    parser.add_argument(
        "-r", "--repo",
        nargs="?",
        const=".",
        type=str,
        help="Path to the target repository (defaults to the current directory if specified without a path)."
    )
    parser.add_argument(
        "-s", "--symlink",
        action="store_true",
        help="Use symbolic links instead of copying actual files/directories."
    )
    parser.add_argument(
        "--only",
        choices=["gemini", "claude", "pi"],
        help="Only install for a specific agent (defaults to installing for all: Gemini, Claude, and Pi)."
    )
    
    args = parser.parse_args()
    
    # If no flags are provided, show help and exit
    if not args.user and args.repo is None:
        parser.print_help()
        sys.exit(1)
        
    # Source paths relative to this script
    source_dir = os.path.dirname(os.path.abspath(__file__))
    skills_src_dir = os.path.join(source_dir, "skills")
    agents_src_file = os.path.join(source_dir, "context", "AGENTS.md")
    
    # Verify sources exist
    if not os.path.isdir(skills_src_dir):
        print(f"Error: Source skills directory not found at {skills_src_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(agents_src_file):
        print(f"Error: Source AGENTS.md file not found at {agents_src_file}", file=sys.stderr)
        sys.exit(1)
        
    # Find all skills (subdirectories in the source skills directory)
    skills = []
    for entry in os.listdir(skills_src_dir):
        entry_path = os.path.join(skills_src_dir, entry)
        if os.path.isdir(entry_path) and not entry.startswith("."):
            skills.append(entry)
            
    print(f"Found {len(skills)} skill(s) to install: {', '.join(skills)}")
    
    target_agents = ["gemini", "claude", "pi"]
    if args.only:
        target_agents = [args.only]
    
    # Install to user if requested
    if args.user:
        print(f"\n--- Installing globally for current user (Agents: {', '.join(target_agents)}) ---")
        
        user_configs = {
            "gemini": {
                "name": "Gemini",
                "skills_dir": os.path.expanduser("~/.gemini/skills"),
                "agents_files": [os.path.expanduser("~/.gemini/AGENTS.md")]
            },
            "claude": {
                "name": "Claude",
                "skills_dir": os.path.expanduser("~/.claude/skills"),
                "agents_files": [os.path.expanduser("~/.claude/CLAUDE.md")]
            },
            "pi": {
                "name": "Pi",
                "skills_dir": os.path.expanduser("~/.pi/agent/skills"),
                "agents_files": [os.path.expanduser("~/.pi/agent/AGENTS.md")]
            }
        }
        
        for agent in target_agents:
            cfg = user_configs[agent]
            print(f"\nConfiguring {cfg['name']}...")
            install_skills_and_context(
                skills_src_dir, agents_src_file,
                cfg["skills_dir"], cfg["agents_files"],
                skills, use_symlink=args.symlink, relative=False
            )
            
        print("\nUser installation complete.")
        
    # Install to repo if requested
    if args.repo is not None:
        target_repo = os.path.abspath(args.repo)
        print(f"\n--- Installing to Repository: {target_repo} (Agents: {', '.join(target_agents)}) ---")
        
        if not os.path.isdir(target_repo):
            print(f"Error: Target repository directory does not exist at {target_repo}", file=sys.stderr)
            sys.exit(1)
            
        repo_configs = {
            "gemini": {
                "name": "Gemini",
                "dot_folders": [".skills", ".agents"],
                "skills_dir": os.path.join(target_repo, ".skills"),
                "agents_files": [os.path.join(target_repo, ".agents", "AGENTS.md")]
            },
            "claude": {
                "name": "Claude",
                "dot_folders": [".claude"],
                "skills_dir": os.path.join(target_repo, ".claude", "skills"),
                "agents_files": [os.path.join(target_repo, ".claude", "CLAUDE.md")]
            },
            "pi": {
                "name": "Pi",
                "dot_folders": [".pi"],
                "skills_dir": os.path.join(target_repo, ".pi", "skills"),
                "agents_files": [
                    os.path.join(target_repo, ".pi", "SYSTEM.md"),
                    os.path.join(target_repo, ".pi", "AGENTS.md")
                ]
            }
        }
        
        # Check if dot-folders existed before creating them
        folders_to_ignore = set()
        for agent in target_agents:
            cfg = repo_configs[agent]
            for folder in cfg["dot_folders"]:
                path = os.path.join(target_repo, folder)
                if not os.path.exists(path):
                    folders_to_ignore.add(folder)
                os.makedirs(path, exist_ok=True)
                
        # Add new dot-folders to .gitignore
        for folder_name in sorted(folders_to_ignore):
            add_to_gitignore(target_repo, folder_name)
            
        # Perform symlink installation
        for agent in target_agents:
            cfg = repo_configs[agent]
            print(f"\nConfiguring {cfg['name']} paths...")
            install_skills_and_context(
                skills_src_dir, agents_src_file,
                cfg["skills_dir"], cfg["agents_files"],
                skills, use_symlink=args.symlink, relative=True
            )
            
        print("\nRepository installation complete.")

if __name__ == "__main__":
    main()
