# Installation mechanics

Download a fresh `https://github.com/hellsy55/wow-addon-miniloot/archive/refs/heads/new-features.zip` into a unique temporary directory. Expected extracted root: `wow-addon-miniloot-new-features`.
Destination: `C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\MiniLoot`.

Require AddOns to exist. Before touching an existing installation, validate MiniLoot.toc, init.lua, messages.lua, formatter.lua, and settings.lua, plus all runtime paths listed in MiniLoot.toc. Remove root dot-prefixed entries and development metadata such as AGENTS.md, .agents, README.md, and LICENSE from the prepared package. Preserve all runtime files; debug.lua is explicitly loaded by the TOC and must remain.

Move an existing installation to a unique sibling backup only after package validation. Move the prepared replacement into place and validate it. On replacement failure, remove only the replacement created by this transaction and restore the old installation. If rollback fails, retain the backup and report its path. Remove the backup only after confirmed installation. Clean temporary data after success; return a nonzero exit code for every required-stage failure.

Never add AlterEgo-specific handling of Libs, Debug directories, @debug@ / @end-debug@ markers, @project-version@ substitution, or library management. The installer must not consume local repository content.
