from __future__ import annotations


allowed = {"bash": ("-i", "-c")}

allowed_commands = ("ssh",)

allowed_args = ()

# TODO(GideonBear): populate from explainshell?
replacements = {
    "curl": {
        "-d": "--data",
        "-f": "--fail",
        "-h": "--help",
        "-i": "--include",
        "-o": "--output",
        "-O": "--remote-name",
        "-s": "--silent",
        "-T": "--upload-file",
        "-u": "--user",
        "-A": "--user-agent",
        "-v": "--verbose",
        "-V": "--version",
    }
}
